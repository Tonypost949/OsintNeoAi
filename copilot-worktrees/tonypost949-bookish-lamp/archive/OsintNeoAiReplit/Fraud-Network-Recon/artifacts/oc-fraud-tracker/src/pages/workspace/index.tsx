import { useEffect, useState, useRef } from "react";
import {
  collection, addDoc, onSnapshot, query, orderBy, deleteDoc, doc,
} from "firebase/firestore";
import {
  GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged, User,
} from "firebase/auth";
import { db, auth } from "@/firebase";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import {
  FolderOpen, Activity, FileText, MessageSquare, Trash2, Plus, LogOut,
  Loader2, ShieldCheck, Send, Upload, Lock, ChevronRight,
} from "lucide-react";
import { format } from "date-fns";
import { useToast } from "@/hooks/use-toast";

const ADMIN_EMAIL = "amd949609@gmail.com";

interface Investigation {
  id: string;
  name: string;
  description?: string;
  status: string;
  entities: number;
  updated: string;
  createdAt: string;
}

interface EvidenceDoc {
  id: string;
  name: string;
  handle: string;
  status: string;
  date: string;
  createdAt: string;
}

interface Comment {
  id: string;
  handle: string;
  text: string;
  timestamp: string;
  createdAt: string;
}

interface ActivityLog {
  id: string;
  action: string;
  target: string;
  type: string;
  time: string;
  status: string;
  createdAt: string;
}

