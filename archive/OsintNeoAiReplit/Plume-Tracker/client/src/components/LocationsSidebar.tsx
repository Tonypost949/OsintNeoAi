import { AlertTriangle, MapPin, Search } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Sidebar, 
  SidebarContent, 
  SidebarHeader,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
} from "@/components/ui/sidebar";
import { useLocations } from "@/hooks/use-locations";
import { CreateLocationDialog } from "./CreateLocationDialog";
import { LocationResponse } from "@shared/schema";
import { Input } from "./ui/input";
import { useState } from "react";

interface LocationsSidebarProps {
  selectedId: number | null;
  onSelect: (id: number) => void;
}

export function LocationsSidebar({ selectedId, onSelect }: LocationsSidebarProps) {
  const { data: locations, isLoading } = useLocations();
  const [search, setSearch] = useState("");

  const filteredLocations = locations?.filter(loc => 
    loc.name.toLowerCase().includes(search.toLowerCase()) || 
    loc.description.toLowerCase().includes(search.toLowerCase())
  );

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-500 hover:bg-red-600 border-red-600 text-white';
      case 'high': return 'bg-orange-500 hover:bg-orange-600 border-orange-600 text-white';
      case 'warning': return 'bg-amber-400 hover:bg-amber-500 border-amber-500 text-amber-950';
      default: return 'bg-slate-200 hover:bg-slate-300 text-slate-800';
    }
  };

  return (
    <Sidebar className="border-r border-border bg-sidebar/50 backdrop-blur-xl">
      <SidebarHeader className="p-4 space-y-4">
        <div className="flex items-center gap-2 px-2">
          <div className="p-2 bg-primary text-primary-foreground rounded-lg shadow-sm">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <h1 className="font-display text-xl font-bold tracking-tight text-foreground">
            EnviroTrack
          </h1>
        </div>
        
        <CreateLocationDialog />
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input 
            placeholder="Search locations..." 
            className="pl-9 bg-background/50"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            Registered Hazards
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <ScrollArea className="h-[calc(100vh-220px)] px-2">
              {isLoading ? (
                <div className="p-4 text-sm text-muted-foreground text-center animate-pulse">
                  Loading location data...
                </div>
              ) : filteredLocations?.length === 0 ? (
                <div className="p-4 text-sm text-muted-foreground text-center">
                  No hazards found.
                </div>
              ) : (
                <div className="space-y-2 pb-4">
                  {filteredLocations?.map((loc) => (
                    <button
                      key={loc.id}
                      onClick={() => onSelect(loc.id)}
                      className={`w-full text-left p-3 rounded-xl transition-all duration-200 border
                        ${selectedId === loc.id 
                          ? 'bg-primary/5 border-primary/20 shadow-sm' 
                          : 'bg-transparent border-transparent hover:bg-muted/50 hover:border-border/50'
                        }
                      `}
                    >
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <h3 className="font-display font-semibold text-sm truncate flex-1">
                          {loc.name}
                        </h3>
                        <Badge variant="outline" className={`text-[10px] px-1.5 py-0 border ${getSeverityColor(loc.severity)}`}>
                          {loc.severity}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground line-clamp-2 mb-2 leading-relaxed">
                        {loc.description}
                      </p>
                      <div className="flex items-center gap-3 text-[10px] text-muted-foreground font-medium">
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3 h-3" />
                          {loc.type}
                        </span>
                        <span className="opacity-50">•</span>
                        <span className="font-mono">{parseFloat(loc.latitude).toFixed(4)}, {parseFloat(loc.longitude).toFixed(4)}</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </ScrollArea>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
