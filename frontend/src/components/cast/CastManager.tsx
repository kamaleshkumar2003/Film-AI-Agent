import React, { useState, useEffect } from 'react';
import { Users, Plus, Trash2, Calendar, DollarSign, Clock, ShieldCheck, AlertCircle, Sparkles } from 'lucide-react';
import { api } from '../../api/client';
import { CastMember, CastAvailability } from '../../types';

interface CastManagerProps {
  projectId: string;
}

export const CastManager: React.FC<CastManagerProps> = ({ projectId }) => {
  const [cast, setCast] = useState<CastMember[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  
  // Form State
  const [name, setName] = useState('');
  const [characterName, setCharacterName] = useState('');
  const [dailyRate, setDailyRate] = useState<number>(35000);
  const [maxHours, setMaxHours] = useState<number>(10);
  const [notes, setNotes] = useState('');

  // Selected date for availability toggle
  const [selectedMember, setSelectedMember] = useState<CastMember | null>(null);
  const [availDate, setAvailDate] = useState('');
  const [isAvailable, setIsAvailable] = useState(false);
  const [availReason, setAvailReason] = useState('');

  const loadCast = async () => {
    setIsLoading(true);
    try {
      const data = await api.getCast(projectId);
      setCast(data);
      if (data.length > 0 && !selectedMember) {
        setSelectedMember(data[0]);
      } else if (selectedMember) {
        const found = data.find((c: CastMember) => c.id === selectedMember.id);
        if (found) setSelectedMember(found);
      }
    } catch (err) {
      console.error('Failed to load cast:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCast();
  }, [projectId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      await api.createCastMember(projectId, {
        name: name.trim(),
        character_name: characterName.trim() || undefined,
        daily_rate: Number(dailyRate) || 0,
        max_hours_per_day: Number(maxHours) || 10,
        notes: notes.trim() || undefined
      });
      setName('');
      setCharacterName('');
      setNotes('');
      setIsAddModalOpen(false);
      await loadCast();
    } catch (err) {
      console.error('Failed to create cast member:', err);
    }
  };

  const handleDelete = async (castId: string) => {
    if (!confirm('Are you sure you want to remove this cast member?')) return;
    try {
      await api.deleteCastMember(projectId, castId);
      if (selectedMember?.id === castId) setSelectedMember(null);
      await loadCast();
    } catch (err) {
      console.error('Failed to delete cast member:', err);
    }
  };

  const handleSetAvailability = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMember || !availDate) return;
    try {
      await api.setCastAvailability(projectId, selectedMember.id, {
        date: availDate,
        is_available: isAvailable,
        notes: availReason || undefined
      });
      setAvailDate('');
      setAvailReason('');
      await loadCast();
    } catch (err) {
      console.error('Failed to set availability:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-cyan-400" />
            Cast & Talent Management
          </h2>
          <p className="text-xs text-slate-400">
            Define lead actors, day rates, turnaround requirements, and blackout dates enforced by the OR-Tools scheduler.
          </p>
        </div>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-md shadow-cyan-500/20 transition"
        >
          <Plus className="w-4 h-4" />
          Add Cast Member
        </button>
      </div>

      {isLoading ? (
        <div className="p-12 text-center text-slate-400 text-sm">Loading cast roster...</div>
      ) : cast.length === 0 ? (
        <div className="p-12 rounded-2xl bg-slate-900/50 border border-slate-800 text-center">
          <Users className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-200 mb-1">No Cast Members Registered</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto mb-5 leading-relaxed">
            Click "Demo Seed" in the header to populate realistic actors (Arjun, Meera, Detective Chen, Chief Vance) or add them manually.
          </p>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
          >
            Add First Cast Member
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Cast Members List */}
          <div className="lg:col-span-2 space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {cast.map((member) => {
                const isSelected = selectedMember?.id === member.id;
                const blackoutCount = member.availabilities.filter((a) => !a.is_available).length;
                return (
                  <div
                    key={member.id}
                    onClick={() => setSelectedMember(member)}
                    className={`p-4 rounded-xl border transition cursor-pointer relative ${
                      isSelected
                        ? 'bg-slate-900 border-cyan-500/50 shadow-lg shadow-cyan-500/5 ring-1 ring-cyan-500/30'
                        : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <h4 className="text-sm font-bold text-white">{member.name}</h4>
                        <span className="text-xs font-medium text-cyan-400">
                          {member.character_name ? `as ${member.character_name}` : 'Unassigned Character'}
                        </span>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(member.id);
                        }}
                        className="text-slate-500 hover:text-rose-400 transition p-1"
                        title="Delete cast member"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400 mb-3 bg-slate-950/60 p-2 rounded-lg border border-slate-800/50">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-500" />
                        <span>Max {member.max_hours_per_day}h / day</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <DollarSign className="w-3 h-3 text-slate-500" />
                        <span>₹{member.daily_rate.toLocaleString()} / day</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-[10px]">
                      <span className="text-slate-400 flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {member.availabilities.length} availability rules
                      </span>
                      {blackoutCount > 0 ? (
                        <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 font-semibold">
                          {blackoutCount} Blackout date(s)
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                          Full Availability
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Availability Details & Inspector */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 h-fit space-y-5">
            {selectedMember ? (
              <>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <ShieldCheck className="w-4 h-4 text-cyan-400" />
                    <h3 className="text-sm font-bold text-white">Availability Rules</h3>
                  </div>
                  <p className="text-xs text-slate-400">
                    Managing constraints for <span className="text-cyan-300 font-semibold">{selectedMember.name}</span>
                  </p>
                </div>

                {/* Existing Rules */}
                <div className="space-y-2">
                  <span className="text-[11px] font-semibold uppercase text-slate-400 tracking-wider">
                    Defined Dates
                  </span>
                  {selectedMember.availabilities.length === 0 ? (
                    <p className="text-xs text-slate-500 italic">No specific blackout or time constraints set. Considered available on all shooting dates.</p>
                  ) : (
                    <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                      {selectedMember.availabilities.map((av, idx) => (
                        <div
                          key={idx}
                          className={`flex items-center justify-between p-2 rounded-lg text-xs border ${
                            av.is_available
                              ? 'bg-emerald-950/30 border-emerald-800/40 text-emerald-300'
                              : 'bg-rose-950/30 border-rose-800/40 text-rose-300'
                          }`}
                        >
                          <div>
                            <span className="font-semibold">{av.date}</span>
                            {av.notes && <span className="block text-[10px] text-slate-400">{av.notes}</span>}
                          </div>
                          <span className="text-[10px] font-bold uppercase px-1.5 py-0.5 rounded bg-slate-950/60">
                            {av.is_available ? 'Available' : 'Blackout'}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Add Rule Form */}
                <form onSubmit={handleSetAvailability} className="space-y-3 pt-3 border-t border-slate-800">
                  <span className="text-[11px] font-semibold uppercase text-slate-400 tracking-wider block">
                    Add Blackout / Constraint
                  </span>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Date</label>
                    <input
                      type="date"
                      required
                      value={availDate}
                      onChange={(e) => setAvailDate(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Status</label>
                    <select
                      value={isAvailable ? 'true' : 'false'}
                      onChange={(e) => setIsAvailable(e.target.value === 'true')}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    >
                      <option value="false">Unavailable / Blackout Date</option>
                      <option value="true">Available / Preferred</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Notes / Reason</label>
                    <input
                      type="text"
                      placeholder="e.g. Prior festival commitment, travel day"
                      value={availReason}
                      onChange={(e) => setAvailReason(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-500"
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold border border-slate-700 transition"
                  >
                    Save Constraint
                  </button>
                </form>
              </>
            ) : (
              <div className="text-center text-xs text-slate-500 py-8">Select a cast member to view availability rules.</div>
            )}
          </div>
        </div>
      )}

      {/* Add Cast Member Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Plus className="w-4 h-4 text-cyan-400" />
              Add Cast Member
            </h3>
            <form onSubmit={handleCreate} className="space-y-3.5">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Actor / Talent Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Arjun Rampal"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Screenplay Character Name</label>
                <input
                  type="text"
                  placeholder="e.g. Arjun"
                  value={characterName}
                  onChange={(e) => setCharacterName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Daily Rate (₹)</label>
                  <input
                    type="number"
                    value={dailyRate}
                    onChange={(e) => setDailyRate(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Max Hours/Day</label>
                  <input
                    type="number"
                    value={maxHours}
                    onChange={(e) => setMaxHours(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Notes</label>
                <textarea
                  rows={2}
                  placeholder="Special clauses, makeup turnaround requirements..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsAddModalOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs font-medium text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-cyan-500 hover:bg-cyan-400 text-slate-950"
                >
                  Create Member
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
