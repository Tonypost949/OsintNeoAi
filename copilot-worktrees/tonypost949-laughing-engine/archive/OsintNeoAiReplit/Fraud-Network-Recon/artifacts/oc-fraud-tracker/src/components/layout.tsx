import { Link, useLocation } from "wouter";
import { 
  ShieldAlert, 
  Users, 
  Building2, 
  Clock, 
  ArrowRightLeft, 
  HelpCircle,
  Menu,
  X,
  Network,
  FolderOpen
} from "lucide-react";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const CASE_NAV_ITEMS = [
  { href: "/", label: "Case Overview", icon: ShieldAlert },
  { href: "/actors", label: "Individuals", icon: Users },
  { href: "/entities", label: "Organizations", icon: Building2 },
  { href: "/timeline", label: "Timeline", icon: Clock },
  { href: "/money-flow", label: "Money Flow", icon: ArrowRightLeft },
  { href: "/questions", label: "Unresolved", icon: HelpCircle },
];

const COLLAB_NAV_ITEMS = [
  { href: "/network", label: "Network Graph", icon: Network },
  { href: "/workspace", label: "Investigations", icon: FolderOpen },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location]);

  return (
    <div className="min-h-[100dvh] flex flex-col md:flex-row bg-background dark text-foreground selection:bg-primary selection:text-primary-foreground">
      {/* Mobile Header */}
      <header className="md:hidden sticky top-0 z-50 flex items-center justify-between p-4 border-b bg-background/95 backdrop-blur">
        <Link href="/" className="font-serif font-bold text-lg tracking-tight">
          OC COVID Fraud Tracker
        </Link>
        <button 
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 -mr-2 text-muted-foreground hover:text-foreground"
          data-testid="button-mobile-menu"
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </header>

      {/* Mobile Nav Overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="md:hidden fixed inset-0 top-[65px] z-40 bg-background border-b overflow-y-auto"
          >
            <nav className="p-4 space-y-2">
              {CASE_NAV_ITEMS.map((item) => {
                const active = location === item.href || (item.href !== "/" && location.startsWith(item.href));
                const Icon = item.icon;
                return (
                  <Link 
                    key={item.href} 
                    href={item.href}
                    className={`flex items-center gap-3 px-4 py-3 rounded-md transition-colors ${
                      active 
                        ? "bg-primary/10 text-primary font-medium" 
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    }`}
                  >
                    <Icon size={20} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
              
              <div className="pt-4 pb-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground px-4">Collaborative</span>
              </div>
              
              {COLLAB_NAV_ITEMS.map((item) => {
                const active = location === item.href || location.startsWith(item.href);
                const Icon = item.icon;
                return (
                  <Link 
                    key={item.href} 
                    href={item.href}
                    className={`flex items-center gap-3 px-4 py-3 rounded-md transition-colors ${
                      active 
                        ? "bg-primary/10 text-primary font-medium" 
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    }`}
                  >
                    <Icon size={20} />
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-64 flex-col fixed inset-y-0 border-r bg-card/50 backdrop-blur z-20">
        <div className="p-6">
          <Link href="/" className="block group">
            <h1 className="font-serif font-bold text-xl leading-tight text-foreground group-hover:text-primary transition-colors">
              OC COVID Fraud
              <span className="block text-muted-foreground font-sans text-sm font-normal mt-1 uppercase tracking-widest">
                Case Tracker
              </span>
            </h1>
          </Link>
        </div>
        
        <div className="flex-1 overflow-y-auto flex flex-col">
          <nav className="px-4 space-y-1 mt-4">
            {CASE_NAV_ITEMS.map((item) => {
              const active = location === item.href || (item.href !== "/" && location.startsWith(item.href));
              const Icon = item.icon;
              return (
                <Link 
                  key={item.href} 
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-md transition-colors text-sm ${
                    active 
                      ? "bg-primary/10 text-primary font-medium" 
                      : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                  }`}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
          
          <div className="px-4 mt-8 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground px-3">Collaborative</span>
          </div>
          
          <nav className="px-4 space-y-1">
            {COLLAB_NAV_ITEMS.map((item) => {
              const active = location === item.href || location.startsWith(item.href);
              const Icon = item.icon;
              return (
                <Link 
                  key={item.href} 
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-md transition-colors text-sm ${
                    active 
                      ? "bg-primary/10 text-primary font-medium" 
                      : "text-muted-foreground hover:bg-muted/50 hover:text-foreground"
                  }`}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="p-4 mt-auto">
          <div className="text-xs text-muted-foreground/70 leading-relaxed border-t pt-4">
            US v. Peter Pham et al.
            <br />
            8:25-CR-00100-JVS
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 md:ml-64 flex flex-col min-h-[100dvh]">
        <div className="flex-1">
          <AnimatePresence mode="wait">
            <motion.div
              key={location}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="h-full"
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </div>

        <footer className="p-6 md:p-12 border-t mt-12 bg-muted/20">
          <div className="max-w-4xl mx-auto text-sm text-muted-foreground leading-relaxed">
            <p className="font-medium text-foreground mb-2">Public Records Disclaimer</p>
            <p>
              All information sourced from public court filings, IRS Form 990 records, CA Secretary of State filings, and published investigative reporting. Individuals who have not been convicted are presumed innocent.
            </p>
          </div>
        </footer>
      </main>
    </div>
  );
}
