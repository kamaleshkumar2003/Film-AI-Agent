import React from 'react';
import { Quote, AlertCircle } from 'lucide-react';
import { EvidenceTag } from '../common/Badge';

interface EvidenceQuoteProps {
  evidence?: string;
  inferred?: boolean;
  reason?: string;
  confidence?: number;
}

export const EvidenceQuote: React.FC<EvidenceQuoteProps> = ({ evidence, inferred, reason, confidence }) => {
  return (
    <div className="mt-2 text-[11px] rounded-lg p-2.5 bg-slate-950/70 border border-slate-800/80">
      <div className="flex items-center justify-between mb-1">
        <EvidenceTag inferred={inferred} confidence={confidence} />
        {confidence && !inferred && (
          <span className="text-[10px] text-slate-500 font-mono">
            {Math.round(confidence * 100)}% match
          </span>
        )}
      </div>

      {evidence && (
        <div className="flex items-start gap-1.5 text-slate-300 italic font-mono text-[11px] leading-relaxed">
          <Quote className="w-3 h-3 text-cyan-400 shrink-0 mt-0.5" />
          <span>"{evidence}"</span>
        </div>
      )}

      {inferred && reason && (
        <div className="flex items-start gap-1.5 text-purple-300 mt-1.5 text-[10px] leading-tight">
          <AlertCircle className="w-3 h-3 text-purple-400 shrink-0 mt-0.5" />
          <span><strong>Inference Rationale:</strong> {reason}</span>
        </div>
      )}
    </div>
  );
};
