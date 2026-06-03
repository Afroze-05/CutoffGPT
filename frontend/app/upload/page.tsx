"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import { 
  Upload, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  User, 
  ShieldCheck,
  Edit3,
  Save
} from "lucide-react";
import { cn } from "@/lib/utils";

const UploadPage = () => {
  // Separate states for student marksheet
  const [marksheetFile, setMarksheetFile] = useState<File | null>(null);
  const [marksheetStatus, setMarksheetStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [marksheetMessage, setMarksheetMessage] = useState("");
  const [profile, setProfile] = useState<any>({
    full_name: "",
    percentage: "",
    obtained_marks: "",
    total_marks: "",
    rank: "",
    category: "Open",
    diploma_branch: "",
    institute_name: "",
    college_name: "",
    year: "",
    preferred_branch: "Computer Engineering",
    preferred_city: "Pune"
  });

  const [isEditing, setIsEditing] = useState(false);
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "success">("idle");

  // Separate states for admin cutoff
  const [cutoffFile, setCutoffFile] = useState<File | null>(null);
  const [cutoffStatus, setCutoffStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [cutoffMessage, setCutoffMessage] = useState("");

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get("/student/profile/1");
      if (response.data) {
        setProfile({
          full_name: response.data.full_name || "",
          percentage: response.data.percentage || "",
          obtained_marks: response.data.obtained_marks || "",
          total_marks: response.data.total_marks || "",
          rank: response.data.rank || "",
          category: response.data.category || "Open",
          diploma_branch: response.data.diploma_branch || "",
          institute_name: response.data.institute_name || "",
          college_name: response.data.college_name || "",
          year: response.data.year || "",
          preferred_branch: response.data.preferred_branch || "Computer Engineering",
          preferred_city: response.data.preferred_city || "Pune"
        });
      }
    } catch (err) {
      console.error("Error fetching profile:", err);
    }
  };

  const onUploadMarksheet = async () => {
    if (!marksheetFile) return;
    setMarksheetStatus("uploading");
    setMarksheetMessage("");
    const formData = new FormData();
    formData.append("file", marksheetFile);
    try {
      const response = await api.post("/student/upload-marksheet?user_id=1", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      
      if (response.data.success) {
        setMarksheetStatus("success");
        setMarksheetMessage(response.data.message);
        
        // Update local profile with extracted data
        const extracted = response.data.extracted;
        setProfile(prev => ({
          ...prev,
          full_name: extracted.full_name || prev.full_name,
          percentage: extracted.percentage || prev.percentage,
          obtained_marks: extracted.obtained_marks || prev.obtained_marks,
          total_marks: extracted.total_marks || prev.total_marks,
          diploma_branch: extracted.diploma_branch || prev.diploma_branch,
          institute_name: extracted.institute_name || prev.institute_name,
          college_name: extracted.college_name || prev.college_name,
          year: extracted.year || prev.year
        }));
        
        // Proactively ask for confirmation after upload
        setTimeout(() => {
          setIsEditing(true);
        }, 1000);
      } else {
        setMarksheetStatus("error");
        setMarksheetMessage(response.data.message || "OCR failed to extract text.");
      }
      
    } catch (error: any) {
      setMarksheetStatus("error");
      setMarksheetMessage(error.response?.data?.message || "Critical error during upload.");
    }
  };

  const onSaveProfile = async () => {
    setSaveStatus("saving");
    try {
      const payload: any = {};
      Object.entries(profile).forEach(([key, value]) => {
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
      console.log("Profile Payload (upload page):", payload);
      await api.put("/student/profile/1", payload);
      setSaveStatus("success");
      setIsEditing(false);
      setTimeout(() => setSaveStatus("idle"), 3000);
    } catch (err: any) {
      console.error("Error saving profile:", err?.response?.data || err);
      alert(err?.response?.data?.message || "Error saving profile. Please check required fields.");
      setSaveStatus("idle");
    }
  };

  const onUploadCutoff = async () => {
    if (!cutoffFile) return;
    setCutoffStatus("uploading");
    const formData = new FormData();
    formData.append("file", cutoffFile);
    try {
      const response = await api.post("/admin/upload-cutoff", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setCutoffStatus("success");
      setCutoffMessage(response.data.message);
    } catch (error: any) {
      setCutoffStatus("error");
      setCutoffMessage(error.response?.data?.message || "Failed to upload cutoff.");
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-10 bg-[#0b0e14] min-h-full text-white">
      <div className="space-y-2 text-center md:text-left">
        <h1 className="text-4xl font-bold tracking-tight">Document Center</h1>
        <p className="text-zinc-400 font-medium">Upload your documents or enter details manually.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Student Marksheet Card */}
        <div className="glass rounded-[32px] p-8 border border-white/10 flex flex-col gap-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-x-4">
              <div className="w-12 h-12 rounded-2xl bg-sky-500/20 flex items-center justify-center text-sky-400 border border-sky-500/30">
                <User className="h-6 w-6" />
              </div>
              <div>
                <h3 className="text-xl font-bold">Student Profile</h3>
                <p className="text-xs text-zinc-500">Marksheet AI Analysis</p>
              </div>
            </div>
            {!isEditing && (
              <button 
                onClick={() => setIsEditing(true)}
                className="p-2 hover:bg-white/5 rounded-lg text-zinc-400 transition-all"
              >
                <Edit3 className="h-4 w-4" />
              </button>
            )}
          </div>

          {!isEditing ? (
            <div className="space-y-6">
              <div className="border-2 border-dashed border-white/10 rounded-2xl p-8 flex flex-col items-center gap-y-4 bg-white/5">
                <input
                  type="file"
                  id="marksheet-upload"
                  className="hidden"
                  onChange={(e) => setMarksheetFile(e.target.files?.[0] || null)}
                  accept="image/*,.pdf"
                />
                <label
                  htmlFor="marksheet-upload"
                  className="cursor-pointer p-4 bg-white/5 border border-white/10 rounded-full hover:bg-white/10 transition-all"
                >
                  <Upload className="h-6 w-6 text-sky-400" />
                </label>
                <p className="text-sm font-bold text-center">
                  {marksheetFile ? marksheetFile.name : "Select Marksheet"}
                </p>
                
                {marksheetFile && marksheetStatus !== "uploading" && (
                  <button
                    onClick={onUploadMarksheet}
                    className="w-full py-2 bg-sky-600 hover:bg-sky-700 rounded-xl font-bold transition-all shadow-lg shadow-sky-600/20"
                  >
                    Upload & Analyze
                  </button>
                )}

                {marksheetStatus === "uploading" && (
                  <div className="flex items-center gap-x-2 text-sky-400">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm font-bold">AI Extracting Data...</span>
                  </div>
                )}

                {marksheetStatus === "error" && (
                  <div className="flex flex-col items-center gap-y-2 text-rose-400 bg-rose-400/10 p-4 rounded-xl border border-rose-400/20 w-full">
                    <div className="flex items-center gap-x-2">
                      <AlertCircle className="h-4 w-4" />
                      <span className="text-xs font-bold uppercase tracking-wider">OCR Error</span>
                    </div>
                    <p className="text-[10px] text-center opacity-80">{marksheetMessage}</p>
                    <button 
                      onClick={() => setIsEditing(true)}
                      className="text-[10px] font-bold underline hover:text-rose-300 transition-all"
                    >
                      Enter Details Manually
                    </button>
                  </div>
                )}
              </div>

              {/* Data Display */}
              <div className="bg-white/5 p-6 rounded-2xl border border-white/10 space-y-4">
                 <div className="flex items-center justify-between">
                    <p className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest">Student Profile</p>
                    {marksheetStatus === "success" && (
                      <div className="flex items-center gap-x-1">
                        <span className="text-[10px] text-emerald-400 font-bold uppercase">Extracted</span>
                        <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                      </div>
                    )}
                 </div>
                 
                 <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                          <p className="text-[10px] text-zinc-500 font-medium">Name</p>
                          <p className="text-sm font-bold text-white">{profile.full_name || "N/A"}</p>
                        </div>
                        <div className="space-y-1">
                          <p className="text-[10px] text-zinc-500 font-medium">Percentage</p>
                          <p className="text-lg font-bold text-sky-400">{profile.percentage ? `${profile.percentage}%` : "N/A"}</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                          <p className="text-[10px] text-zinc-500 font-medium">Diploma Branch</p>
                          <p className="text-sm font-bold text-white">{profile.diploma_branch || "N/A"}</p>
                        </div>
                        <div className="space-y-1">
                          <p className="text-[10px] text-zinc-500 font-medium">Year</p>
                          <p className="text-sm font-bold text-white">{profile.year || "N/A"}</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-1">
                          <p className="text-[10px] text-zinc-500 font-medium">Obtained Marks</p>
                          <p className="text-sm font-bold text-white">{profile.obtained_marks || "N/A"}</p>
                        </div>
                        <div className="space-y-1">
                          <p className="text-[10px] text-zinc-500 font-medium">Total Marks</p>
                          <p className="text-sm font-bold text-white">{profile.total_marks || "N/A"}</p>
                        </div>
                    </div>

                    <div className="space-y-1">
                        <p className="text-[10px] text-zinc-500 font-medium">Institute</p>
                        <p className="text-sm font-bold text-white">{profile.institute_name || profile.college_name || "N/A"}</p>
                    </div>

                    <div className="grid grid-cols-2 gap-4 pt-2 border-t border-white/5">
                        <div className="space-y-1">
                          <p className="text-[10px] text-zinc-500 font-medium">Category</p>
                          <p className="text-sm font-bold text-sky-400">{profile.category || "Open"}</p>
                        </div>
                        <div className="space-y-1">
                          <p className="text-[10px] text-zinc-500 font-medium">Target Branch</p>
                          <p className="text-sm font-bold text-white truncate">{profile.preferred_branch || "Computer Engineering"}</p>
                        </div>
                    </div>
                 </div>

                 {marksheetStatus === "success" && (
                   <div className="pt-2">
                     <button 
                       onClick={() => setIsEditing(true)}
                       className="w-full py-2 bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 rounded-xl text-xs font-bold hover:bg-yellow-500/20 transition-all"
                     >
                       Edit or Confirm Details
                     </button>
                   </div>
                 )}
              </div>
            </div>
          ) : (
            <div className="space-y-4 animate-in fade-in duration-300">
               <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                      <label className="text-[10px] font-bold text-zinc-500 uppercase">Full Name</label>
                      <input 
                        type="text" 
                        value={profile.full_name}
                        onChange={(e) => setProfile({...profile, full_name: e.target.value})}
                        className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:ring-1 ring-sky-500 outline-none"
                        placeholder="e.g. John Doe"
                      />
                  </div>
                  <div className="space-y-2">
                      <label className="text-[10px] font-bold text-zinc-500 uppercase">Percentage</label>
                      <input 
                        type="number" 
                        value={profile.percentage}
                        onChange={(e) => setProfile({...profile, percentage: e.target.value ? parseFloat(e.target.value) : ""})}
                        className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:ring-1 ring-sky-500 outline-none"
                        placeholder="e.g. 94.20"
                      />
                  </div>
               </div>

               <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                      <label className="text-[10px] font-bold text-zinc-500 uppercase">Diploma Branch</label>
                      <input 
                        type="text" 
                        value={profile.diploma_branch}
                        onChange={(e) => setProfile({...profile, diploma_branch: e.target.value})}
                        className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:ring-1 ring-sky-500 outline-none"
                        placeholder="e.g. Computer Engineering"
                      />
                  </div>
                  <div className="space-y-2">
                      <label className="text-[10px] font-bold text-zinc-500 uppercase">Year</label>
                      <input 
                        type="number" 
                        value={profile.year}
                        onChange={(e) => setProfile({...profile, year: e.target.value ? parseInt(e.target.value) : ""})}
                        className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:ring-1 ring-sky-500 outline-none"
                        placeholder="e.g. 2024"
                      />
                  </div>
               </div>

               <div className="space-y-2">
                  <label className="text-[10px] font-bold text-zinc-500 uppercase">Institute Name</label>
                  <input 
                    type="text" 
                    value={profile.institute_name || profile.college_name}
                    onChange={(e) => setProfile({...profile, institute_name: e.target.value, college_name: e.target.value})}
                    className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-sm focus:ring-1 ring-sky-500 outline-none"
                    placeholder="e.g. Government Polytechnic, Pune"
                  />
               </div>

               <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                      <label className="text-[10px] font-bold text-zinc-500 uppercase">Category</label>
                      <select 
                        value={profile.category}
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
                      <label className="text-[10px] font-bold text-zinc-500 uppercase">Target Branch</label>
                      <select 
                        value={profile.preferred_branch}
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
               </div>
               
               <div className="flex gap-x-3 pt-2">
                  <button 
                    onClick={onSaveProfile}
                    className="flex-1 bg-sky-600 hover:bg-sky-700 py-3 rounded-xl font-bold flex items-center justify-center gap-x-2 transition-all"
                  >
                    {saveStatus === "saving" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                    Save Profile
                  </button>
                  <button 
                    onClick={() => setIsEditing(false)}
                    className="px-6 bg-white/5 border border-white/10 rounded-xl font-bold"
                  >
                    Cancel
                  </button>
               </div>
            </div>
          )}
        </div>

        {/* Admin Cutoff Card */}
        <div className="glass rounded-[32px] p-8 border border-white/10 flex flex-col gap-y-6">
          <div className="flex items-center gap-x-4">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 flex items-center justify-center text-emerald-400 border border-emerald-500/30">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-xl font-bold">Admin Cutoff PDF</h3>
              <p className="text-xs text-zinc-500">DSE/CET cutoff ingestion</p>
            </div>
          </div>

          <div className="border-2 border-dashed border-white/10 rounded-2xl p-8 flex flex-col items-center gap-y-4 bg-white/5">
            <input
              type="file"
              id="cutoff-upload"
              className="hidden"
              onChange={(e) => setCutoffFile(e.target.files?.[0] || null)}
              accept=".pdf"
            />
            <label
              htmlFor="cutoff-upload"
              className="cursor-pointer p-4 bg-white/5 border border-white/10 rounded-full hover:bg-white/10 transition-all"
            >
              <Upload className="h-6 w-6 text-emerald-400" />
            </label>
            <p className="text-sm font-bold text-center">
              {cutoffFile ? cutoffFile.name : "Select Cutoff PDF"}
            </p>
            
            {cutoffFile && cutoffStatus !== "uploading" && (
              <button
                onClick={onUploadCutoff}
                className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 rounded-xl font-bold transition-all shadow-lg shadow-emerald-600/20"
              >
                Process PDF
              </button>
            )}

            {cutoffStatus === "uploading" && (
              <div className="flex items-center gap-x-2 text-emerald-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm font-bold">Processing...</span>
              </div>
            )}
          </div>

          {cutoffStatus === "success" && (
            <div className="flex items-center gap-x-2 text-emerald-400 bg-emerald-400/10 p-3 rounded-xl border border-emerald-400/20">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              <span className="text-xs font-bold">{cutoffMessage}</span>
            </div>
          )}

          {cutoffStatus === "error" && (
            <div className="flex items-center gap-x-2 text-rose-400 bg-rose-400/10 p-3 rounded-xl border border-rose-400/20">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span className="text-xs font-bold">{cutoffMessage}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
