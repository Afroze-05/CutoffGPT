"use client";

import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { useEffect, useState } from "react";
import api from "@/lib/api";
import { GraduationCap, Briefcase, IndianRupee, MapPin } from "lucide-react";

// Fix leaflet icon issue
const icon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

interface MapComponentProps {
  cityFilter?: string;
  engineeringOnly?: boolean;
}

const PUNE_ENGINEERING_MASTER = [
  { name: "COEP Technological University", address: "Shivajinagar, Pune", latitude: 18.5293, longitude: 73.8565, website: "https://www.coep.org.in", phone: "Not Available", courses: "Computer Engineering, IT, ENTC, Mechanical, Civil" },
  { name: "PICT Pune", address: "Dhankawadi, Pune", latitude: 18.4575, longitude: 73.8508, website: "https://www.pict.edu", phone: "Not Available", courses: "Computer Engineering, IT, ENTC" },
  { name: "PCCOE Pune", address: "Nigdi, Pune", latitude: 18.6517, longitude: 73.7615, website: "https://www.pccoepune.com", phone: "Not Available", courses: "Computer Engineering, IT, ENTC, Mechanical, Civil" },
  { name: "VIT Pune", address: "Bibwewadi, Pune", latitude: 18.4635, longitude: 73.8683, website: "https://www.vit.edu", phone: "Not Available", courses: "Computer Engineering, IT, ENTC, Mechanical, AI & DS" },
  { name: "AISSMS COE Pune", address: "Shivajinagar, Pune", latitude: 18.5312, longitude: 73.8580, website: "https://aissmscoe.com", phone: "Not Available", courses: "Computer Engineering, IT, ENTC, Mechanical, Civil" },
  { name: "DY Patil Pimpri", address: "Pimpri, Pune", latitude: 18.6214, longitude: 73.8184, website: "https://www.dypcoeakurdi.ac.in", phone: "Not Available", courses: "Computer Engineering, IT, ENTC, Mechanical" },
  { name: "VIIT Pune", address: "Kondhwa, Pune", latitude: 18.4592, longitude: 73.8833, website: "https://viit.ac.in", phone: "Not Available", courses: "Computer Engineering, IT, ENTC, Mechanical, AI & DS" },
  { name: "PVG COET Pune", address: "Sahakar Nagar, Pune", latitude: 18.4912, longitude: 73.8510, website: "https://www.pvgcoet.ac.in", phone: "Not Available", courses: "Computer Engineering, IT, ENTC, Mechanical" },
  { name: "MMCOE Pune", address: "Karvenagar, Pune", latitude: 18.4901, longitude: 73.8138, website: "https://www.mmcoe.edu.in", phone: "Not Available", courses: "Computer Engineering, IT, ENTC, Mechanical" },
  { name: "Sinhgad Vadgaon", address: "Vadgaon, Pune", latitude: 18.4608, longitude: 73.8344, website: "https://cms.sinhgad.edu", phone: "Not Available", courses: "Computer Engineering, IT, ENTC, Mechanical, Civil" },
  { name: "JSPM Tathawade", address: "Tathawade, Pune", latitude: 18.6186, longitude: 73.7511, website: "https://jspm.edu.in", phone: "Not Available", courses: "Computer Engineering, IT, ENTC, Mechanical" },
  { name: "MIT-WPU Pune", address: "Kothrud, Pune", latitude: 18.5186, longitude: 73.8150, website: "https://mitwpu.edu.in", phone: "Not Available", courses: "Computer Engineering, IT, ENTC, Mechanical, AI & DS" },
  { name: "Cummins College of Engineering for Women", address: "Karvenagar, Pune", latitude: 18.4880, longitude: 73.8170, website: "https://cumminscollege.org", phone: "Not Available", courses: "Computer Engineering, IT, ENTC, Mechanical" },
  { name: "Modern College of Engineering", address: "Shivajinagar, Pune", latitude: 18.5300, longitude: 73.8450, website: "https://moderncoe.edu.in", phone: "Not Available", courses: "Computer Engineering, IT, ENTC, Mechanical" },
];

