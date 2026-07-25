import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Link } from "wouter";
import { Loader2, Trash2 } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

export default function AnalysisList() {
  const { data: analyses, isLoading, refetch } = trpc.analysis.list.useQuery();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
      </div>
    );
  }

  if (!analyses || analyses.length === 0) {
    return (
      <Card>
        <CardContent className="pt-6 text-center">
          <p className="text-slate-600">No analyses yet. Create one to get started!</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-4">
      {analyses.map((analysis) => (
        <Card key={analysis.id} className="hover:shadow-md transition-shadow">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <CardTitle className="text-lg">{analysis.title}</CardTitle>
                <CardDescription>
                  {analysis.description}
                </CardDescription>
              </div>
              <Badge
                variant={
                  analysis.status === "completed"
                    ? "default"
                    : analysis.status === "failed"
                    ? "destructive"
                    : "secondary"
                }
              >
                {analysis.status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div>
                <p className="text-sm text-slate-600">Files Analyzed</p>
                <p className="text-2xl font-semibold text-slate-900">
                  {analysis.filesAnalyzed}
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-600">People Found</p>
                <p className="text-2xl font-semibold text-slate-900">
                  {analysis.peopleFound}
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-600">Relationships</p>
                <p className="text-2xl font-semibold text-slate-900">
                  {analysis.relationshipsFound}
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-600">Created</p>
                <p className="text-sm font-medium text-slate-900">
                  {formatDistanceToNow(new Date(analysis.createdAt), {
                    addSuffix: true,
                  })}
                </p>
              </div>
            </div>

            <div className="flex gap-2">
              <Link href={`/analysis/${analysis.id}`}>
                <Button variant="default" size="sm">
                  View Analysis
                </Button>
              </Link>
              <Button variant="outline" size="sm">
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
