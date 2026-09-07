import React from 'react';
import {
  Clapperboard,
  Plus,
  Upload,
  RefreshCw,
  FolderOpen,
  Calendar,
  Users,
  HardHat,
  MapPin,
  Sparkles,
  FileText,
  FileSpreadsheet,
  FileCode2,
} from 'lucide-react';
import { Project } from '../../types';

export type NavTab = 'breakdown' | 'cast' | 'crew' | 'locations' | 'schedule';

interface HeaderProps {
  currentProject: Project | null;
  projects: Project[];
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  onSelectProject: (id: string) => void;
  onOpenCreateProject: () => void;
  onOpenUpload: () => void;
  onAnalyze: () => void;
  isAnalyzing: boolean;
  onSeedDemo: () => void;
  isSeedingDemo: boolean;
  onExportJson: () => void;
  onExportCsv: () => void;
  onExportPdf: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentProject,
  projects,
  activeTab,
  onTabChange,
  onSelectProject,
  onOpenCreateProject,
  onOpenUpload,
  onAnalyze,
  isAnalyzing,
  onSeedDemo,
  isSeedingDemo,
  onExportJson,
  onExportCsv,
  onExportPdf,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-slate-900/95 backdrop-blur border-b border-slate-800 px-6 py-2.5">
      <div className="max-w-7xl mx-auto flex flex-col gap-2.5">
        {/* Top Bar: Brand, Project Switcher, Actions */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          {/* Logo & Branding */}
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 text-white shadow-lg shadow-cyan-500/20">
              <Clapperboard className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold tracking-tight text-white">SCRIPTBREAKDOWN</h1>
                <span className="px-2 py-0.5 text-[10px] font-black tracking-wider rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1 shadow-sm">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  V2 OPTIMIZED
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                AI Screenplay Breakdown & CP-SAT Schedule Optimization
              </p>
            </div>
          </div>

          {/* Project Selector & Actions */}
          <div className="flex items-center gap-2.5 flex-wrap">
            {/* Project Switcher */}
            <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 rounded-lg p-0.5">
              <FolderOpen className="w-3.5 h-3.5 text-slate-400 ml-2" />
              <select
                className="bg-transparent text-xs text-slate-200 font-medium focus:outline-none pr-3 py-1 cursor-pointer"
                value={currentProject?.id || ''}
                onChange={(e) => onSelectProject(e.target.value)}
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id} className="bg-slate-900 text-white">
                    {p.name} ({p.production_type})
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={onOpenCreateProject}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition border border-slate-700 shadow-sm"
            >
              <Plus className="w-3.5 h-3.5" />
              New
            </button>

            {currentProject && (
              <>
                <button
                  onClick={onOpenUpload}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition border border-slate-700 shadow-sm"
                >
                  <Upload className="w-3.5 h-3.5" />
                  Upload Script
                </button>

                <button
                  onClick={onAnalyze}
                  disabled={isAnalyzing}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold shadow-md transition ${
                    isAnalyzing
                      ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-cyan-500/20'
                  }`}
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
                  {isAnalyzing ? 'Analyzing...' : 'Analyze'}
                </button>

                <button
                  onClick={onSeedDemo}
                  disabled={isSeedingDemo}
                  title="Populate realistic sample Cast, Crew, Locations, and Constraints for scheduling"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-900/60 hover:bg-indigo-800 text-indigo-200 border border-indigo-700/50 shadow-sm transition"
                >
                  <Sparkles className={`w-3.5 h-3.5 text-indigo-400 ${isSeedingDemo ? 'animate-spin' : ''}`} />
                  {isSeedingDemo ? 'Seeding...' : 'Demo Seed'}
                </button>

                {/* Exports */}
                <div className="flex items-center gap-1 border-l border-slate-800 pl-2.5">
                  <button
                    onClick={onExportPdf}
                    title="Export Production Daily Call Sheet PDF"
                    className="flex items-center gap-1 px-2.5 py-1.5 rounded-md text-xs font-semibold bg-rose-950/60 hover:bg-rose-900/80 text-rose-300 border border-rose-800/60 transition"
                  >
                    <FileText className="w-3.5 h-3.5 text-rose-400" />
                    PDF
                  </button>
                  <button
                    onClick={onExportCsv}
                    title="Export industry-standard CSV breakdown"
                    className="flex items-center gap-1 px-2 py-1.5 rounded-md text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
                  >
                    <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
                    CSV
                  </button>
                  <button
                    onClick={onExportJson}
                    title="Export complete structured JSON"
                    className="flex items-center gap-1 px-2 py-1.5 rounded-md text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition"
                  >
                    <FileCode2 className="w-3.5 h-3.5 text-cyan-400" />
                    JSON
                  </button>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Bottom Bar: V2 Navigation Tabs */}
        {currentProject && (
          <nav className="flex items-center gap-1 border-t border-slate-800/80 pt-2 -mb-1">
            <button
              onClick={() => onTabChange('breakdown')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'breakdown'
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Clapperboard className="w-3.5 h-3.5" />
              Screenplay Breakdown
            </button>

            <button
              onClick={() => onTabChange('cast')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'cast'
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              Cast & Availability
            </button>

            <button
              onClick={() => onTabChange('crew')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'crew'
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <HardHat className="w-3.5 h-3.5" />
              Crew & Departments
            </button>

            <button
              onClick={() => onTabChange('locations')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'locations'
                  ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <MapPin className="w-3.5 h-3.5" />
              Locations & Travel
            </button>

            <button
              onClick={() => onTabChange('schedule')}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
                activeTab === 'schedule'
                  ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Calendar className="w-3.5 h-3.5 text-emerald-400" />
              <span className="flex items-center gap-1.5">
                Optimized Schedule
                <span className="px-1.5 py-0.2 bg-emerald-500/20 text-emerald-300 text-[9px] font-bold rounded">
                  CP-SAT
                </span>
              </span>
            </button>
          </nav>
        )}
      </div>
    </header>
  );
};
