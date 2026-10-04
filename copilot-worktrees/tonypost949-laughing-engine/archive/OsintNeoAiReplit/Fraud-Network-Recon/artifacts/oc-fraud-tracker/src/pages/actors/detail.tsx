import { ACTORS, TIER_LABELS, type LegalStatus } from "@/data/caseData";
import { useRoute, Link } from "wouter";
import { ArrowLeft, ExternalLink, Link as LinkIcon } from "lucide-react";
import { StatusBadge } from "@/pages/actors/index";
import { Card, CardContent } from "@/components/ui/card";

export default function ActorDetail() {
  const [, params] = useRoute("/actors/:id");
  const id = params?.id;
  const actor = ACTORS.find(a => a.id === id);

  if (!actor) {
    return <div className="p-12 text-center text-muted-foreground">Actor not found.</div>;
  }

  const connections = ACTORS.filter(a => actor.connections.includes(a.id));

  return (
    <div className="max-w-4xl mx-auto p-6 md:p-12 space-y-8">
      <Link href="/actors" className="inline-flex items-center text-sm font-medium text-muted-foreground hover:text-foreground transition-colors mb-4">
        <ArrowLeft className="w-4 h-4 mr-2" /> Back to Network
      </Link>

      <header className="space-y-6 pb-8 border-b">
        <div className="flex flex-wrap items-center gap-4">
          <StatusBadge status={actor.status} />
          <span className="text-sm font-mono text-muted-foreground bg-muted px-2.5 py-1 rounded">
            {TIER_LABELS[actor.tier]}
          </span>
        </div>
        
        <h1 className="text-4xl md:text-5xl font-serif font-bold text-foreground">
          {actor.name}
        </h1>
        
        <div className="text-xl text-foreground/80 font-medium">
          {actor.role}
        </div>
        
        {actor.organization && (
          <div className="text-muted-foreground">
            Organization: <span className="font-medium text-foreground">{actor.organization}</span>
          </div>
        )}
      </header>

      <div className="grid md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-10">
          <section className="space-y-4">
            <h2 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">Legal Status</h2>
            <div className="bg-card p-5 rounded-lg border border-border text-foreground leading-relaxed">
              {actor.statusDetail}
              
              {actor.indictmentDesignation && (
                <div className="mt-4 pt-4 border-t font-mono text-xs text-muted-foreground">
                  Indictment Designation: {actor.indictmentDesignation}
                </div>
              )}
            </div>
            
            {(actor.status === "not_charged" || actor.status === "unnamed_individual") && (
              <div className="text-xs text-muted-foreground/70 italic mt-2">
                Note: This individual has not been criminally charged. Information sourced from civil complaints or implicitly identified in federal indictments.
              </div>
            )}
          </section>

          {actor.crimes && actor.crimes.length > 0 && (
            <section className="space-y-4">
              <h2 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">Allegations & Actions</h2>
              <ul className="space-y-3">
                {actor.crimes.map((crime, i) => (
                  <li key={i} className="flex items-start">
                    <span className="text-destructive mr-3 mt-1.5 text-xs">■</span>
                    <span className="text-foreground leading-relaxed">{crime}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {actor.notes && (
            <section className="space-y-4">
              <h2 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">Investigative Notes</h2>
              <div className="prose prose-sm dark:prose-invert text-muted-foreground leading-relaxed">
                <p>{actor.notes}</p>
              </div>
            </section>
          )}
        </div>

        <div className="space-y-6">
          <h2 className="text-sm font-bold uppercase tracking-widest text-muted-foreground">Known Connections</h2>
          <div className="space-y-3">
            {connections.map(conn => (
              <Link key={conn.id} href={`/actors/${conn.id}`} className="block group">
                <Card className="bg-muted/30 border-border hover:border-primary/50 transition-colors">
                  <CardContent className="p-4 flex items-center justify-between">
                    <div>
                      <div className="font-serif font-bold text-foreground group-hover:text-primary transition-colors">
                        {conn.name}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1 truncate max-w-[150px]">
                        {conn.role}
                      </div>
                    </div>
                    <LinkIcon className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
