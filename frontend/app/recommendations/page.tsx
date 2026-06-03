"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import "leaflet/dist/leaflet.css";
import api from "@/lib/api";
import { 
  Trophy, 
  CheckCircle, 
  AlertCircle, 
  Loader2, 
  TrendingUp, 
  MapPin, 
  Briefcase,
  GraduationCap
} from "lucide-react";
import { cn } from "@/lib/utils";

const MapComponent = dynamic(() => import("@/components/MapComponent"), {
  ssr: false,
  loading: () => <div className="h-[380px] w-full bg-[#0d1117] rounded-2xl border border-white/10 animate-pulse" />,
});

interface Recommendation {
  college_name: string;
  branch: string;
  category: "Safe" | "Target" | "Dream";
  round1_prob: string;
  round2_prob: string;
  round3_prob: string;
  last_year_cutoff: string;
  fees: string;
  placement: string;
  reason: string;
  possibility_label?: "High Possibility" | "Medium Possibility" | "Low Possibility";
  possibility_badge?: string;
  difference?: number;
  student_percentage?: string;
  cutoff_category?: string;
  round?: number;
}

const RecommendationsPage = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [profile, setProfile] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const profileRes = await api.get("/student/profile/1");
        setProfile(profileRes.data);
        
        const response = await api.get("/colleges/recommendations/1"); // Mock user_id=1
        setRecommendations(response.data);
      } catch (err: any) {
        console.error(err);
        setError(err.response?.data?.detail || "Failed to fetch recommendations. Ensure your marksheet is uploaded.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  if (isLoading) {
    return (
      <div className="h-full flex flex-col items-center justify-center space-y-4">
        <Loader2 className="h-12 w-12 animate-spin text-sky-400" />
        <p className="text-zinc-400 font-medium">Analyzing historical cutoffs and generating recommendations...</p>
      </div>
    );
  }

  if (!isLoading && (!profile?.percentage || recommendations.length === 0)) {
    return (
      <div className="p-8 max-w-4xl mx-auto space-y-8 bg-[#0b0e14] min-h-full text-white">
        <div className="space-y-2 text-center">
          <AlertCircle className="h-16 w-16 text-yellow-500 mx-auto" />
          <h1 className="text-3xl font-bold">Find Your Best Colleges</h1>
          <p className="text-zinc-400">
            {profile?.percentage 
              ? `We found your percentage (${profile.percentage}%) but couldn't find matches. Try adjusting your preferences below.`
              : "Please provide your percentage and category to see personalized recommendations."}
          </p>
        </div>

        <div className="glass rounded-[32px] p-8 border border-white/10 space-y-6 max-w-md mx-auto">
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-[10px] font-bold text-zinc-500 uppercase">Aggregate Percentage</label>
              <input 
                type="number" 
                value={profile?.percentage || ""}
                onChange={(e) => setProfile({...profile, percentage: e.target.value})}
                className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:ring-1 ring-sky-500 outline-none"
                placeholder="e.g. 94.20"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-zinc-500 uppercase">Category</label>
                  <select 
                    value={profile?.category || "Open"}
                    onChange={(e) => setProfile({...profile, category: e.target.value})}
                    className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:ring-1 ring-sky-500 outline-none"
                  >
                    <option value="Open">Open</option>
                    <option value="OBC">OBC</option>
                    <option value="SC">SC</option>
                    <option value="ST">ST</option>
                    <option value="EWS">EWS</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-zinc-500 uppercase">Preferred City</label>
                  <select 
                    value={profile?.preferred_city || "Pune"}
                    onChange={(e) => setProfile({...profile, preferred_city: e.target.value})}
                    className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:ring-1 ring-sky-500 outline-none"
                  >
                    <option value="Pune">Pune</option>
                    <option value="Mumbai">Mumbai</option>
                    <option value="Nagpur">Nagpur</option>
                    <option value="All Maharashtra">All Maharashtra</option>
                  </select>
                </div>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-bold text-zinc-500 uppercase">Interested Branch</label>
              <select 
                value={profile?.preferred_branch || "Computer Engineering"}
                onChange={(e) => setProfile({...profile, preferred_branch: e.target.value})}
                className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:ring-1 ring-sky-500 outline-none"
              >
                <option value="Computer Engineering">Computer Engineering</option>
                <option value="Information Technology">Information Technology</option>
                <option value="AI & Data Science">AI & Data Science</option>
                <option value="ENTC">ENTC</option>
                <option value="Mechanical Engineering">Mechanical Engineering</option>
                <option value="Civil Engineering">Civil Engineering</option>
              </select>
            </div>

            <button 
              onClick={async () => {
                setIsLoading(true);
                try {
                const payload: any = {};
                Object.entries(profile || {}).forEach(([key, value]) => {
                  if (value === "" || value === null || typeof value === "undefined") return;
                  if (["percentage", "obtained_marks", "total_marks", "year", "rank", "budget"].includes(key)) {
                    const num = typeof value === "number" ? value : parseFloat(String(value));
                    if (!Number.isNaN(num)) {
                      payload[key] = num;
                    }
                    return;
                  }
                  payload[key] = value;
                });
                console.log("Profile Payload (recommendations page):", payload);
                await api.put("/student/profile/1", payload);
                  const response = await api.get("/colleges/recommendations/1");
                  setRecommendations(response.data);
                  setError(null);
                } catch (err) {
                console.error("Error saving profile from recommendations page:", err);
                } finally {
                  setIsLoading(false);
                }
              }}
              className="w-full bg-sky-600 hover:bg-sky-700 py-3 rounded-xl font-bold transition-all shadow-lg shadow-sky-600/20"
            >
              Generate Top 10 Colleges
            </button>
            <p className="text-center text-xs text-zinc-500">
              OR <a href="/upload" className="text-sky-400 hover:underline">Upload Marksheet</a> for auto-analysis
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 bg-[#0b0e14] min-h-full text-white">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold flex items-center gap-x-3">
          <Trophy className="text-yellow-400" />
          Recommended Colleges
        </h1>
        {profile && profile.percentage && (
          <p className="text-zinc-400 font-medium">
            Personalized admission path based on your <span className="text-sky-400 font-bold">{profile.percentage}%</span> score 
            {profile.category && <> and <span className="text-sky-400 font-bold">{profile.category}</span> category</>}.
          </p>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {recommendations.map((item, index) => (
          <div 
            key={index} 
            className={cn(
              "glass rounded-2xl overflow-hidden border border-white/10 card-hover flex flex-col",
              item.category === "Safe" && "border-emerald-500/30",
              item.category === "Target" && "border-sky-500/30",
              item.category === "Dream" && "border-yellow-500/30"
            )}
          >
            <div className={cn(
              "p-4 flex items-center justify-between border-b border-white/10",
              item.category === "Safe" && "bg-emerald-500/10",
              item.category === "Target" && "bg-sky-500/10",
              item.category === "Dream" && "bg-yellow-500/10"
            )}>
              <span className={cn(
                "text-xs font-bold uppercase tracking-wider px-2 py-1 rounded-md",
                item.category === "Safe" && "text-emerald-400 bg-emerald-400/20",
                item.category === "Target" && "text-sky-400 bg-sky-400/20",
                item.category === "Dream" && "text-yellow-400 bg-yellow-400/20"
              )}>
                {item.category} College
              </span>
              <CheckCircle className={cn(
                "h-5 w-5",
                item.category === "Safe" && "text-emerald-400",
                item.category === "Target" && "text-sky-400",
                item.category === "Dream" && "text-yellow-400"
              )} />
            </div>
            
            <div className="p-6 flex-1 space-y-4">
              <div className="space-y-1">
                <h3 className="text-xl font-bold text-white line-clamp-2 leading-tight">
                  {item.college_name}
                </h3>
                <p className="text-sm text-sky-400 font-medium">{item.branch}</p>
                {item.possibility_label && (
                  <p className="text-xs font-bold">
                    {item.possibility_label === "High Possibility" && "🟢 High Possibility"}
                    {item.possibility_label === "Medium Possibility" && "🟡 Medium Possibility"}
                    {item.possibility_label === "Low Possibility" && "🔴 Low Possibility"}
                  </p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <p className="text-[10px] text-zinc-500 uppercase font-bold">Round 1 Prob</p>
                  <p className="text-sm font-semibold text-white">{item.round1_prob}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-[10px] text-zinc-500 uppercase font-bold">Last Year Cutoff</p>
                  <p className="text-sm font-semibold text-white">{item.last_year_cutoff}</p>
                </div>
              </div>

              <div className="space-y-3 pt-4 border-t border-white/5">
                <div className="flex items-center gap-x-3 text-sm text-zinc-400">
                  <TrendingUp className="h-4 w-4 text-sky-400" />
                  <span>Fees: {item.fees}</span>
                </div>
                <div className="flex items-center gap-x-3 text-sm text-zinc-400">
                  <Briefcase className="h-4 w-4 text-emerald-400" />
                  <span>Placement: {item.placement}</span>
                </div>
              </div>

              <div className="p-4 bg-white/5 rounded-xl mt-4">
                <p className="text-xs text-zinc-400 leading-relaxed">
                  <span className="text-white font-bold mr-1 italic">Why this?</span>
                  {item.reason}
                </p>
                <p className="text-[11px] text-zinc-500 mt-2">
                  Category: {item.cutoff_category || profile?.category || "N/A"} | Round: {item.round || "N/A"} | Student: {item.student_percentage || profile?.percentage || "N/A"} | Difference: {item.difference ?? "N/A"}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {recommendations.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 border-2 border-dashed border-white/10 rounded-3xl bg-white/5 text-zinc-500">
           <GraduationCap className="h-12 w-12 mb-4 opacity-20" />
           <p>No recommendations found for your profile. Try updating your preferences.</p>
        </div>
      )}

      <div className="space-y-3">
        <h2 className="text-2xl font-bold">Pune Engineering College Map</h2>
        <p className="text-zinc-400 text-sm">All Pune engineering colleges with clickable markers, website links, and directions.</p>
        <div className="h-[420px] rounded-2xl overflow-hidden border border-white/10">
          <MapComponent cityFilter="Pune" engineeringOnly={true} />
        </div>
      </div>
    </div>
  );
};

export default RecommendationsPage;
