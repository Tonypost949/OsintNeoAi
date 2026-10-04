import { MONEY_FLOWS } from "@/data/caseData";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowRight, AlertCircle } from "lucide-react";

export default function MoneyFlowIndex() {
  return (
    <div className="max-w-5xl mx-auto p-6 md:p-12 space-y-8">
      <header className="mb-12">
        <h1 className="text-4xl font-serif font-bold text-foreground mb-4">Follow the Money</h1>
        <p className="text-lg text-muted-foreground max-w-3xl leading-relaxed">
          How millions in federal COVID relief funds were redirected from pandemic meals into private real estate, luxury goods, and political bribes.
        </p>
      </header>

      <div className="space-y-6">
        {MONEY_FLOWS.map((flow, i) => (
          <Card key={i} className="bg-card border-border overflow-hidden">
            <div className="flex flex-col md:flex-row">
              {/* Flow Visual */}
              <div className="p-6 md:w-2/5 bg-muted/20 flex flex-col justify-center border-b md:border-b-0 md:border-r border-border">
                <div className="flex items-center justify-between text-sm font-mono text-muted-foreground">
                  <div className="font-bold text-foreground max-w-[120px] truncate">{flow.from.replace(/-/g, ' ')}</div>
                  <ArrowRight className="text-primary w-5 h-5 mx-2 flex-shrink-0" />
                  <div className="font-bold text-foreground max-w-[120px] text-right truncate">{flow.to.replace(/-/g, ' ')}</div>
                </div>
                <div className="mt-4 text-3xl font-serif font-bold text-primary text-center">
                  {flow.amount}
                </div>
              </div>
              
              {/* Details */}
              <div className="p-6 md:w-3/5 flex flex-col justify-center">
                <p className="text-lg text-foreground font-medium leading-relaxed">
                  {flow.description}
                </p>
                {flow.legalCharge && (
                  <div className="mt-4 flex items-center text-sm font-medium text-destructive bg-destructive/10 px-3 py-2 rounded-md w-fit border border-destructive/20">
                    <AlertCircle className="w-4 h-4 mr-2" />
                    Charged as: {flow.legalCharge}
                  </div>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
