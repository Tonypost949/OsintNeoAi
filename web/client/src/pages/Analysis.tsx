import { useParams, Link } from "wouter";
import { trpc } from "@/lib/trpc";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, Download, ArrowLeft, Network, Shield } from "lucide-react";
import { toast } from "sonner";
import NetworkVisualization from "@/components/NetworkVisualization";
import AnalysisStats from "@/components/AnalysisStats";
import TextReport from "@/components/TextReport";
import EntityFilter from "@/components/EntityFilter";

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
      await generateReportMutation.mutateAsync({ analysisId: id });
      toast.success("Report generated successfully");
    } catch (error) {
      toast.error("Failed to generate report");
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="text-center">
          <Loader2 className="w-10 h-10 animate-spin text-cyan-400 mx-auto mb-4" />
          <p className="text-slate-400 font-medium">Resolving Case Dossier...</p>
        </div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100">
        <div className="text-center max-w-md p-6 bg-slate-900/40 border border-slate-800 rounded-2xl">
          <Shield className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-slate-400 font-semibold mb-6">Analysis Folder Not Found</p>
          <Link href="/">
            <Button className="bg-blue-600 hover:bg-blue-500 font-bold rounded-xl px-6">
              Back to Workspace
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  const { analysis, entities, relationships, report } = analysisData;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      {/* Header bar */}
      <header className="border-b border-slate-800/80 bg-slate-900/40 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/">
              <Button variant="outline" size="sm" className="border-slate-800 hover:bg-slate-800 hover:text-white rounded-xl text-slate-400 gap-2 transition-all">
                <ArrowLeft className="w-4 h-4" />
                Back
              </Button>
            </Link>
            <div className="h-6 w-[1px] bg-slate-800"></div>
            <div>
              <h1 className="text-lg font-bold text-white bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                {analysis.title}
              </h1>
              <p className="text-xs text-slate-400 font-medium truncate max-w-[200px] sm:max-w-md">
                {analysis.description || "No description provided."}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center shadow-lg shadow-cyan-500/5">
              <Network className="w-4 h-4 text-cyan-400" />
            </div>
          </div>
        </div>
      </header>

      {/* Main dashboard content */}
      <main className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        <AnalysisStats analysis={analysis} />

        {/* Main Content Tabs */}
        <Tabs defaultValue="visualization" className="w-full mt-8">
          <TabsList className="bg-slate-900/60 border border-slate-800/80 backdrop-blur-md p-1 rounded-xl grid grid-cols-4 max-w-2xl mb-8">
            <TabsTrigger value="visualization" className="rounded-lg text-slate-400 data-[state=active]:bg-slate-800 data-[state=active]:text-white font-medium py-2">
              Network Graph
            </TabsTrigger>
            <TabsTrigger value="entities" className="rounded-lg text-slate-400 data-[state=active]:bg-slate-800 data-[state=active]:text-white font-medium py-2">
              Entities
            </TabsTrigger>
            <TabsTrigger value="report" className="rounded-lg text-slate-400 data-[state=active]:bg-slate-800 data-[state=active]:text-white font-medium py-2">
              Report
            </TabsTrigger>
            <TabsTrigger value="exports" className="rounded-lg text-slate-400 data-[state=active]:bg-slate-800 data-[state=active]:text-white font-medium py-2">
              Exports
            </TabsTrigger>
          </TabsList>

          {/* Network Visualization */}
          <TabsContent value="visualization" className="outline-none">
            <Card className="bg-slate-900/30 border-slate-800/60 backdrop-blur-md shadow-2xl rounded-2xl overflow-hidden">
              <CardHeader className="border-b border-slate-800/50 pb-4">
                <CardTitle className="text-white text-lg font-bold">Relationship Network</CardTitle>
                <CardDescription className="text-slate-400 text-xs">
                  Interactive visualization of extracted personnel and their mapped connections.
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <NetworkVisualization
                  entities={entities}
                  relationships={relationships.map(r => ({ ...r, strength: r.strength ?? "0.5" }))}
                />
              </CardContent>
            </Card>
          </TabsContent>

          {/* Entities List with Filtering */}
          <TabsContent value="entities" className="outline-none space-y-4">
            <EntityFilter onFilterChange={() => {}} />
            <Card className="bg-slate-900/30 border-slate-800/60 backdrop-blur-md shadow-2xl rounded-2xl overflow-hidden">
              <CardHeader className="border-b border-slate-800/50 pb-4">
                <CardTitle className="text-white text-lg font-bold">Extracted Entities</CardTitle>
                <CardDescription className="text-slate-400 text-xs">
                  {entities.length} distinct targets found in this case.
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-3">
                  {entities
                    .sort((a, b) => b.connectionCount - a.connectionCount)
                    .map((entity) => (
                      <div
                        key={entity.id}
                        className="flex items-center justify-between p-4 border border-slate-800/80 bg-slate-900/20 rounded-xl hover:bg-slate-800/40 hover:border-slate-700/60 transition-all duration-200"
                      >
                        <div>
                          <p className="font-bold text-white text-base">{entity.name}</p>
                          <p className="text-xs text-slate-400 mt-1 font-medium">
                            Type: <span className="text-cyan-400 uppercase tracking-wider text-[10px] font-semibold bg-cyan-950/40 border border-cyan-800/30 px-1.5 py-0.5 rounded mr-2">{entity.type}</span> 
                            Files: <span className="text-slate-200 mr-2">{entity.fileCount}</span>
                            Connections: <span className="text-slate-200">{entity.connectionCount}</span>
                          </p>
                          {entity.emails && entity.emails.length > 0 && (
                            <p className="text-xs text-slate-400 mt-1.5">
                              Emails: <code className="text-slate-300 font-mono">{entity.emails.join(", ")}</code>
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
          <TabsContent value="report" className="outline-none">
            <Card className="bg-slate-900/30 border-slate-800/60 backdrop-blur-md shadow-2xl rounded-2xl overflow-hidden">
              <CardHeader className="border-b border-slate-800/50 pb-4">
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-white text-lg font-bold">Analysis Report</CardTitle>
                    <CardDescription className="text-slate-400 text-xs">
                      Summary statistics and compiled narrative findings.
                    </CardDescription>
                  </div>
                  <Button
                    onClick={handleGenerateReport}
                    disabled={generateReportMutation.isPending}
                    className="bg-blue-600 hover:bg-blue-500 font-bold rounded-xl"
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
              <CardContent className="pt-6">
                {report ? (
                  <TextReport report={report} />
                ) : (
                  <p className="text-slate-400 text-center py-12 text-sm">
                    No report has been compiled yet. Click "Generate Report" to build the intelligence dossier.
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Exports */}
          <TabsContent value="exports" className="outline-none">
            <div className="max-w-md">
              <Card className="bg-slate-900/30 border-slate-800/60 backdrop-blur-md shadow-2xl rounded-2xl overflow-hidden">
                <CardHeader className="border-b border-slate-800/50 pb-4">
                  <CardTitle className="text-white text-lg font-bold">Download Vault Logs</CardTitle>
                  <CardDescription className="text-slate-400 text-xs">
                    Export case details for external network graph ingestion.
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-6 space-y-4">
                  {report ? (
                    <>
                      {report.csvPeopleUrl && (
                        <a href={report.csvPeopleUrl} download>
                          <Button variant="outline" className="w-full border-slate-800 hover:bg-slate-800 hover:text-white rounded-xl text-slate-300 font-semibold gap-2 py-5">
                            <Download className="w-4 h-4" />
                            Download People CSV
                          </Button>
                        </a>
                      )}
                      {report.csvRelationshipsUrl && (
                        <a href={report.csvRelationshipsUrl} download>
                          <Button variant="outline" className="w-full border-slate-800 hover:bg-slate-800 hover:text-white rounded-xl text-slate-300 font-semibold gap-2 py-5">
                            <Download className="w-4 h-4" />
                            Download Relationships CSV
                          </Button>
                        </a>
                      )}
                    </>
                  ) : (
                    <p className="text-slate-400 text-center py-12 text-sm">
                      Compile an analysis report first to enable download downloads.
                    </p>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
