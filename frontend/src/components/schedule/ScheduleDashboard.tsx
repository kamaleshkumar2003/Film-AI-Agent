import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Sparkles,
  Zap,
  Sliders,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Sun,
  Moon,
  Sunrise,
  Sunset,
  CloudRain,
  Lock,
  Unlock,
  ArrowUp,
  ArrowDown,
  FileText,
  HelpCircle,
  Car,
  ShieldAlert,
  ChevronRight,
  TrendingUp,
  RefreshCw,
  X,
} from 'lucide-react';
import { api } from '../../api/client';
import {
  ScheduleVersion,
  ShootingDay,
  ScheduleItem,
  ScheduleConflict,
  OptimizationProfile,
  WhatIfResponse,
} from '../../types';

interface ScheduleDashboardProps {
  projectId: string;
}

export const ScheduleDashboard: React.FC<ScheduleDashboardProps> = ({ projectId }) => {
  const [versions, setVersions] = useState<ScheduleVersion[]>([]);
  const [currentVersion, setCurrentVersion] = useState<ScheduleVersion | null>(null);
  const [selectedProfile, setSelectedProfile] = useState<OptimizationProfile>('BALANCED');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // What-If Sandbox state
  const [isWhatIfOpen, setIsWhatIfOpen] = useState(false);
  const [scenarioType, setScenarioType] = useState<'cast_unavailable' | 'location_unavailable' | 'lose_day'>('cast_unavailable');
  const [scenarioActor, setScenarioActor] = useState('Meera');
  const [scenarioDate, setScenarioDate] = useState('');
  const [scenarioLoc, setScenarioLoc] = useState('Chennai Marina Beach Pier 42');
  const [isSimulating, setIsSimulating] = useState(false);
  const [whatIfResult, setWhatIfResult] = useState<WhatIfResponse | null>(null);

  const loadVersions = async () => {
    setIsLoading(true);
    try {
      const data = await api.getScheduleVersions(projectId);
      setVersions(data);
      if (data.length > 0) {
        if (!currentVersion || !data.some((v: ScheduleVersion) => v.id === currentVersion.id)) {
          setCurrentVersion(data[0]);
        } else {
          const refreshed = data.find((v: ScheduleVersion) => v.id === currentVersion.id);
          if (refreshed) setCurrentVersion(refreshed);
        }
      }
    } catch (err) {
      console.error('Failed to load schedule versions:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadVersions();
  }, [projectId]);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const newVersion = await api.generateSchedule(projectId, {
        objective_profile: selectedProfile,
      });
      await loadVersions();
      setCurrentVersion(newVersion);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Schedule generation failed. Ensure scenes exist and dates are valid.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleToggleLock = async (item: ScheduleItem, dayNumber: number) => {
    try {
      await api.lockScene(projectId, {
        scene_id: item.scene_id,
        is_locked: !item.is_locked,
        locked_day_number: !item.is_locked ? dayNumber : undefined,
        locked_start_time: !item.is_locked ? item.planned_start_time : undefined,
      });
      await loadVersions();
    } catch (err) {
      console.error('Failed to toggle lock:', err);
    }
  };

  const handleMoveItem = async (dayId: string, itemId: string, newOrder: number) => {
    if (!currentVersion) return;
    try {
      await api.moveScheduleItem(projectId, currentVersion.id, itemId, {
        target_shooting_day_id: dayId,
        new_order: newOrder,
      });
      await loadVersions();
    } catch (err) {
      console.error('Failed to move item:', err);
    }
  };

  const handleRunWhatIf = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSimulating(true);
    setWhatIfResult(null);
    try {
      const params: Record<string, any> = {};
      if (scenarioType === 'cast_unavailable') {
        params.cast_member_name = scenarioActor;
        params.date = scenarioDate;
      } else if (scenarioType === 'location_unavailable') {
        params.location_name = scenarioLoc;
        params.date = scenarioDate;
      }
      const res = await api.runWhatIf(projectId, {
        scenario_type: scenarioType,
        parameters: params,
      });
      setWhatIfResult(res);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'What-If simulation failed.');
    } finally {
      setIsSimulating(false);
    }
  };

  const handleExportPdf = () => {
    if (!currentVersion) return;
    window.open(api.getExportPdfUrl(projectId, currentVersion.id), '_blank');
  };

  // Helper for score color
  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    if (score >= 70) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
  };

  return (
    <div className="space-y-6">
      {/* Top Controls Bar */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
        {/* Profile & Generator */}
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-xl p-1">
            <Sliders className="w-4 h-4 text-cyan-400 ml-2" />
            <select
              value={selectedProfile}
              onChange={(e) => setSelectedProfile(e.target.value as OptimizationProfile)}
              className="bg-transparent text-xs text-slate-200 font-semibold focus:outline-none pr-3 py-1 cursor-pointer"
            >
              <option value="BALANCED" className="bg-slate-900">Balanced (Trade-offs)</option>
              <option value="FASTEST" className="bg-slate-900">Fastest (Min Days)</option>
              <option value="CHEAPEST" className="bg-slate-900">Cheapest (Min Rates)</option>
              <option value="BEST_QUALITY" className="bg-slate-900">Best Quality (Golden Hour)</option>
            </select>
          </div>

          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-white shadow-lg transition ${
              isGenerating
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 shadow-emerald-500/20'
            }`}
          >
            <Sparkles className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
            {isGenerating ? 'Solving CP-SAT Optimization...' : 'Generate Schedule (OR-Tools)'}
          </button>
        </div>

        {/* Version Switcher & Tools */}
        <div className="flex items-center gap-2.5 flex-wrap">
          {versions.length > 0 && (
            <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5">
              <span className="text-[11px] font-semibold text-slate-400">Version:</span>
              <select
                value={currentVersion?.id || ''}
                onChange={(e) => {
                  const found = versions.find((v) => v.id === e.target.value);
                  if (found) setCurrentVersion(found);
                }}
                className="bg-transparent text-xs text-white font-medium focus:outline-none cursor-pointer"
              >
                {versions.map((v) => (
                  <option key={v.id} value={v.id} className="bg-slate-900 text-white">
                    V{v.version_number}: {v.name} ({v.quality_score} pts)
                  </option>
                ))}
              </select>
            </div>
          )}

          <button
            onClick={() => setIsWhatIfOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-indigo-950/70 hover:bg-indigo-900 text-indigo-200 border border-indigo-700/60 shadow-sm transition"
          >
            <Zap className="w-3.5 h-3.5 text-indigo-400" />
            What-If Sandbox
          </button>

          {currentVersion && (
            <button
              onClick={handleExportPdf}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-rose-950/70 hover:bg-rose-900 text-rose-200 border border-rose-800/60 shadow-sm transition"
            >
              <FileText className="w-3.5 h-3.5 text-rose-400" />
              Call Sheet PDF
            </button>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="p-16 text-center text-slate-400 text-sm">Loading production schedules...</div>
      ) : !currentVersion ? (
        <div className="p-16 rounded-3xl bg-slate-900/40 border border-slate-800 text-center max-w-xl mx-auto space-y-4">
          <div className="p-4 rounded-2xl bg-emerald-500/10 text-emerald-400 w-fit mx-auto">
            <Calendar className="w-10 h-10" />
          </div>
          <h3 className="text-lg font-bold text-white">No Schedule Generated Yet</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Click <span className="text-emerald-400 font-semibold">"Generate Schedule (OR-Tools)"</span> above to run
            mathematical discrete optimization. The solver will automatically align scenes with NOAA astronomical solar windows,
            weather forecasts, and cast & location constraints.
          </p>
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-lg shadow-emerald-500/20 transition"
          >
            {isGenerating ? 'Optimizing...' : 'Generate First Schedule'}
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Quality Score & Metric Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Overall Score */}
            <div className={`p-4 rounded-2xl border flex items-center justify-between ${getScoreColor(currentVersion.quality_score)}`}>
              <div>
                <span className="text-[11px] uppercase font-bold tracking-wider opacity-80">Schedule Quality</span>
                <div className="text-3xl font-black mt-0.5">{currentVersion.quality_score} / 100</div>
                <span className="text-[10px] font-medium opacity-90">
                  {currentVersion.quality_score >= 85 ? 'Highly Optimized' : currentVersion.quality_score >= 70 ? 'Viable Production' : 'Heavy Constraints'}
                </span>
              </div>
              <TrendingUp className="w-8 h-8 opacity-80" />
            </div>

            {/* Days & Efficiency */}
            <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800">
              <span className="text-[11px] uppercase font-semibold text-slate-400 tracking-wider">Shooting Days</span>
              <div className="text-2xl font-bold text-white mt-1">{currentVersion.total_shooting_days} Days</div>
              <span className="text-[10px] text-slate-500">
                {currentVersion.shooting_days.reduce((acc, d) => acc + d.items.length, 0)} scenes scheduled
              </span>
            </div>

            {/* Weather & Sun Alignment */}
            <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800">
              <span className="text-[11px] uppercase font-semibold text-slate-400 tracking-wider">Sun & Weather Score</span>
              <div className="text-2xl font-bold text-cyan-400 mt-1">
                {currentVersion.score_breakdown?.weather_compliance_score ?? 90}%
              </div>
              <span className="text-[10px] text-slate-500">
                Lighting: {currentVersion.score_breakdown?.lighting_compliance_score ?? 95}% aligned
              </span>
            </div>

            {/* Company Moves & Travel */}
            <div className="p-4 rounded-2xl bg-slate-900/70 border border-slate-800">
              <span className="text-[11px] uppercase font-semibold text-slate-400 tracking-wider">Location Grouping</span>
              <div className="text-2xl font-bold text-indigo-400 mt-1">
                {currentVersion.score_breakdown?.location_grouping_score ?? 88}%
              </div>
              <span className="text-[10px] text-slate-500">
                Transit: {currentVersion.score_breakdown?.travel_minimization_score ?? 85}% minimized
              </span>
            </div>
          </div>

          {/* AI Explanation & Review */}
          {currentVersion.explanation && (
            <div className="p-4 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900 border border-indigo-800/30 space-y-2">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-300">
                  AI Production Scheduler Explanation
                </h4>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">{currentVersion.explanation}</p>
              
              {currentVersion.ai_review && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2 text-[11px]">
                  {currentVersion.ai_review.strengths && currentVersion.ai_review.strengths.length > 0 && (
                    <div className="p-2.5 rounded-xl bg-slate-950/60 border border-emerald-800/30">
                      <span className="font-semibold text-emerald-400 block mb-1">Key Strengths:</span>
                      <ul className="list-disc list-inside text-slate-300 space-y-0.5">
                        {currentVersion.ai_review.strengths.map((s: string, idx: number) => (
                          <li key={idx}>{s}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {currentVersion.ai_review.potential_risks && currentVersion.ai_review.potential_risks.length > 0 && (
                    <div className="p-2.5 rounded-xl bg-slate-950/60 border border-amber-800/30">
                      <span className="font-semibold text-amber-400 block mb-1">Production Risks:</span>
                      <ul className="list-disc list-inside text-slate-300 space-y-0.5">
                        {currentVersion.ai_review.potential_risks.map((r: string, idx: number) => (
                          <li key={idx}>{r}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Conflicts Warning Banner */}
          {currentVersion.conflicts && currentVersion.conflicts.length > 0 && (
            <div className="p-4 rounded-2xl bg-rose-950/30 border border-rose-800/50 space-y-2">
              <div className="flex items-center gap-2 text-rose-400 text-xs font-bold">
                <ShieldAlert className="w-4 h-4" />
                Detected Schedule Conflicts ({currentVersion.conflicts.length})
              </div>
              <div className="space-y-1.5">
                {currentVersion.conflicts.map((c, idx) => (
                  <div
                    key={idx}
                    className="flex items-start justify-between gap-3 text-xs bg-rose-950/50 p-2.5 rounded-lg border border-rose-800/30 text-rose-200"
                  >
                    <div>
                      <span className="font-bold uppercase tracking-wider text-[10px] text-rose-300 mr-2">
                        [{c.conflict_type}]
                      </span>
                      {c.message}
                    </div>
                    <span className="px-2 py-0.5 text-[9px] font-bold rounded bg-rose-900 text-rose-100 uppercase shrink-0">
                      {c.severity}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Shooting Stripboard Days */}
          <div className="space-y-5">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <Calendar className="w-4 h-4 text-emerald-400" />
                Daily Production Call Stripboard
              </h3>
              <span className="text-xs text-slate-500">
                NOAA Astronomical Solar calculations & Open-Meteo weather integration active
              </span>
            </div>

            <div className="space-y-4">
              {currentVersion.shooting_days.map((day) => (
                <div
                  key={day.id}
                  className="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-lg"
                >
                  {/* Day Header Banner */}
                  <div className="bg-slate-950/80 px-5 py-3.5 border-b border-slate-800/80 flex flex-wrap items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className="px-3 py-1 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-extrabold tracking-wider">
                        DAY {day.day_number}
                      </div>
                      <div>
                        <span className="text-sm font-bold text-white">{day.date}</span>
                        <span className="text-xs text-slate-400 ml-2 font-medium">
                          ({day.primary_location_name || 'Primary Stage'})
                        </span>
                      </div>
                    </div>

                    {/* Solar & Weather Strip */}
                    <div className="flex items-center gap-4 text-xs text-slate-400 flex-wrap">
                      {day.sunrise_time && (
                        <div className="flex items-center gap-1 text-amber-300">
                          <Sunrise className="w-3.5 h-3.5" />
                          <span>Rise: {day.sunrise_time}</span>
                        </div>
                      )}
                      {day.sunset_time && (
                        <div className="flex items-center gap-1 text-rose-300">
                          <Sunset className="w-3.5 h-3.5" />
                          <span>Set: {day.sunset_time}</span>
                        </div>
                      )}
                      {day.weather_summary && (
                        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-slate-200">
                          <CloudRain className="w-3 h-3 text-cyan-400" />
                          <span>{day.weather_summary}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-1 text-slate-300 font-semibold">
                        <Clock className="w-3.5 h-3.5 text-slate-500" />
                        <span>Call {day.call_time} ➔ Wrap {day.wrap_time}</span>
                      </div>
                    </div>
                  </div>

                  {/* Scene Strips inside Day */}
                  <div className="p-4 space-y-2">
                    {day.items.length === 0 ? (
                      <p className="text-xs text-slate-500 py-2 italic text-center">No scenes scheduled on this day.</p>
                    ) : (
                      day.items.map((item, idx) => {
                        const scene = item.scene;
                        return (
                          <React.Fragment key={item.id}>
                            {/* Company Move Alert if changing location */}
                            {item.company_move_before && (
                              <div className="flex items-center gap-2 p-2 rounded-lg bg-amber-950/40 border border-amber-800/40 text-amber-300 text-xs font-semibold">
                                <Car className="w-4 h-4 text-amber-400" />
                                <span>COMPANY MOVE: Transit + Setup Buffer ({item.travel_time_minutes_before} minutes)</span>
                              </div>
                            )}

                            <div className="flex items-center justify-between gap-3 p-3 rounded-xl bg-slate-950/70 border border-slate-800 hover:border-slate-700 transition">
                              {/* Left: Timing & Scene Code */}
                              <div className="flex items-center gap-3">
                                <div className="text-center w-14 shrink-0">
                                  <span className="block text-xs font-extrabold text-cyan-400">
                                    {item.planned_start_time}
                                  </span>
                                  <span className="block text-[10px] text-slate-500 font-medium">
                                    {item.duration_minutes}m
                                  </span>
                                </div>

                                <div className="border-l border-slate-800 pl-3">
                                  <div className="flex items-center gap-2 mb-0.5">
                                    <span className="px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 text-[10px] font-bold">
                                      {scene?.scene_code || `SC-${item.order_in_day}`}
                                    </span>
                                    <h5 className="text-xs font-bold text-white">
                                      {scene?.scene_heading || 'SCENE HEADING'}
                                    </h5>
                                  </div>
                                  <div className="flex items-center gap-2 text-[11px] text-slate-400">
                                    <span>{scene?.location_name || 'Location'}</span>
                                    <span>•</span>
                                    <span>{scene?.day_night || 'DAY'}</span>
                                    {scene?.weather_sensitivity === 'CRITICAL' && (
                                      <>
                                        <span>•</span>
                                        <span className="text-rose-400 font-semibold">Weather Critical</span>
                                      </>
                                    )}
                                  </div>
                                </div>
                              </div>

                              {/* Middle: Cast Badges */}
                              <div className="hidden md:flex items-center gap-1 flex-wrap max-w-xs">
                                {scene?.character_names?.map((cName, cIdx) => (
                                  <span
                                    key={cIdx}
                                    className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[10px] text-slate-300 font-medium"
                                  >
                                    {cName}
                                  </span>
                                ))}
                              </div>

                              {/* Right: Lock & Actions */}
                              <div className="flex items-center gap-2 shrink-0">
                                <button
                                  onClick={() => handleToggleLock(item, day.day_number)}
                                  title={item.is_locked ? 'Scene is locked to this day' : 'Lock scene to this day'}
                                  className={`p-1.5 rounded-lg border transition ${
                                    item.is_locked
                                      ? 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                                      : 'bg-slate-900 text-slate-500 border-slate-800 hover:text-slate-300'
                                  }`}
                                >
                                  {item.is_locked ? <Lock className="w-3.5 h-3.5" /> : <Unlock className="w-3.5 h-3.5" />}
                                </button>

                                <div className="flex items-center gap-0.5 bg-slate-900 border border-slate-800 rounded-lg p-0.5">
                                  <button
                                    disabled={idx === 0}
                                    onClick={() => handleMoveItem(day.id, item.id, item.order_in_day - 1)}
                                    className="p-1 text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
                                    title="Move scene up in day"
                                  >
                                    <ArrowUp className="w-3 h-3" />
                                  </button>
                                  <button
                                    disabled={idx === day.items.length - 1}
                                    onClick={() => handleMoveItem(day.id, item.id, item.order_in_day + 1)}
                                    className="p-1 text-slate-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
                                    title="Move scene down in day"
                                  >
                                    <ArrowDown className="w-3 h-3" />
                                  </button>
                                </div>
                              </div>
                            </div>
                          </React.Fragment>
                        );
                      })
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* What-If Sandbox Modal */}
      {isWhatIfOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-indigo-400" />
                <h3 className="text-base font-bold text-white">What-If Rescheduling Sandbox</h3>
              </div>
              <button
                onClick={() => setIsWhatIfOpen(false)}
                className="text-slate-500 hover:text-white transition"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-slate-400">
              Simulate disruptions (e.g. actor illness, location permit denial, lost shooting day) without touching your saved schedule.
            </p>

            <form onSubmit={handleRunWhatIf} className="space-y-3.5">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Disruption Scenario</label>
                <select
                  value={scenarioType}
                  onChange={(e) => setScenarioType(e.target.value as any)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="cast_unavailable">Lead Actor Becomes Unavailable (Illness / Delay)</option>
                  <option value="location_unavailable">Location Closed / Permit Revoked</option>
                  <option value="lose_day">Lost Production Day (Extreme Weather / Curtailment)</option>
                </select>
              </div>

              {scenarioType === 'cast_unavailable' && (
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Actor Name</label>
                    <input
                      type="text"
                      value={scenarioActor}
                      onChange={(e) => setScenarioActor(e.target.value)}
                      placeholder="e.g. Meera"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Unavailable Date</label>
                    <input
                      type="date"
                      required
                      value={scenarioDate}
                      onChange={(e) => setScenarioDate(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>
              )}

              {scenarioType === 'location_unavailable' && (
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Location Name</label>
                    <input
                      type="text"
                      value={scenarioLoc}
                      onChange={(e) => setScenarioLoc(e.target.value)}
                      placeholder="e.g. Marina Beach"
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Closed Date</label>
                    <input
                      type="date"
                      required
                      value={scenarioDate}
                      onChange={(e) => setScenarioDate(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>
              )}

              <button
                type="submit"
                disabled={isSimulating}
                className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/20 transition flex items-center justify-center gap-2"
              >
                <Zap className={`w-3.5 h-3.5 ${isSimulating ? 'animate-spin' : ''}`} />
                {isSimulating ? 'Simulating Re-optimization...' : 'Run Simulation'}
              </button>
            </form>

            {/* What-If Result Display */}
            {whatIfResult && (
              <div
                className={`p-4 rounded-xl border text-xs space-y-2 mt-4 ${
                  whatIfResult.feasible
                    ? 'bg-emerald-950/30 border-emerald-800/40 text-emerald-200'
                    : 'bg-rose-950/30 border-rose-800/40 text-rose-200'
                }`}
              >
                <div className="flex items-center gap-2 font-bold text-sm">
                  {whatIfResult.feasible ? (
                    <>
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      <span>Feasible Re-route Found</span>
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-4 h-4 text-rose-400" />
                      <span>Schedule Infeasible Under Scenario</span>
                    </>
                  )}
                </div>
                <p className="leading-relaxed">{whatIfResult.message}</p>
                {whatIfResult.diff_summary && (
                  <p className="text-[11px] text-slate-400 italic">{whatIfResult.diff_summary}</p>
                )}
                {whatIfResult.quality_score !== undefined && (
                  <div className="flex items-center gap-3 pt-1 text-[11px] font-semibold">
                    <span>Projected Quality: {whatIfResult.quality_score} pts</span>
                    <span>Active Days: {whatIfResult.hypothetical_days_count}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
