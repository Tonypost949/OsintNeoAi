import { useState } from "react";
import { Link, useLocation } from "wouter";
import { useUser } from "@clerk/react";
import {
  useGetStats,
  getGetStatsQueryKey,
  useCreateSession,
  getListSessionsQueryKey,
} from "@workspace/api-client-react";
import { Layout } from "@/components/layout";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageSquare, Terminal, Plus, Clock, Loader2, ArrowRight } from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { formatDistanceToNow } from "date-fns";

export default function Home() {
  const { user, isLoaded } = useUser();
  const { data: stats, isLoading, isError } = useGetStats({
    query: { queryKey: getGetStatsQueryKey() },
  });
  const [isOpen, setIsOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [, setLocation] = useLocation();
  const queryClient = useQueryClient();
  const createSession = useCreateSession();

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    createSession.mutate(
      { data: { title: title.trim() } },
      {
        onSuccess: (session) => {
          queryClient.invalidateQueries({ queryKey: getGetStatsQueryKey() });
          queryClient.invalidateQueries({ queryKey: getListSessionsQueryKey() });
          setIsOpen(false);
          setTitle("");
          setLocation(`/sessions/${session.id}`);
        },
      },
    );
  };

  // Landing page for signed-out users
  if (isLoaded && !user) {
    return (
      <div className="min-h-[100dvh] flex flex-col bg-background text-foreground">
        <header className="flex items-center justify-between px-6 py-4 border-b border-border/50">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-md bg-primary/10 flex items-center justify-center text-primary">
              <Terminal className="w-5 h-5" />
            </div>
            <span className="font-mono font-semibold tracking-tight text-lg">
              OpenCode<span className="text-primary">_</span>
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/sign-in">
              <Button variant="ghost" size="sm">Sign in</Button>
            </Link>
            <Link href="/sign-up">
              <Button size="sm">Get started</Button>
            </Link>
          </div>
        </header>
        <main className="flex-1 flex flex-col items-center justify-center px-6 py-20 text-center">
          <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center text-primary mb-8">
            <Terminal className="w-8 h-8" />
          </div>
          <h1 className="text-5xl font-bold tracking-tight mb-4">
            Think in code.
          </h1>
          <p className="text-lg text-muted-foreground max-w-lg mb-10">
            A focused workspace for coding conversations. Create sessions,
            ask questions, and keep your knowledge organized.
          </p>
          <div className="flex items-center gap-4">
            <Link href="/sign-up">
              <Button size="lg" className="gap-2">
                <Plus className="w-4 h-4" />
                Create your workspace
              </Button>
            </Link>
            <Link href="/sign-in">
              <Button variant="outline" size="lg">
                Sign in
              </Button>
            </Link>
          </div>
        </main>
      </div>
    );
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4 text-muted-foreground">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
            <p className="font-mono text-sm">Loading workspace...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (isError || !stats) {
    return (
      <Layout>
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
          <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center text-destructive mb-6">
            <Terminal className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-semibold mb-2">Connection failed</h2>
          <p className="text-muted-foreground mb-6 max-w-md">
            Could not reach the API. Try refreshing the page.
          </p>
          <Button onClick={() => window.location.reload()} variant="outline">
            Retry
          </Button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-6 md:p-10 w-full">
        <div className="max-w-4xl mx-auto space-y-10">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <h1 className="text-4xl font-bold tracking-tight mb-2">Dashboard</h1>
              <p className="text-muted-foreground">
                Your coding sessions and conversations.
              </p>
            </div>
            <Dialog open={isOpen} onOpenChange={(open) => { setIsOpen(open); if (!open) setTitle(""); }}>
              <DialogTrigger asChild>
                <Button size="lg" className="font-mono tracking-tight gap-2">
                  <Plus className="w-4 h-4" />
                  New Session
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-md border-border bg-card shadow-2xl">
                <form onSubmit={handleCreate}>
                  <DialogHeader>
                    <DialogTitle className="font-mono flex items-center gap-2">
                      <Terminal className="w-5 h-5 text-primary" />
                      New Session
                    </DialogTitle>
                  </DialogHeader>
                  <div className="py-6 space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="title" className="font-mono text-xs text-muted-foreground uppercase tracking-wider">
                        Session name
                      </Label>
                      <Input
                        id="title"
                        placeholder="e.g. TypeScript error help"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        className="font-mono bg-background focus-visible:ring-primary"
                        autoFocus
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button type="button" variant="ghost" onClick={() => setIsOpen(false)}>
                      Cancel
                    </Button>
                    <Button type="submit" disabled={!title.trim() || createSession.isPending}>
                      {createSession.isPending ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : null}
                      Create
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="bg-card border-border/50 shadow-sm">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                  Sessions
                </CardTitle>
                <Terminal className="w-4 h-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold font-mono">{stats.totalSessions}</div>
              </CardContent>
            </Card>
            <Card className="bg-card border-border/50 shadow-sm">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                  Messages
                </CardTitle>
                <MessageSquare className="w-4 h-4 text-primary" />
              </CardHeader>
              <CardContent>
                <div className="text-4xl font-bold font-mono">{stats.totalMessages}</div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <h3 className="text-xl font-semibold flex items-center gap-2">
              <Clock className="w-5 h-5 text-muted-foreground" />
              Recent Sessions
            </h3>
            {stats.recentSessions.length === 0 ? (
              <div className="border border-dashed border-border rounded-lg p-10 text-center flex flex-col items-center">
                <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mb-4">
                  <Terminal className="w-6 h-6 text-muted-foreground" />
                </div>
                <h4 className="text-lg font-medium mb-1">No sessions yet</h4>
                <p className="text-muted-foreground max-w-sm">
                  Start a new session to begin coding conversations.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-3">
                {stats.recentSessions.map((session) => (
                  <Link href={`/sessions/${session.id}`} key={session.id} className="block group">
                    <Card className="bg-card border-border/50 hover:border-primary/50 transition-colors shadow-sm cursor-pointer">
                      <CardContent className="p-4 flex items-center justify-between">
                        <div className="flex flex-col gap-1">
                          <span className="font-mono font-medium text-foreground group-hover:text-primary transition-colors">
                            {session.title}
                          </span>
                          <span className="text-xs text-muted-foreground flex items-center gap-2">
                            <span>ID: #{session.id}</span>
                            <span>•</span>
                            <span>{formatDistanceToNow(new Date(session.createdAt), { addSuffix: true })}</span>
                          </span>
                        </div>
                        <div className="flex items-center gap-4">
                          <span className="text-xs font-mono bg-muted text-muted-foreground px-2 py-1 rounded-md">
                            {session.messageCount} msgs
                          </span>
                          <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
                        </div>
                      </CardContent>
                    </Card>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
