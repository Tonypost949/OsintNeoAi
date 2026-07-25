import React, { useState, useRef } from 'react';
import { GoogleGenAI } from '@google/genai';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { ScrollArea } from './ui/scroll-area';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { DOSSIER_DATA } from '../data/dossier';
import { Sparkles, Send, Bot, User, Paperclip } from 'lucide-react';
import { analyzeDocText, ExtractedEvidence } from '../lib/googleDocs';

interface NeoAnalysisProps {
  onCommitEvidence?: (items: ExtractedEvidence[]) => void;
}

export const NeoAnalysis: React.FC<NeoAnalysisProps> = ({ onCommitEvidence }) => {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([
    { role: 'assistant', content: 'NEO AI ONLINE. Investigation dossier WN-2026-001-CA loaded. How can I assist with the forensic synthesis?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || '' });
      const systemInstruction = `You are NEO AI, an advanced OSINT and forensic analysis agent.
      You have access to the following investigation dossier:
      ${JSON.stringify(DOSSIER_DATA)}
      
      The case involves corruption in California homelessness services ($24B missing), 
      environmental crimes in Huntington Beach (Hexavalent Chromium), 
      and suppressed 19th-century "Bunker Seed" technology.
      
      Answer questions based on this dossier. Be technical, analytical, and professional. 
      If data is missing, state that further forensic audit is required. 
      Highlight links between entities when asked.`;

      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: [
            { role: 'user', parts: [{ text: userMsg }] }
        ],
        config: {
          systemInstruction,
        }
      });

      const aiText = response.text || 'Error generating analysis.';
      setMessages(prev => [...prev, { role: 'assistant', content: aiText }]);
    } catch (error) {
      console.error('AI Error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection to Neo Core failed. Check API configuration.' }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (event) => {
      const text = event.target?.result as string;
      if (!text) return;

      const results = analyzeDocText(text, file.name, 'Local File:');
      
      let uploadSummary = `File uploaded: ${file.name}. Size: ${file.size} bytes.\n`;
      if (results.length > 0) {
        uploadSummary += `\nExtracted Forensic Indicators:\n`;
        results.forEach(r => {
          uploadSummary += `- [${r.id}] ${r.description} (Confidence: ${r.confidence})\n`;
        });

        // Automatically prompt to commit if onCommitEvidence is provided
        if (onCommitEvidence) {
          uploadSummary += `\n\n>> EVIDENCE AUTOMATICALLY FORWARDED TO VAULT PENDING APPROVAL <<`;
          onCommitEvidence(results);
        }
      } else {
        uploadSummary += `\nNo recognized forensic indicators found in file.`;
      }

      setMessages(prev => [
        ...prev, 
        { role: 'user', content: `[SYS_INJECT: Uploaded ${file.name}]` },
        { role: 'assistant', content: uploadSummary }
      ]);
      
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    };
    reader.readAsText(file);
  };

  return (
    <Card className="h-full flex flex-col bg-black border-0 rounded-none">
      <CardHeader className="border-b-4 border-[#00FF41] bg-[#003310]/50 sticky top-0 z-10 flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2 text-4xl font-black uppercase text-[#00FF41]">
          <Sparkles className="w-8 h-8 text-[#00FF41]" />
          Neo AI Synthesis
        </CardTitle>
        <div className="flex items-center gap-2">
          <input 
            type="file" 
            accept=".txt,.log,.md,.csv" 
            className="hidden" 
            ref={fileInputRef}
            onChange={handleFileUpload}
          />
          <Button 
            variant="outline" 
            onClick={() => fileInputRef.current?.click()}
            className="bg-[#002202] text-[#00FF41] border-[#00FF41] hover:bg-[#00FF41] hover:text-black font-bold uppercase text-[10px] rounded-none px-4"
          >
            <Paperclip className="w-3 h-3 mr-2" />
            Inject File
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
        <ScrollArea className="flex-1 p-6">
          <div className="space-y-6">
            {messages.map((m, i) => (
              <div key={i} className={`flex gap-4 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {m.role === 'assistant' && (
                  <div className="w-10 h-10 rounded-none bg-[#00FF41] flex items-center justify-center shrink-0 border-2 border-[#00FF41]">
                    <Bot className="w-6 h-6 text-black" />
                  </div>
                )}
                <div className={`max-w-[80%] p-4 border-2 font-mono leading-relaxed text-sm whitespace-pre-wrap snap-end ${
                  m.role === 'user' 
                  ? 'bg-zinc-900 border-[#00FF41]/30 text-zinc-100' 
                  : 'bg-[#003310]/20 border-[#00FF41] text-[#00FF41]'
                }`}>
                  <span className="text-[10px] opacity-40 block mb-1 uppercase tracking-widest">{m.role === 'user' ? 'User' : 'Neo_Core'}</span>
                  {m.content}
                </div>
                {m.role === 'user' && (
                  <div className="w-10 h-10 rounded-none bg-zinc-800 flex items-center justify-center shrink-0 border-2 border-zinc-600">
                    <User className="w-6 h-6 text-zinc-100" />
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div className="flex gap-4 justify-start">
                <div className="w-10 h-10 rounded-none bg-[#00FF41]/20 flex items-center justify-center shrink-0 animate-pulse border-2 border-[#00FF41]/50">
                  <Bot className="w-6 h-6 text-[#00FF41]" />
                </div>
                <div className="bg-[#003310]/10 border-2 border-[#00FF41]/20 p-4 font-mono text-[#00FF41]/50 text-sm italic animate-pulse">
                  &gt; SYNTHESIZING_ARTIFACTS...
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
        <div className="p-6 border-t-4 border-[#00FF41] bg-[#001100] flex gap-3">
          <Input 
            placeholder="PROMPT_NEO_CORE > Search artifacts, cross-reference entities..." 
            className="bg-black border-2 border-[#00FF41] text-[#00FF41] font-mono rounded-none h-14"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          />
          <Button 
            disabled={loading} 
            onClick={handleSend}
            className="bg-[#00FF41] hover:bg-white text-black font-black uppercase rounded-none h-14 px-8 border-0"
          >
            <Send className="w-6 h-6" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
