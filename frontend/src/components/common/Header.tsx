import React from 'react';
import { Clapperboard, Plus, Upload, Download, RefreshCw, FolderOpen } from 'lucide-react';
import { Project } from '../../types';

interface HeaderProps {
  currentProject: Project | null;
  projects: Project[];
  onSelectProject: (id: string) => void;
  onOpenCreateProject: () => void;
  onOpenUpload: () => void;
  onAnalyze: () => void;
  isAnalyzing: boolean;
  onExportJson: () => void;
  onExportCsv: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentProject,
  projects,
  onSelectProject,
  onOpenCreateProject,
  onOpenUpload,
  onAnalyze,
  isAnalyzing,
  onExportJson,
  onExportCsv,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-slate-900/90 backdrop-blur border-b border-slate-800 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
        {/* Logo & Branding */}
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-gradient-to-tr from-cyan-600 to-indigo-600 text-white shadow-lg shadow-cyan-500/20">
            <Clapperboard className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-white">SCRIPTBREAKDOWN</h1>
              <span className="px-2 py-0.5 text-[10px] font-bold rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                V1 PRODUCTION
              </span>
            </div>
            <p className="text-xs text-slate-400">AI Screenplay Breakdown & Production Planning</p>
          </div>
        </div>

        {/* Project Selector & Actions */}
        <div className="flex items-center gap-3">
          {/* Project Switcher */}
          <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-lg p-1">
            <FolderOpen className="w-4 h-4 text-slate-400 ml-2" />
            <select
              className="bg-transparent text-sm text-slate-200 font-medium focus:outline-none pr-4 py-1 cursor-pointer"
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
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition border border-slate-700 shadow-sm"
          >
            <Plus className="w-3.5 h-3.5" />
            New Project
          </button>

          {currentProject && (
            <>
              <button
                onClick={onOpenUpload}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition border border-slate-700 shadow-sm"
              >
                <Upload className="w-3.5 h-3.5" />
                Upload Script
              </button>

              <button
                onClick={onAnalyze}
                disabled={isAnalyzing}
                className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold shadow-md transition ${
                  isAnalyzing
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-cyan-500/20'
                }`}
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isAnalyzing ? 'animate-spin' : ''}`} />
                {isAnalyzing ? 'Analyzing...' : 'Analyze Screenplay'}
              </button>

              {/* Exports */}
              <div className="flex items-center gap-1 border-l border-slate-800 pl-3">
                <button
                  onClick={onExportJson}
                  title="Export complete structured JSON"
                  className="px-2.5 py-1.5 rounded-md text-xs font-medium bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/60"
                >
                  JSON
                </button>
                <button
                  onClick={onExportCsv}
                  title="Export industry-standard CSV breakdown"
                  className="px-2.5 py-1.5 rounded-md text-xs font-medium bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700/60"
                >
                  CSV
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
};
