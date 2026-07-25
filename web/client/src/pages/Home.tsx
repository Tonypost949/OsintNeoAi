import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, Network, FileText, BarChart3, ShieldAlert, LogOut } from "lucide-react";
import { getLoginUrl } from "@/const";
import FileUploadArea from "@/components/FileUploadArea";
import AnalysisList from "@/components/AnalysisList";

export default function Home() {
  const { user, loading, isAuthenticated, logout } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto mb-4"></div>
          <p className="text-slate-400 font-medium">Initializing Security Protocols...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950/40 flex flex-col items-center justify-center px-4 relative overflow-hidden">
        {/* Subtle decorative glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="max-w-3xl text-center z-10">
          <div className="mb-8 animate-fade-in">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 shadow-lg shadow-cyan-500/5 mb-6 backdrop-blur-md">
              <Network className="w-10 h-10 text-cyan-400" />
            </div>
            <h1 className="text-5xl font-black tracking-tight text-white mb-4 bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
              OSINT Analyzer
            </h1>
            <p className="text-xl text-slate-400 max-w-xl mx-auto font-medium">
              Extract, map, and visualize complex networks of people and relationships from unstructured intelligence documents.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10 text-left">
            <Card className="bg-slate-900/40 backdrop-blur-md border-slate-800/80 hover:border-slate-700/80 transition-all shadow-xl">
              <CardHeader className="pb-2">
                <Upload className="w-8 h-8 text-cyan-400 mb-2" />
                <CardTitle className="text-white text-lg font-semibold">Multi-Format Ingestion</CardTitle>
              </CardHeader>
              <CardContent className="text-slate-400 text-sm">
                Direct parsing support for TXT, PDF, DOCX, CSV, JSON, and EML mail formats.
              </CardContent>
            </Card>

            <Card className="bg-slate-900/40 backdrop-blur-md border-slate-800/80 hover:border-slate-700/80 transition-all shadow-xl">
              <CardHeader className="pb-2">
                <Network className="w-8 h-8 text-purple-400 mb-2" />
                <CardTitle className="text-white text-lg font-semibold">Relationship Mapping</CardTitle>
              </CardHeader>
              <CardContent className="text-slate-400 text-sm">
                Advanced entity co-occurrence detection to automatically plot network connections.
              </CardContent>
            </Card>

            <Card className="bg-slate-900/40 backdrop-blur-md border-slate-800/80 hover:border-slate-700/80 transition-all shadow-xl">
              <CardHeader className="pb-2">
                <BarChart3 className="w-8 h-8 text-emerald-400 mb-2" />
                <CardTitle className="text-white text-lg font-semibold">Forensic Analytics</CardTitle>
              </CardHeader>
              <CardContent className="text-slate-400 text-sm">
                Identify density, central nodes, and top-connected key targets in your case.
              </CardContent>
            </Card>

            <Card className="bg-slate-900/40 backdrop-blur-md border-slate-800/80 hover:border-slate-700/80 transition-all shadow-xl">
              <CardHeader className="pb-2">
                <FileText className="w-8 h-8 text-amber-400 mb-2" />
                <CardTitle className="text-white text-lg font-semibold">Export Intelligence</CardTitle>
              </CardHeader>
              <CardContent className="text-slate-400 text-sm">
                Download formatted text reports and CSV files of connections for external visualizers.
              </CardContent>
            </Card>
          </div>

          <a href={getLoginUrl()} className="inline-block transform active:scale-95 transition-all">
            <Button size="lg" className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold px-8 py-6 rounded-xl shadow-lg shadow-indigo-600/30">
              Sign in to Get Started
            </Button>
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950">
      {/* Header bar */}
      <header className="border-b border-slate-800/80 bg-slate-900/40 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/10">
              <Network className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                OSINT Neo AI
              </h1>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest">
                  Secure Workspace
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <p className="text-xs text-slate-400">Authenticated Agent</p>
              <p className="text-sm font-semibold text-slate-200">{user?.name || user?.email}</p>
            </div>
            <Button
              variant="outline"
              size="icon"
              onClick={logout}
              className="border-slate-800 hover:bg-red-500/10 hover:text-red-400 text-slate-400 hover:border-red-500/30 transition-all rounded-xl"
              title="Logout Session"
            >
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main dashboard content */}
      <main className="container mx-auto px-4 py-8">
        {/* Status notification banner */}
        <div className="mb-8 p-4 rounded-xl bg-cyan-950/20 border border-cyan-800/30 flex items-start gap-3 shadow-lg">
          <ShieldAlert className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-cyan-300 text-sm">Active Forensic Pipeline</h4>
            <p className="text-xs text-slate-400 mt-0.5">
              Case files are processed locally. All extracted metadata, entities, and relationship vectors are mapped securely under project: <code className="text-cyan-400 bg-cyan-950/60 px-1.5 py-0.5 rounded text-[10px]">project-9c94c2fa-3af4-49f1-a7b</code>.
            </p>
          </div>
        </div>

        <Tabs defaultValue="new-analysis" className="w-full">
          <TabsList className="bg-slate-900/60 border border-slate-800/80 backdrop-blur-md p-1 rounded-xl grid grid-cols-2 max-w-md mb-8">
            <TabsTrigger 
              value="new-analysis" 
              className="rounded-lg text-slate-400 data-[state=active]:bg-slate-800 data-[state=active]:text-white transition-all font-medium py-2.5"
            >
              New Analysis Session
            </TabsTrigger>
            <TabsTrigger 
              value="history"
              className="rounded-lg text-slate-400 data-[state=active]:bg-slate-800 data-[state=active]:text-white transition-all font-medium py-2.5"
            >
              Case History
            </TabsTrigger>
          </TabsList>

          <TabsContent value="new-analysis" className="outline-none">
            <Card className="bg-slate-900/30 border-slate-800/60 backdrop-blur-md shadow-2xl rounded-2xl overflow-hidden">
              <CardHeader className="border-b border-slate-800/50 pb-4">
                <CardTitle className="text-white text-lg font-bold">Initiate Ingestion</CardTitle>
                <CardDescription className="text-slate-400 text-xs">
                  Select and upload case files or intelligence briefs to extract networks of interest.
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <FileUploadArea />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history" className="outline-none">
            <Card className="bg-slate-900/30 border-slate-800/60 backdrop-blur-md shadow-2xl rounded-2xl overflow-hidden">
              <CardHeader className="border-b border-slate-800/50 pb-4">
                <CardTitle className="text-white text-lg font-bold">Ingested Dossiers</CardTitle>
                <CardDescription className="text-slate-400 text-xs">
                  Review and analyze previously completed relationship mapping runs.
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <AnalysisList />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
