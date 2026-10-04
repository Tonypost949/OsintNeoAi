import { OUTSTANDING_QUESTIONS, ACTORS } from "@/data/caseData";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Link } from "wouter";
import { HelpCircle } from "lucide-react";

export default function QuestionsIndex() {
  return (
    <div className="max-w-4xl mx-auto p-6 md:p-12 space-y-8">
      <header className="mb-12">
        <h1 className="text-4xl font-serif font-bold text-foreground mb-4">Unresolved Questions</h1>
        <p className="text-lg text-muted-foreground max-w-3xl leading-relaxed">
          Despite federal indictments and civil lawsuits, major gaps remain in the public record. These are the active threads investigative journalists and authorities continue to pursue.
        </p>
      </header>

      <div className="space-y-6">
        {OUTSTANDING_QUESTIONS.map((q) => {
          const relatedActors = q.relatedActors 
            ? ACTORS.filter(a => q.relatedActors?.includes(a.id))
            : [];

          return (
            <Card key={q.id} className="bg-card border-border hover:border-primary/40 transition-colors">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-start gap-3 text-xl font-serif leading-snug">
                  <HelpCircle className="w-6 h-6 text-primary flex-shrink-0 mt-0.5" />
                  {q.question}
                </CardTitle>
              </CardHeader>
              <CardContent className="ml-9">
                <p className="text-muted-foreground leading-relaxed">
                  {q.context}
                </p>

                {relatedActors.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-border flex items-center gap-2 text-sm text-muted-foreground">
                    <span className="font-semibold uppercase tracking-widest text-xs">Relevant Figures:</span>
                    <div className="flex flex-wrap gap-2 ml-2">
                      {relatedActors.map(actor => (
                        <Link 
                          key={actor.id} 
                          href={`/actors/${actor.id}`}
                          className="hover:text-primary underline decoration-border underline-offset-2 transition-colors"
                        >
                          {actor.name}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
