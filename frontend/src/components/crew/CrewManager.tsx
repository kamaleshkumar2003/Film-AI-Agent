import React, { useState, useEffect } from 'react';
import { HardHat, Plus, Trash2, Calendar, DollarSign, Clock, ShieldCheck } from 'lucide-react';
import { api } from '../../api/client';
import { CrewMember } from '../../types';

interface CrewManagerProps {
  projectId: string;
}

export const CrewManager: React.FC<CrewManagerProps> = ({ projectId }) => {
  const [crew, setCrew] = useState<CrewMember[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // Form
  const [name, setName] = useState('');
  const [role, setRole] = useState('DOP');
  const [dailyRate, setDailyRate] = useState<number>(30000);
  const [maxHours, setMaxHours] = useState<number>(12);
  const [notes, setNotes] = useState('');

  // Selected Crew Member
  const [selectedMember, setSelectedMember] = useState<CrewMember | null>(null);
  const [availDate, setAvailDate] = useState('');
  const [isAvailable, setIsAvailable] = useState(false);
  const [availReason, setAvailReason] = useState('');

  const loadCrew = async () => {
    setIsLoading(true);
    try {
      const data = await api.getCrew(projectId);
      setCrew(data);
      if (data.length > 0 && !selectedMember) {
        setSelectedMember(data[0]);
      } else if (selectedMember) {
        const found = data.find((c: CrewMember) => c.id === selectedMember.id);
        if (found) setSelectedMember(found);
      }
    } catch (err) {
      console.error('Failed to load crew:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCrew();
  }, [projectId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      await api.createCrewMember(projectId, {
        name: name.trim(),
        role: role.trim(),
        daily_rate: Number(dailyRate) || 0,
        max_hours_per_day: Number(maxHours) || 12,
        notes: notes.trim() || undefined
      });
      setName('');
      setNotes('');
      setIsAddModalOpen(false);
      await loadCrew();
    } catch (err) {
      console.error('Failed to create crew member:', err);
    }
  };

  const handleDelete = async (crewId: string) => {
    if (!confirm('Are you sure you want to remove this crew member?')) return;
    try {
      await api.deleteCrewMember(projectId, crewId);
      if (selectedMember?.id === crewId) setSelectedMember(null);
      await loadCrew();
    } catch (err) {
      console.error('Failed to delete crew member:', err);
    }
  };

  const handleSetAvailability = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMember || !availDate) return;
    try {
      await api.setCrewAvailability(projectId, selectedMember.id, {
        date: availDate,
        is_available: isAvailable,
        notes: availReason || undefined
      });
      setAvailDate('');
      setAvailReason('');
      await loadCrew();
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
            <HardHat className="w-5 h-5 text-indigo-400" />
            Crew & Department Management
          </h2>
          <p className="text-xs text-slate-400">
            Track key department heads, technical leads (DOP, Stunt Coordinator, Armorer, Sound), day rates, and union turnaround limits.
          </p>
        </div>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/20 transition"
        >
          <Plus className="w-4 h-4" />
          Add Crew Member
        </button>
      </div>

      {isLoading ? (
        <div className="p-12 text-center text-slate-400 text-sm">Loading crew roster...</div>
      ) : crew.length === 0 ? (
        <div className="p-12 rounded-2xl bg-slate-900/50 border border-slate-800 text-center">
          <HardHat className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-200 mb-1">No Crew Members Registered</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto mb-5 leading-relaxed">
            Click "Demo Seed" in the header to populate key technicians (Santosh Sivan - DOP, Peter Hein - Stunt Coordinator, Jack Miller - Armorer) or add them manually.
          </p>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
          >
            Add First Crew Member
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Crew List */}
          <div className="lg:col-span-2 space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {crew.map((member) => {
                const isSelected = selectedMember?.id === member.id;
                const blackoutCount = member.availabilities.filter((a) => !a.is_available).length;
                return (
                  <div
                    key={member.id}
                    onClick={() => setSelectedMember(member)}
                    className={`p-4 rounded-xl border transition cursor-pointer relative ${
                      isSelected
                        ? 'bg-slate-900 border-indigo-500/50 shadow-lg shadow-indigo-500/5 ring-1 ring-indigo-500/30'
                        : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <h4 className="text-sm font-bold text-white">{member.name}</h4>
                        <span className="text-xs font-semibold text-indigo-400">
                          {member.role}
                        </span>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(member.id);
                        }}
                        className="text-slate-500 hover:text-rose-400 transition p-1"
                        title="Delete crew member"
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

          {/* Availability Inspector */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 h-fit space-y-5">
            {selectedMember ? (
              <>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <ShieldCheck className="w-4 h-4 text-indigo-400" />
                    <h3 className="text-sm font-bold text-white">Crew Availability</h3>
                  </div>
                  <p className="text-xs text-slate-400">
                    Managing constraints for <span className="text-indigo-300 font-semibold">{selectedMember.name}</span> ({selectedMember.role})
                  </p>
                </div>

                {/* Existing Rules */}
                <div className="space-y-2">
                  <span className="text-[11px] font-semibold uppercase text-slate-400 tracking-wider">
                    Defined Dates
                  </span>
                  {selectedMember.availabilities.length === 0 ? (
                    <p className="text-xs text-slate-500 italic">No specific blackout rules set. Available for all scheduled shoot days.</p>
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
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Status</label>
                    <select
                      value={isAvailable ? 'true' : 'false'}
                      onChange={(e) => setIsAvailable(e.target.value === 'true')}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                    >
                      <option value="false">Unavailable / Blackout</option>
                      <option value="true">Available</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Notes</label>
                    <input
                      type="text"
                      placeholder="e.g. Gear maintenance day"
                      value={availReason}
                      onChange={(e) => setAvailReason(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
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
              <div className="text-center text-xs text-slate-500 py-8">Select a crew member to view availability rules.</div>
            )}
          </div>
        </div>
      )}

      {/* Add Crew Member Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Plus className="w-4 h-4 text-indigo-400" />
              Add Crew Member
            </h3>
            <form onSubmit={handleCreate} className="space-y-3.5">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Full Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Santosh Sivan"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Department / Role *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Director of Photography (DOP), Stunt Coordinator, Sound Engineer"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Daily Rate (₹)</label>
                  <input
                    type="number"
                    value={dailyRate}
                    onChange={(e) => setDailyRate(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Max Hours/Day</label>
                  <input
                    type="number"
                    value={maxHours}
                    onChange={(e) => setMaxHours(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Notes</label>
                <textarea
                  rows={2}
                  placeholder="Equipment packages, special certifications..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
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
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white"
                >
                  Create Crew Member
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
