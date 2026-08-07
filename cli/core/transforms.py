import socket
import random
from .entities import Entity, IPAddress, SocialProfile

class Transform:
    name = "BaseTransform"
    input_type = Entity
    output_type = Entity

    def run(self, entity: Entity) -> list[Entity]:
        raise NotImplementedError

class DomainToIP(Transform):
    name = "DomainToIP"

    def run(self, entity: Entity) -> list[Entity]:
        if entity.type != "Domain":
            raise ValueError("Expected Domain entity")
        
        print(f"[*] Resolving domain: {entity.value}")
        try:
            # In a real scenario, use socket.gethostbyname
            # Here we simulate or try a real basic DNS resolution
            ip = socket.gethostbyname(entity.value)
            return [IPAddress(value=ip)]
        except Exception as e:
            print(f"[-] Failed to resolve {entity.value}: {e}")
            return []

class EmailToSocialProfile(Transform):
    name = "EmailToSocialProfile"

    def run(self, entity: Entity) -> list[Entity]:
        if entity.type != "Email":
            raise ValueError("Expected Email entity")
        
        print(f"[*] Searching social profiles for: {entity.value}")
        # Simulated transform
        username = entity.value.split('@')[0]
        networks = ["Twitter", "LinkedIn", "GitHub"]
        results = []
        for net in random.sample(networks, 2):
            results.append(SocialProfile(value=f"{net}: @{username}"))
        
        return results

class IPToShodanInfo(Transform):
    name = "IPToShodanInfo"

    def run(self, entity: Entity) -> list[Entity]:
        if entity.type != "IPAddress":
            raise ValueError("Expected IPAddress entity")
        
        print(f"[*] Querying Shodan for: {entity.value}")
        api_key = os.environ.get("SHODAN_API_KEY")
        if not api_key:
            print("[-] SHODAN_API_KEY not set. Returning dummy data.")
            return [ServiceInfo(value="80/tcp: http"), ServiceInfo(value="443/tcp: https")]
        
        try:
            import shodan
            api = shodan.Shodan(api_key)
            host = api.host(entity.value)
            results = []
            for item in host.get('data', []):
                port = item.get('port')
                results.append(ServiceInfo(value=f"{port}/tcp"))
            return results
        except Exception as e:
            print(f"[-] Shodan query failed: {e}")
            return []

class DomainToVirusTotal(Transform):
    name = "DomainToVirusTotal"

    def run(self, entity: Entity) -> list[Entity]:
        if entity.type != "Domain":
            raise ValueError("Expected Domain entity")
        
        print(f"[*] Querying VirusTotal for: {entity.value}")
        api_key = os.environ.get("VT_API_KEY")
        if not api_key:
            print("[-] VT_API_KEY not set. Returning dummy threat score.")
            return [ThreatScore(value="Score: 2/89 (Low Risk)")]
        
        try:
            import requests
            url = f"https://www.virustotal.com/api/v3/domains/{entity.value}"
            headers = {"x-apikey": api_key}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            stats = data['data']['attributes']['last_analysis_stats']
            malicious = stats.get('malicious', 0)
            total = sum(stats.values())
            return [ThreatScore(value=f"Score: {malicious}/{total}")]
        except Exception as e:
            print(f"[-] VirusTotal query failed: {e}")
            return []

# Registry of available transforms
AVAILABLE_TRANSFORMS = {
    DomainToIP.name.lower(): DomainToIP(),
    EmailToSocialProfile.name.lower(): EmailToSocialProfile(),
    IPToShodanInfo.name.lower(): IPToShodanInfo(),
    DomainToVirusTotal.name.lower(): DomainToVirusTotal()
}