export default function WorkspacePage() {
  const [user, setUser] = useState<User | null>(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [selectedInv, setSelectedInv] = useState<Investigation | null>(null);
  const [uploads, setUploads] = useState<EvidenceDoc[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [activeTab, setActiveTab] = useState<"evidence" | "comments">("evidence");
  const [isNewModalOpen, setIsNewModalOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [uploadName, setUploadName] = useState("");
  const [commentText, setCommentText] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const commentsEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Auth listener
  useEffect(() => {
    return onAuthStateChanged(auth, (u) => {
      setUser(u);
      setIsAdmin(u?.email === ADMIN_EMAIL);
    });
  }, []);

  // Investigations listener
  useEffect(() => {
    const q = query(collection(db, "investigations"), orderBy("createdAt", "desc"));
    const unsub = onSnapshot(q, (snap) => {
      const invs = snap.docs.map(d => ({ id: d.id, ...d.data() } as Investigation));
      setInvestigations(invs);
      setLoading(false);
      // Auto-select first investigation
      if (invs.length > 0 && !selectedInv) {
        setSelectedInv(invs[0]);
      }
    }, (err) => {
      console.error(err);
      setError("Could not connect to the investigation database.");
      setLoading(false);
    });
    return () => unsub();
  }, []);

  // Activity feed listener
  useEffect(() => {
    const q = query(collection(db, "activities"), orderBy("createdAt", "desc"));
    return onSnapshot(q, (snap) => {
      setActivities(snap.docs.map(d => ({ id: d.id, ...d.data() } as ActivityLog)));
    }, console.error);
  }, []);

  // Sub-collection listeners for selected investigation
  useEffect(() => {
    if (!selectedInv) return;
    setUploads([]);
    setComments([]);

    const uq = query(collection(db, `investigations/${selectedInv.id}/uploads`), orderBy("createdAt", "asc"));
    const unsubUploads = onSnapshot(uq, (snap) => {
      setUploads(snap.docs.map(d => ({ id: d.id, ...d.data() } as EvidenceDoc)));
    }, console.error);

    const cq = query(collection(db, `investigations/${selectedInv.id}/comments`), orderBy("createdAt", "asc"));
    const unsubComments = onSnapshot(cq, (snap) => {
      setComments(snap.docs.map(d => ({ id: d.id, ...d.data() } as Comment)));
    }, console.error);

    return () => { unsubUploads(); unsubComments(); };
  }, [selectedInv?.id]);

  // Scroll comments to bottom on new message
  useEffect(() => {
    if (activeTab === "comments") {
      commentsEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [comments, activeTab]);

  const handleLogin = async () => {
    try {
      await signInWithPopup(auth, new GoogleAuthProvider());
    } catch (e: any) {
      toast({ title: "Login failed", description: e.message, variant: "destructive" });
    }
  };

  const handleLogout = async () => {
    await signOut(auth);
    toast({ title: "Signed out" });
  };

  const handleCreateInvestigation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    setSubmitting(true);
    try {
      const now = new Date().toISOString();
      await addDoc(collection(db, "investigations"), {
        name: newName,
        description: newDesc,
        status: "Active",
        entities: 0,
        updated: "Just now",
        createdAt: now,
      });
      await addDoc(collection(db, "activities"), {
        action: "Investigation Created",
        target: newName,
        type: "investigation",
        time: "Just now",
        status: "active",
        createdAt: now,
      });
      setNewName("");
      setNewDesc("");
      setIsNewModalOpen(false);
      toast({ title: "Investigation created" });
    } catch (e: any) {
      toast({ title: "Error", description: e.message, variant: "destructive" });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteInvestigation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!isAdmin || !window.confirm("Delete this investigation?")) return;
    try {
      await deleteDoc(doc(db, "investigations", id));
      if (selectedInv?.id === id) setSelectedInv(null);
    } catch (e: any) {
      toast({ title: "Error", description: e.message, variant: "destructive" });
    }
  };

  const handleAddEvidence = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadName.trim() || !selectedInv || !user) return;
    setSubmitting(true);
    try {
      const now = new Date().toISOString();
      await addDoc(collection(db, `investigations/${selectedInv.id}/uploads`), {
        name: uploadName,
        handle: user.displayName || user.email?.split("@")[0] || "Unknown",
        status: "Logged",
        date: format(new Date(), "MMM d, yyyy"),
        createdAt: now,
      });
      await addDoc(collection(db, "activities"), {
        action: "Evidence Added",
        target: uploadName,
        type: "evidence",
        time: "Just now",
        status: "success",
        createdAt: now,
      });
      setUploadName("");
      toast({ title: "Evidence logged" });
    } catch (e: any) {
      toast({ title: "Error", description: e.message, variant: "destructive" });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteEvidence = async (id: string) => {
    if (!isAdmin || !selectedInv) return;
    try {
      await deleteDoc(doc(db, `investigations/${selectedInv.id}/uploads`, id));
    } catch (e: any) {
      toast({ title: "Error", description: e.message, variant: "destructive" });
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentText.trim() || !selectedInv || !user) return;
    setSubmitting(true);
    try {
      const now = new Date().toISOString();
      await addDoc(collection(db, `investigations/${selectedInv.id}/comments`), {
        handle: user.displayName || user.email?.split("@")[0] || "Unknown",
        text: commentText,
        timestamp: format(new Date(), "MMM d, yyyy HH:mm"),
        createdAt: now,
      });
      await addDoc(collection(db, "activities"), {
        action: "Comment Added",
        target: selectedInv.name,
        type: "comment",
        time: "Just now",
        status: "active",
        createdAt: now,
      });
      setCommentText("");
    } catch (e: any) {
      toast({ title: "Error", description: e.message, variant: "destructive" });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteComment = async (id: string) => {
    if (!isAdmin || !selectedInv) return;
    try {
      await deleteDoc(doc(db, `investigations/${selectedInv.id}/comments`, id));
    } catch (e: any) {
      toast({ title: "Error", description: e.message, variant: "destructive" });
    }
  };

  return (
    <div className="flex flex-col bg-background" style={{ height: "calc(100dvh - 0px)", minHeight: 0 }}>

      {/* ── Top Bar ── */}
      <header className="flex items-center justify-between px-6 py-3 border-b bg-card/60 backdrop-blur shrink-0">
        <div className="flex items-center gap-3">
          <FolderOpen className="text-primary" size={22} />
          <h1 className="text-lg font-serif font-bold">OSINT Investigations Workspace</h1>
        </div>
        <div className="flex items-center gap-3">
          {user ? (
            <>
              {isAdmin && (
                <Badge className="gap-1 bg-primary text-primary-foreground text-xs border-transparent">
                  <ShieldCheck size={12} /> Admin
                </Badge>
              )}
              <span className="text-xs text-muted-foreground hidden sm:block truncate max-w-[160px]">{user.email}</span>
              <Button variant="outline" size="sm" onClick={handleLogout} className="h-8">
                <LogOut size={14} className="mr-1.5" /> Sign Out
              </Button>
            </>
          ) : (
            <Button size="sm" className="h-8 gap-1.5" onClick={handleLogin}>
              Sign In to Collaborate
            </Button>
          )}
        </div>
      </header>

      {error && (
        <div className="mx-4 mt-3 p-3 bg-destructive/10 text-destructive text-sm rounded border border-destructive/20 shrink-0">
          {error}
        </div>
      )}

      {/* ── Main 3-Column Layout ── */}
      <div className="flex flex-1 overflow-hidden">

        {/* ── Left: Investigations List ── */}
        <aside className="w-64 shrink-0 border-r flex flex-col bg-muted/5">
          <div className="px-4 py-3 border-b flex items-center justify-between shrink-0">
            <span className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Investigations</span>
            <Dialog open={isNewModalOpen} onOpenChange={setIsNewModalOpen}>
              <DialogTrigger asChild>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-7 px-2 text-xs gap-1"
                  onClick={!user ? handleLogin : undefined}
                  title={!user ? "Sign in to create an investigation" : "New investigation"}
                >
                  <Plus size={14} /> New
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Start New Investigation</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleCreateInvestigation} className="space-y-4 pt-2">
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Name <span className="text-destructive">*</span></label>
                    <Input
                      value={newName}
                      onChange={e => setNewName(e.target.value)}
                      placeholder="e.g. Shell Entity Funding Trail"
                      required
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-medium">Description</label>
                    <Textarea
                      value={newDesc}
                      onChange={e => setNewDesc(e.target.value)}
                      placeholder="Scope of this investigation thread..."
                      rows={3}
                    />
                  </div>
                  <Button type="submit" className="w-full" disabled={submitting}>
                    {submitting ? <><Loader2 size={16} className="animate-spin mr-2" />Creating...</> : "Create Investigation"}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {loading ? (
              <div className="flex justify-center pt-8"><Loader2 className="animate-spin text-muted-foreground" size={20} /></div>
            ) : investigations.length === 0 ? (
              <div className="text-xs text-muted-foreground text-center pt-8 leading-relaxed">
                No active investigations.<br />Sign in and click New to start one.
              </div>
            ) : (
              investigations.map(inv => (
                <button
                  key={inv.id}
                  onClick={() => setSelectedInv(inv)}
                  className={`w-full text-left rounded-lg border p-3 transition-all group relative ${
                    selectedInv?.id === inv.id
                      ? "border-primary bg-primary/8 shadow-sm"
                      : "border-border bg-card hover:border-primary/40 hover:bg-muted/30"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <span className="font-medium text-sm text-foreground leading-tight line-clamp-2 pr-4">{inv.name}</span>
                    <ChevronRight size={14} className={`shrink-0 mt-0.5 text-muted-foreground transition-opacity ${selectedInv?.id === inv.id ? "opacity-100 text-primary" : "opacity-0 group-hover:opacity-50"}`} />
                  </div>
                  {inv.description && (
                    <p className="text-xs text-muted-foreground mt-1 line-clamp-1">{inv.description}</p>
                  )}
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="outline" className="text-[10px] font-normal py-0 h-4">{inv.status}</Badge>
                    <span className="text-[10px] text-muted-foreground">{inv.entities} entities</span>
                  </div>
                  {isAdmin && (
                    <button
                      onClick={e => handleDeleteInvestigation(inv.id, e)}
                      className="absolute top-2.5 right-2.5 text-muted-foreground opacity-0 group-hover:opacity-60 hover:opacity-100 hover:text-destructive transition-opacity"
                      title="Delete investigation"
                    >
                      <Trash2 size={12} />
                    </button>
                  )}
                </button>
              ))
            )}
          </div>
        </aside>

        {/* ── Center: Investigation Detail ── */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {selectedInv ? (
            <>
              {/* Investigation Header */}
              <div className="px-6 py-4 border-b shrink-0 bg-card/30">
                <div className="flex items-center gap-3 mb-1">
                  <h2 className="text-xl font-serif font-bold text-foreground leading-tight">{selectedInv.name}</h2>
                  <Badge variant="secondary" className="text-xs shrink-0">{selectedInv.status}</Badge>
                </div>
                {selectedInv.description && (
                  <p className="text-sm text-muted-foreground max-w-2xl">{selectedInv.description}</p>
                )}
                <p className="text-xs text-muted-foreground mt-2">
                  Created {format(new Date(selectedInv.createdAt), "MMM d, yyyy")}
                </p>
              </div>

              {/* Tabs */}
              <div className="flex border-b shrink-0 px-6 bg-card/20">
                {(["evidence", "comments"] as const).map(tab => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`flex items-center gap-1.5 px-0 mr-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === tab
                        ? "border-primary text-primary"
                        : "border-transparent text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {tab === "evidence" ? <Upload size={15} /> : <MessageSquare size={15} />}
                    {tab === "evidence" ? "Evidence" : "Discussion"}
                    {tab === "evidence" && uploads.length > 0 && (
                      <span className="ml-1 text-[10px] bg-muted text-muted-foreground rounded-full px-1.5 py-0.5">{uploads.length}</span>
                    )}
                    {tab === "comments" && comments.length > 0 && (
                      <span className="ml-1 text-[10px] bg-muted text-muted-foreground rounded-full px-1.5 py-0.5">{comments.length}</span>
                    )}
                  </button>
                ))}
              </div>

              {/* ── Evidence Tab ── */}
              {activeTab === "evidence" && (
                <div className="flex-1 flex flex-col overflow-hidden">
                  {/* Evidence List */}
                  <div className="flex-1 overflow-y-auto px-6 py-4 space-y-2">
                    {uploads.length === 0 ? (
                      <div className="flex flex-col items-center justify-center h-full text-center py-12">
                        <FileText size={36} className="text-muted-foreground/20 mb-3" />
                        <p className="text-sm text-muted-foreground">No evidence logged yet.</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {user ? "Use the form below to log a document or reference." : "Sign in to log evidence."}
                        </p>
                      </div>
                    ) : (
                      uploads.map(up => (
                        <div key={up.id} className="flex items-center justify-between p-3.5 rounded-lg border bg-card/50 group">
                          <div className="flex items-start gap-3">
                            <div className="mt-0.5 p-1.5 rounded bg-primary/10 text-primary shrink-0">
                              <FileText size={14} />
                            </div>
                            <div>
                              <p className="text-sm font-medium text-foreground">{up.name}</p>
                              <p className="text-xs text-muted-foreground mt-0.5">
                                Logged by <span className="font-medium text-foreground/70">@{up.handle}</span> · {up.date}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-3 shrink-0">
                            <Badge variant="outline" className="text-[10px] font-normal">{up.status}</Badge>
                            {isAdmin && (
                              <button
                                onClick={() => handleDeleteEvidence(up.id)}
                                className="text-muted-foreground opacity-0 group-hover:opacity-60 hover:opacity-100 hover:text-destructive transition-opacity"
                              >
                                <Trash2 size={14} />
                              </button>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>

                  {/* Evidence Submit Bar */}
                  <div className="px-6 py-4 border-t bg-card/30 shrink-0">
                    {user ? (
                      <form onSubmit={handleAddEvidence} className="flex gap-3">
                        <div className="flex-1 relative">
                          <Upload size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
                          <Input
                            value={uploadName}
                            onChange={e => setUploadName(e.target.value)}
                            placeholder="Document name, court filing reference, URL..."
                            className="pl-9"
                            required
                          />
                        </div>
                        <Button type="submit" disabled={submitting || !uploadName.trim()} className="shrink-0">
                          {submitting ? <Loader2 size={15} className="animate-spin" /> : "Log Evidence"}
                        </Button>
                      </form>
                    ) : (
                      <div className="flex items-center justify-between p-3 rounded-lg border border-dashed bg-muted/20">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Lock size={14} />
                          Sign in to log evidence to this investigation
                        </div>
                        <Button size="sm" variant="outline" className="h-8" onClick={handleLogin}>
                          Sign In
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* ── Comments/Discussion Tab ── */}
              {activeTab === "comments" && (
                <div className="flex-1 flex flex-col overflow-hidden">
                  {/* Comments List */}
                  <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
                    {comments.length === 0 ? (
                      <div className="flex flex-col items-center justify-center h-full text-center py-12">
                        <MessageSquare size={36} className="text-muted-foreground/20 mb-3" />
                        <p className="text-sm text-muted-foreground">No discussion yet.</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {user ? "Be the first to post a note or tip." : "Sign in to join the investigation."}
                        </p>
                      </div>
                    ) : (
                      comments.map(c => (
                        <div key={c.id} className="flex gap-3 group">
                          <div className="w-8 h-8 rounded-full bg-primary/15 text-primary flex items-center justify-center text-xs font-bold uppercase shrink-0 mt-0.5">
                            {(c.handle || "?").substring(0, 2)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-baseline gap-2 mb-1">
                              <span className="text-sm font-semibold text-foreground">@{c.handle}</span>
                              <span className="text-xs text-muted-foreground">{c.timestamp}</span>
                              {isAdmin && (
                                <button
                                  onClick={() => handleDeleteComment(c.id)}
                                  className="ml-auto text-muted-foreground opacity-0 group-hover:opacity-60 hover:opacity-100 hover:text-destructive transition-opacity"
                                >
                                  <Trash2 size={12} />
                                </button>
                              )}
                            </div>
                            <p className="text-sm text-foreground/90 whitespace-pre-wrap leading-relaxed">{c.text}</p>
                          </div>
                        </div>
                      ))
                    )}
                    <div ref={commentsEndRef} />
                  </div>

                  {/* Comment Input Bar */}
                  <div className="px-6 py-4 border-t bg-card/30 shrink-0">
                    {user ? (
                      <form onSubmit={handleAddComment} className="flex gap-3 items-end">
                        <div className="flex-1">
                          <Textarea
                            value={commentText}
                            onChange={e => setCommentText(e.target.value)}
                            placeholder="Share investigative notes, tips, or observations..."
                            rows={2}
                            className="resize-none text-sm"
                            onKeyDown={e => {
                              if (e.key === "Enter" && !e.shiftKey) {
                                e.preventDefault();
                                if (commentText.trim()) handleAddComment(e as any);
                              }
                            }}
                          />
                          <p className="text-[10px] text-muted-foreground mt-1">Enter to send · Shift+Enter for new line</p>
                        </div>
                        <Button type="submit" size="icon" className="h-10 w-10 shrink-0 mb-5" disabled={submitting || !commentText.trim()}>
                          {submitting ? <Loader2 size={15} className="animate-spin" /> : <Send size={15} />}
                        </Button>
                      </form>
                    ) : (
                      <div className="flex items-center justify-between p-3 rounded-lg border border-dashed bg-muted/20">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Lock size={14} />
                          Sign in with Google to join the discussion
                        </div>
                        <Button size="sm" variant="outline" className="h-8" onClick={handleLogin}>
                          Sign In
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-12">
              <FolderOpen size={48} className="text-muted-foreground/15 mb-4" />
              <p className="text-muted-foreground text-sm">Select an investigation from the left</p>
            </div>
          )}
        </div>

        {/* ── Right: Activity Feed ── */}
        <aside className="hidden xl:flex w-64 shrink-0 border-l flex-col bg-muted/5">
          <div className="px-4 py-3 border-b flex items-center gap-2 shrink-0">
            <Activity size={14} className="text-muted-foreground" />
            <span className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">Activity Feed</span>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            {activities.length === 0 ? (
              <p className="text-xs text-muted-foreground text-center pt-6">No recent activity</p>
            ) : (
              <div className="space-y-4">
                {activities.slice(0, 30).map(act => (
                  <div key={act.id} className="relative pl-5 border-l-2 border-primary/20 pb-4 last:pb-0">
                    <div
                      className={`absolute w-2 h-2 rounded-full -left-[5px] top-1.5 ${
                        act.type === "investigation" ? "bg-blue-500" :
                        act.type === "evidence" ? "bg-green-500" :
                        act.type === "comment" ? "bg-amber-500" : "bg-primary"
                      }`}
                    />
                    <p className="text-xs font-semibold text-foreground leading-tight">{act.action}</p>
                    <p className="text-xs text-primary font-mono mt-0.5 truncate">{act.target}</p>
                    <p className="text-[10px] text-muted-foreground mt-1">{act.time}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </aside>

      </div>
    </div>
  );
}
