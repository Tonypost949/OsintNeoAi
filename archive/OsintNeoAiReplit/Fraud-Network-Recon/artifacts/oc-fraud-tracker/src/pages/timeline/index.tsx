import { TIMELINE, CATEGORY_COLORS, ACTORS } from "@/data/caseData";
import { Link } from "wouter";

export default function TimelineIndex() {
  return (
    <div className="max-w-4xl mx-auto p-6 md:p-12 space-y-12">
      <header>
        <h1 className="text-4xl font-serif font-bold text-foreground mb-4">Chronology of Events</h1>
        <p className="text-lg text-muted-foreground max-w-2xl leading-relaxed">
          From the initial authorization of funds to federal indictments and flight.
        </p>
      </header>

      <div className="relative border-l-2 border-muted ml-4 md:ml-6 pb-8">
        {TIMELINE.map((item, i) => {
          const actors = ACTORS.filter(a => item.actors?.includes(a.id));
          const colorClass = CATEGORY_COLORS[item.category] || "bg-muted";

          return (
            <div key={i} className="mb-10 ml-8 relative group">
              <span className={`absolute -left-[41px] top-1 h-5 w-5 rounded-full border-4 border-background ${colorClass} shadow-sm group-hover:scale-125 transition-transform`} />
              
              <div className="flex flex-col md:flex-row md:items-baseline gap-2 md:gap-4 mb-2">
                <time className="text-sm font-mono font-bold text-foreground/70 bg-muted/50 px-2 py-0.5 rounded w-fit">
                  {item.date}
                </time>
                <span className="text-xs uppercase tracking-widest font-semibold text-muted-foreground">
                  {item.category}
                </span>
              </div>
              
              <div className="bg-card p-5 rounded-lg border border-border shadow-sm group-hover:border-primary/40 transition-colors">
                <p className="text-lg text-foreground font-medium leading-relaxed">
                  {item.event}
                </p>
                
                {item.amount && (
                  <div className="mt-3 text-lg font-mono font-bold text-primary">
                    {item.amount}
                  </div>
                )}

                {actors.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-border flex flex-wrap gap-2">
                    {actors.map(actor => (
                      <Link 
                        key={actor.id} 
                        href={`/actors/${actor.id}`}
                        className="text-xs font-medium text-muted-foreground hover:text-primary transition-colors underline decoration-border underline-offset-4"
                      >
                        {actor.name}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
