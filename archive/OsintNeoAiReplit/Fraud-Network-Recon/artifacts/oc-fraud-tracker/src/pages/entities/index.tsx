import { ENTITIES, ACTORS } from "@/data/caseData";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Building2, Utensils, Home, CircleDashed, Users, DollarSign } from "lucide-react";
import { Link } from "wouter";

const TYPE_ICONS = {
  nonprofit: Users,
  shell_company: Building2,
  restaurant: Utensils,
  real_estate: Home,
  government: Building2,
  church: Home,
  unknown: CircleDashed
};

export default function EntitiesIndex() {
  return (
    <div className="max-w-6xl mx-auto p-6 md:p-12 space-y-8">
      <header className="mb-12">
        <h1 className="text-4xl font-serif font-bold text-foreground mb-4">Organizations & Shell Entities</h1>
        <p className="text-lg text-muted-foreground max-w-3xl leading-relaxed">
          The network of nonprofits, shell companies, and businesses used to launder and distribute stolen county funds.
        </p>
      </header>

      <div className="grid md:grid-cols-2 gap-6">
        {ENTITIES.map(entity => {
          const Icon = TYPE_ICONS[entity.type] || CircleDashed;
          const relatedActors = ACTORS.filter(a => entity.relatedActors.includes(a.id));

          return (
            <Card key={entity.id} className="bg-card border-border overflow-hidden flex flex-col">
              <div className="bg-muted/50 p-4 border-b flex justify-between items-center">
                <span className="text-xs font-mono font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                  <Icon size={14} />
                  {entity.type.replace('_', ' ')}
                </span>
                {entity.fundsReceived && (
                  <span className="text-sm font-bold text-primary flex items-center">
                    <DollarSign size={14} className="mr-1"/>
                    {entity.fundsReceived}
                  </span>
                )}
              </div>
              <CardContent className="p-6 flex-1 flex flex-col">
                <h3 className="font-serif text-2xl font-bold text-foreground mb-3">{entity.name}</h3>
                <p className="text-sm text-foreground/80 leading-relaxed mb-6 font-medium">
                  {entity.role}
                </p>
                
                {entity.notes && (
                  <p className="text-sm text-muted-foreground mb-6 leading-relaxed bg-muted/20 p-3 rounded border border-border/50">
                    {entity.notes}
                  </p>
                )}

                <div className="mt-auto pt-4 border-t border-border/50">
                  <h4 className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-3">Linked Individuals</h4>
                  <div className="flex flex-wrap gap-2">
                    {relatedActors.map(actor => (
                      <Link 
                        key={actor.id} 
                        href={`/actors/${actor.id}`}
                        className="text-xs px-2.5 py-1 rounded bg-muted text-muted-foreground hover:bg-primary/10 hover:text-primary transition-colors border border-border"
                      >
                        {actor.name}
                      </Link>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
