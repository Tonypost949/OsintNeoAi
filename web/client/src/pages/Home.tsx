import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload, Network, FileText, BarChart3 } from "lucide-react";
import { getLoginUrl } from "@/const";
import { Link } from "wouter";
import FileUploadArea from "@/components/FileUploadArea";
import AnalysisList from "@/components/AnalysisList";

export default function Home() {
  const { user, loading, isAuthenticated } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex flex-col items-center justify-center px-4">
        <div className="max-w-2xl text-center">
          <div className="mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-500/10 mb-6">
              <Network className="w-8 h-8 text-blue-500" />
            </div>
            <h1 className="text-4xl font-bold text-white mb-4">OSINT Analyzer</h1>
            <p className="text-xl text-slate-300 mb-8">
              Extract people and their relationships from documents. Visualize connections as interactive network graphs.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <Upload className="w-8 h-8 text-blue-400 mb-2" />
                <CardTitle className="text-white">Multi-Format Upload</CardTitle>
              </CardHeader>
              <CardContent className="text-slate-300">
                Support for TXT, PDF, DOCX, CSV, JSON, and EML files
              </CardContent>
            </Card>

            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <Network className="w-8 h-8 text-purple-400 mb-2" />
                <CardTitle className="text-white">Relationship Mapping</CardTitle>
              </CardHeader>
              <CardContent className="text-slate-300">
                Automatically detect and visualize connections between people
              </CardContent>
            </Card>

            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <BarChart3 className="w-8 h-8 text-green-400 mb-2" />
                <CardTitle className="text-white">Analytics</CardTitle>
              </CardHeader>
              <CardContent className="text-slate-300">
                Comprehensive statistics and top connected individuals
              </CardContent>
            </Card>

            <Card className="bg-slate-800 border-slate-700">
              <CardHeader>
                <FileText className="w-8 h-8 text-orange-400 mb-2" />
                <CardTitle className="text-white">Export Reports</CardTitle>
              </CardHeader>
              <CardContent className="text-slate-300">
                Generate text reports and CSV exports of your analysis
              </CardContent>
            </Card>
          </div>

          <a href={getLoginUrl()}>
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-white">
              Sign in to Get Started
            </Button>
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">OSINT Analyzer</h1>
          <p className="text-slate-600 mt-2">Welcome, {user?.name || user?.email}</p>
        </div>

        <Tabs defaultValue="new-analysis" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="new-analysis">New Analysis</TabsTrigger>
            <TabsTrigger value="history">Analysis History</TabsTrigger>
          </TabsList>

          <TabsContent value="new-analysis" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Create New Analysis</CardTitle>
                <CardDescription>
                  Upload documents to extract people and their relationships
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FileUploadArea />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history">
            <AnalysisList />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
