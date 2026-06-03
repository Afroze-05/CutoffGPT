"use client";

import dynamic from "next/dynamic";
import "leaflet/dist/leaflet.css";
import { Info, Map as MapIcon, Navigation } from "lucide-react";

const MapComponent = dynamic(() => import("@/components/MapComponent"), { 
  ssr: false,
  loading: () => <div className="h-[600px] w-full bg-[#0d1117] animate-pulse rounded-3xl border border-white/10 flex items-center justify-center text-zinc-500">Loading Interactive Map...</div>
});

const MapPage = () => {
  return (
    <div className="p-8 space-y-8 bg-[#0b0e14] min-h-full text-white">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold flex items-center gap-x-3">
            <MapIcon className="text-emerald-400" />
            Pune Engineering Map
          </h1>
          <p className="text-zinc-400">Explore the top engineering colleges, hostels, and nearby facilities across Pune.</p>
        </div>
        <div className="flex items-center gap-x-3 px-4 py-2 glass rounded-2xl border border-white/10 text-sm">
           <Navigation className="h-4 w-4 text-sky-400" />
           <span className="font-medium">15 Colleges Found</span>
        </div>
      </div>

      <div className="h-[600px] rounded-3xl overflow-hidden border border-white/10 shadow-2xl relative">
        <MapComponent />
        
        {/* Map Overlay Controls */}
        <div className="absolute bottom-6 left-6 right-6 flex flex-wrap gap-4 z-[1000]">
           <div className="glass px-4 py-2 rounded-xl flex items-center gap-x-2 text-xs border-emerald-500/30">
              <div className="w-2 h-2 rounded-full bg-blue-500" />
              <span>Colleges</span>
           </div>
           <div className="glass px-4 py-2 rounded-xl flex items-center gap-x-2 text-xs border-orange-500/30">
              <div className="w-2 h-2 rounded-full bg-orange-500" />
              <span>Hostels</span>
           </div>
           <div className="glass px-4 py-2 rounded-xl flex items-center gap-x-2 text-xs border-sky-500/30">
              <div className="w-2 h-2 rounded-full bg-sky-500" />
              <span>Stations</span>
           </div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
         <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
            <div className="w-10 h-10 rounded-xl bg-emerald-400/10 flex items-center justify-center">
               <Info className="h-5 w-5 text-emerald-400" />
            </div>
            <h3 className="font-bold">Pro Tip</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">Click on any marker to see detailed information about the college, including fees, placements, and available branches.</p>
         </div>
         <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
            <div className="w-10 h-10 rounded-xl bg-sky-400/10 flex items-center justify-center">
               <Navigation className="h-5 w-5 text-sky-400" />
            </div>
            <h3 className="font-bold">Accessibility</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">Most colleges in Shivajinagar and Kothrud have excellent connectivity to Pune Railway Station and Bus Stops.</p>
         </div>
         <div className="glass p-6 rounded-2xl border border-white/10 space-y-4">
            <div className="w-10 h-10 rounded-xl bg-orange-400/10 flex items-center justify-center">
               <MapIcon className="h-5 w-5 text-orange-400" />
            </div>
            <h3 className="font-bold">Nearby Facilities</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">Markers also show nearby hospitals and student-friendly areas with multiple hostel options.</p>
         </div>
      </div>
    </div>
  );
};

export default MapPage;