const MapComponent = ({ cityFilter = "", engineeringOnly = false }: MapComponentProps) => {
  const [colleges, setColleges] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    const fetchColleges = async () => {
      try {
        const response = await api.get("/colleges/");
        let rows = response.data || [];
        if (cityFilter) {
          rows = rows.filter((c: any) => (c.location || "").toLowerCase().includes(cityFilter.toLowerCase()));
        }
        if (engineeringOnly) {
          rows = rows.filter((c: any) => {
            const b = (c.branches || "").toLowerCase();
            const n = (c.name || "").toLowerCase();
            return b.includes("engineering") || b.includes("computer") || b.includes("mechanical") || b.includes("civil") || n.includes("engineering");
          });
        }
        // Merge with curated Pune engineering list so major colleges are always shown on map.
        const byName = new Map<string, any>();
        [...rows, ...PUNE_ENGINEERING_MASTER].forEach((item: any) => {
          const key = (item.name || "").toLowerCase().trim();
          if (!key) return;
          const existing = byName.get(key) || {};
          byName.set(key, {
            ...existing,
            ...item,
            location: item.location || item.city || existing.location || "Pune",
            address: item.address || existing.address || "Pune",
            branches: item.branches || item.courses || existing.branches || "",
          });
        });
        setColleges(Array.from(byName.values()));
      } catch (error) {
        console.error("Failed to fetch colleges for map:", error);
      }
    };
    fetchColleges();
  }, [cityFilter, engineeringOnly]);

  const center: [number, number] = [18.5204, 73.8567];

  return (
    <div className="h-full w-full relative">
      <div className="absolute z-[1000] top-3 left-3 right-3">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search Pune colleges..."
          className="w-full bg-black/60 border border-white/20 rounded-lg px-3 py-2 text-xs text-white"
        />
      </div>
      <MapContainer 
        center={center} 
        zoom={13} 
        style={{ height: "100%", width: "100%", background: "#0d1117" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {colleges
          .filter((c: any) => {
            if (!searchQuery.trim()) return true;
            const q = searchQuery.toLowerCase();
            return (c.name || "").toLowerCase().includes(q) || (c.address || "").toLowerCase().includes(q);
          })
          .map((college) => (
            college.latitude && college.longitude && (
              <Marker 
                key={college.id || college.name} 
                position={[college.latitude, college.longitude]}
                icon={icon}
              >
                <Popup className="custom-popup">
                  <div className="p-2 min-w-[220px] bg-slate-900 text-white rounded-lg">
                    <h3 className="font-bold text-sky-400 text-sm mb-1 leading-tight">{college.name}</h3>
                    <div className="flex items-center gap-x-1 text-[10px] text-zinc-400 mb-2">
                      <MapPin className="h-3 w-3" />
                      <span className="line-clamp-2">{college.address || college.location}</span>
                    </div>
                    <p className="text-[10px] text-zinc-300 mb-1">Phone: {college.phone || "Not Available"}</p>
                    <div className="space-y-2 mb-3">
                      <div className="flex items-center justify-between text-[10px]">
                        <div className="flex items-center gap-x-1 text-zinc-300">
                          <IndianRupee className="h-3 w-3 text-emerald-400" />
                          <span>Annual Fees</span>
                        </div>
                        <span className="font-bold">₹{college.fees?.toLocaleString() || "N/A"}</span>
                      </div>
                      <div className="flex items-center justify-between text-[10px]">
                        <div className="flex items-center gap-x-1 text-zinc-300">
                          <Briefcase className="h-3 w-3 text-sky-400" />
                          <span>Avg Package</span>
                        </div>
                        <span className="font-bold">{college.avg_package || "N/A"} LPA</span>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-white/10">
                      <p className="text-[9px] text-zinc-500 uppercase font-bold mb-1">Courses</p>
                      <div className="flex flex-wrap gap-1">
                        {(college.branches || "Computer Engineering, IT, Mechanical").split(",").slice(0, 5).map((b: string) => (
                          <span key={b} className="text-[8px] bg-white/5 border border-white/10 px-1.5 py-0.5 rounded text-zinc-300">
                            {b.trim()}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="pt-2 mt-2 border-t border-white/10 space-y-1">
                      <a
                        href={college.website || `https://www.google.com/search?q=${encodeURIComponent(college.name + " official website")}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[10px] text-sky-300 underline block"
                      >
                        Open Website
                      </a>
                      <a
                        href={`https://www.google.com/maps/dir/?api=1&destination=${college.latitude},${college.longitude}`}
                        target="_blank"
                        rel="noreferrer"
                        className="text-[10px] text-emerald-300 underline block"
                      >
                        Open Directions
                      </a>
                    </div>
                  </div>
                </Popup>
              </Marker>
            )
          ))}
      </MapContainer>
    </div>
  );
};

export default MapComponent;
