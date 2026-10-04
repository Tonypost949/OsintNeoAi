import { ACTORS, TIER_LABELS, STATUS_LABELS, STATUS_COLORS, type LegalStatus, type ActorTier } from "@/data/caseData";
import { Link } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useState, useMemo } from "react";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export function StatusBadge({ status }: { status: LegalStatus }) {
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${STATUS_COLORS[status]}`}>
      {STATUS_LABELS[status]}
    </span>
  );
}

export default function ActorsIndex() {
  const [search, setSearch] = useState("");
  const [tierFilter, setTierFilter] = useState<ActorTier | "all">("all");
  const [statusFilter, setStatusFilter] = useState<LegalStatus | "all">("all");

  const filteredActors = useMemo(() => {
    return ACTORS.filter(actor => {
      const matchesSearch = actor.name.toLowerCase().includes(search.toLowerCase()) || 
                            actor.role.toLowerCase().includes(search.toLowerCase());
      const matchesTier = tierFilter === "all" || actor.tier === tierFilter;
      const matchesStatus = statusFilter === "all" || actor.status === statusFilter;
      return matchesSearch && matchesTier && matchesStatus;
    });
  }, [search, tierFilter, statusFilter]);

  return (
    <div className="max-w-6xl mx-auto p-6 md:p-12 space-y-8">
      <header>
        <h1 className="text-4xl font-serif font-bold text-foreground mb-4">Individuals</h1>
        <p className="text-lg text-muted-foreground max-w-3xl leading-relaxed">
          The network of politicians, family members, associates, and public officials implicated in the scheme.
        </p>
      </header>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input 
            placeholder="Search by name or role..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 bg-card border-border"
            data-testid="input-search-actors"
          />
        </div>
        <Select value={tierFilter} onValueChange={(v: any) => setTierFilter(v)}>
          <SelectTrigger className="w-full md:w-[220px] bg-card border-border" data-testid="select-tier">
            <SelectValue placeholder="All Tiers" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Network Tiers</SelectItem>
            {Object.entries(TIER_LABELS).map(([key, label]) => (
              <SelectItem key={key} value={key}>{label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={statusFilter} onValueChange={(v: any) => setStatusFilter(v)}>
          <SelectTrigger className="w-full md:w-[220px] bg-card border-border" data-testid="select-status">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Legal Statuses</SelectItem>
            {Object.entries(STATUS_LABELS).map(([key, label]) => (
              <SelectItem key={key} value={key}>{label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredActors.map(actor => (
          <Link key={actor.id} href={`/actors/${actor.id}`} className="group">
            <Card className="h-full border-border hover:border-primary/50 transition-colors bg-card hover:bg-card/80">
              <CardHeader className="pb-3 space-y-4">
                <div className="flex justify-between items-start gap-4">
                  <CardTitle className="font-serif text-xl group-hover:text-primary transition-colors">
                    {actor.name}
                  </CardTitle>
                  <StatusBadge status={actor.status} />
                </div>
                <div className="text-sm font-medium text-foreground/80">
                  {actor.role}
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-xs text-muted-foreground line-clamp-3 leading-relaxed">
                  {actor.statusDetail}
                </div>
                <div className="mt-4 pt-4 border-t border-border flex justify-between items-center text-xs text-muted-foreground font-mono">
                  <span>{TIER_LABELS[actor.tier]}</span>
                  {actor.crimes && <span>{actor.crimes.length} Allegations</span>}
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
      
      {filteredActors.length === 0 && (
        <div className="text-center py-20 text-muted-foreground">
          No individuals match your current filters.
        </div>
      )}
    </div>
  );
}
