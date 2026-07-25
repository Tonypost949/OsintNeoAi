import { useEffect, useRef, useState } from "react";
import { MapView } from "@/components/Map";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MapPin, RefreshCw, Shield, Globe, Server, Loader2 } from "lucide-react";
import { trpc } from "@/lib/trpc";

interface Marker {
  id: string;
  domain: string;
  ip: string;
  city: string;
  state: string;
  country: string;
  lat: number | null;
  lng: number | null;
  isp?: string;
  org?: string;
  org_type: string;
  risk_score: number;
  source: string;
  last_updated: string;
}

interface Stats {
  total: number;
  cities: string[];
  last_updated: string;
}

export default function CityCyberReconMap() {
  const mapRef = useRef<google.maps.Map | null>(null);
  const markersRef = useRef<google.maps.marker.AdvancedMarkerElement[]>([]);
  const [selectedMarker, setSelectedMarker] = useState<Marker | null>(null);

  const { data, isLoading, error, refetch } = trpc.markers.list.useQuery();
  const markers: Marker[] = data?.markers || [];
  const stats: Stats | null = data?.stats || null;

  useEffect(() => {
    if (!mapRef.current || markers.length === 0) return;

    // Clear existing markers
    markersRef.current.forEach((m) => m.setMap(null));
    markersRef.current = [];

    // Add new markers
    markers.forEach((marker) => {
      if (!marker.lat || !marker.lng) return;

      const markerElement = new google.maps.marker.AdvancedMarkerElement({
        map: mapRef.current!,
        position: { lat: marker.lat, lng: marker.lng },
        title: marker.domain,
      });

      const infoWindow = new google.maps.InfoWindow({
        content: `
          <div style="padding: 8px; max-width: 280px;">
            <h3 style="font-weight: bold; margin: 0 0 4px 0; font-size: 14px;">${marker.domain}</h3>
            <p style="margin: 2px 0; font-size: 12px; color: #666;">${marker.city}, ${marker.state}</p>
            <p style="margin: 2px 0; font-size: 12px; color: #666;">IP: ${marker.ip}</p>
            ${marker.isp ? `<p style="margin: 2px 0; font-size: 12px; color: #666;">ISP: ${marker.isp}</p>` : ""}
            <div style="margin-top: 8px;">
              <span style="background: ${marker.risk_score > 70 ? "#ef4444" : marker.risk_score > 40 ? "#f59e0b" : "#22c55e"}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">
                Risk: ${marker.risk_score}
              </span>
            </div>
          </div>
        `,
      });

      markerElement.addListener("click", () => {
        infoWindow.open(mapRef.current, markerElement);
        setSelectedMarker(marker);
      });

      markersRef.current.push(markerElement);
    });

    // Fit bounds to markers
    if (markersRef.current.length > 0) {
      const bounds = new google.maps.LatLngBounds();
      markersRef.current.forEach((m) => {
        if (m.position) bounds.extend(m.position as google.maps.LatLng);
      });
      mapRef.current?.fitBounds(bounds, 50);
    }
  }, [markers]);

  const handleMapReady = (map: google.maps.Map) => {
    mapRef.current = map;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-800/80 bg-slate-900/40 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/10">
              <MapPin className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                City Cyber Recon Map
              </h1>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest">
                  Live Geolocation Feed
                </span>
              </div>
            </div>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isLoading}
            className="border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white transition-all"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {/* Loading State */}
        {isLoading && (
          <div className="h-[600px] flex items-center justify-center bg-slate-900/20 rounded-xl border border-slate-800/60">
            <div className="text-center">
              <Loader2 className="w-10 h-10 animate-spin text-cyan-400 mx-auto mb-4" />
              <p className="text-slate-400 font-medium">Loading reconnaissance data...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="h-[600px] flex items-center justify-center bg-slate-900/20 rounded-xl border border-slate-800/60">
            <div className="text-center">
              <Shield className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <p className="text-red-400 mb-2">Failed to load marker data</p>
              <p className="text-slate-500 text-sm mb-4">{error.message}</p>
              <Button variant="outline" onClick={() => refetch()} className="text-slate-400">
                Retry
              </Button>
            </div>
          </div>
        )}

        {/* Stats Bar */}
        {!isLoading && !error && stats && (
          <>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <Card className="bg-slate-900/40 border-slate-800/60">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <Globe className="w-5 h-5 text-cyan-400" />
                    <div>
                      <p className="text-2xl font-bold text-white">{stats.total}</p>
                      <p className="text-xs text-slate-400">Total Targets</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-slate-900/40 border-slate-800/60">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <MapPin className="w-5 h-5 text-emerald-400" />
                    <div>
                      <p className="text-2xl font-bold text-white">{stats.cities?.length || 0}</p>
                      <p className="text-xs text-slate-400">Unique Cities</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-slate-900/40 border-slate-800/60">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <Shield className="w-5 h-5 text-amber-400" />
                    <div>
                      <p className="text-2xl font-bold text-white">
                        {markers.filter((m) => m.risk_score > 70).length}
                      </p>
                      <p className="text-xs text-slate-400">High Risk</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-slate-900/40 border-slate-800/60">
                <CardContent className="p-4">
                  <div className="flex items-center gap-3">
                    <Server className="w-5 h-5 text-purple-400" />
                    <div>
                      <p className="text-2xl font-bold text-white">
                        {markers.filter((m) => m.source === "geoip2").length}
                      </p>
                      <p className="text-xs text-slate-400">GeoIP2 Local</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Map Container */}
            <Card className="bg-slate-900/40 border-slate-800/60 overflow-hidden">
              <CardHeader className="border-b border-slate-800/50 pb-3">
                <CardTitle className="text-white text-sm font-semibold flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-cyan-400" />
                  Geographic Reconnaissance View
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <MapView
                  className="h-[600px]"
                  initialCenter={{ lat: 33.7, lng: -117.9 }}
                  initialZoom={10}
                  onMapReady={handleMapReady}
                />
              </CardContent>
            </Card>

            {/* Selected Marker Details */}
            {selectedMarker && (
              <Card className="mt-6 bg-slate-900/40 border-slate-800/60">
                <CardHeader className="border-b border-slate-800/50 pb-3">
                  <CardTitle className="text-white text-sm font-semibold">
                    Target Details: {selectedMarker.domain}
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-xs text-slate-400 mb-1">IP Address</p>
                      <p className="text-sm text-white font-mono">{selectedMarker.ip}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Location</p>
                      <p className="text-sm text-white">
                        {selectedMarker.city}, {selectedMarker.state}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">ISP</p>
                      <p className="text-sm text-white">{selectedMarker.isp || "N/A"}</p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Risk Score</p>
                      <Badge
                        variant="outline"
                        className={
                          selectedMarker.risk_score > 70
                            ? "border-red-500 text-red-400"
                            : selectedMarker.risk_score > 40
                            ? "border-amber-500 text-amber-400"
                            : "border-emerald-500 text-emerald-400"
                        }
                      >
                        {selectedMarker.risk_score}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Markers Table */}
            {markers.length > 0 && (
              <Card className="mt-6 bg-slate-900/40 border-slate-800/60">
                <CardHeader className="border-b border-slate-800/50 pb-3">
                  <CardTitle className="text-white text-sm font-semibold">
                    All Targets ({markers.length})
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-800/50">
                          <th className="text-left p-3 text-slate-400 font-medium">Domain</th>
                          <th className="text-left p-3 text-slate-400 font-medium">City</th>
                          <th className="text-left p-3 text-slate-400 font-medium">IP</th>
                          <th className="text-left p-3 text-slate-400 font-medium">Type</th>
                          <th className="text-left p-3 text-slate-400 font-medium">Risk</th>
                          <th className="text-left p-3 text-slate-400 font-medium">Source</th>
                        </tr>
                      </thead>
                      <tbody>
                        {markers.slice(0, 20).map((marker) => (
                          <tr
                            key={marker.id}
                            className="border-b border-slate-800/30 hover:bg-slate-800/20 cursor-pointer"
                            onClick={() => setSelectedMarker(marker)}
                          >
                            <td className="p-3 text-white font-mono text-xs">{marker.domain}</td>
                            <td className="p-3 text-slate-300">
                              {marker.city}, {marker.state}
                            </td>
                            <td className="p-3 text-slate-300 font-mono text-xs">{marker.ip}</td>
                            <td className="p-3">
                              <Badge variant="outline" className="border-slate-700 text-slate-400 text-xs">
                                {marker.org_type}
                              </Badge>
                            </td>
                            <td className="p-3">
                              <Badge
                                variant="outline"
                                className={
                                  marker.risk_score > 70
                                    ? "border-red-500/50 text-red-400"
                                    : marker.risk_score > 40
                                    ? "border-amber-500/50 text-amber-400"
                                    : "border-emerald-500/50 text-emerald-400"
                                }
                              >
                                {marker.risk_score}
                              </Badge>
                            </td>
                            <td className="p-3 text-slate-400 text-xs">{marker.source}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </main>
    </div>
  );
}
