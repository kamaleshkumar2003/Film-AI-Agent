import React, { useState } from 'react';
import { SceneSummary, LocationType, DayNight, WeatherSensitivity } from '../../types';
import { StatusBadge, WeatherBadge } from '../common/Badge';
import { Search, Filter, ChevronRight, Clock, Users, Package, Car, Eye } from 'lucide-react';

interface SceneTableProps {
  scenes: SceneSummary[];
  onSelectScene: (sceneId: string) => void;
  selectedSceneId: string | null;
}

export const SceneTable: React.FC<SceneTableProps> = ({ scenes, onSelectScene, selectedSceneId }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterIntExt, setFilterIntExt] = useState<string>('ALL');
  const [filterDayNight, setFilterDayNight] = useState<string>('ALL');
  const [filterWeather, setFilterWeather] = useState<string>('ALL');

  const filteredScenes = scenes.filter((s) => {
    const matchesSearch =
      s.scene_heading.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.location_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.character_names.some((cn) => cn.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesIntExt = filterIntExt === 'ALL' || s.int_ext === filterIntExt;
    const matchesDayNight = filterDayNight === 'ALL' || s.day_night === filterDayNight;
    const matchesWeather = filterWeather === 'ALL' || s.weather_sensitivity === filterWeather;

    return matchesSearch && matchesIntExt && matchesDayNight && matchesWeather;
  });

  return (
    <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur shadow-xl">
      {/* Search & Filter Toolbar */}
      <div className="p-4 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 flex-1 min-w-[240px]">
          <div className="relative w-full max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search scene, location, character..."
              className="w-full pl-9 pr-4 py-1.5 text-xs rounded-xl bg-slate-950 border border-slate-800 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap text-xs">
          <div className="flex items-center gap-1.5 text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <span>Filters:</span>
          </div>

          <select
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-300 focus:outline-none focus:border-cyan-500"
            value={filterIntExt}
            onChange={(e) => setFilterIntExt(e.target.value)}
          >
            <option value="ALL">INT / EXT (All)</option>
            <option value="INTERIOR">INTERIOR (INT)</option>
            <option value="EXTERIOR">EXTERIOR (EXT)</option>
            <option value="INT_EXT">INT / EXT</option>
          </select>

          <select
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-300 focus:outline-none focus:border-cyan-500"
            value={filterDayNight}
            onChange={(e) => setFilterDayNight(e.target.value)}
          >
            <option value="ALL">Day / Night (All)</option>
            <option value="DAY">DAY</option>
            <option value="NIGHT">NIGHT</option>
            <option value="DUSK">DUSK / SUNSET</option>
            <option value="DAWN">DAWN / SUNRISE</option>
            <option value="CONTINUOUS">CONTINUOUS</option>
          </select>

          <select
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-slate-300 focus:outline-none focus:border-cyan-500"
            value={filterWeather}
            onChange={(e) => setFilterWeather(e.target.value)}
          >
            <option value="ALL">Weather (All)</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
            <option value="CRITICAL">CRITICAL</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800 font-semibold">
            <tr>
              <th className="py-3 px-4">Scene #</th>
              <th className="py-3 px-4">Scene Heading</th>
              <th className="py-3 px-4">Type</th>
              <th className="py-3 px-4">Location</th>
              <th className="py-3 px-4">Time</th>
              <th className="py-3 px-4">Pages</th>
              <th className="py-3 px-4">Cast</th>
              <th className="py-3 px-4">Props & Veh</th>
              <th className="py-3 px-4">Weather</th>
              <th className="py-3 px-4">Est. Shoot</th>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredScenes.length === 0 ? (
              <tr>
                <td colSpan={12} className="py-8 text-center text-slate-500">
                  No scenes match the selected filters.
                </td>
              </tr>
            ) : (
              filteredScenes.map((s) => {
                const isSelected = selectedSceneId === s.id;
                return (
                  <tr
                    key={s.id}
                    onClick={() => onSelectScene(s.id)}
                    className={`hover:bg-slate-800/40 cursor-pointer transition ${
                      isSelected ? 'bg-cyan-950/30 border-l-2 border-cyan-400' : ''
                    }`}
                  >
                    <td className="py-3.5 px-4 font-mono font-bold text-cyan-400">{s.scene_code}</td>
                    <td className="py-3.5 px-4 font-semibold text-slate-100 max-w-xs truncate" title={s.scene_heading}>
                      {s.scene_heading}
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-medium text-slate-300">
                        {s.int_ext}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 truncate max-w-[140px]">{s.location_name}</td>
                    <td className="py-3.5 px-4 text-slate-300 font-mono text-[11px]">{s.script_time}</td>
                    <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                      p. {s.source_page_start}{s.source_page_end > s.source_page_start ? `-${s.source_page_end}` : ''}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center gap-1.5" title={s.character_names.join(', ')}>
                        <Users className="w-3.5 h-3.5 text-indigo-400" />
                        <span className="font-semibold text-indigo-300">{s.character_count}</span>
                        {s.character_names.length > 0 && (
                          <span className="text-[11px] text-slate-400 truncate max-w-[120px]">
                            ({s.character_names.slice(0, 2).join(', ')}{s.character_names.length > 2 ? '...' : ''})
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">
                      <div className="flex items-center gap-3">
                        <span className="flex items-center gap-1 text-blue-400" title={`${s.prop_count} Props`}>
                          <Package className="w-3 h-3" /> {s.prop_count}
                        </span>
                        <span className="flex items-center gap-1 text-rose-400" title={`${s.vehicle_count} Vehicles`}>
                          <Car className="w-3 h-3" /> {s.vehicle_count}
                        </span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <WeatherBadge sensitivity={s.weather_sensitivity} />
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-mono text-[11px]">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-500" />
                        {s.estimated_duration_minutes}m
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={s.status} />
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectScene(s.id);
                        }}
                        className="p-1 rounded-lg hover:bg-slate-700 text-slate-400 hover:text-white transition"
                        title="View & Edit Scene"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
