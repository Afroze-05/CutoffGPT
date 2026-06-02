"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { 
  LayoutDashboard, 
  MessageSquare, 
  Upload, 
  Map, 
  Layers, 
  GraduationCap, 
  Trophy,
  User
} from "lucide-react";

const routes = [
  {
    label: "Dashboard",
    icon: LayoutDashboard,
    href: "/",
    color: "text-sky-400",
  },
  {
    label: "AI Counselor",
    icon: MessageSquare,
    href: "/chat",
    color: "text-violet-400",
  },
  {
    label: "Recommended Colleges",
    icon: Trophy,
    href: "/recommendations",
    color: "text-yellow-400",
  },
  {
    label: "Upload Documents",
    icon: Upload,
    href: "/upload",
    color: "text-pink-400",
  },
  {
    label: "Comparison",
    icon: Layers,
    href: "/compare",
    color: "text-orange-400",
  },
  {
    label: "Interactive Map",
    icon: Map,
    href: "/map",
    color: "text-emerald-400",
  },
  {
    label: "Branch Guide",
    icon: GraduationCap,
    href: "/guide",
    color: "text-green-400",
  },
];

export const Sidebar = () => {
  const pathname = usePathname();

  return (
    <div className="space-y-4 py-4 flex flex-col h-full bg-[#0d1117] border-r border-white/10 text-white">
      <div className="px-3 py-2 flex-1">
        <Link href="/" className="flex items-center pl-3 mb-14">
          <div className="relative w-8 h-8 mr-4">
             <Trophy className="text-sky-400 w-8 h-8" />
          </div>
          <h1 className="text-xl font-bold tracking-tight">
            CollegePath <span className="text-sky-400">AI</span>
          </h1>
        </Link>
        <div className="space-y-1">
          {routes.map((route) => (
            <Link
              key={route.href}
              href={route.href}
              className={cn(
                "text-sm group flex p-3 w-full justify-start font-medium cursor-pointer hover:bg-white/5 rounded-lg transition-all",
                pathname === route.href ? "text-white bg-white/10" : "text-zinc-400",
              )}
            >
              <div className="flex items-center flex-1">
                <route.icon className={cn("h-5 w-5 mr-3", route.color)} />
                {route.label}
              </div>
            </Link>
          ))}
        </div>
      </div>
      <div className="px-3 py-2 border-t border-white/10">
         <div className="flex items-center gap-x-3 p-3 text-zinc-400 text-sm">
            <User className="h-5 w-5" />
            <span>Student Account</span>
         </div>
      </div>
    </div>
  );
};
