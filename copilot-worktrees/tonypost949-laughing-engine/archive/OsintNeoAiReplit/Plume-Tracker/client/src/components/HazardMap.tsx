import { useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { LocationResponse } from '@shared/schema';
import { AlertTriangle, Droplet, Radio } from 'lucide-react';
import { createRoot } from 'react-dom/client';
import { Badge } from '@/components/ui/badge';

interface HazardMapProps {
  locations: LocationResponse[];
  selectedId: number | null;
  onSelect: (id: number) => void;
}

// Component to handle flying to selected location
function MapController({ selectedLocation }: { selectedLocation?: LocationResponse }) {
  const map = useMap();
  
  useEffect(() => {
    if (selectedLocation) {
      const lat = parseFloat(selectedLocation.latitude);
      const lng = parseFloat(selectedLocation.longitude);
      if (!isNaN(lat) && !isNaN(lng)) {
        map.flyTo([lat, lng], 16, { duration: 1.5 });
      }
    }
  }, [selectedLocation, map]);

  return null;
}

// Create completely custom pure CSS markers to bypass asset pipelines and match design system
const createCustomIcon = (type: string, severity: string, isSelected: boolean) => {
  let bgColor = 'bg-slate-500';
  let shadowColor = 'shadow-slate-500/50';
  
  if (severity === 'critical') {
    bgColor = 'bg-red-500';
    shadowColor = 'shadow-red-500/50';
  } else if (severity === 'high') {
    bgColor = 'bg-orange-500';
    shadowColor = 'shadow-orange-500/50';
  } else if (severity === 'warning') {
    bgColor = 'bg-amber-400';
    shadowColor = 'shadow-amber-400/50';
  }

  const selectedRing = isSelected ? 'ring-4 ring-primary/20 scale-110' : '';

  return L.divIcon({
    className: 'bg-transparent border-none',
    html: `
      <div class="relative flex items-center justify-center w-6 h-6">
        <div class="absolute inset-0 rounded-full ${bgColor} shadow-lg ${shadowColor} border-2 border-white transition-transform duration-300 ${selectedRing}"></div>
        <div class="absolute -bottom-1 left-1/2 w-1.5 h-1.5 -translate-x-1/2 rotate-45 ${bgColor} border-r-2 border-b-2 border-white z-0"></div>
      </div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 24],
    popupAnchor: [0, -26],
  });
};

export function HazardMap({ locations, selectedId, onSelect }: HazardMapProps) {
  const selectedLocation = useMemo(() => 
    locations.find(loc => loc.id === selectedId), 
  [locations, selectedId]);

  return (
    <div className="w-full h-full relative bg-muted/20">
      <MapContainer 
        center={[33.68, -117.99]} 
        zoom={13} 
        className="w-full h-full z-[1]"
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />
        
        <MapController selectedLocation={selectedLocation} />

        {locations.map((loc) => {
          const lat = parseFloat(loc.latitude);
          const lng = parseFloat(loc.longitude);
          
          // Skip invalid coordinates
          if (isNaN(lat) || isNaN(lng)) return null;

          const isSelected = selectedId === loc.id;

          return (
            <Marker 
              key={loc.id} 
              position={[lat, lng]}
              icon={createCustomIcon(loc.type, loc.severity, isSelected)}
              eventHandlers={{
                click: () => onSelect(loc.id),
              }}
            >
              <Popup className="custom-popup border-0 bg-transparent p-0 m-0">
                <div className="p-4 w-64 space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-display font-bold text-sm leading-tight m-0">{loc.name}</h4>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium tracking-wide uppercase
                      ${loc.severity === 'critical' ? 'bg-red-100 text-red-700' :
                        loc.severity === 'high' ? 'bg-orange-100 text-orange-700' :
                        'bg-amber-100 text-amber-800'}`}
                    >
                      {loc.severity}
                    </span>
                  </div>
                  
                  <p className="text-xs text-muted-foreground m-0 leading-relaxed">
                    {loc.description}
                  </p>
                  
                  <div className="pt-2 mt-2 border-t border-border flex justify-between items-center text-[10px] text-muted-foreground font-mono">
                    <span className="capitalize">{loc.type}</span>
                    <span>{lat.toFixed(4)}, {lng.toFixed(4)}</span>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
      
      {/* Absolute overlay for visual framing */}
      <div className="absolute inset-0 pointer-events-none border-[12px] border-background/20 z-[2] mix-blend-overlay"></div>
    </div>
  );
}
