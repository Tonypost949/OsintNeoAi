import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Map as MapIcon, 
  Share2, 
  FileText, 
  Sparkles, 
  AlertTriangle,
  ChevronRight,
  Database,
  Activity,
  User,
  Info,
  Zap,
  Terminal,
  Sliders,
  ChevronLeft
} from 'lucide-react';
import { NetworkGraph } from './components/NetworkGraph';
import { MapTracker } from './components/MapTracker';
import { NeoAnalysis } from './components/NeoAnalysis';
import { DOSSIER_DATA } from './data/dossier';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Button } from './components/ui/button';
import { ScrollArea } from './components/ui/scroll-area';
import { Separator } from './components/ui/separator';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './components/ui/table';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from './lib/utils';
import { Input } from './components/ui/input';

// Google Authentication & Docs Extractions
import { 
  initAuth, 
  googleSignIn, 
  logout as googleLogout 
} from './lib/googleAuth';
import { 
  fetchGoogleDoc, 
  extractDocId, 
  analyzeDocText, 
  ExtractedEvidence 
} from './lib/googleDocs';
import { fetchDriveFiles, DriveFile } from './lib/googleDrive';
import { fetchRecentEmails, EmailMessage } from './lib/googleMail';
import { fetchGoogleSheet, extractSheetId } from './lib/googleSheets';
import { User as FirebaseUser } from 'firebase/auth';

type ViewMode = 'NETWORK' | 'MAP' | 'DOSSIER' | 'AI';
type AuthPhase = 'INTRO' | 'SCANNING' | 'RESULTS' | 'DASHBOARD';

