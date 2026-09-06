import React, { useState } from 'react';
import { EvidenceQuote } from './EvidenceQuote';
import { PresenceBadge, StatusBadge } from '../common/Badge';
import { Plus, Trash2, LucideIcon } from 'lucide-react';

interface EntitySectionProps {
  title: string;
  icon: LucideIcon;
  count: number;
  items: any[];
  entityType: string;
  onAdd: (entityType: string, data: any) => Promise<void>;
  onDelete: (entityType: string, entityId: string) => Promise<void>;
  renderItem: (item: any) => React.ReactNode;
  newFields: { name: string; label: string; type?: string; defaultValue?: any; options?: string[] }[];
}

export const EntitySection: React.FC<EntitySectionProps> = ({
  title,
  icon: Icon,
  count,
  items,
  entityType,
  onAdd,
  onDelete,
  renderItem,
  newFields
}) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [isAdding, setIsAdding] = useState(false);

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAdding(true);
    try {
      await onAdd(entityType, formData);
      setFormData({});
      setShowAddForm(false);
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <div className="bg-slate-900/40 border border-slate-800/80 rounded-2xl p-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-slate-800 text-cyan-400">
            <Icon className="w-4 h-4" />
          </div>
          <h4 className="font-bold text-slate-100 text-xs tracking-wider uppercase">{title}</h4>
          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 text-slate-300">
            {count}
          </span>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-1 text-[11px] font-semibold text-cyan-400 hover:text-cyan-300 transition"
        >
          <Plus className="w-3 h-3" />
          {showAddForm ? 'Cancel' : 'Add'}
        </button>
      </div>

      {showAddForm && (
        <form onSubmit={handleAddSubmit} className="mb-4 p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-2.5">
          <div className="grid grid-cols-2 gap-2">
            {newFields.map((f) => (
              <div key={f.name}>
                <label className="block text-[10px] font-medium text-slate-400 mb-1">{f.label}</label>
                {f.options ? (
                  <select
                    className="w-full px-2.5 py-1 text-xs rounded-lg bg-slate-900 border border-slate-700 text-slate-200"
                    value={formData[f.name] || f.options[0]}
                    onChange={(e) => setFormData({ ...formData, [f.name]: e.target.value })}
                  >
                    {f.options.map((opt) => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                ) : (
                  <input
                    type={f.type || 'text'}
                    required
                    placeholder={f.label}
                    className="w-full px-2.5 py-1 text-xs rounded-lg bg-slate-900 border border-slate-700 text-slate-200"
                    value={formData[f.name] || ''}
                    onChange={(e) => setFormData({ ...formData, [f.name]: e.target.value })}
                  />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setShowAddForm(false)}
              className="px-2.5 py-1 text-xs rounded-lg bg-slate-800 text-slate-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isAdding}
              className="px-3 py-1 text-xs rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold"
            >
              {isAdding ? 'Adding...' : 'Save'}
            </button>
          </div>
        </form>
      )}

      {items.length === 0 ? (
        <p className="text-xs text-slate-500 italic py-2">None detected in this scene.</p>
      ) : (
        <div className="space-y-2.5">
          {items.map((item) => (
            <div
              key={item.id}
              className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 hover:border-slate-700 transition relative group"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  {renderItem(item)}
                  <EvidenceQuote
                    evidence={item.evidence}
                    inferred={item.inferred}
                    reason={item.reason}
                    confidence={item.confidence}
                  />
                </div>
                <button
                  onClick={() => onDelete(entityType, item.id)}
                  className="opacity-0 group-hover:opacity-100 p-1 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition"
                  title="Delete item"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
