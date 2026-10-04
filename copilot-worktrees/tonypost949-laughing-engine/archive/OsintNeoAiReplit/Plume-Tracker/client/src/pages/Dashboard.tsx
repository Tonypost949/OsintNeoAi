import { useState } from "react";
import { SidebarProvider } from "@/components/ui/sidebar";
import { LocationsSidebar } from "@/components/LocationsSidebar";
import { HazardMap } from "@/components/HazardMap";
import { useLocations } from "@/hooks/use-locations";

export default function Dashboard() {
  const [selectedLocationId, setSelectedLocationId] = useState<number | null>(null);
  const { data: locations = [] } = useLocations();

  return (
    <SidebarProvider style={{ "--sidebar-width": "22rem" } as React.CSSProperties}>
      <div className="flex h-screen w-full overflow-hidden bg-background">
        <LocationsSidebar 
          selectedId={selectedLocationId} 
          onSelect={setSelectedLocationId} 
        />
        <main className="flex-1 relative h-full flex flex-col">
          {/* Subtle top gradient for depth */}
          <div className="absolute top-0 left-0 right-0 h-24 bg-gradient-to-b from-black/5 to-transparent z-10 pointer-events-none"></div>
          
          <HazardMap 
            locations={locations} 
            selectedId={selectedLocationId}
            onSelect={setSelectedLocationId}
          />
          
          {/* Decorative element conveying "tracker" nature */}
          <div className="absolute bottom-6 right-6 z-10 bg-card/80 backdrop-blur-md border border-border/50 shadow-xl rounded-2xl p-4 flex items-center gap-4 pointer-events-none">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500"></span>
              </span>
              <span className="text-xs font-mono font-medium text-muted-foreground uppercase tracking-wider">
                Live Monitoring
              </span>
            </div>
            <div className="h-4 w-[1px] bg-border"></div>
            <span className="text-xs font-mono font-medium text-foreground">
              {locations.length} Entities
            </span>
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
}
