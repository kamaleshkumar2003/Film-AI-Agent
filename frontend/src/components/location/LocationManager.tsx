import React, { useState, useEffect } from 'react';
import { MapPin, Plus, Trash2, Clock, DollarSign, Navigation, Calendar, ShieldCheck, Car } from 'lucide-react';
import { api } from '../../api/client';
import { ProductionLocation, TravelMatrixItem, LocationType } from '../../types';

interface LocationManagerProps {
  projectId: string;
}

export const LocationManager: React.FC<LocationManagerProps> = ({ projectId }) => {
  const [locations, setLocations] = useState<ProductionLocation[]>([]);
  const [travelMatrix, setTravelMatrix] = useState<TravelMatrixItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  // Add Location Form
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [locType, setLocType] = useState<LocationType>('EXTERIOR');
  const [dailyRental, setDailyRental] = useState<number>(25000);
  const [openingTime, setOpeningTime] = useState('06:00');
  const [closingTime, setClosingTime] = useState('20:00');
  const [setupMins, setSetupMins] = useState<number>(30);
  const [packupMins, setPackupMins] = useState<number>(30);
  const [notes, setNotes] = useState('');

  // Selected Location for Availability
  const [selectedLoc, setSelectedLoc] = useState<ProductionLocation | null>(null);
  const [availDate, setAvailDate] = useState('');
  const [isAvailable, setIsAvailable] = useState(false);
  const [availReason, setAvailReason] = useState('');

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [locsData, matrixData] = await Promise.all([
        api.getLocations(projectId),
        api.getTravelMatrix(projectId)
      ]);
      setLocations(locsData);
      setTravelMatrix(matrixData);
      if (locsData.length > 0 && !selectedLoc) {
        setSelectedLoc(locsData[0]);
      } else if (selectedLoc) {
        const found = locsData.find((l: ProductionLocation) => l.id === selectedLoc.id);
        if (found) setSelectedLoc(found);
      }
    } catch (err) {
      console.error('Failed to load locations:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [projectId]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    try {
      await api.createLocation(projectId, {
        name: name.trim(),
        address: address.trim() || undefined,
        location_type: locType,
        daily_rental_cost: Number(dailyRental) || 0,
        opening_time: openingTime,
        closing_time: closingTime,
        setup_time_minutes: Number(setupMins) || 30,
        packup_time_minutes: Number(packupMins) || 30,
        notes: notes.trim() || undefined
      });
      setName('');
      setAddress('');
      setNotes('');
      setIsAddModalOpen(false);
      await loadData();
    } catch (err) {
      console.error('Failed to create location:', err);
    }
  };

  const handleDelete = async (locId: string) => {
    if (!confirm('Are you sure you want to remove this location?')) return;
    try {
      await api.deleteLocation(projectId, locId);
      if (selectedLoc?.id === locId) setSelectedLoc(null);
      await loadData();
    } catch (err) {
      console.error('Failed to delete location:', err);
    }
  };

  const handleSetAvailability = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedLoc || !availDate) return;
    try {
      await api.setLocationAvailability(projectId, selectedLoc.id, {
        date: availDate,
        is_available: isAvailable,
        notes: availReason || undefined
      });
      setAvailDate('');
      setAvailReason('');
      await loadData();
    } catch (err) {
      console.error('Failed to set location availability:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <MapPin className="w-5 h-5 text-emerald-400" />
            Filming Locations & Travel Matrix
          </h2>
          <p className="text-xs text-slate-400">
            Define shooting stages, permits, operating hours, day rates, and transit times for Company Move optimization.
          </p>
        </div>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-600/20 transition"
        >
          <Plus className="w-4 h-4" />
          Add Location
        </button>
      </div>

      {isLoading ? (
        <div className="p-12 text-center text-slate-400 text-sm">Loading locations & travel matrix...</div>
      ) : locations.length === 0 ? (
        <div className="p-12 rounded-2xl bg-slate-900/50 border border-slate-800 text-center">
          <MapPin className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-200 mb-1">No Locations Registered</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto mb-5 leading-relaxed">
            Click "Demo Seed" in the top bar to automatically load the 4 filming locations and travel matrix, or add locations manually.
          </p>
          <button
            onClick={() => setIsAddModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
          >
            Add First Location
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Location Cards */}
          <div className="lg:col-span-2 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
              {locations.map((loc) => {
                const isSelected = selectedLoc?.id === loc.id;
                const blackoutCount = loc.availabilities.filter((a) => !a.is_available).length;
                return (
                  <div
                    key={loc.id}
                    onClick={() => setSelectedLoc(loc)}
                    className={`p-4 rounded-xl border transition cursor-pointer relative ${
                      isSelected
                        ? 'bg-slate-900 border-emerald-500/50 shadow-lg shadow-emerald-500/5 ring-1 ring-emerald-500/30'
                        : 'bg-slate-900/60 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div>
                        <div className="flex items-center gap-1.5 mb-1">
                          <span className={`px-2 py-0.5 text-[9px] font-bold rounded ${
                            loc.location_type === 'EXTERIOR'
                              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                              : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                          }`}>
                            {loc.location_type}
                          </span>
                          <span className="text-[11px] text-slate-400">
                            {loc.opening_time} - {loc.closing_time}
                          </span>
                        </div>
                        <h4 className="text-sm font-bold text-white">{loc.name}</h4>
                        {loc.address && (
                          <p className="text-xs text-slate-400 truncate max-w-[240px]">{loc.address}</p>
                        )}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(loc.id);
                        }}
                        className="text-slate-500 hover:text-rose-400 transition p-1"
                        title="Delete location"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400 mb-3 bg-slate-950/60 p-2 rounded-lg border border-slate-800/50">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3 text-slate-500" />
                        <span>Buffer: {loc.setup_time_minutes}m setup</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <DollarSign className="w-3 h-3 text-slate-500" />
                        <span>₹{loc.daily_rental_cost.toLocaleString()} / day</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-[10px]">
                      <span className="text-slate-400 flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {loc.availabilities.length} availability rules
                      </span>
                      {blackoutCount > 0 ? (
                        <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20 font-semibold">
                          {blackoutCount} Closed date(s)
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                          Open All Dates
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Travel Matrix Section */}
            {travelMatrix.length > 0 && (
              <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                    <Car className="w-4 h-4 text-emerald-400" />
                    Company Move Travel Times (Travel Matrix)
                  </h4>
                  <span className="text-[10px] text-slate-400">
                    Used by CP-SAT to calculate transit buffers & penalties
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                  {travelMatrix.map((tm, idx) => {
                    const fromLoc = locations.find((l) => l.id === tm.from_location_id);
                    const toLoc = locations.find((l) => l.id === tm.to_location_id);
                    return (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-2 rounded-lg bg-slate-950/60 border border-slate-800/60 text-slate-300"
                      >
                        <div className="truncate pr-2">
                          <span className="text-slate-200 font-semibold">{fromLoc?.name || 'Location A'}</span>
                          <span className="text-slate-500 mx-1.5">➔</span>
                          <span className="text-slate-200 font-semibold">{toLoc?.name || 'Location B'}</span>
                        </div>
                        <div className="text-right shrink-0">
                          <span className="text-emerald-400 font-bold">{tm.travel_time_minutes} mins</span>
                          {tm.distance_km && (
                            <span className="block text-[10px] text-slate-500">{tm.distance_km} km</span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Location Inspector & Blackouts */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 h-fit space-y-5">
            {selectedLoc ? (
              <>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    <h3 className="text-sm font-bold text-white">Location Permit Dates</h3>
                  </div>
                  <p className="text-xs text-slate-400">
                    Managing availability for <span className="text-emerald-300 font-semibold">{selectedLoc.name}</span>
                  </p>
                </div>

                {/* Existing Rules */}
                <div className="space-y-2">
                  <span className="text-[11px] font-semibold uppercase text-slate-400 tracking-wider">
                    Permit / Blackout Exceptions
                  </span>
                  {selectedLoc.availabilities.length === 0 ? (
                    <p className="text-xs text-slate-500 italic">Available and open for shooting on all candidate dates.</p>
                  ) : (
                    <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                      {selectedLoc.availabilities.map((av, idx) => (
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
                            {av.is_available ? 'Permitted' : 'Closed'}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Add Availability Form */}
                <form onSubmit={handleSetAvailability} className="space-y-3 pt-3 border-t border-slate-800">
                  <span className="text-[11px] font-semibold uppercase text-slate-400 tracking-wider block">
                    Add Permit Restriction
                  </span>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Date</label>
                    <input
                      type="date"
                      required
                      value={availDate}
                      onChange={(e) => setAvailDate(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Permit Status</label>
                    <select
                      value={isAvailable ? 'true' : 'false'}
                      onChange={(e) => setIsAvailable(e.target.value === 'true')}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500"
                    >
                      <option value="false">Closed / No Permit Granted</option>
                      <option value="true">Permit Approved / Available</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-[11px] text-slate-400 block mb-1">Reason / Condition</label>
                    <input
                      type="text"
                      placeholder="e.g. Public event closure, maintenance"
                      value={availReason}
                      onChange={(e) => setAvailReason(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500"
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold border border-slate-700 transition"
                  >
                    Save Restriction
                  </button>
                </form>
              </>
            ) : (
              <div className="text-center text-xs text-slate-500 py-8">Select a location to manage availability.</div>
            )}
          </div>
        </div>
      )}

      {/* Add Location Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Plus className="w-4 h-4 text-emerald-400" />
              Add Filming Location
            </h3>
            <form onSubmit={handleCreate} className="space-y-3.5">
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Location Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Chennai Marina Beach Pier 42"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-slate-300 block mb-1">Address / Geographical Notes</label>
                <input
                  type="text"
                  placeholder="e.g. Marina Beach Road, Chennai"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Location Type</label>
                  <select
                    value={locType}
                    onChange={(e) => setLocType(e.target.value as LocationType)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="EXTERIOR">EXTERIOR (Sun & Weather sensitive)</option>
                    <option value="INTERIOR">INTERIOR (Controlled sound stage)</option>
                    <option value="INT_EXT">INT_EXT (Compound / Hybrid)</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Daily Rental Cost (₹)</label>
                  <input
                    type="number"
                    value={dailyRental}
                    onChange={(e) => setDailyRental(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Permit Opening Time</label>
                  <input
                    type="time"
                    value={openingTime}
                    onChange={(e) => setOpeningTime(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Permit Closing Time</label>
                  <input
                    type="time"
                    value={closingTime}
                    onChange={(e) => setClosingTime(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
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
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white"
                >
                  Create Location
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
