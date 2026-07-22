#!/usr/bin/env python3
"""
WebSocket Server for Live Marker Updates
Provides real-time marker updates to the frontend via WebSocket.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Set

try:
    import websockets
except ImportError:
    print("[!] websockets not installed. Run: pip install websockets")
    sys.exit(1)

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("[!] Redis not available, using in-memory pub/sub")

# Global state
connected_clients: Set = set()
marker_cache: Dict = {}
update_queue: asyncio.Queue = asyncio.Queue()

# Redis channels
REDIS_CHANNEL = "osint:markers:update"


class MarkerBroadcast:
    def __init__(self):
        self.redis_client = None
        self.pubsub = None

    async def connect_redis(self):
        """Connect to Redis for pub/sub if available."""
        if not REDIS_AVAILABLE:
            return
        try:
            self.redis_client = redis.from_url(
                os.environ.get("REDIS_URL", "redis://localhost:6379")
            )
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe(REDIS_CHANNEL)
            print("[+] Connected to Redis for pub/sub")
        except Exception as e:
            print(f"[!] Redis connection failed: {e}")
            self.redis_client = None

    async def publish_update(self, marker_data: Dict):
        """Publish marker update to Redis."""
        if self.redis_client:
            try:
                await self.redis_client.publish(
                    REDIS_CHANNEL,
                    json.dumps(marker_data)
                )
            except Exception as e:
                print(f"[!] Redis publish failed: {e}")

        # Also add to local queue
        await update_queue.put(marker_data)

    async def listen_redis(self):
        """Listen for Redis updates and broadcast to clients."""
        if not self.pubsub:
            return

        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    await broadcast_to_clients(data)
        except Exception as e:
            print(f"[!] Redis listen error: {e}")


async def broadcast_to_clients(data: Dict):
    """Broadcast data to all connected WebSocket clients."""
    if not connected_clients:
        return

    message = json.dumps(data)
    disconnected = set()

    for client in connected_clients:
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            disconnected.add(client)
        except Exception as e:
            print(f"[!] Broadcast error: {e}")
            disconnected.add(client)

    # Clean up disconnected clients
    connected_clients.difference_update(disconnected)


async def handle_client(websocket, path=None):
    """Handle individual WebSocket client connection."""
    connected_clients.add(websocket)
    client_id = id(websocket)
    print(f"[+] Client connected: {client_id} (Total: {len(connected_clients)})")

    try:
        # Send current cache on connect
        await websocket.send(json.dumps({
            "type": "init",
            "markers": marker_cache,
            "timestamp": datetime.utcnow().isoformat()
        }))

        # Keep connection alive and handle messages
        async for message in websocket:
            try:
                data = json.loads(message)
                await handle_client_message(websocket, data)
            except json.JSONDecodeError:
                pass
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        connected_clients.discard(websocket)
        print(f"[-] Client disconnected: {client_id} (Total: {len(connected_clients)})")


async def handle_client_message(websocket, data: Dict):
    """Handle messages from clients."""
    msg_type = data.get("type")

    if msg_type == "ping":
        await websocket.send(json.dumps({"type": "pong"}))

    elif msg_type == "request_markers":
        await websocket.send(json.dumps({
            "type": "markers_update",
            "markers": marker_cache,
            "timestamp": datetime.utcnow().isoformat()
        }))

    elif msg_type == "subscribe_domain":
        domain = data.get("domain")
        if domain:
            # Future: per-client subscriptions
            pass


async def marker_updater():
    """Background task that updates markers periodically."""
    while True:
        try:
            # Read from cache file
            cache_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..', 'opencode_work', 'city_markers_cache.json'
            )

            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    new_markers = json.load(f)

                # Check for updates
                if new_markers != marker_cache:
                    marker_cache.clear()
                    marker_cache.update(new_markers)

                    await broadcast_to_clients({
                        "type": "markers_update",
                        "markers": marker_cache,
                        "timestamp": datetime.utcnow().isoformat()
                    })

        except Exception as e:
            print(f"[!] Marker updater error: {e}")

        await asyncio.sleep(5)  # Check every 5 seconds


async def threat_scanner():
    """Background task that runs threat scans periodically."""
    while True:
        try:
            # Import and run threat scans
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

            try:
                from otx_threat_feed import OTXThreatFeed
                from vt_threat_feed import VirusTotalFeed

                otx = OTXThreatFeed()
                vt = VirusTotalFeed()

                # Scan domains that need updating
                for domain, marker in list(marker_cache.items()):
                    last_checked = marker.get("last_threat_check")
                    if not last_checked:
                        # Run scan
                        try:
                            otx_result = otx.scan_target(domain, marker.get("ip"))
                            vt_result = vt.scan_target(domain, marker.get("ip"))

                            marker["otx_threat"] = otx_result.get("threat_info", {})
                            marker["vt_threat"] = vt_result.get("threat_info", {})
                            marker["last_threat_check"] = datetime.utcnow().isoformat()

                            # Update risk score based on combined threats
                            otx_score = marker.get("otx_threat", {}).get("score", 0)
                            vt_score = marker.get("vt_threat", {}).get("score", 0)
                            marker["risk_score"] = max(otx_score, vt_score)

                            await broadcast_to_clients({
                                "type": "marker_threat_update",
                                "domain": domain,
                                "marker": marker,
                                "timestamp": datetime.utcnow().isoformat()
                            })

                        except Exception as e:
                            print(f"[!] Threat scan error for {domain}: {e}")

                        await asyncio.sleep(2)  # Rate limiting

            except ImportError as e:
                print(f"[!] Threat feed modules not available: {e}")

        except Exception as e:
            print(f"[!] Threat scanner error: {e}")

        await asyncio.sleep(300)  # Run every 5 minutes


async def main(host: str = "0.0.0.0", port: int = 8765):
    """Start WebSocket server."""
    print(f"[*] Starting WebSocket server on ws://{host}:{port}")

    # Initialize Redis connection
    broadcaster = MarkerBroadcast()
    await broadcaster.connect_redis()

    # Start background tasks
    asyncio.create_task(marker_updater())
    asyncio.create_task(threat_scanner())
    if broadcaster.pubsub:
        asyncio.create_task(broadcaster.listen_redis())

    # Start WebSocket server
    async with websockets.serve(handle_client, host, port):
        print(f"[+] WebSocket server running on ws://{host}:{port}")
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
    asyncio.run(main(host, port))
