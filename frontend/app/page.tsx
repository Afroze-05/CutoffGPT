"use client";

import { useEffect, useState } from "react";
import api from "@/lib/api";
import { 
  GraduationCap, 
  TrendingUp, 
  MapPin, 
  CheckCircle,
  ArrowRight,
  Plus,
  Loader2,
  Trophy,
  Users,
  Building2,
  Zap
} from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

const Dashboard = () => {
  const [stats, setStats] = useState({
    colleges: 0,
    applications: 12,
    recommendations: 5
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchColleges = async () => {
      try {
        const response = await api.get("/colleges/");
        setStats(prev => ({ ...prev, colleges: response.data.length }));
      } catch (error) {
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchColleges();
  }, []);

  const features = [
    {
      title: "Recommended Colleges",
      desc: "AI-curated list of colleges based on your specific rank and category.",
      icon: Trophy,
      href: "/recommendations",
      color: "text-yellow-400",
      bgColor: "bg-yellow-400/10"
    },
    {
      title: "AI Counselor",
      desc: "Interactive chatbot to guide you through the admission process.",
      icon: Users,
      href: "/chat",
      color: "text-violet-400",
      bgColor: "bg-violet-400/10"
    },
    {
      title: "Interactive Map",
      desc: "Explore Pune colleges and their connectivity options.",
      icon: MapPin,
      href: "/map",
      color: "text-emerald-400",
      bgColor: "bg-emerald-400/10"
    }
  ];

  return (
    <div className="p-8 space-y-10 bg-[#0b0e14] min-h-full text-white">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">Student Dashboard</h1>
          <p className="text-zinc-400">Welcome back! Your admission journey is being analyzed by AI.</p>
        </div>
        <Link 
          href="/upload"
          className="flex items-center gap-x-2 bg-sky-600 text-white px-6 py-3 rounded-2xl hover:bg-sky-700 transition-all shadow-lg shadow-sky-600/20 font-bold"
        >
          <Plus className="h-5 w-5" />
          Update Marks
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass p-8 rounded-[32px] border border-white/10 space-y-4 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
             <Building2 className="w-24 h-24" />
          </div>
          <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Available Colleges</p>
          {isLoading ? <Loader2 className="h-8 w-8 animate-spin text-sky-500" /> : <p className="text-4xl font-black text-white">{stats.colleges}</p>}
          <div className="flex items-center text-xs text-emerald-400 font-bold">
             <TrendingUp className="h-3 w-3 mr-1" />
             <span>+2 Added Recently</span>
          </div>
        </div>
        <div className="glass p-8 rounded-[32px] border border-white/10 space-y-4 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
             <GraduationCap className="w-24 h-24" />
          </div>
          <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Shortlisted</p>
          <p className="text-4xl font-black text-white">{stats.applications}</p>
          <div className="flex items-center text-xs text-sky-400 font-bold">
             <Zap className="h-3 w-3 mr-1" />
             <span>Syncing with Profile</span>
          </div>
        </div>
        <div className="glass p-8 rounded-[32px] border border-white/10 space-y-4 relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
             <Trophy className="w-24 h-24" />
          </div>
          <p className="text-xs font-bold text-zinc-500 uppercase tracking-widest">AI Recommendations</p>
          <p className="text-4xl font-black text-white">{stats.recommendations}</p>
          <div className="flex items-center text-xs text-yellow-400 font-bold">
             <CheckCircle className="h-3 w-3 mr-1" />
             <span>Updated 2m ago</span>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map((feature) => (
          <Link 
            key={feature.title} 
            href={feature.href}
            className="group glass p-8 rounded-[32px] border border-white/10 hover:border-sky-500/50 transition-all space-y-6 flex flex-col"
          >
            <div className={cn("w-14 h-14 rounded-2xl flex items-center justify-center transition-transform group-hover:scale-110", feature.bgColor)}>
              <feature.icon className={cn("h-7 w-7", feature.color)} />
            </div>
            <div className="space-y-2 flex-1">
              <h3 className="font-bold text-xl">{feature.title}</h3>
              <p className="text-sm text-zinc-500 leading-relaxed">{feature.desc}</p>
            </div>
            <div className="flex items-center text-sm font-bold text-sky-400 group-hover:gap-x-4 transition-all gap-x-2">
              Explore Now
              <ArrowRight className="h-4 w-4" />
            </div>
          </Link>
        ))}
      </div>

      {/* Recent Activity Section */}
      <div className="glass rounded-[40px] border border-white/10 overflow-hidden shadow-2xl">
        <div className="p-8 border-b border-white/10 flex items-center justify-between bg-white/5">
          <h3 className="font-bold text-xl flex items-center gap-x-3">
             <Zap className="text-yellow-400 h-5 w-5" />
             Top Matches for You
          </h3>
          <Link href="/recommendations" className="text-xs font-bold text-sky-400 hover:underline uppercase tracking-widest">View All</Link>
        </div>
        <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { name: "COEP Pune", branch: "Computer Engineering", prob: "High", color: "text-emerald-400", bgColor: "bg-emerald-400/10" },
            { name: "PICT Pune", branch: "IT Engineering", prob: "Safe", color: "text-sky-400", bgColor: "bg-sky-400/10" },
            { name: "VIT Pune", branch: "AI & DS", prob: "Dream", color: "text-yellow-400", bgColor: "bg-yellow-400/10" },
            { name: "PCCOE Pune", branch: "ENTC", prob: "High", color: "text-emerald-400", bgColor: "bg-emerald-400/10" },
          ].map((college, i) => (
            <div key={i} className="flex items-center justify-between p-5 rounded-2xl bg-white/5 border border-white/5 hover:bg-white/10 transition-all group">
              <div className="flex items-center gap-x-4">
                <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center border border-white/10 group-hover:border-sky-500/30 transition-all">
                  <GraduationCap className="h-6 w-6 text-sky-400" />
                </div>
                <div>
                  <p className="font-bold text-sm text-white">{college.name}</p>
                  <p className="text-xs text-zinc-500">{college.branch}</p>
                </div>
              </div>
              <div className="flex items-center gap-x-2">
                <span className={cn("text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-md", college.bgColor, college.color)}>
                  {college.prob}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
