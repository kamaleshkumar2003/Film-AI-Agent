import React from 'react';
import { ProvenanceStatus, WeatherSensitivity, CharacterPresence } from '../../types';
import { Bot, UserCheck, ShieldAlert, Sun, CloudRain, Clock, AlertTriangle } from 'lucide-react';

export const StatusBadge: React.FC<{ status: ProvenanceStatus }> = ({ status }) => {
  if (status === 'HUMAN_CONFIRMED') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
        <UserCheck className="w-3 h-3 text-emerald-400" />
        Confirmed
      </span>
    );
  }
  if (status === 'HUMAN_EDITED') {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
        <UserCheck className="w-3 h-3 text-amber-400" />
        Human Edited
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
      <Bot className="w-3 h-3 text-cyan-400" />
      AI Generated
    </span>
  );
};

export const WeatherBadge: React.FC<{ sensitivity: WeatherSensitivity }> = ({ sensitivity }) => {
  const map = {
    LOW: { color: 'bg-slate-800 text-slate-300 border-slate-700', icon: Sun },
    MEDIUM: { color: 'bg-blue-900/30 text-blue-300 border-blue-700/50', icon: Sun },
    HIGH: { color: 'bg-amber-900/30 text-amber-300 border-amber-700/50', icon: AlertTriangle },
    CRITICAL: { color: 'bg-rose-900/40 text-rose-300 border-rose-600/60 animate-pulse', icon: CloudRain }
  };
  const cfg = map[sensitivity] || map.LOW;
  const Icon = cfg.icon;

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium border ${cfg.color}`}>
      <Icon className="w-3 h-3" />
      {sensitivity}
    </span>
  );
};

export const PresenceBadge: React.FC<{ presence: CharacterPresence }> = ({ presence }) => {
  const styles: Record<CharacterPresence, string> = {
    APPEARS: 'bg-emerald-950/40 text-emerald-300 border-emerald-800/40',
    VOICE_ONLY: 'bg-indigo-950/40 text-indigo-300 border-indigo-800/40',
    MENTIONED_ONLY: 'bg-slate-900 text-slate-400 border-slate-800',
    BACKGROUND: 'bg-cyan-950/40 text-cyan-300 border-cyan-800/40',
    CROWD: 'bg-purple-950/40 text-purple-300 border-purple-800/40',
    FLASHBACK: 'bg-amber-950/40 text-amber-300 border-amber-800/40',
    DREAM: 'bg-pink-950/40 text-pink-300 border-pink-800/40',
  };

  return (
    <span className={`px-2 py-0.5 rounded text-[11px] font-medium border ${styles[presence] || styles.APPEARS}`}>
      {presence.replace('_', ' ')}
    </span>
  );
};

export const EvidenceTag: React.FC<{ inferred?: boolean; confidence?: number }> = ({ inferred, confidence }) => {
  if (inferred) {
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-purple-500/10 text-purple-300 border border-purple-500/30" title="Inferred production requirement based on context">
        ⚡ Inferred
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/10 text-emerald-300 border border-emerald-500/20" title={`Explicit in screenplay (${Math.round((confidence || 0.9) * 100)}% confidence)`}>
      ✓ Explicit ({Math.round((confidence || 0.9) * 100)}%)
    </span>
  );
};
