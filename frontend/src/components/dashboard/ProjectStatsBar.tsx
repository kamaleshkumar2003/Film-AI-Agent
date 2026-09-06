import React from 'react';
import { ProjectStats } from '../../types';
import { Film, Users, MapPin, Package, Car, CloudLightning, CheckCircle2 } from 'lucide-react';

export const ProjectStatsBar: React.FC<{ stats?: ProjectStats; projectName: string }> = ({ stats, projectName }) => {
  if (!stats) return null;

  const items = [
    { label: 'Total Scenes', value: stats.total_scenes, icon: Film, color: 'text-cyan-400', bg: 'bg-cyan-500/10' },
    { label: 'Analyzed', value: `${stats.analyzed_scenes} / ${stats.total_scenes}`, icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
    { label: 'Characters', value: stats.total_characters, icon: Users, color: 'text-indigo-400', bg: 'bg-indigo-500/10' },
    { label: 'Locations', value: stats.total_locations, icon: MapPin, color: 'text-amber-400', bg: 'bg-amber-500/10' },
    { label: 'Props', value: stats.total_props, icon: Package, color: 'text-blue-400', bg: 'bg-blue-500/10' },
    { label: 'Vehicles', value: stats.total_vehicles, icon: Car, color: 'text-rose-400', bg: 'bg-rose-500/10' },
    { label: 'Critical Weather', value: stats.critical_weather_scenes, icon: CloudLightning, color: 'text-purple-400', bg: 'bg-purple-500/10' },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 mb-6">
      {items.map((it, idx) => {
        const Icon = it.icon;
        return (
          <div
            key={idx}
            className="bg-slate-900/60 border border-slate-800 rounded-xl p-3.5 flex items-center gap-3 backdrop-blur shadow-sm hover:border-slate-700 transition"
          >
            <div className={`p-2.5 rounded-lg ${it.bg} ${it.color}`}>
              <Icon className="w-4 h-4" />
            </div>
            <div>
              <p className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">{it.label}</p>
              <p className="text-lg font-bold text-white tracking-tight">{it.value}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
};
