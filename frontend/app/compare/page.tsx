"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import { 
  Layers, 
  Check, 
  X, 
  Loader2, 
  Plus, 
  Trash2, 
  IndianRupee, 
  Briefcase, 
  MapPin, 
  Award,
  BookOpen
} from "lucide-react";
import { cn } from "@/lib/utils";

const ComparePage = () => {
  const [colleges, setColleges] = useState<any[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [comparisonData, setComparisonData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchColleges = async () => {
      try {
        const response = await api.get("/colleges/");
        setColleges(response.data);
      } catch (error) {
        console.error(error);
      }
    };
    fetchColleges();
  }, []);

  useEffect(() => {
    if (selectedIds.length > 0) {
      const fetchComparison = async () => {
        setIsLoading(true);
        try {
          const queryParams = selectedIds.map(id => `ids=${id}`).join("&");
          const response = await api.get(`/colleges/compare?${queryParams}`);
          setComparisonData(response.data);
        } catch (error) {
          console.error(error);
        } finally {
          setIsLoading(false);
        }
      };
      fetchComparison();
    } else {
      setComparisonData([]);
    }
  }, [selectedIds]);

  const toggleSelection = (id: number) => {
    setSelectedIds(prev => 
      prev.includes(id) 
        ? prev.filter(i => i !== id) 
        : (prev.length < 3 ? [...prev, id] : prev)
    );
  };

  const removeCollege = (id: number) => {
    setSelectedIds(prev => prev.filter(i => i !== id));
  };

  return (
    <div className="p-8 space-y-8 bg-[#0b0e14] min-h-full text-white">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold flex items-center gap-x-3">
          <Layers className="text-orange-400" />
          College Comparison
        </h1>
        <p className="text-zinc-400">Select up to 3 colleges to compare side-by-side on fees, placement, and more.</p>
      </div>

      {/* College Selection Dropdown/Chips */}
      <div className="glass p-6 rounded-3xl border border-white/10 space-y-6">
         <div className="flex flex-wrap gap-3">
            {colleges.map((college) => (
              <button
                key={college.id}
                onClick={() => toggleSelection(college.id)}
                disabled={!selectedIds.includes(college.id) && selectedIds.length >= 3}
                className={cn(
                  "px-4 py-2 rounded-xl border text-sm font-medium transition-all flex items-center gap-x-2",
                  selectedIds.includes(college.id) 
                    ? "bg-orange-500 border-orange-500 text-white shadow-lg shadow-orange-500/20" 
                    : "bg-white/5 border-white/10 text-zinc-400 hover:bg-white/10 disabled:opacity-30"
                )}
              >
                {selectedIds.includes(college.id) ? <Check className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                {college.name}
              </button>
            ))}
         </div>
      </div>

      {/* Comparison Grid */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <Loader2 className="h-10 w-10 animate-spin text-orange-400 mb-4" />
          <p className="text-zinc-400 font-medium tracking-wide">Building side-by-side comparison...</p>
        </div>
      ) : comparisonData.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
           {comparisonData.map((college) => (
             <div key={college.id} className="glass rounded-3xl border border-white/10 overflow-hidden flex flex-col">
                <div className="p-6 border-b border-white/10 bg-white/5 flex items-start justify-between">
                   <div>
                      <h3 className="text-xl font-bold text-white leading-tight">{college.name}</h3>
                      <p className="text-xs text-zinc-400 mt-1 flex items-center gap-x-1">
                         <MapPin className="h-3 w-3" />
                         {college.location}
                      </p>
                   </div>
                   <button 
                     onClick={() => removeCollege(college.id)}
                     className="p-2 hover:bg-rose-500/10 text-zinc-500 hover:text-rose-500 transition rounded-lg"
                   >
                      <Trash2 className="h-4 w-4" />
                   </button>
                </div>

                <div className="p-6 space-y-6 flex-1">
                   <div className="space-y-4">
                  <div className="flex items-center justify-between">
                         <div className="flex items-center gap-x-2 text-zinc-400 text-sm">
                            <IndianRupee className="h-4 w-4 text-emerald-400" />
                            <span>Fees (Annual)</span>
                         </div>
                         <span className="font-bold">₹{college.fees?.toLocaleString() || "Not Available"}</span>
                      </div>
                      <div className="flex items-center justify-between">
                         <div className="flex items-center gap-x-2 text-zinc-400 text-sm">
                            <Briefcase className="h-4 w-4 text-sky-400" />
                            <span>Avg Package</span>
                         </div>
                         <span className="font-bold">{college.avg_package ? `${college.avg_package} LPA` : "Not Available"}</span>
                      </div>
                      <div className="flex items-center justify-between">
                         <div className="flex items-center gap-x-2 text-zinc-400 text-sm">
                            <Award className="h-4 w-4 text-yellow-400" />
                            <span>NAAC Rating</span>
                         </div>
                         <span className="font-bold text-yellow-400">{college.naac_rating || "Not Available"}</span>
                      </div>
                      <div className="flex items-center justify-between">
                         <div className="flex items-center gap-x-2 text-zinc-400 text-sm">
                            <Check className="h-4 w-4 text-emerald-400" />
                            <span>NBA Accredited</span>
                         </div>
                         {college.nba_accreditation ? <Check className="h-4 w-4 text-emerald-400" /> : <X className="h-4 w-4 text-rose-500" />}
                      </div>
                      <div className="flex items-center justify-between">
                         <div className="flex items-center gap-x-2 text-zinc-400 text-sm">
                            <Briefcase className="h-4 w-4 text-violet-400" />
                            <span>Highest Package</span>
                         </div>
                         <span className="font-bold">{college.highest_package ? `${college.highest_package} LPA` : "Not Available"}</span>
                      </div>
                      <div className="flex items-center justify-between">
                         <div className="flex items-center gap-x-2 text-zinc-400 text-sm">
                            <Award className="h-4 w-4 text-cyan-400" />
                            <span>Placement %</span>
                         </div>
                         <span className="font-bold">{college.placement_percentage ? `${college.placement_percentage}%` : "Not Available"}</span>
                      </div>
                      <div className="flex items-center justify-between">
                         <div className="flex items-center gap-x-2 text-zinc-400 text-sm">
                            <IndianRupee className="h-4 w-4 text-orange-400" />
                            <span>Hostel Fees</span>
                         </div>
                         <span className="font-bold">{college.hostel_fees ? `₹${college.hostel_fees}` : "Not Available"}</span>
                      </div>
                      <div className="flex items-center justify-between">
                         <div className="flex items-center gap-x-2 text-zinc-400 text-sm">
                            <MapPin className="h-4 w-4 text-blue-400" />
                            <span>Campus Area</span>
                         </div>
                         <span className="font-bold">{college.campus_area || "Not Available"}</span>
                      </div>
                      <div className="flex items-center justify-between">
                         <div className="flex items-center gap-x-2 text-zinc-400 text-sm">
                            <Check className="h-4 w-4 text-emerald-400" />
                            <span>Autonomous Status</span>
                         </div>
                         <span className="font-bold">{college.name?.toLowerCase().includes("autonomous") ? "Autonomous" : "Affiliated"}</span>
                      </div>
                   </div>

                   <div className="pt-6 border-t border-white/5 space-y-3">
                      <div className="flex items-center gap-x-2 text-zinc-400 text-xs font-bold uppercase tracking-widest">
                         <BookOpen className="h-3 w-3" />
                         <span>Available Branches</span>
                      </div>
                      <div className="flex flex-wrap gap-2">
                         {(college.branches || "Computer, IT, ENTC").split(",").map((b: string) => (
                           <span key={b} className="px-2 py-1 bg-white/5 border border-white/10 rounded-md text-[10px] text-zinc-300">
                              {b.trim()}
                           </span>
                         ))}
                      </div>
                   </div>
                </div>
             </div>
           ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-32 border-2 border-dashed border-white/10 rounded-[40px] bg-white/5 text-zinc-500">
          <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center mb-6">
             <Layers className="h-10 w-10 opacity-20" />
          </div>
          <h3 className="text-xl font-bold text-zinc-400">No Colleges Selected</h3>
          <p className="text-sm mt-2">Select up to 3 colleges from the list above to see the comparison.</p>
        </div>
      )}
    </div>
  );
};

export default ComparePage;
