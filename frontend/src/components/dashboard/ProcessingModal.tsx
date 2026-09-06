import React from 'react';
import { JobResponse } from '../../types';
import { RefreshCw, CheckCircle2, AlertCircle, FileText, Search, Cpu, Database } from 'lucide-react';

interface ProcessingModalProps {
  job: JobResponse | null;
  onClose: () => void;
}

export const ProcessingModal: React.FC<ProcessingModalProps> = ({ job, onClose }) => {
  if (!job) return null;

  const isComplete = job.status === 'COMPLETED';
  const isFailed = job.status === 'FAILED';

  const steps = [
    { label: 'Extract Screenplay Document', icon: FileText, done: true },
    { label: 'Detect Scene Sluglines & Page Numbers', icon: Search, done: true },
    { label: `AI Scene Breakdown (${job.processed_scenes} / ${job.total_scenes} scenes)`, icon: Cpu, done: isComplete, inProgress: !isComplete && !isFailed },
    { label: 'Validate Facts & Distinguish Evidence from Inferences', icon: Database, done: isComplete },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2.5">
            <div className={`p-2 rounded-xl ${isFailed ? 'bg-rose-500/10 text-rose-400' : isComplete ? 'bg-emerald-500/10 text-emerald-400' : 'bg-cyan-500/10 text-cyan-400'}`}>
              {isFailed ? <AlertCircle className="w-5 h-5" /> : isComplete ? <CheckCircle2 className="w-5 h-5" /> : <RefreshCw className="w-5 h-5 animate-spin" />}
            </div>
            <div>
              <h3 className="font-bold text-white text-base">
                {isFailed ? 'Analysis Failed' : isComplete ? 'Breakdown Complete' : 'Analyzing Screenplay'}
              </h3>
              <p className="text-xs text-slate-400">{job.current_step}</p>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-950 rounded-full h-2.5 overflow-hidden border border-slate-800 mb-5">
          <div
            className={`h-full transition-all duration-300 ${isFailed ? 'bg-rose-500' : isComplete ? 'bg-emerald-500' : 'bg-gradient-to-r from-cyan-500 to-blue-500'}`}
            style={{ width: `${job.progress_percentage}%` }}
          />
        </div>

        {/* Step List */}
        <div className="space-y-3 mb-6">
          {steps.map((s, idx) => {
            const Icon = s.icon;
            return (
              <div key={idx} className="flex items-center justify-between text-xs py-1.5 px-3 rounded-lg bg-slate-950/60 border border-slate-800/60">
                <div className="flex items-center gap-2 text-slate-300">
                  <Icon className="w-3.5 h-3.5 text-slate-400" />
                  <span>{s.label}</span>
                </div>
                {s.done ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : s.inProgress ? (
                  <RefreshCw className="w-3.5 h-3.5 text-cyan-400 animate-spin" />
                ) : (
                  <span className="w-2 h-2 rounded-full bg-slate-700" />
                )}
              </div>
            );
          })}
        </div>

        {isFailed && (
          <div className="mb-4 p-3 rounded-lg bg-rose-950/40 border border-rose-800/50 text-xs text-rose-300">
            {job.error_message}
          </div>
        )}

        <div className="flex justify-end">
          <button
            onClick={onClose}
            disabled={!isComplete && !isFailed}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition ${
              isComplete || isFailed
                ? 'bg-slate-800 hover:bg-slate-700 text-white'
                : 'bg-slate-800/50 text-slate-500 cursor-not-allowed'
            }`}
          >
            {isComplete ? 'View Breakdown' : isFailed ? 'Close' : 'Processing in background...'}
          </button>
        </div>
      </div>
    </div>
  );
};
