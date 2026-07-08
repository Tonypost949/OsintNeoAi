import { type ReactNode } from "react";
import { Link } from "wouter";
import { useUser, useClerk } from "@clerk/react";
import { Terminal, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";

const basePath = import.meta.env.BASE_URL.replace(/\/$/, "");

export function Layout({ children }: { children: ReactNode }) {
  const { user } = useUser();
  const { signOut } = useClerk();

  return (
    <div className="min-h-[100dvh] flex flex-col bg-background text-foreground">
      <header className="flex items-center justify-between px-6 py-3.5 border-b border-border/50 sticky top-0 z-50 bg-background/80 backdrop-blur-md">
        <Link href="/" className="flex items-center gap-2.5 group transition-opacity hover:opacity-80">
          <div className="w-8 h-8 rounded-md bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary/20 transition-colors">
            <Terminal className="w-5 h-5" />
          </div>
          <span className="font-mono font-semibold tracking-tight text-lg">
            OpenCode<span className="text-primary">_</span>
          </span>
        </Link>

        {user && (
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground hidden sm:inline">
              {user.firstName || user.emailAddresses[0]?.emailAddress || "User"}
            </span>
            <Button
              variant="ghost"
              size="sm"
              className="gap-1.5 text-muted-foreground hover:text-foreground"
              onClick={() => signOut({ redirectUrl: basePath || "/" })}
            >
              <LogOut className="w-4 h-4" />
              <span className="hidden sm:inline">Sign out</span>
            </Button>
          </div>
        )}
      </header>
      <main className="flex-1 flex flex-col w-full">
        {children}
      </main>
    </div>
  );
}
