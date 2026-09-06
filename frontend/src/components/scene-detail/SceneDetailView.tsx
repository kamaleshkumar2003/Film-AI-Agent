import React, { useState, useEffect } from 'react';
import { SceneDetail, LocationType, DayNight, WeatherSensitivity } from '../../types';
import { StatusBadge, WeatherBadge, PresenceBadge } from '../common/Badge';
import { EntitySection } from './EntitySection';
import {
  X, CheckCircle, Save, ArrowLeft, ArrowRight,
  Users, Package, Car, Shirt, Sparkles, Wrench, Shield, Zap,
  Clock, Sun, CloudRain, FileText, ChevronDown, ChevronUp
} from 'lucide-react';

interface SceneDetailViewProps {
  scene: SceneDetail;
  onClose: () => void;
  onUpdate: (updated: Partial<SceneDetail>) => Promise<void>;
  onConfirm: () => Promise<void>;
  onAddEntity: (entityType: string, data: any) => Promise<void>;
  onDeleteEntity: (entityType: string, entityId: string) => Promise<void>;
  onPrevScene?: () => void;
  onNextScene?: () => void;
  hasPrev?: boolean;
  hasNext?: boolean;
}

export const SceneDetailView: React.FC<SceneDetailViewProps> = ({
  scene,
  onClose,
  onUpdate,
  onConfirm,
  onAddEntity,
  onDeleteEntity,
  onPrevScene,
  onNextScene,
  hasPrev,
  hasNext,
}) => {
  const [heading, setHeading] = useState(scene.scene_heading);
  const [locationName, setLocationName] = useState(scene.location_name);
  const [intExt, setIntExt] = useState<LocationType>(scene.int_ext);
  const [dayNight, setDayNight] = useState<DayNight>(scene.day_night);
  const [scriptTime, setScriptTime] = useState(scene.script_time);
  const [weatherSens, setWeatherSens] = useState<WeatherSensitivity>(scene.weather_sensitivity);
  const [duration, setDuration] = useState(scene.estimated_duration_minutes);
  const [productionNotes, setProductionNotes] = useState(scene.production_notes || '');
  const [continuityNotes, setContinuityNotes] = useState(scene.continuity_notes || '');
  const [specialReqs, setSpecialReqs] = useState(scene.special_requirements || '');
  const [showScriptDrawer, setShowScriptDrawer] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    setHeading(scene.scene_heading);
    setLocationName(scene.location_name);
    setIntExt(scene.int_ext);
    setDayNight(scene.day_night);
    setScriptTime(scene.script_time);
    setWeatherSens(scene.weather_sensitivity);
    setDuration(scene.estimated_duration_minutes);
    setProductionNotes(scene.production_notes || '');
    setContinuityNotes(scene.continuity_notes || '');
    setSpecialReqs(scene.special_requirements || '');
  }, [scene]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onUpdate({
        scene_heading: heading,
        location_name: locationName,
        int_ext: intExt,
        day_night: dayNight,
        script_time: scriptTime,
        weather_sensitivity: weatherSens,
        estimated_duration_minutes: Number(duration),
        production_notes: productionNotes,
        continuity_notes: continuityNotes,
        special_requirements: specialReqs,
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-150">
      {/* Top Banner Navigation */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 backdrop-blur shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition"
              title="Return to Table"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-cyan-400 font-bold text-sm">{scene.scene_code}</span>
                <span className="text-slate-500">•</span>
                <span className="text-xs text-slate-400 font-mono">
                  Pages {scene.source_page_start} - {scene.source_page_end}
                </span>
                <StatusBadge status={scene.status} />
              </div>
              <h2 className="text-xl font-extrabold text-white tracking-tight mt-0.5">
                {scene.scene_heading}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {hasPrev && (
              <button
                onClick={onPrevScene}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-medium"
              >
                ← Prev Scene
              </button>
            )}
            {hasNext && (
              <button
                onClick={onNextScene}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs text-slate-300 font-medium"
              >
                Next Scene →
              </button>
            )}

            <button
              onClick={onConfirm}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-md shadow-emerald-600/20 transition"
            >
              <CheckCircle className="w-3.5 h-3.5" />
              Confirm Breakdown
            </button>

            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-semibold shadow-md shadow-cyan-500/20 transition"
            >
              <Save className="w-3.5 h-3.5" />
              {isSaving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>

      {/* Screenplay Drawer Toggle */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur">
        <button
          onClick={() => setShowScriptDrawer(!showScriptDrawer)}
          className="w-full px-5 py-3 flex items-center justify-between hover:bg-slate-800/40 text-xs font-semibold text-slate-300"
        >
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-cyan-400" />
            <span>Screenplay Source Text ({scene.raw_text.split('\n').length} lines)</span>
          </div>
          {showScriptDrawer ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showScriptDrawer && (
          <div className="p-5 border-t border-slate-800 bg-slate-950/80">
            <pre className="script-font text-xs text-slate-300 whitespace-pre-wrap leading-relaxed max-h-72 overflow-y-auto">
              {scene.raw_text}
            </pre>
          </div>
        )}
      </div>

      {/* Metadata Form Panel */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur">
        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
          Scene Production Parameters
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div>
            <label className="block text-slate-400 font-medium mb-1">Heading</label>
            <input
              type="text"
              className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-mono"
              value={heading}
              onChange={(e) => setHeading(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1">Location Name</label>
            <input
              type="text"
              className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-medium"
              value={locationName}
              onChange={(e) => setLocationName(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1">Interior / Exterior</label>
            <select
              className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-white"
              value={intExt}
              onChange={(e) => setIntExt(e.target.value as LocationType)}
            >
              <option value="INTERIOR">INTERIOR (INT)</option>
              <option value="EXTERIOR">EXTERIOR (EXT)</option>
              <option value="INT_EXT">INT / EXT</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1">Time of Day</label>
            <select
              className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-white"
              value={dayNight}
              onChange={(e) => setDayNight(e.target.value as DayNight)}
            >
              <option value="DAY">DAY</option>
              <option value="NIGHT">NIGHT</option>
              <option value="DUSK">DUSK / SUNSET</option>
              <option value="DAWN">DAWN / SUNRISE</option>
              <option value="MORNING">MORNING</option>
              <option value="EVENING">EVENING</option>
              <option value="CONTINUOUS">CONTINUOUS</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1">Weather Sensitivity</label>
            <select
              className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-semibold"
              value={weatherSens}
              onChange={(e) => setWeatherSens(e.target.value as WeatherSensitivity)}
            >
              <option value="LOW">LOW (Controlled interior)</option>
              <option value="MEDIUM">MEDIUM (Standard daylight)</option>
              <option value="HIGH">HIGH (Magic hour / Sunset)</option>
              <option value="CRITICAL">CRITICAL (Rain / Storm)</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-400 font-medium mb-1">Est. Shooting Duration</label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="15"
                step="15"
                className="w-full px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-800 text-white font-mono"
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
              />
              <span className="text-slate-400 font-mono text-xs">mins</span>
            </div>
          </div>

          <div className="sm:col-span-2">
            <label className="block text-slate-400 font-medium mb-1">Weather Rationale</label>
            <p className="px-3 py-1.5 rounded-lg bg-slate-950/60 border border-slate-800 text-slate-300 text-xs italic">
              {scene.weather_reason || 'Standard weather parameters.'}
            </p>
          </div>
        </div>
      </div>

      {/* Production Breakdown Entities Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {/* Cast */}
        <EntitySection
          title="Cast & Characters"
          icon={Users}
          count={scene.characters.length}
          items={scene.characters}
          entityType="character"
          onAdd={onAddEntity}
          onDelete={onDeleteEntity}
          newFields={[
            { name: 'name', label: 'Character Name' },
            { name: 'presence_type', label: 'Presence', options: ['APPEARS', 'VOICE_ONLY', 'MENTIONED_ONLY', 'BACKGROUND', 'CROWD'] }
          ]}
          renderItem={(c) => (
            <div>
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-100 text-sm">{c.name}</span>
                <PresenceBadge presence={c.presence_type} />
              </div>
              {c.description && <p className="text-xs text-slate-400 mt-0.5">{c.description}</p>}
            </div>
          )}
        />

        {/* Props */}
        <EntitySection
          title="Props"
          icon={Package}
          count={scene.props.length}
          items={scene.props}
          entityType="prop"
          onAdd={onAddEntity}
          onDelete={onDeleteEntity}
          newFields={[
            { name: 'name', label: 'Prop Name' },
            { name: 'quantity', label: 'Quantity', type: 'number', defaultValue: 1 }
          ]}
          renderItem={(p) => (
            <div className="flex items-center justify-between">
              <span className="font-bold text-slate-100 text-sm">{p.name}</span>
              <span className="font-mono text-cyan-400 text-xs font-semibold">Qty: {p.quantity}</span>
            </div>
          )}
        />

        {/* Vehicles */}
        <EntitySection
          title="Vehicles"
          icon={Car}
          count={scene.vehicles.length}
          items={scene.vehicles}
          entityType="vehicle"
          onAdd={onAddEntity}
          onDelete={onDeleteEntity}
          newFields={[
            { name: 'name', label: 'Vehicle Name' },
            { name: 'state', label: 'State', options: ['ON_SCREEN', 'MOVING', 'PARKED', 'DRIVEN', 'BACKGROUND'] }
          ]}
          renderItem={(v) => (
            <div className="flex items-center justify-between">
              <div>
                <span className="font-bold text-slate-100 text-sm">{v.name}</span>
                <p className="text-[10px] text-slate-400 font-mono">{v.vehicle_type}</p>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-500/10 text-rose-300 border border-rose-500/20">
                {v.state}
              </span>
            </div>
          )}
        />

        {/* Costume */}
        <EntitySection
          title="Costumes"
          icon={Shirt}
          count={scene.costumes.length}
          items={scene.costumes}
          entityType="costume"
          onAdd={onAddEntity}
          onDelete={onDeleteEntity}
          newFields={[
            { name: 'character_name', label: 'Character' },
            { name: 'description', label: 'Costume Requirement' }
          ]}
          renderItem={(cost) => (
            <div>
              <span className="font-semibold text-slate-200 text-xs">{cost.description}</span>
              {cost.character_name && (
                <p className="text-[10px] text-cyan-400 font-medium">For: {cost.character_name}</p>
              )}
            </div>
          )}
        />

        {/* Makeup & Hair */}
        <EntitySection
          title="Makeup & Hair"
          icon={Sparkles}
          count={scene.makeup.length}
          items={scene.makeup}
          entityType="makeup"
          onAdd={onAddEntity}
          onDelete={onDeleteEntity}
          newFields={[
            { name: 'character_name', label: 'Character' },
            { name: 'description', label: 'Makeup Effect' }
          ]}
          renderItem={(mk) => (
            <div>
              <span className="font-semibold text-slate-200 text-xs">{mk.description}</span>
              {mk.character_name && (
                <p className="text-[10px] text-cyan-400 font-medium">For: {mk.character_name}</p>
              )}
            </div>
          )}
        />

        {/* Special Crew */}
        <EntitySection
          title="Special Crew"
          icon={Shield}
          count={scene.crew_requirements.length}
          items={scene.crew_requirements}
          entityType="crew"
          onAdd={onAddEntity}
          onDelete={onDeleteEntity}
          newFields={[
            { name: 'role', label: 'Special Role (e.g. Armorer, Stunt Coord)' }
          ]}
          renderItem={(cr) => (
            <span className="font-bold text-amber-300 text-xs">{cr.role}</span>
          )}
        />

        {/* Special Equipment */}
        <EntitySection
          title="Special Equipment"
          icon={Wrench}
          count={scene.equipment.length}
          items={scene.equipment}
          entityType="equipment"
          onAdd={onAddEntity}
          onDelete={onDeleteEntity}
          newFields={[
            { name: 'item_name', label: 'Equipment Name' }
          ]}
          renderItem={(eq) => (
            <span className="font-bold text-blue-300 text-xs">{eq.item_name}</span>
          )}
        />

        {/* VFX & Stunts */}
        <EntitySection
          title="VFX & Stunts"
          icon={Zap}
          count={scene.vfx_stunts.length}
          items={scene.vfx_stunts}
          entityType="vfx_stunt"
          onAdd={onAddEntity}
          onDelete={onDeleteEntity}
          newFields={[
            { name: 'category', label: 'Category', options: ['VFX', 'SFX', 'STUNT', 'ANIMAL'] },
            { name: 'description', label: 'Description' }
          ]}
          renderItem={(vx) => (
            <div>
              <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-purple-900/50 text-purple-300 border border-purple-700/50 mr-2">
                {vx.category}
              </span>
              <span className="font-medium text-slate-200 text-xs">{vx.description}</span>
            </div>
          )}
        />
      </div>

      {/* Production Notes & Continuity */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            Production Notes
          </h4>
          <textarea
            rows={3}
            className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-500"
            placeholder="Director / Producer production notes..."
            value={productionNotes}
            onChange={(e) => setProductionNotes(e.target.value)}
          />
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 backdrop-blur">
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
            Continuity Notes
          </h4>
          <textarea
            rows={3}
            className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-xs focus:outline-none focus:border-cyan-500"
            placeholder="Wardrobe / prop / injury continuity notes..."
            value={continuityNotes}
            onChange={(e) => setContinuityNotes(e.target.value)}
          />
        </div>
      </div>
    </div>
  );
};
