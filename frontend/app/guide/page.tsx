"use client";

import { useState } from "react";
import { 
  GraduationCap, 
  Code, 
  Cpu, 
  Settings, 
  PenTool, 
  Zap, 
  CheckCircle2,
  ArrowRight,
  RotateCcw,
  Briefcase,
  Rocket
} from "lucide-react";
import { cn } from "@/lib/utils";

const questions = [
  {
    id: "coding",
    question: "Do you enjoy writing code and solving logic puzzles?",
    icon: Code,
    color: "text-sky-400"
  },
  {
    id: "ai",
    question: "Are you interested in Artificial Intelligence and Data Science?",
    icon: Zap,
    color: "text-violet-400"
  },
  {
    id: "hardware",
    question: "Do you like working with computer hardware and networking?",
    icon: Cpu,
    color: "text-emerald-400"
  },
  {
    id: "electronics",
    question: "Are you interested in circuits, microcontrollers, and electronics?",
    icon: Settings,
    color: "text-orange-400"
  },
  {
    id: "machines",
    question: "Do you enjoy learning about engines, machines, and manufacturing?",
    icon: Settings,
    color: "text-rose-400"
  },
  {
    id: "design",
    question: "Do you have an interest in structural design and construction?",
    icon: PenTool,
    color: "text-yellow-400"
  }
];

const BranchGuidePage = () => {
  const [answers, setAnswers] = useState<Record<string, boolean>>({});
  const [step, setStep] = useState(0);
  const [showResult, setShowResult] = useState(false);

  const handleAnswer = (val: boolean) => {
    setAnswers({ ...answers, [questions[step].id]: val });
    if (step < questions.length - 1) {
      setStep(step + 1);
    } else {
      setShowResult(true);
    }
  };

  const reset = () => {
    setAnswers({});
    setStep(0);
    setShowResult(false);
  };

  const getRecommendations = () => {
    const recs = [];
    if (answers.coding && answers.ai) {
      recs.push({ 
        name: "AI & Data Science", 
        reason: "Since you love coding and are fascinated by AI, this is the perfect emerging branch for you.",
        career: "AI Engineer, Data Scientist, Machine Learning Specialist"
      });
    }
    if (answers.coding && !answers.ai) {
      recs.push({ 
        name: "Computer Engineering / IT", 
        reason: "Your strong interest in coding and logic makes you a great fit for traditional software branches.",
        career: "Software Developer, Systems Architect, Full Stack Engineer"
      });
    }
    if (answers.electronics || answers.hardware) {
      recs.push({ 
        name: "Electronics & Telecommunication (ENTC)", 
        reason: "You have a natural inclination towards circuits and hardware systems.",
        career: "Embedded Systems Engineer, VLSI Designer, Network Engineer"
      });
    }
    if (answers.machines) {
      recs.push({ 
        name: "Mechanical Engineering", 
        reason: "Your interest in how things work and machines aligns perfectly with Mechanical Engineering.",
        career: "Automotive Engineer, Robotics Engineer, Design Consultant"
      });
    }
    if (answers.design) {
      recs.push({ 
        name: "Civil Engineering", 
        reason: "Designing structures and construction seems to be your area of interest.",
        career: "Structural Engineer, Urban Planner, Project Manager"
      });
    }

    if (recs.length === 0) {
      recs.push({ 
        name: "Computer Engineering", 
        reason: "It's the most versatile branch with high placement opportunities in Pune.",
        career: "General Software Engineering, Technical Consulting"
      });
    }
    return recs;
  };

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-8 bg-[#0b0e14] min-h-full text-white">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold flex items-center gap-x-3">
          <GraduationCap className="text-sky-400" />
          Branch Selection Guide
        </h1>
        <p className="text-zinc-400 font-medium">Find your ideal engineering path based on your personal interests.</p>
      </div>

      {!showResult ? (
        <div className="glass rounded-[40px] p-12 space-y-8 border border-white/10 animate-in fade-in zoom-in duration-300">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-sky-400 uppercase tracking-widest">Question {step + 1} of {questions.length}</span>
            <div className="flex gap-x-1">
              {questions.map((_, i) => (
                <div key={i} className={cn("h-1.5 w-8 rounded-full transition-all", i <= step ? "bg-sky-500" : "bg-white/10")} />
              ))}
            </div>
          </div>

          <div className="space-y-6 py-4 text-center md:text-left">
             <div className={cn("w-20 h-20 mx-auto md:mx-0 rounded-[24px] bg-white/5 flex items-center justify-center border border-white/10 mb-6", questions[step].color)}>
                {(() => {
                  const Icon = questions[step].icon;
                  return <Icon className="h-10 w-10" />;
                })()}
             </div>
             <h2 className="text-3xl font-bold leading-tight">{questions[step].question}</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
             <button 
               onClick={() => handleAnswer(true)}
               className="p-5 rounded-2xl bg-sky-600 hover:bg-sky-700 text-lg font-bold transition-all flex items-center justify-center gap-x-3 shadow-lg shadow-sky-600/20"
             >
               <CheckCircle2 className="h-6 w-6" />
               Yes, I am
             </button>
             <button 
               onClick={() => handleAnswer(false)}
               className="p-5 rounded-2xl bg-white/5 hover:bg-white/10 text-lg font-bold border border-white/10 transition-all text-zinc-400 hover:text-white"
             >
               Not really
             </button>
          </div>
        </div>
      ) : (
        <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-500">
           <div className="glass rounded-[40px] p-8 md:p-12 border border-emerald-500/20">
              <div className="flex items-center gap-x-4 mb-10">
                 <div className="w-12 h-12 rounded-2xl bg-emerald-500/20 flex items-center justify-center border border-emerald-500/30">
                    <Rocket className="h-6 w-6 text-emerald-400" />
                 </div>
                 <h2 className="text-3xl font-bold">Your Ideal Career Path</h2>
              </div>
              
              <div className="grid gap-6">
                 {getRecommendations().map((rec, i) => (
                   <div key={i} className="p-8 rounded-3xl bg-white/5 border border-white/10 space-y-4 group hover:border-sky-500/50 transition-all">
                      <div className="flex items-center justify-between">
                         <h3 className="text-2xl font-bold text-sky-400">{rec.name}</h3>
                         <div className="px-3 py-1 bg-sky-400/10 text-sky-400 rounded-full text-[10px] font-bold uppercase tracking-widest border border-sky-400/20">
                            Match Found
                         </div>
                      </div>
                      
                      <div className="space-y-4">
                         <div className="flex gap-x-3">
                            <Info className="h-5 w-5 text-zinc-500 shrink-0 mt-1" />
                            <p className="text-zinc-400 leading-relaxed font-medium">{rec.reason}</p>
                         </div>
                         
                         <div className="flex gap-x-3 pt-4 border-t border-white/5">
                            <Briefcase className="h-5 w-5 text-emerald-500 shrink-0 mt-1" />
                            <div>
                               <p className="text-[10px] text-zinc-500 font-bold uppercase tracking-widest mb-1">Career Options</p>
                               <p className="text-sm font-bold text-emerald-400">{rec.career}</p>
                            </div>
                         </div>
                      </div>
                   </div>
                 ))}
              </div>
           </div>

           <button 
             onClick={reset}
             className="flex items-center gap-x-2 text-zinc-500 hover:text-white transition-all text-sm font-bold mx-auto py-4 uppercase tracking-widest"
           >
             <RotateCcw className="h-4 w-4" />
             Take Test Again
           </button>
        </div>
      )}
    </div>
  );
};

export default BranchGuidePage;
