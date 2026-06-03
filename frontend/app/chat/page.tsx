"use client";

import { useState, useRef, useEffect } from "react";
import api from "@/lib/api";
import { Send, User, Bot, Loader2, AlertCircle, Trash2, Info, Trophy } from "lucide-react";
import { cn } from "@/lib/utils";

const ChatPage = () => {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  // Initial greeting
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get("/student/profile/1");
        const profile = response.data;
        if (profile && profile.percentage) {
          setMessages([
            { 
              role: "bot", 
              content: `Hello! I am your CollegePath AI Admission Counselor. I've found your marksheet data: ${profile.percentage}% percentage and rank ${profile.rank || 'N/A'}.\n\nTo help you find the best colleges in Pune, could you please confirm your category (Open/OBC/SC/ST/EWS) and which engineering branch you are interested in?` 
            }
          ]);
        } else {
          setMessages([
            { 
              role: "bot", 
              content: "Hello! I am your CollegePath AI Admission Counselor. I couldn't find your marksheet data yet.\n\nPlease upload your marksheet in the Document Center first, or tell me your percentage, rank, and category here so I can assist you!" 
            }
          ]);
        }
      } catch (err) {
        setMessages([
          { 
            role: "bot", 
            content: "Hello! I am your CollegePath AI Admission Counselor. How can I help you today with your engineering admissions in Pune?" 
          }
        ]);
      }
    };
    fetchProfile();
  }, []);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    setError(null);
    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      console.log("User Message:", input);
      const normalizedHistory = messages.map((m) => ({
        role: m.role === "bot" ? "assistant" : m.role,
        content: m.content,
      }));
      console.log("AI Request Sent");
      const response = await api.post("/chat/", {
        user_id: 1, // Mock user ID
        message: input,
        history: normalizedHistory
      });
      const aiResponse = response.data?.response;
      console.log("AI Response:", aiResponse);

      const botMessage = { role: "bot", content: aiResponse || "I could not generate a response. Please try again." };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err: any) {
      console.error(err);
      setError(err?.response?.data?.error || "Failed to connect to the AI Counselor. Please check your internet or backend status.");
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      { 
        role: "bot", 
        content: "Chat cleared. How can I help you today with your college admissions?" 
      }
    ]);
  };

  return (
    <div className="flex flex-col h-full bg-[#0b0e14] text-white">
      {/* Header */}
      <div className="p-6 border-b border-white/10 flex items-center justify-between bg-[#0d1117]">
        <div className="flex items-center gap-x-3">
          <div className="w-10 h-10 rounded-full bg-sky-500/20 flex items-center justify-center border border-sky-500/30">
            <Bot className="h-6 w-6 text-sky-400" />
          </div>
          <div>
            <h2 className="text-lg font-bold">AI Admission Counselor</h2>
            <div className="flex items-center gap-x-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-[10px] text-zinc-400 uppercase tracking-widest font-bold">Active Now</span>
            </div>
          </div>
        </div>
        <button 
          onClick={clearChat}
          className="p-2 hover:bg-white/5 rounded-lg text-zinc-400 transition"
          title="Clear Chat"
        >
          <Trash2 className="h-5 w-5" />
        </button>
      </div>

      {/* Messages */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth"
      >
        {messages.map((message, index) => (
          <div
            key={index}
            className={cn(
              "flex w-full animate-in fade-in slide-in-from-bottom-2",
              message.role === "user" ? "justify-end" : "justify-start"
            )}
          >
            <div
              className={cn(
                "flex items-start gap-x-4 max-w-[85%] lg:max-w-[70%] p-4 rounded-2xl",
                message.role === "user" 
                  ? "bg-sky-600 text-white rounded-tr-none shadow-lg shadow-sky-600/10" 
                  : "glass rounded-tl-none"
              )}
            >
              {message.role === "bot" && (
                <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center shrink-0 border border-white/10">
                  <Bot className="h-4 w-4 text-sky-400" />
                </div>
              )}
              <div className="text-sm whitespace-pre-wrap leading-relaxed">
                {message.content}
              </div>
              {message.role === "user" && (
                <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center shrink-0 border border-white/10">
                  <User className="h-4 w-4 text-white" />
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="glass p-4 rounded-2xl rounded-tl-none flex items-center gap-x-3">
              <Loader2 className="h-4 w-4 animate-spin text-sky-400" />
              <span className="text-sm text-zinc-400">Counselor is typing...</span>
            </div>
          </div>
        )}
        {error && (
          <div className="flex justify-center">
            <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-3 rounded-xl flex items-center gap-x-2 text-xs">
              <AlertCircle className="h-4 w-4" />
              {error}
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-6 bg-[#0d1117] border-t border-white/10">
        <form 
          onSubmit={onSubmit}
          className="max-w-4xl mx-auto relative group"
        >
          <input
            className="w-full bg-white/5 border border-white/10 rounded-2xl p-4 pr-16 focus:outline-none focus:ring-2 focus:ring-sky-500/50 focus:border-sky-500/50 transition-all placeholder:text-zinc-600 text-sm"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your question here (e.g. 'What are the top computer colleges in Pune?')"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="absolute right-2 top-2 bottom-2 px-4 bg-sky-600 text-white rounded-xl hover:bg-sky-700 transition-all disabled:opacity-50 disabled:bg-zinc-800 flex items-center justify-center"
          >
            <Send className="h-5 w-5" />
          </button>
        </form>
        <div className="mt-3 flex items-center justify-center gap-x-4 text-[10px] text-zinc-500 font-bold uppercase tracking-widest">
           <div className="flex items-center gap-x-1">
              <Info className="h-3 w-3" />
              <span>AI-Generated Advice</span>
           </div>
           <div className="flex items-center gap-x-1">
              <Trophy className="h-3 w-3" />
              <span>Historical Cutoff Data</span>
           </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