export default function App() {
  const [authPhase, setAuthPhase] = useState<AuthPhase>('INTRO');
  const [viewMode, setViewMode] = useState<ViewMode>('NETWORK');
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const [tickerIndex, setTickerIndex] = useState(0);

  // Intel target parameters state
  const [targetName, setTargetName] = useState('Anthony DiMarcello');
  const [targetPhone, setTargetPhone] = useState('+1 (949) 555-0199');
  const [targetEmail, setTargetEmail] = useState('anthonymd949@gmail.com');
  const [targetCaseRef, setTargetCaseRef] = useState('WB-2026-001-CA');

  // Animation states during Pinball Flash-Scan
  const [scanStep, setScanStep] = useState(0);
  const [matrixStates, setMatrixStates] = useState<boolean[]>(Array(16).fill(false));
  const [pinballBlink, setPinballBlink] = useState(false);
  const [terminalTicks, setTerminalTicks] = useState(0);

  // Stateful tracking of dossier data and google connection
  const [dossierState, setDossierState] = useState(DOSSIER_DATA);
  const [googleUser, setGoogleUser] = useState<FirebaseUser | null>(null);
  const [googleToken, setGoogleToken] = useState<string | null>(null);
  const [googleDocInput, setGoogleDocInput] = useState('');
  const [isFetchingDoc, setIsFetchingDoc] = useState(false);
  const [extractedEvidence, setExtractedEvidence] = useState<ExtractedEvidence[]>([]);
  const [loadedDocTitle, setLoadedDocTitle] = useState('');
  const [docErrorMessage, setDocErrorMessage] = useState('');

  // Drive state
  const [driveFiles, setDriveFiles] = useState<DriveFile[]>([]);
  const [isScanningDrive, setIsScanningDrive] = useState(false);

  // Gmail State
  const [interceptedEmails, setInterceptedEmails] = useState<EmailMessage[]>([]);
  const [isScanningGmail, setIsScanningGmail] = useState(false);

  // Set up Firebase auth observer on load
  useEffect(() => {
    const unsubscribe = initAuth(
      (user, token) => {
        setGoogleUser(user);
        setGoogleToken(token);
      },
      () => {
        setGoogleUser(null);
        setGoogleToken(null);
      }
    );
    return () => {
      if (unsubscribe) unsubscribe();
    };
  }, []);

  const handleGoogleSignIn = async () => {
    try {
      setDocErrorMessage('');
      const res = await googleSignIn();
      if (res) {
        setGoogleUser(res.user);
        setGoogleToken(res.accessToken);
      }
    } catch (err: any) {
      setDocErrorMessage(err?.message || 'Failed to authenticate Google account.');
    }
  };

  const handleGoogleSignOut = async () => {
    try {
      setDocErrorMessage('');
      await googleLogout();
      setGoogleUser(null);
      setGoogleToken(null);
      setExtractedEvidence([]);
      setLoadedDocTitle('');
      setDriveFiles([]);
    } catch (err: any) {
      setDocErrorMessage(err?.message || 'Failed to terminate session.');
    }
  };

  const handleFetchGoogleDoc = async () => {
    const docId = extractDocId(googleDocInput);
    if (!docId) {
      setDocErrorMessage('Please provide a valid Google Doc ID or Document URL.');
      return;
    }
    if (!googleToken) {
      setDocErrorMessage('Connection status: Offline. Authenticate Google Account.');
      return;
    }

    setIsFetchingDoc(true);
    setDocErrorMessage('');
    setExtractedEvidence([]);
    setLoadedDocTitle('');

    try {
      const { title, bodyText } = await fetchGoogleDoc(docId, googleToken);
      setLoadedDocTitle(title);
      const extracted = analyzeDocText(bodyText, title);
      setExtractedEvidence(extracted);
    } catch (err: any) {
      console.error(err);
      setDocErrorMessage(err?.message || 'Access Denied. Confirm your Google Account has permission and connection is online.');
    } finally {
      setIsFetchingDoc(false);
    }
  };

  const handleCommitEvidence = (items: ExtractedEvidence[]) => {
    if (items.length === 0) return;

    const confirmCommit = window.confirm(
      `Ingest and translate ${items.length} extracted OSINT evidence artifact(s) into the database?`
    );
    if (!confirmCommit) return;

    const newEvidence = items.map(item => ({
      id: `${item.id}-${Math.floor(Math.random() * 900 + 100)}`,
      source: item.source,
      description: item.description,
      status: 'Imported',
      date: new Date().toISOString().split('T')[0]
    }));

    setDossierState(prev => ({
      ...prev,
      evidence: [...newEvidence, ...prev.evidence]
    }));

    setExtractedEvidence([]);
    setLoadedDocTitle('');
    setGoogleDocInput('');
  };

  const handleScanDrive = async () => {
    if (!googleToken) {
      setDocErrorMessage('Authenticate Google Account first.');
      return;
    }
    setIsScanningDrive(true);
    setDocErrorMessage('');
    try {
      const files = await fetchDriveFiles(googleToken);
      setDriveFiles(files);
    } catch (err: any) {
      setDocErrorMessage(err?.message || 'Drive Scan Failed: ' + err.message);
    } finally {
      setIsScanningDrive(false);
    }
  };

  const handleIngestDriveFile = async (file: DriveFile) => {
    let extraData = '';
    
    // If it's a Google Sheet, let's actually read it
    if (file.mimeType.includes('spreadsheet') && googleToken) {
      try {
        const sheetData = await fetchGoogleSheet(file.id, googleToken);
        const rowCount = sheetData.rows.length;
        extraData = ` [SHEET SYNCED: Extracted ${rowCount} row(s) of structured intelligence.]`;
      } catch (err) {
        console.warn("Failed to extract sheet content:", err);
      }
    }

    const newEvidence = {
      id: `DRV-${file.id.substring(0,6).toUpperCase()}-${Math.floor(Math.random()*900+100)}`,
      source: `Google Drive: ${file.name}`,
      description: `Ingested restricted cloud file [Type: ${file.mimeType}]. Accessed via synchronized data port.${extraData}`,
      status: 'Target Loaded',
      date: new Date().toISOString().split('T')[0]
    };

    setDossierState(prev => ({
      ...prev,
      evidence: [newEvidence, ...prev.evidence]
    }));

    // hide from the working queue
    setDriveFiles(prev => prev.filter(f => f.id !== file.id));
  };

  const handleScanGmail = async () => {
    if (!googleToken) {
      setDocErrorMessage('Authenticate Google Account first.');
      return;
    }
    setIsScanningGmail(true);
    setDocErrorMessage('');
    try {
      const emails = await fetchRecentEmails(googleToken);
      setInterceptedEmails(emails);
    } catch (err: any) {
      setDocErrorMessage(err?.message || 'Gmail Scan Failed: ' + err.message);
    } finally {
      setIsScanningGmail(false);
    }
  };

  const handleIngestEmail = (email: EmailMessage) => {
    const newEvidence = {
      id: `GML-${email.id.substring(0,6).toUpperCase()}-${Math.floor(Math.random()*900+100)}`,
      source: `Intercepted Email: ${email.subject}`,
      description: `Communication Trace from: ${email.from}. Excerpt: "${email.snippet}"`,
      status: 'Intercepted',
      date: new Date().toISOString().split('T')[0]
    };

    setDossierState(prev => ({
      ...prev,
      evidence: [newEvidence, ...prev.evidence]
    }));

    setInterceptedEmails(prev => prev.filter(e => e.id !== email.id));
  };

  const selectedEntity = dossierState.entities.find(e => e.id === selectedEntityId);

  const tickerMessages = [
    "REAL-TIME UPDATE [06:15 AM]: Sector 4 - River Basin - Flash Flood (Active)",
    "FORENSIC ALERT: Hexavalent Chromium detected at 49x EPA safety limit",
    "CASE UPDATE: WB-2026-001-CA dossier moved to V3 synthesis stage",
    "TRACKER: Whistleblower 'Ironman' signal stable in Tijuana secure zone",
    "AUDIT LOG: $24B oversight failure confirmed at State Level"
  ];

  const terminalScanLogs = [
    "&gt; COLD START CORES... OK",
    "&gt; RESOLVING PORT LINK ... LOCATING GUEST EXEMPTIONS...",
    "&gt; CRITICAL EXPOSURE: HARVESTING GMAIL ATTACHMENTS...",
    "&gt; AUDITING CAL ICH HIGH-VELOCITY DISBURSEMENTS...",
    "&gt; TARGET RECORD DETECTED FOR: " + targetName.toUpperCase(),
    "&gt; SKEWING GEO-IP LOCATION TRACKER ANTENNAS...",
    "&gt; CROSS-CORRELATING SOIL TOXICITIES FOR HBNC...",
    "&gt; DECIPHERING BLOCKED DOCUMENTS AND HIDDEN FLASHDRIVE PARTITIONS...",
    "&gt; SYSTEM APPROVAL CODES EMITTED... ACCESS AUTHORIZED IN FULL.",
    "&gt; FORENSIC MATRIX DECRYPTED SUCCESSFULLY [98.4% MATCH CONFIDENCE]"
  ];

  // Dynamic status updates
  useEffect(() => {
    const timer = setInterval(() => {
      setTickerIndex(prev => (prev + 1) % tickerMessages.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  // Fast Pinball Backgrid flashing animation
  useEffect(() => {
    if (authPhase !== 'SCANNING') return;

    const lightsTimer = setInterval(() => {
      setMatrixStates(prev => prev.map(() => Math.random() > 0.45));
      setTerminalTicks(t => t + Math.floor(Math.random() * 300 + 40));
      setPinballBlink(b => !b);
    }, 110);

    return () => clearInterval(lightsTimer);
  }, [authPhase]);

  // Handle Scan Typewriter Sequence Control
  useEffect(() => {
    if (authPhase !== 'SCANNING') return;

    setScanStep(0);
    const traceTimer = setInterval(() => {
      setScanStep(prev => {
        if (prev >= terminalScanLogs.length - 1) {
          clearInterval(traceTimer);
          // Auto route to sheet findings
          setTimeout(() => {
            setAuthPhase('RESULTS');
          }, 600);
          return prev;
        }
        return prev + 1;
      });
    }, 400);

    return () => clearInterval(traceTimer);
  }, [authPhase]);

  const handleLaunchScan = (e: React.FormEvent) => {
    e.preventDefault();
    setAuthPhase('SCANNING');
  };

  // Preset quick binders
  const loadPreset = (name: string, phone: string, email: string) => {
    setTargetName(name);
    setTargetPhone(phone);
    setTargetEmail(email);
  };

  if (authPhase === 'INTRO') {
    return (
      <div className="h-screen w-full bg-[#050505] text-[#00FF41] flex flex-col font-mono overflow-auto border-4 border-[#00FF41] relative">
        {/* Dynamic Scan Interface grid lines */}
        <div className="absolute inset-0 pointer-events-none opacity-[0.08]" 
             style={{ backgroundImage: 'linear-gradient(#ffffff 1px, transparent 1px), linear-gradient(90deg, #ffffff 1px, transparent 1px)', backgroundSize: '25px 25px' }} />

        {/* Branding Terminal Header */}
        <header className="flex items-end justify-between px-6 py-4 border-b-4 border-[#00FF41] shrink-0 bg-black z-10">
          <div>
            <h1 className="text-7xl font-black leading-none tracking-tighter uppercase py-1">OSINT.v2</h1>
            <p className="text-[10px] opacity-70 tracking-[0.2em] uppercase text-[#00FF41]">OPEN SOURCE INTELLIGENCE NETWORK TERMINAL // COLD INGRESS</p>
          </div>
          <div className="text-right uppercase hidden sm:block">
            <div className="text-2xl font-black text-[#00FF41] animate-pulse">[ INTRUDER_SCAN ]</div>
            <div className="text-[10px] opacity-60">SYSTEM STATUS: READY FOR INPUT</div>
          </div>
        </header>

        {/* Central Card Form */}
        <div className="flex-1 max-w-5xl w-full mx-auto p-4 md:p-8 flex flex-col justify-center z-10">
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-[#002202] border-4 border-[#00FF41] shadow-[0_0_15px_rgba(0,255,65,0.4)] animate-pulse mb-3">
              <Zap className="w-10 h-10 text-[#00FF41]" />
            </div>
            <h2 className="text-4xl font-black uppercase tracking-widest text-[#00FF41] mb-1">Target Subject Ingress</h2>
            <p className="text-xs text-[#00FF41]/70 max-w-xl mx-auto uppercase">
              Enter variable credentials for active forensic tracking across environmental telemetry databases.
            </p>
          </div>

          <form onSubmit={handleLaunchScan} className="border-4 border-[#00FF41] bg-black p-6 md:p-8 space-y-6 relative">
            <div className="absolute top-0 right-0 bg-[#00FF41] text-black font-black text-[10px] px-3 py-1 uppercase scale-90 translate-y-[-100%] translate-x-1">
              SYS-ENTRY MODULE
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-[#00FF41] block">
                  Subject Identifier Name:
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-3 text-[#00FF41]/50 text-xs font-bold">NAME_ID &gt;</span>
                  <Input 
                    type="text" 
                    required
                    value={targetName}
                    onChange={(e) => setTargetName(e.target.value)}
                    className="pl-24 bg-black border-2 border-[#00FF41] text-[#00FF41] font-mono h-11 focus:ring-1 focus:ring-[#00FF41] rounded-none focus:outline-none placeholder-emerald-900 font-bold"
                    placeholder="e.g. Anthony DiMarcello"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-[#00FF41] block">
                  Forensic Reference Code:
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-3 text-[#00FF41]/50 text-xs font-bold">CASE_ID &gt;</span>
                  <Input 
                    type="text" 
                    required
                    value={targetCaseRef}
                    onChange={(e) => setTargetCaseRef(e.target.value)}
                    className="pl-24 bg-black border-2 border-[#00FF41] text-[#00FF41] font-mono h-11 focus:ring-1 focus:ring-[#00FF41] rounded-none focus:outline-none placeholder-emerald-900 font-bold"
                    placeholder="e.g. WB-2026-001-CA"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-[#00FF41] block">
                  Subject Phone Contact:
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-3 text-[#00FF41]/50 text-xs font-bold">TELE_ID &gt;</span>
                  <Input 
                    type="text" 
                    required
                    value={targetPhone}
                    onChange={(e) => setTargetPhone(e.target.value)}
                    className="pl-24 bg-black border-2 border-[#00FF41] text-[#00FF41] font-mono h-11 focus:ring-1 focus:ring-[#00FF41] rounded-none focus:outline-none placeholder-emerald-900 font-bold"
                    placeholder="e.g. +1 (949) 555-0199"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold uppercase tracking-wider text-[#00FF41] block">
                  Subject Email Contact:
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-3 text-[#00FF41]/50 text-xs font-bold">MAIL_ID &gt;</span>
                  <Input 
                    type="email" 
                    required
                    value={targetEmail}
                    onChange={(e) => setTargetEmail(e.target.value)}
                    className="pl-24 bg-black border-2 border-[#00FF41] text-[#00FF41] font-mono h-11 focus:ring-1 focus:ring-[#00FF41] rounded-none focus:outline-none placeholder-emerald-900 font-bold"
                    placeholder="e.g. anthonymd949@gmail.com"
                  />
                </div>
              </div>
            </div>

            {/* Quick hot load presets */}
            <div className="p-3 bg-[#001100] border border-[#00FF41]/40">
              <span className="text-[9px] uppercase font-black text-[#00FF41]/60 block mb-2 tracking-widest">
                Forensic Autocompleter Presets (Select subject Variable set):
              </span>
              <div className="flex flex-wrap gap-2">
                <button 
                  type="button"
                  onClick={() => loadPreset("Anthony DiMarcello", "+1 (949) 555-0199", "anthonymd949@gmail.com")}
                  className="px-2.5 py-1 bg-black hover:bg-[#003310] text-[#00FF41] border border-[#00FF41] text-[10px] font-bold uppercase transition-colors rounded-none"
                >
                  PRESET_A: Ironman Whistleblower
                </button>
                <button 
                  type="button"
                  onClick={() => loadPreset("Elias Thorne", "+1 (714) 555-0242", "elias.thorne.pro@gmail.com")}
                  className="px-2.5 py-1 bg-black hover:bg-[#003310] text-[#00FF41] border border-[#00FF41] text-[10px] font-bold uppercase transition-colors rounded-none"
                >
                  PRESET_B: Lead Environmental Insp.
                </button>
                <button 
                  type="button"
                  onClick={() => loadPreset("Scott Davis", "+1 (310) 555-0988", "sdavis.bunktech@outlook.com")}
                  className="px-2.5 py-1 bg-black hover:bg-[#003310] text-[#00FF41] border border-[#00FF41] text-[10px] font-bold uppercase transition-colors rounded-none"
                >
                  PRESET_C: Suppressed Alchemist
                </button>
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full bg-[#00FF41] text-black hover:text-white hover:bg-black border-2 border-[#00FF41] h-14 text-xl font-black uppercase transition-all rounded-none tracking-wider cursor-pointer shadow-[0_0_15px_rgba(0,255,65,0.3)] gap-2 flex items-center justify-center p-0"
            >
              <Terminal className="w-5 h-5 shrink-0" />
              SOLICIT HARVEST & FLASH SYSTEM
            </Button>
          </form>
        </div>

        <footer className="bg-[#00FF41] text-black px-6 py-2 text-center text-xs font-bold uppercase shrink-0 mt-auto">
          OSINT HARVEST INFRASTRUCTURE ONLINE // DIRECT ENTRY MODULE
        </footer>
      </div>
    );
  }

  if (authPhase === 'SCANNING') {
    return (
      <div className="h-screen w-full bg-[#050505] text-[#00FF41] flex flex-col font-mono overflow-hidden border-4 border-[#00FF41] relative">
        {/* Rapid color flashing simulating custom pinball bumpers */}
        {pinballBlink && (
          <div className="absolute inset-0 bg-[#00FF41]/5 pointer-events-none transition-all duration-75" />
        )}

        <header className="flex justify-between items-center px-6 py-4 border-b-4 border-[#00FF41] bg-black">
          <div>
            <h1 className="text-4xl font-black uppercase tracking-tight text-[#00FF41] animate-pulse">FLASH-HARVEST DIAGNOSTIC SEQUENCER</h1>
            <p className="text-[10px] opacity-70 uppercase tracking-widest">BUMPER MATRIX HIGH-VOLTAGE INDUCTION ACTIVE</p>
          </div>
          <div className="text-right">
            <span className="inline-block px-3 py-1 bg-red-600 text-white font-black text-xs animate-ping uppercase">HARVESTING</span>
          </div>
        </header>

        <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 p-6 overflow-hidden">
          {/* Diagnostic Lights Deck representing retro pinball machine indicators */}
          <div className="border-4 border-[#00FF41] bg-black p-6 flex flex-col justify-between items-center relative gap-4">
            <div className="absolute top-2 left-2 text-[10px] opacity-50 uppercase font-black">SOLENOID BANK GRID</div>
            <div className="text-center w-full mt-4">
              <div className="text-zinc-500 text-[9px] uppercase font-bold tracking-widest">Current Points Accumulator</div>
              <div className="text-3xl font-black text-white mt-1 tracking-wider">
                SCORE: {terminalTicks.toLocaleString()} PL
              </div>
            </div>

            {/* Backbox Blinking Matrix */}
            <div className="grid grid-cols-4 gap-3 p-4 bg-[#001100] border-4 border-[#00FF41] shrink-0">
              {matrixStates.map((val, idx) => (
                <div 
                  key={idx} 
                  className={cn(
                    "w-10 h-10 rounded-none border-2 transition-all duration-75 flex items-center justify-center font-black text-xs",
                    val 
                      ? "bg-[#00FF41] border-white text-black shadow-[0_0_15px_#00FF41]" 
                      : "bg-[#002202] border-[#00FF41]/40 text-[#00FF41]/30"
                  )}
                >
                  {val ? '⚡' : '●'}
                </div>
              ))}
            </div>

            {/* Dynamic Signal Logs */}
            <div className="w-full space-y-1 text-xs">
              <div className="flex justify-between items-center p-2 border border-[#00FF41]/30 bg-[#001100]">
                <span className="font-bold opacity-60">PULL SLINGSHOT B</span>
                <span className="text-white animate-pulse">TRIGGERED</span>
              </div>
              <div className="flex justify-between items-center p-2 border border-[#00FF41]/30 bg-[#001100]">
                <span className="font-bold opacity-60">OUTLANE SENSORS</span>
                <span className="text-[#00FF41] animate-bounce">LOCK IN_ZONE</span>
              </div>
              <div className="flex justify-between items-center p-2 border border-[#00FF41]/30 bg-[#001100]">
                <span className="font-bold opacity-60">COVERT TELEMETRY</span>
                <span className="text-[#00FF41]">ACTIVE [98.4%]</span>
              </div>
            </div>
          </div>

          {/* Running logs outputting typewriter information */}
          <div className="col-span-2 border-4 border-[#00FF41] bg-black p-6 flex flex-col justify-between overflow-hidden">
            <div className="flex justify-between items-center border-b-2 border-[#00FF41] pb-3 mb-4">
              <div className="text-sm font-black uppercase tracking-wider flex items-center gap-2 text-[#00FF41]">
                <Terminal className="w-4 h-4 text-[#00FF41]" />
                Harvest stream diagnostic trace
              </div>
              <div className="text-[9px] text-[#00FF41]/40 uppercase font-bold">PORT INTEGRATION: STABLE</div>
            </div>

            <ScrollArea className="flex-1 font-mono text-sm space-y-1.5 pr-2">
              <AnimatePresence>
                {terminalScanLogs.slice(0, scanStep + 1).map((log, idx) => (
                  <motion.div 
                    key={idx}
                    initial={{ opacity: 0, x: -6 }}
                    animate={{ opacity: 1, x: 0 }}
                    className={cn(
                      "py-0.5 break-all",
                      idx === scanStep ? "text-white font-extrabold text-base" : "text-[#00FF41]/70"
                    )}
                    dangerouslySetInnerHTML={{ __html: log }}
                  />
                ))}
              </AnimatePresence>
            </ScrollArea>

            <div className="border-t-2 border-[#00FF41] pt-4 mt-4 flex items-center justify-between bg-[#001100] p-3 text-xs">
              <div className="flex items-center gap-2">
                <Sliders className="w-4 h-4 animate-spin text-[#00FF41]" />
                <span className="font-bold uppercase tracking-widest text-[#00FF41]">MATRIX ALIGNMENT LEVEL: EXCELLENT</span>
              </div>
              <div className="text-white uppercase font-black">
                STABLE: {(scanStep + 1) * 10}%
              </div>
            </div>
          </div>
        </div>

        <footer className="bg-[#00FF41] text-black px-6 py-2 text-center text-xs font-bold uppercase shrink-0">
          COMPILING HARVEST DATA DISCOVERIES INTO ALIGNED RELATION SHEETS
        </footer>
      </div>
    );
  }

  if (authPhase === 'RESULTS') {
    return (
      <div className="h-screen w-full bg-[#050505] text-[#00FF41] flex flex-col font-mono overflow-auto border-4 border-[#00FF41] relative">
        <header className="flex items-end justify-between px-6 py-4 border-b-4 border-[#00FF41] bg-black shrink-0">
          <div>
            <h1 className="text-6xl font-black leading-none tracking-tighter uppercase py-1 text-[#00FF41]">SYNTHESIZED SHEET FINDINGS</h1>
            <p className="text-[10px] opacity-70 tracking-[0.2em] uppercase text-[#00FF41]">CONSOLIDATED TARGET AUDIT RESULTS // REAL-TIME ALCHEMY</p>
          </div>
          <div className="text-right uppercase">
            <div className="text-xs opacity-50">STATUS: MATCH ARCHIVES POPULATED</div>
            <div className="text-lg font-bold text-white">CASE REF: {targetCaseRef}</div>
          </div>
        </header>

        <div className="flex-1 p-6 max-w-6xl w-full mx-auto space-y-6">
          <div className="bg-[#001100] border-4 border-[#00FF41] p-4 text-xs tracking-wider uppercase leading-relaxed text-center font-bold">
            ⚡ MATCH RECOVERY COMPLETE! THE FOLLOWING SPREADSHEET DETAILED ENTRIES SECURELY INTERSECT WITH FILES IN ACTIVE ARCHIVE DIRECTORIES:
          </div>

          <div className="border-4 border-[#00FF41] bg-black overflow-hidden shadow-[0_0_20px_rgba(0,170,40,0.2)]">
            <Table>
              <TableHeader className="bg-[#003310]">
                <TableRow className="border-b-4 border-[#00FF41] hover:bg-transparent">
                  <TableHead className="text-black font-black uppercase text-center w-12 bg-[#00FF41]">SEC</TableHead>
                  <TableHead className="text-[#00FF41] font-black uppercase tracking-wider pl-4">SUBMITTED PARAMETER</TableHead>
                  <TableHead className="text-[#00FF41] font-black uppercase tracking-wider pl-4">YOUR DATA ENTRIES</TableHead>
                  <TableHead className="text-[#00FF41] font-black uppercase tracking-wider pl-4">RECOVERED DATABASE MATCH FILES</TableHead>
                  <TableHead className="text-[#00FF41] font-black uppercase tracking-wider pl-4">STATUS CONFIDENCE</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow className="border-b-2 border-[#00FF41]/20 hover:bg-[#003310]/10 text-[#00FF41]">
                  <TableCell className="font-bold text-center bg-[#00FF41]/10">01</TableCell>
                  <TableCell className="font-bold uppercase tracking-tight pl-4">TARGET LEGAL NAME</TableCell>
                  <TableCell className="font-bold text-white pl-4">{targetName}</TableCell>
                  <TableCell className="pl-4 text-xs">
                    Whistleblower profile matching Anthony DiMarcello (Ironman) flagged active in Tijuana Secure Area.
                  </TableCell>
                  <TableCell className="pl-4">
                    <Badge className="bg-[#00FF41] text-black font-black text-[10px] rounded-none">98.4% CONFIRMED</Badge>
                  </TableCell>
                </TableRow>

                <TableRow className="border-b-2 border-[#00FF41]/20 hover:bg-[#003310]/10 text-[#00FF41]">
                  <TableCell className="font-bold text-center bg-[#00FF41]/10">02</TableCell>
                  <TableCell className="font-bold uppercase tracking-tight pl-4">TARGET MOBILE CONTACT</TableCell>
                  <TableCell className="font-bold text-white pl-4">{targetPhone}</TableCell>
                  <TableCell className="pl-4 text-xs">
                    Located in hidden spreadsheet partitions and non-standard communications logs on local forensic disk.
                  </TableCell>
                  <TableCell className="pl-4">
                    <Badge className="bg-[#003310] text-[#00FF41] border border-[#00FF41] font-black text-[10px] rounded-none">SECURE TRACE</Badge>
                  </TableCell>
                </TableRow>

                <TableRow className="border-b-2 border-[#00FF41]/20 hover:bg-[#003310]/10 text-[#00FF41]">
                  <TableCell className="font-bold text-center bg-[#00FF41]/10">03</TableCell>
                  <TableCell className="font-bold uppercase tracking-tight pl-4">TARGET EMAIL SERVER</TableCell>
                  <TableCell className="font-bold text-white pl-4">{targetEmail}</TableCell>
                  <TableCell className="pl-4 text-xs">
                    Historic mail communications found relating to Huntington Beach CEQA review bypass bypass.
                  </TableCell>
                  <TableCell className="pl-4">
                    <Badge className="bg-[#003310] text-red-500 border border-red-500/50 font-black text-[10px] rounded-none">HIGH SECURITY RISK</Badge>
                  </TableCell>
                </TableRow>

                <TableRow className="border-b-2 border-[#00FF41]/20 hover:bg-[#003310]/10 text-[#00FF41]">
                  <TableCell className="font-bold text-center bg-[#00FF41]/10">04</TableCell>
                  <TableCell className="font-bold uppercase tracking-tight pl-4">PRIMARY CONTAMINANT</TableCell>
                  <TableCell className="font-bold text-white pl-4">HEXAVALENT CHROMIUM</TableCell>
                  <TableCell className="pl-4 text-xs">
                    Associated site Huntington Beach Navigation Center (HBNC) contains toxicity levels at 49x standard limit.
                  </TableCell>
                  <TableCell className="pl-4">
                    <Badge className="bg-red-700 text-white font-black text-[10px] rounded-none">LETHAL TOXICITY</Badge>
                  </TableCell>
                </TableRow>

                <TableRow className="hover:bg-[#003310]/10 text-[#00FF41]">
                  <TableCell className="font-bold text-center bg-[#00FF41]/10">05</TableCell>
                  <TableCell className="font-bold uppercase tracking-tight pl-4">BUDGET FRAUD INDICATORS</TableCell>
                  <TableCell className="font-bold text-white pl-4">$24.0 BILLION AUDIT</TableCell>
                  <TableCell className="pl-4 text-xs">
                    Cal ICH failure to monitor effectiveness. Orange County housing grant diversion schemas confirmed.
                  </TableCell>
                  <TableCell className="pl-4">
                    <Badge className="bg-purple-900 text-purple-300 font-black text-[10px] rounded-none">FRAUD_LINK</Badge>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between pt-4">
            <div className="text-zinc-500 text-xs text-center sm:text-left font-bold uppercase tracking-tight leading-relaxed">
              * Click below to migrate these findings directly into the relational topological matrix, mapping grids, and AI core.
            </div>
            <div className="flex gap-4">
              <Button 
                onClick={() => setAuthPhase('INTRO')}
                className="bg-black hover:bg-zinc-950 text-[#00FF41] border-2 border-[#00FF41] h-14 px-6 text-sm font-black uppercase rounded-none tracking-tight cursor-pointer"
              >
                &lt;&lt; BACK TO DATA INPUT
              </Button>
              <Button 
                onClick={() => setAuthPhase('DASHBOARD')}
                className="bg-[#00FF41] text-black hover:bg-white hover:text-black border-2 border-[#000000] h-14 px-8 text-lg font-black uppercase rounded-none tracking-tight cursor-pointer shadow-[0_0_15px_rgba(0,255,65,0.4)]"
              >
                ACCESS RELATIONAL SYSTEM BACKBONE &gt;&gt;
              </Button>
            </div>
          </div>
        </div>

        <footer className="bg-[#00FF41] text-black px-6 py-2 text-center text-xs font-bold uppercase shrink-0 mt-auto">
          DATA SHEET COALIGNMENT COMPLETED SUCCESSFULLY // SECURE EXPORT DEPLOYED
        </footer>
      </div>
    );
  }

  // Normal dashboard view returning from authPhase === 'DASHBOARD'
  return (
    <div className="h-screen w-full bg-[#050505] text-[#00FF41] flex flex-col font-mono overflow-hidden border-4 border-[#00FF41]">
      {/* Header */}
      <header className="flex items-end justify-between px-6 py-4 border-b border-[#00FF41]">
        <div>
          <h1 className="text-8xl font-black leading-none tracking-tighter uppercase py-2">OSINT.v2</h1>
          <p className="text-[10px] mt-1 opacity-70 tracking-[0.2em] uppercase">OPEN SOURCE INTELLIGENCE NETWORK TERMINAL // ACCESS GRANTED</p>
        </div>
        <div className="text-right uppercase">
          <div className="text-4xl font-bold font-mono">OP_NIGHTFALL</div>
          <div className="text-xs">SYSTEM STATUS: OPTIMAL</div>
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden">
        {/* Navigation Rail / Aside */}
        <aside className="w-72 border-r border-[#00FF41] p-6 flex flex-col gap-6 bg-[#050505]">
          <section>
            <label className="text-[10px] uppercase tracking-widest block mb-2 opacity-60">Operations</label>
            <div className="space-y-2 font-mono">
              <NavBtn 
                active={viewMode === 'NETWORK'} 
                icon={<Share2 className="w-4 h-4 text-inherit" />} 
                label="Target Mapping" 
                onClick={() => setViewMode('NETWORK')}
              />
              <NavBtn 
                active={viewMode === 'MAP'} 
                icon={<MapIcon className="w-4 h-4 text-inherit" />} 
                label="Geospatial Tracker" 
                onClick={() => setViewMode('MAP')}
              />
              <NavBtn 
                active={viewMode === 'DOSSIER'} 
                icon={<FileText className="w-4 h-4 text-inherit" />} 
                label="Evidence Vault" 
                onClick={() => setViewMode('DOSSIER')}
              />
              <NavBtn 
                active={viewMode === 'AI'} 
                icon={<Sparkles className="w-4 h-4 text-inherit" />} 
                label="Neo AI Core" 
                onClick={() => setViewMode('AI')}
              />
            </div>
          </section>

          <section className="flex-1">
            <label className="text-[10px] uppercase tracking-widest block mb-2 opacity-60">Quick Filters</label>
            <div className="space-y-2 font-mono">
              <FilterBtn label="Lethal Toxicity" color="bg-[#003310] border-[#00FF41] text-[#00FF41]" />
              <FilterBtn label="State Corruption" color="bg-[#003310] border-[#00FF41] text-[#00FF41]" />
              <FilterBtn label="Suppressed Tech" color="bg-[#003310] border-[#00FF41] text-[#00FF41]" />
            </div>
          </section>

          <div className="mt-auto border-t border-[#00FF41] pt-4">
            <div className="text-[40px] font-black leading-none mb-1">98.4%</div>
            <div className="text-[10px] uppercase opacity-60">Confidence Index</div>
          </div>
        </aside>

        {/* Content Area */}
        <section className="flex-1 flex flex-col bg-[#050505]">
          <div className="p-6 flex-1 bg-[radial-gradient(#00FF41_1px,transparent_1px)] [background-size:20px_20px] relative overflow-hidden">
            <header className="h-14 border border-[#00FF41] flex items-center justify-between px-6 bg-black/80 backdrop-blur-sm z-10 mb-6 font-mono">
              <div className="flex items-center gap-4">
                <span className="text-[10px] font-mono text-[#00FF41] opacity-70 uppercase tracking-widest">CASE ID: {targetCaseRef}</span>
                <Separator orientation="vertical" className="h-4 bg-[#00FF41]/30" />
                <Badge variant="outline" className="text-[9px] border-[#00FF41] text-[#00FF41] uppercase tracking-widest bg-[#003310]">
                  Target: {targetName}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" className="text-[#00FF41] hover:bg-[#003310]" onClick={() => setAuthPhase('INTRO')}>
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  INTRO
                </Button>
                <Button size="sm" className="bg-[#00FF41] text-black font-bold uppercase transition-colors hover:bg-white border-0" onClick={() => setAuthPhase('INTRO')}>
                  <Sliders className="w-3 h-3 mr-2" />
                  RE-HARVEST
                </Button>
              </div>
            </header>

            <div className="h-[calc(100%-80px)]">
              <AnimatePresence mode="wait">
                <motion.div 
                  key={viewMode}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="h-full w-full"
                >
                  {viewMode === 'NETWORK' && (
                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full">
                      <div className="lg:col-span-3 h-full border-4 border-[#00FF41] bg-black">
                        <NetworkGraph data={dossierState} onNodeClick={setSelectedEntityId} />
                      </div>
                      <div className="lg:col-span-1 border-4 border-[#00FF41] bg-black p-6 overflow-auto">
                        <EntityInspector entity={selectedEntity} connections={dossierState.connections} />
                      </div>
                    </div>
                  )}

                  {viewMode === 'MAP' && (
                    <div className="h-full border-4 border-[#00FF41]">
                      <MapTracker />
                    </div>
                  )}

                  {viewMode === 'DOSSIER' && (
                    <div className="h-full border-4 border-[#00FF41]">
                      <EvidenceVault 
                        evidenceList={dossierState.evidence}
                        googleUser={googleUser}
                        googleToken={googleToken}
                        googleDocInput={googleDocInput}
                        setGoogleDocInput={setGoogleDocInput}
                        isFetchingDoc={isFetchingDoc}
                        extractedEvidence={extractedEvidence}
                        loadedDocTitle={loadedDocTitle}
                        docErrorMessage={docErrorMessage}
                        driveFiles={driveFiles}
                        isScanningDrive={isScanningDrive}
                        interceptedEmails={interceptedEmails}
                        isScanningGmail={isScanningGmail}
                        onGoogleSignIn={handleGoogleSignIn}
                        onGoogleSignOut={handleGoogleSignOut}
                        onFetchGoogleDoc={handleFetchGoogleDoc}
                        onCommitEvidence={handleCommitEvidence}
                        onScanDrive={handleScanDrive}
                        onIngestDriveFile={handleIngestDriveFile}
                        onScanGmail={handleScanGmail}
                        onIngestEmail={handleIngestEmail}
                        onCancelDoc={() => {
                          setExtractedEvidence([]);
                          setLoadedDocTitle('');
                          setGoogleDocInput('');
                        }}
                      />
                    </div>
                  )}

                  {viewMode === 'AI' && (
                    <div className="h-full border-4 border-[#00FF41]">
                      <NeoAnalysis onCommitEvidence={handleCommitEvidence} />
                    </div>
                  )}
                </motion.div>
              </AnimatePresence>
            </div>
          </div>

          <div className="h-48 border-t border-[#00FF41] bg-[#001100] p-6 overflow-hidden relative">
            <div className="text-[10px] uppercase opacity-60 mb-2 flex items-center justify-between">
              <span>Live Activity Stream</span>
              <Activity className="w-3 h-3 text-[#00FF41] animate-pulse" />
            </div>
            <div className="space-y-1 text-xs opacity-80 font-mono">
              <p className="text-[#00FF41] tracking-tighter transition-all duration-300">
                &gt; {tickerMessages[tickerIndex]}
              </p>
              <p>&gt; Scanned Target Account: {targetEmail}</p>
              <p>&gt; Verification Source: {targetPhone}</p>
              <p>&gt; Whistleblowing dossier indexed successfully.</p>
              <p className="text-white">&gt; Status: Connection Optimized</p>
            </div>
          </div>
        </section>

        {/* Right Sidebar */}
        <aside className="w-64 border-l border-[#00FF41] flex flex-col bg-[#050505]">
          <div className="p-4 border-b border-[#00FF41] flex flex-col gap-2 font-mono">
            <div>
              <div className="text-[10px] uppercase opacity-60 font-mono tracking-widest">Target Hash</div>
              <div className="break-all text-[11px] font-mono text-[#00FF41]">8f2e4a9b1c5d7e0f9b8a7c6d5e4f3a2b</div>
            </div>
          </div>
          <div className="flex-1 p-4">
            <div className="text-[10px] uppercase opacity-60 mb-4 font-mono tracking-widest">Visual Intel</div>
            <div className="grid grid-cols-2 gap-2">
              <div className="aspect-square bg-[#003310] border border-[#00FF41]/30 flex items-center justify-center text-[10px] text-[#00FF41]/50 italic text-center font-bold">REF_A</div>
              <div className="aspect-square bg-[#003310] border border-[#00FF41]/30 flex items-center justify-center text-[10px] text-[#00FF41]/50 italic text-center font-bold">REF_B</div>
              <div className="aspect-square bg-[#003310] border border-[#00FF41]/30 flex items-center justify-center text-[10px] text-[#00FF41]/50 italic text-center font-bold">REF_C</div>
              <div className="aspect-square bg-[#003310] border border-[#00FF41]/30 flex items-center justify-center text-[10px] text-[#00FF41]/50 italic text-center font-bold">REF_D</div>
            </div>
          </div>
          <button 
            type="button"
            className="m-4 bg-[#00FF41] text-black font-black py-4 uppercase text-lg hover:bg-white transition-colors cursor-pointer border-0"
            onClick={() => {
              setTargetName('Anthony DiMarcello');
              setTargetPhone('+1 (949) 555-0199');
              setTargetEmail('anthonymd949@gmail.com');
              setTargetCaseRef('WB-2026-001-CA');
              setAuthPhase('INTRO');
            }}
          >
            RESET ALL
          </button>
        </aside>
      </main>

      <footer className="bg-[#00FF41] text-black px-6 py-1 flex justify-between items-center text-[10px] font-bold uppercase z-20">
        <div className="flex gap-8 font-mono">
          <span>LAT: 38.8951 N</span>
          <span>LON: 77.0364 W</span>
          <span>ALT: 18M</span>
        </div>
        <div className="animate-pulse">RECORDING DATA STREAM [ LIVE ]</div>
      </footer>
    </div>
  );
}

function NavBtn({ active, icon, label, onClick }: { active: boolean, icon: any, label: string, onClick: () => void }) {
  return (
    <button 
      onClick={onClick}
      className={cn(
        "w-full flex items-center gap-3 px-4 py-3 text-sm transition-all duration-200 group text-left border-2 uppercase font-black tracking-tighter cursor-pointer",
        active 
          ? "bg-[#00FF41] text-black border-[#00FF41]" 
          : "text-[#00FF41]/60 hover:text-[#00FF41] hover:bg-[#003310] border-transparent"
      )}
    >
      <span className="flex-shrink-0">{icon}</span>
      <span className="truncate">{label}</span>
      {active && <ChevronRight className="ml-auto w-4 h-4" />}
    </button>
  );
}

function FilterBtn({ label, color }: { label: string, color: string }) {
  return (
    <button className={cn("w-full text-left px-3 py-2 border transition-colors hover:brightness-125 text-[10px] uppercase font-bold tracking-widest cursor-pointer", color)}>
      {label}
    </button>
  );
}

function EntityInspector({ entity, connections }: { entity: any, connections: any[] }) {
  if (!entity) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-4">
        <User className="w-12 h-12 text-[#00FF41]/20 mb-4" />
        <h3 className="text-[#00FF41] font-black uppercase text-xs mb-2">TARGET SELECTION REQUIRED</h3>
        <p className="text-[10px] text-[#00FF41]/50 font-mono animate-pulse">Select a node from the network graph to decrypt terminal forensic data.</p>
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="space-y-6 overflow-hidden"
    >
      <div>
        <Badge className="mb-2 bg-[#003310] text-[#00FF41] border-[#00FF41] text-[9px] uppercase tracking-widest">{entity.type}</Badge>
        <h2 className="text-4xl font-black uppercase leading-none text-[#00FF41] break-words">{entity.name}</h2>
        <p className="text-xs text-[#00FF41]/70 mt-4 leading-relaxed font-mono italic">{entity.description}</p>
      </div>

      <Separator className="bg-[#00FF41]/20" />

      <div className="space-y-4 font-mono text-[11px]">
        <h4 className="text-[#00FF41]/50 uppercase tracking-widest text-[9px] font-black">Forensic Tags</h4>
        <div className="flex flex-wrap gap-2">
          {entity.type === 'PERSON' && <Badge variant="secondary" className="bg-[#003310] text-[#00FF41] text-[9px] border border-[#00FF41]/30">Verified Identity</Badge>}
          {entity.type === 'LOCATION' && <Badge variant="secondary" className="bg-[#003310] text-red-500 border border-red-500/30 text-[9px]">Biohazard Site</Badge>}
          {entity.type === 'TECHNOLOGY' && <Badge variant="secondary" className="bg-[#003310] text-purple-400 border border-purple-400/30 text-[9px]">Suppressed Archive</Badge>}
        </div>
      </div>

      <Separator className="bg-[#00FF41]/20" />

      <div className="space-y-3">
        <h4 className="text-[#00FF41]/50 uppercase tracking-widest text-[9px] font-black font-mono">Relational Links</h4>
        <div className="space-y-2">
          {connections
            .filter(c => c.source === entity.id || c.target === entity.id)
            .map((c, i) => (
              <div key={i} className="bg-[#003310]/30 p-2 border-2 border-[#00FF41]/10 flex flex-col gap-1 transition-colors hover:border-[#00FF41]">
                <span className="text-[10px] text-white truncate font-bold">
                  {c.source === entity.id ? c.target : c.source}
                </span>
                <span className="text-[9px] font-mono text-[#00FF41] uppercase">{c.label}</span>
              </div>
            ))
          }
        </div>
      </div>
    </motion.div>
  );
}

interface EvidenceVaultProps {
  evidenceList: any[];
  googleUser: FirebaseUser | null;
  googleToken: string | null;
  googleDocInput: string;
  setGoogleDocInput: (val: string) => void;
  isFetchingDoc: boolean;
  extractedEvidence: ExtractedEvidence[];
  loadedDocTitle: string;
  docErrorMessage: string;
  driveFiles: DriveFile[];
  isScanningDrive: boolean;
  interceptedEmails: EmailMessage[];
  isScanningGmail: boolean;
  onGoogleSignIn: () => Promise<void>;
  onGoogleSignOut: () => Promise<void>;
  onFetchGoogleDoc: () => Promise<void>;
  onCommitEvidence: (items: ExtractedEvidence[]) => void;
  onScanDrive: () => Promise<void>;
  onIngestDriveFile: (file: DriveFile) => void;
  onScanGmail: () => Promise<void>;
  onIngestEmail: (email: EmailMessage) => void;
  onCancelDoc: () => void;
}

function EvidenceVault({
  evidenceList,
  googleUser,
  googleToken,
  googleDocInput,
  setGoogleDocInput,
  isFetchingDoc,
  extractedEvidence,
  loadedDocTitle,
  docErrorMessage,
  driveFiles,
  isScanningDrive,
  interceptedEmails,
  isScanningGmail,
  onGoogleSignIn,
  onGoogleSignOut,
  onFetchGoogleDoc,
  onCommitEvidence,
  onScanDrive,
  onIngestDriveFile,
  onScanGmail,
  onIngestEmail,
  onCancelDoc
}: EvidenceVaultProps) {
  return (
    <Card className="bg-black border-0 rounded-none h-full overflow-auto text-[#00FF41]">
      <CardHeader className="border-b-4 border-[#00FF41] bg-[#003310]/50 sticky top-0 z-10 flex flex-col md:flex-row md:items-center justify-between p-6 gap-4">
        <div>
          <CardTitle className="text-4xl font-black uppercase text-[#00FF41]">Artifact Repository</CardTitle>
          <CardDescription className="text-[#00FF41]/70 text-[10px] font-mono uppercase tracking-[0.2em]">
            Consolidated Forensic Evidence Audit // Case WB-2026
          </CardDescription>
        </div>
        
        {/* Google Connection Header */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 bg-black border-2 border-[#00FF41]/30 p-2 text-xs">
          {!googleUser ? (
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-[#00FF41]/60 uppercase font-bold">Docs Extraction Core:</span>
              <button 
                onClick={onGoogleSignIn}
                className="text-xs py-1.5 px-3 bg-[#002202] text-[#00FF41] hover:text-white border border-[#00FF41] font-black uppercase transition-all tracking-wider flex items-center justify-center gap-1.5 cursor-pointer hover:bg-[#004404]"
              >
                <div style={{ width: '12px', height: '12px' }} className="shrink-0 flex items-center justify-center">
                  <svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
                    <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"></path>
                    <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"></path>
                    <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"></path>
                    <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"></path>
                  </svg>
                </div>
                <span className="text-[10px]">Google Connect</span>
              </button>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row sm:items-center gap-3">
              <div className="text-left">
                <div className="text-[9px] uppercase text-[#00FF41]/50 font-bold">Connected Agent:</div>
                <div className="font-bold text-white text-[11px] max-w-[140px] truncate">{googleUser.email}</div>
              </div>
              <button 
                onClick={onGoogleSignOut} 
                className="px-2 py-1 bg-black hover:bg-red-950 text-red-500 border border-red-500 text-[10px] font-black uppercase transition-colors rounded-none cursor-pointer"
              >
                Disconnect
              </button>
            </div>
          )}
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* If user is connected to Google, show URL loading form */}
        {googleUser && (
          <div className="p-4 border-2 border-[#00FF41]/50 bg-[#001100]/20 relative">
            <div className="absolute top-0 right-3 bg-[#00FF41] text-black font-black text-[9px] px-2 py-0.5 uppercase translate-y-[-50%]">
              Live Google Doc Ingestion Core &nbsp;[Active]
            </div>
            
            <div className="space-y-4 pt-1">
              <div>
                <p className="text-xs font-bold text-[#00FF41] uppercase tracking-wide mb-2">
                  Target Google Document URL or Document ID:
                </p>
                <div className="flex flex-col sm:flex-row gap-2">
                  <Input 
                    type="text"
                    value={googleDocInput}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => setGoogleDocInput(e.target.value)}
                    placeholder="https://docs.google.com/document/d/..."
                    className="flex-1 bg-black border border-[#00FF41] text-[#00FF41] font-mono h-10 px-3 placeholder:text-emerald-950 text-xs rounded-none"
                  />
                  <Button 
                    onClick={onFetchGoogleDoc}
                    disabled={isFetchingDoc || !googleDocInput}
                    className="bg-[#00FF41] text-black hover:bg-white hover:text-black font-extrabold text-xs rounded-none h-10 px-6 shrink-0 border-0"
                  >
                    {isFetchingDoc ? 'PULLING...' : 'EXTRACT EVIDENCE'}
                  </Button>
                </div>
              </div>

              {docErrorMessage && (
                <div className="p-2 border border-red-500/50 bg-red-950/20 text-red-500 text-xs font-mono font-bold uppercase tracking-tight flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span>{docErrorMessage}</span>
                </div>
              )}

              {/* If loaded results, display staging evidence ready to inject */}
              {extractedEvidence.length > 0 && (
                <div className="border-2 border-dashed border-[#00FF41]/40 p-4 bg-black space-y-4">
                  <div className="flex justify-between items-center border-b border-[#00FF41]/20 pb-2">
                    <div>
                      <span className="text-[9px] text-[#00FF41]/60 font-bold uppercase block tracking-wider font-mono">Document Harvested:</span>
                      <span className="text-md text-white font-black uppercase tracking-tight font-mono">{loadedDocTitle}</span>
                    </div>
                    <Button 
                      onClick={onCancelDoc}
                      className="bg-black hover:bg-zinc-900 text-zinc-400 border border-zinc-700 font-bold text-[10px] uppercase h-7 px-2 py-0 rounded-none cursor-pointer"
                    >
                      Dismiss
                    </Button>
                  </div>

                  <div className="space-y-3">
                    <p className="text-xs font-black text-[#00FF41] uppercase tracking-widest font-mono">
                      Matched Relational Forensics:
                    </p>
                    
                    <div className="space-y-2">
                      {extractedEvidence.map((item, index) => (
                        <div key={index} className="p-3 bg-[#001100] border-2 border-[#00FF41]/20 flex flex-col gap-2 font-mono">
                          <div className="flex flex-wrap items-center gap-2">
                            <Badge className="bg-[#00FF41] text-black text-[9px] font-black rounded-none">
                              {item.id}
                            </Badge>
                            <Badge className="border border-[#00FF41]/50 text-[#00FF41] text-[9px] font-black rounded-none bg-black">
                              {item.confidence}
                            </Badge>
                            {item.keywordsMatched.map((kw: string, i: number) => (
                              <span key={i} className="text-[9px] text-[#00FF41]/70 font-bold uppercase px-1 py-0.5 bg-[#002202]/50 border border-[#00FF41]/20">
                                #{kw}
                              </span>
                            ))}
                          </div>
                          <p className="text-xs text-white leading-normal font-medium font-sans">
                            {item.description}
                          </p>
                        </div>
                      ))}
                    </div>

                    <Button 
                      onClick={() => onCommitEvidence(extractedEvidence)}
                      className="w-full bg-[#00FF41] text-black hover:bg-white hover:text-black h-11 text-xs font-black uppercase rounded-none tracking-widest border-0"
                    >
                      MUTATE VAULT: COMMIT DISCOVERED ARTIFACTS &gt;&gt;
                    </Button>
                  </div>
                </div>
              )}

              {isFetchingDoc && (
                <div className="text-center py-6 border border-[#00FF41]/20 bg-[#001100]/40 flex flex-col items-center justify-center gap-2">
                  <div className="w-8 h-8 rounded-none border-2 border-t-[#00FF41] border-[#003310] animate-spin mb-1" />
                  <span className="text-[10px] text-[#00FF41] uppercase font-bold animate-pulse tracking-widest font-mono">
                    Harvesting text run bodies from secure Google Docs Cloud Node...
                  </span>
                </div>
              )}

              {!isFetchingDoc && extractedEvidence.length === 0 && (
                <div className="text-[10px] text-zinc-500 uppercase font-black leading-normal tracking-wider font-mono">
                  💡 PRO TIP: Paste the URL of any Google Doc that you have access to. The applet will load, decode, and parse structural content to auto-generate intelligence logs dynamically matched with the local case model.
                </div>
              )}

              {/* Secure Drive Scanning Area */}
              <div className="mt-6 pt-4 border-t border-[#00FF41]/20">
                <div className="flex justify-between items-center mb-3">
                  <p className="text-xs font-bold text-[#00FF41] uppercase tracking-wide">
                    {`>>`} Secure Cloud Drive Scan (Recent Targets)
                  </p>
                  <Button 
                    onClick={onScanDrive}
                    disabled={isScanningDrive}
                    className="bg-black text-[#00FF41] border border-[#00FF41] hover:bg-[#00FF41] hover:text-black font-extrabold text-[10px] rounded-none h-8 px-4"
                  >
                    {isScanningDrive ? 'SCANNING SECURE DRIVE...' : 'EXECUTE DRIVE SCAN'}
                  </Button>
                </div>

                {driveFiles.length > 0 && (
                  <div className="space-y-2 max-h-[160px] overflow-auto pr-2 border-l-2 border-[#00FF41]/50 pl-2">
                    {driveFiles.map(file => (
                      <div key={file.id} className="flex justify-between items-center bg-[#000800] border border-[#00FF41]/30 p-2 hover:border-[#00FF41]/80 transition-colors">
                        <div className="overflow-hidden pr-2 flex-grow">
                          <div className="text-xs font-bold text-white truncate" title={file.name}>{file.name}</div>
                          <div className="text-[9px] text-[#00FF41]/60 uppercase truncate">{file.mimeType.split('.').pop() || file.mimeType} / Last Mod: {new Date(file.modifiedTime).toLocaleDateString()}</div>
                        </div>
                        <Button
                          onClick={() => onIngestDriveFile(file)}
                          className="bg-[#003310] text-[#00FF41] border border-[#00FF41]/50 hover:bg-[#00FF41] hover:text-black font-bold text-[9px] rounded-none h-6 px-3 shrink-0"
                        >
                          INGEST TARGET
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Secure Gmail Interception Area */}
              <div className="mt-6 pt-4 border-t border-[#00FF41]/20">
                <div className="flex justify-between items-center mb-3">
                  <p className="text-xs font-bold text-[#00FF41] uppercase tracking-wide">
                    {`>>`} Comms Terminal Intercept (Recent Mails)
                  </p>
                  <Button 
                    onClick={onScanGmail}
                    disabled={isScanningGmail}
                    className="bg-black text-[#00FF41] border border-[#00FF41] hover:bg-[#00FF41] hover:text-black font-extrabold text-[10px] rounded-none h-8 px-4"
                  >
                    {isScanningGmail ? 'INTERCEPTING COMMS...' : 'EXECUTE COMMS INTERCEPT'}
                  </Button>
                </div>

                {interceptedEmails.length > 0 && (
                  <div className="space-y-2 max-h-[160px] overflow-auto pr-2 border-l-2 border-[#00FF41]/50 pl-2">
                    {interceptedEmails.map(email => (
                      <div key={email.id} className="flex justify-between items-center bg-[#000800] border border-[#00FF41]/30 p-2 hover:border-[#00FF41]/80 transition-colors">
                        <div className="overflow-hidden pr-2 flex-grow">
                          <div className="text-xs font-bold text-white truncate" title={email.subject}>{email.subject}</div>
                          <div className="text-[9px] text-[#00FF41]/60 uppercase truncate">From: {email.from} / {new Date(email.date).toLocaleDateString()}</div>
                        </div>
                        <Button
                          onClick={() => onIngestEmail(email)}
                          className="bg-[#330000] text-red-500 border border-red-500/50 hover:bg-red-500 hover:text-white font-bold text-[9px] rounded-none h-6 px-3 shrink-0"
                        >
                          INGEST INTEL
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Existing Vault evidence list */}
        <div className="border border-[#00FF41]/30">
          <Table>
            <TableHeader className="bg-[#001100]">
              <TableRow className="border-b-2 border-[#00FF41]/50 hover:bg-[#001100]">
                <TableHead className="text-[#00FF41] text-[10px] font-black uppercase">ID</TableHead>
                <TableHead className="text-[#00FF41] text-[10px] font-black uppercase">Source</TableHead>
                <TableHead className="text-[#00FF41] text-[10px] font-black uppercase">Artifact Description</TableHead>
                <TableHead className="text-[#00FF41] text-[10px] font-black uppercase">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {evidenceList.map((item) => (
                <TableRow key={item.id} className="border-b border-[#00FF41]/20 hover:bg-[#003310]/20 text-[#00FF41] h-16">
                  <TableCell className="font-mono text-zinc-400 font-bold">{item.id}</TableCell>
                  <TableCell className="font-mono text-[10px] opacity-70 uppercase max-w-[150px] truncate" title={item.source}>{item.source}</TableCell>
                  <TableCell className="text-sm font-bold tracking-tight">{item.description}</TableCell>
                  <TableCell>
                    <Badge 
                      variant="outline" 
                      className={cn(
                        "text-[9px] uppercase font-black border-2 rounded-none",
                        item.status === 'Recovered' || item.status === 'Verified' || item.status === 'Confirmed' || item.status === 'Imported'
                          ? "text-black bg-[#00FF41] border-[#00FF41]" 
                          : "text-[#00FF41] border-[#00FF41] bg-[#003310]"
                      )}
                    >
                      {item.status}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
