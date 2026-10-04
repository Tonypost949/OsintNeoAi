import { CASE_SUMMARY, ACTORS, ENTITIES } from "@/data/caseData";
import { Link } from "wouter";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowRight, BookOpen, AlertTriangle, Users, Building2 } from "lucide-react";
import { motion } from "framer-motion";

export default function Overview() {
  const stats = {
    indicted: ACTORS.filter(a => a.status === "indicted" || a.status === "convicted" || a.status === "fugitive").length,
    convicted: ACTORS.filter(a => a.status === "convicted").length,
    fugitive: ACTORS.filter(a => a.status === "fugitive").length,
    civil: ACTORS.filter(a => a.status === "civil_defendant").length,
    entities: ENTITIES.length
  };

  return (
    <div className="max-w-5xl mx-auto p-6 md:p-12 space-y-12">
      <header className="space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-destructive/10 text-destructive text-sm font-medium border border-destructive/20">
          <AlertTriangle size={16} />
          Active Federal Prosecution
        </div>
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-serif font-bold text-foreground leading-tight tracking-tight">
          {CASE_SUMMARY.totalStolen} in COVID Relief Funds Stolen
        </h1>
        <div className="text-xl md:text-2xl text-muted-foreground font-serif leading-relaxed max-w-3xl">
          {CASE_SUMMARY.title}
        </div>
      </header>

      <section className="prose prose-lg dark:prose-invert prose-headings:font-serif prose-p:text-muted-foreground prose-p:leading-relaxed max-w-4xl">
        <p className="text-xl text-foreground font-medium border-l-4 border-primary pl-6 py-2">
          {CASE_SUMMARY.fraudMechanism}
        </p>
      </section>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="bg-card border-border hover:border-primary/50 transition-colors">
          <CardContent className="p-6">
            <div className="text-4xl font-mono text-foreground mb-2">{stats.indicted}</div>
            <div className="text-sm text-muted-foreground uppercase tracking-wider font-medium">Charged</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border hover:border-primary/50 transition-colors">
          <CardContent className="p-6">
            <div className="text-4xl font-mono text-destructive mb-2">{stats.convicted}</div>
            <div className="text-sm text-muted-foreground uppercase tracking-wider font-medium">Convictions</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border hover:border-primary/50 transition-colors">
          <CardContent className="p-6">
            <div className="text-4xl font-mono text-orange-500 mb-2">{stats.fugitive}</div>
            <div className="text-sm text-muted-foreground uppercase tracking-wider font-medium">Fugitives</div>
          </CardContent>
        </Card>
        <Card className="bg-card border-border hover:border-primary/50 transition-colors">
          <CardContent className="p-6">
            <div className="text-4xl font-mono text-foreground mb-2">{stats.entities}</div>
            <div className="text-sm text-muted-foreground uppercase tracking-wider font-medium">Shell Entities</div>
          </CardContent>
        </Card>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <Link href="/actors" className="group block">
          <Card className="h-full border-border hover:border-primary transition-all duration-300 hover:shadow-md bg-gradient-to-br from-card to-card/50">
            <CardContent className="p-8 flex flex-col h-full">
              <Users className="w-8 h-8 text-primary mb-4" />
              <h3 className="text-2xl font-serif font-bold mb-2 group-hover:text-primary transition-colors">The Network</h3>
              <p className="text-muted-foreground flex-1">
                Profiles of the politicians, family members, and associates involved in the scheme.
              </p>
              <div className="flex items-center text-primary font-medium mt-6 group-hover:translate-x-1 transition-transform">
                View Individuals <ArrowRight className="ml-2 w-4 h-4" />
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/money-flow" className="group block">
          <Card className="h-full border-border hover:border-primary transition-all duration-300 hover:shadow-md bg-gradient-to-br from-card to-card/50">
            <CardContent className="p-8 flex flex-col h-full">
              <BookOpen className="w-8 h-8 text-primary mb-4" />
              <h3 className="text-2xl font-serif font-bold mb-2 group-hover:text-primary transition-colors">Follow the Money</h3>
              <p className="text-muted-foreground flex-1">
                How millions in public funds were funneled through fake nonprofits to purchase luxury real estate.
              </p>
              <div className="flex items-center text-primary font-medium mt-6 group-hover:translate-x-1 transition-transform">
                View Flows <ArrowRight className="ml-2 w-4 h-4" />
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      <section className="bg-muted/30 p-8 rounded-lg border border-border">
        <h3 className="text-sm font-bold uppercase tracking-widest text-muted-foreground mb-6">Primary Sources</h3>
        <ul className="space-y-3">
          {CASE_SUMMARY.primarySources.map((source, i) => (
            <li key={i} className="flex items-start text-sm text-foreground/80">
              <span className="text-primary mr-3 mt-0.5">•</span>
              {source}
            </li>
          ))}
        </ul>
        <div className="mt-8 pt-6 border-t text-xs text-muted-foreground font-mono">
          Case Number: {CASE_SUMMARY.caseNumber}
          <br />
          Data compiled: {CASE_SUMMARY.compiledDate}
        </div>
      </section>
    </div>
  );
}
