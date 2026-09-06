import React, { useState } from 'react';
import { X, Clapperboard } from 'lucide-react';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (data: {
    name: string;
    production_type: string;
    description?: string;
    director?: string;
    production_company?: string;
  }) => Promise<void>;
}

export const CreateProjectModal: React.FC<CreateProjectModalProps> = ({ isOpen, onClose, onCreate }) => {
  const [name, setName] = useState('');
  const [productionType, setProductionType] = useState('Feature Film');
  const [description, setDescription] = useState('');
  const [director, setDirector] = useState('');
  const [productionCompany, setProductionCompany] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setIsSubmitting(true);
    try {
      await onCreate({
        name,
        production_type: productionType,
        description: description || undefined,
        director: director || undefined,
        production_company: productionCompany || undefined,
      });
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl animate-in fade-in zoom-in-95">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400">
              <Clapperboard className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-base">Create New Film Production</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block text-slate-300 font-medium mb-1.5">Project Name *</label>
            <input
              type="text"
              required
              placeholder="e.g. Project X, Neon Harbor"
              className="w-full px-3.5 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-300 font-medium mb-1.5">Production Type</label>
              <select
                className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 focus:outline-none focus:border-cyan-500"
                value={productionType}
                onChange={(e) => setProductionType(e.target.value)}
              >
                <option value="Feature Film">Feature Film</option>
                <option value="Short Film">Short Film</option>
                <option value="Television Series">Television Series</option>
                <option value="Commercial">Commercial</option>
                <option value="Documentary">Documentary</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1.5">Director</label>
              <input
                type="text"
                placeholder="e.g. Christopher Nolan"
                className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                value={director}
                onChange={(e) => setDirector(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-300 font-medium mb-1.5">Production Company</label>
            <input
              type="text"
              placeholder="e.g. Syncopy / Warner Bros."
              className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              value={productionCompany}
              onChange={(e) => setProductionCompany(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-slate-300 font-medium mb-1.5">Description</label>
            <textarea
              rows={3}
              placeholder="Brief project synopsis or production notes..."
              className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <div className="flex justify-end gap-2.5 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !name.trim()}
              className="px-5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold transition"
            >
              {isSubmitting ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
