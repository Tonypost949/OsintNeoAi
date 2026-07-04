import { useParams, Link } from "wouter";
import { useState } from "react";
import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, Download, ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import NetworkVisualization from "@/components/NetworkVisualization";
import AnalysisStats from "@/components/AnalysisStats";
import TextReport from "@/components/TextReport";
import EntityFilter, { FilterState } from "@/components/EntityFilter";
import GoogleDriveConnect from "@/components/GoogleDriveConnect";

export default function Analysis() {
  const { analysisId } = useParams<{ analysisId: string }>();
  const id = parseInt(analysisId || "0", 10);

  const { data: analysisData, isLoading } = trpc.analysis.get.useQuery(
    { analysisId: id },
    { enabled: id > 0 }
  );

  const generateReportMutation = trpc.report.generate.useMutation();

  const handleGenerateReport = async () => {
    try {
      const result = await generateReportMutation.mutateAsync({ analysisId: id });
      toast.success("Report generated successfully");
    } catch (error) {
      toast.error("Failed to generate report");
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-600 mb-4">Analysis not found</p>
          <Link href="/">
            <Button variant="default">Back to Home</Button>
          </Link>
        </div>
      </div>
    );
  }

  const { analysis, entities, relationships, report } = analysisData;

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/">
            <Button variant="outline" size="sm" className="mb-4">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
          </Link>
          <h1 className="text-3xl font-bold text-slate-900">{analysis.title}</h1>
          <p className="text-slate-600 mt-2">{analysis.description}</p>
        </div>

        {/* Stats Overview */}
        <AnalysisStats analysis={analysis} />

        {/* Main Content Tabs */}
        <Tabs defaultValue="visualization" className="w-full mt-8">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="visualization">Network Graph</TabsTrigger>
            <TabsTrigger value="entities">Entities</TabsTrigger>
            <TabsTrigger value="report">Report</TabsTrigger>
            <TabsTrigger value="exports">Exports</TabsTrigger>
          </TabsList>

          {/* Network Visualization */}
          <TabsContent value="visualization" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Relationship Network</CardTitle>
                <CardDescription>
                  Interactive visualization of people and their connections
                </CardDescription>
              </CardHeader>
              <CardContent>
                <NetworkVisualization
                  entities={entities}
                  relationships={relationships}
                />
              </CardContent>
            </Card>
          </TabsContent>

          {/* Entities List with Filtering */}
          <TabsContent value="entities" className="mt-6 space-y-4">
            <EntityFilter onFilterChange={(filters) => {
              // Filter logic would be applied here
            }} />
            <Card>
              <CardHeader>
                <CardTitle>Extracted Entities</CardTitle>
                <CardDescription>
                  {entities.length} entities found in the analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {entities
                    .sort((a, b) => b.connectionCount - a.connectionCount)
                    .map((entity) => (
                      <div
                        key={entity.id}
                        className="flex items-center justify-between p-3 border border-slate-200 rounded-lg hover:bg-slate-50"
                      >
                        <div>
                          <p className="font-medium text-slate-900">{entity.name}</p>
                          <p className="text-sm text-slate-600">
                            Type: {entity.type} • Files: {entity.fileCount} • Connections: {entity.connectionCount}
                          </p>
                          {entity.emails && entity.emails.length > 0 && (
                            <p className="text-xs text-slate-500 mt-1">
                              Emails: {entity.emails.join(", ")}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Text Report */}
          <TabsContent value="report" className="mt-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Analysis Report</CardTitle>
                    <CardDescription>
                      Summary statistics and detailed analysis
                    </CardDescription>
                  </div>
                  <Button
                    onClick={handleGenerateReport}
                    disabled={generateReportMutation.isPending}
                  >
                    {generateReportMutation.isPending ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      "Generate Report"
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {report ? (
                  <TextReport report={report} />
                ) : (
                  <p className="text-slate-600 text-center py-8">
                    No report generated yet. Click "Generate Report" to create one.
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Exports */}
          <TabsContent value="exports" className="mt-6">
            <div className="grid gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>Download Exports</CardTitle>
                  <CardDescription>
                    Export analysis results in various formats
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {report ? (
                    <>
                      {report.csvPeopleUrl && (
                        <a href={report.csvPeopleUrl} download>
                          <Button variant="outline" className="w-full">
                            <Download className="w-4 h-4 mr-2" />
                            Download People CSV
                          </Button>
                        </a>
                      )}
                      {report.csvRelationshipsUrl && (
                        <a href={report.csvRelationshipsUrl} download>
                          <Button variant="outline" className="w-full">
                            <Download className="w-4 h-4 mr-2" />
                            Download Relationships CSV
                          </Button>
                        </a>
                      )}
                    </>
                  ) : (
                    <p className="text-slate-600 text-center py-8">
                      Generate a report first to download exports
                    </p>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
