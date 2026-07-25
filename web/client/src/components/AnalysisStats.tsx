import { Card, CardContent } from "@/components/ui/card";
import { Users, Mail, Phone, Link2 } from "lucide-react";

interface AnalysisStatsProps {
  analysis: {
    filesAnalyzed: number;
    peopleFound: number;
    relationshipsFound: number;
    status: string;
  };
}

export default function AnalysisStats({ analysis }: AnalysisStatsProps) {
  const stats = [
    {
      label: "Files Analyzed",
      value: analysis.filesAnalyzed,
      icon: "📄",
      color: "bg-blue-50 text-blue-700",
    },
    {
      label: "People Found",
      value: analysis.peopleFound,
      icon: "👥",
      color: "bg-purple-50 text-purple-700",
    },
    {
      label: "Relationships",
      value: analysis.relationshipsFound,
      icon: "🔗",
      color: "bg-green-50 text-green-700",
    },
    {
      label: "Status",
      value: analysis.status.charAt(0).toUpperCase() + analysis.status.slice(1),
      icon: "✓",
      color: "bg-slate-50 text-slate-700",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <Card key={index} className={stat.color}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-600">{stat.label}</p>
                <p className="text-2xl font-bold mt-2">{stat.value}</p>
              </div>
              <span className="text-3xl">{stat.icon}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
