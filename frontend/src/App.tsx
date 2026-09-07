import React, { useState, useEffect, useRef } from 'react';
import { api } from './api/client';
import { Project, SceneSummary, SceneDetail, JobResponse } from './types';
import { Header, NavTab } from './components/common/Header';
import { ProjectStatsBar } from './components/dashboard/ProjectStatsBar';
import { SceneTable } from './components/dashboard/SceneTable';
import { SceneDetailView } from './components/scene-detail/SceneDetailView';
import { CastManager } from './components/cast/CastManager';
import { CrewManager } from './components/crew/CrewManager';
import { LocationManager } from './components/location/LocationManager';
import { ScheduleDashboard } from './components/schedule/ScheduleDashboard';
import { CreateProjectModal } from './components/project/CreateProjectModal';
import { UploadScreenplayModal } from './components/project/UploadScreenplayModal';
import { ProcessingModal } from './components/dashboard/ProcessingModal';
import { Film, UploadCloud } from 'lucide-react';

export function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [scenes, setScenes] = useState<SceneSummary[]>([]);
  const [selectedSceneId, setSelectedSceneId] = useState<string | null>(null);
  const [selectedSceneDetail, setSelectedSceneDetail] = useState<SceneDetail | null>(null);

  // V2 Navigation Tab State
  const [activeTab, setActiveTab] = useState<NavTab>('breakdown');
  const [isSeedingDemo, setIsSeedingDemo] = useState(false);

  // Modals & Jobs
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [currentJob, setCurrentJob] = useState<JobResponse | null>(null);
  const [isProcessingOpen, setIsProcessingOpen] = useState(false);

  // Poll job status
  const jobPollRef = useRef<any>(null);

  // Fetch projects on load
  const loadProjects = async () => {
    try {
      const data = await api.getProjects();
      setProjects(data);
      if (data.length > 0 && !currentProject) {
        setCurrentProject(data[0]);
      }
    } catch (err) {
      console.error("Failed to load projects", err);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  // Fetch scenes when current project changes
  const loadScenes = async (projectId: string) => {
    try {
      const data = await api.getScenes(projectId);
      setScenes(data);
      // Also refresh project stats
      const proj = await api.getProject(projectId);
      setCurrentProject(proj);
    } catch (err) {
      console.error("Failed to load scenes", err);
    }
  };

  useEffect(() => {
    if (currentProject) {
      loadScenes(currentProject.id);
      setSelectedSceneId(null);
      setSelectedSceneDetail(null);
    }
  }, [currentProject?.id]);

  // Fetch Scene Detail when scene selected
  useEffect(() => {
    if (currentProject && selectedSceneId) {
      api.getSceneDetail(currentProject.id, selectedSceneId).then((detail) => {
        setSelectedSceneDetail(detail);
      }).catch(err => console.error("Failed to load scene detail", err));
    } else {
      setSelectedSceneDetail(null);
    }
  }, [selectedSceneId, currentProject?.id]);

  // Job Polling
  useEffect(() => {
    if (currentJob && (currentJob.status === 'PENDING' || currentJob.status === 'ANALYZING' || currentJob.status === 'EXTRACTING')) {
      jobPollRef.current = setInterval(async () => {
        try {
          const updated = await api.getJobStatus(currentJob.id);
          setCurrentJob(updated);
          if (updated.status === 'COMPLETED' || updated.status === 'FAILED') {
            clearInterval(jobPollRef.current);
            if (currentProject) {
              loadScenes(currentProject.id);
            }
          }
        } catch (err) {
          console.error("Job polling error", err);
          clearInterval(jobPollRef.current);
        }
      }, 1500);
    }
    return () => {
      if (jobPollRef.current) clearInterval(jobPollRef.current);
    };
  }, [currentJob?.id, currentJob?.status]);

  // Actions
  const handleCreateProject = async (data: any) => {
    const newProj = await api.createProject(data);
    setProjects([newProj, ...projects]);
    setCurrentProject(newProj);
  };

  const handleUploadScreenplay = async (file: File) => {
    if (!currentProject) return;
    await api.uploadScreenplay(currentProject.id, file);
    await loadScenes(currentProject.id);
  };

  const handleStartAnalysis = async () => {
    if (!currentProject) return;
    const job = await api.startAnalysis(currentProject.id);
    setCurrentJob(job);
    setIsProcessingOpen(true);
  };

  const handleSeedDemo = async () => {
    if (!currentProject) return;
    setIsSeedingDemo(true);
    try {
      const res = await api.seedDemoData(currentProject.id);
      alert(`Demo Data Successfully Seeded for "${currentProject.name}"!\n\n• ${res.locations_created} Production Locations (with Travel Matrix)\n• ${res.cast_created} Cast Members (Arjun Rampal, Meera Jasmine, David Chen, Victor Vance)\n• ${res.crew_created} Crew Leads (DOP Santosh Sivan, Stunts, Armorer)\n• Constraint: ${res.test_constraint}\n\nYou can now test the Schedule tab to run OR-Tools CP-SAT optimization!`);
      const updated = await api.getProject(currentProject.id);
      setCurrentProject(updated);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Demo seed failed.');
    } finally {
      setIsSeedingDemo(false);
    }
  };

  const handleUpdateScene = async (data: Partial<SceneDetail>) => {
    if (!currentProject || !selectedSceneId) return;
    const updated = await api.updateScene(currentProject.id, selectedSceneId, data);
    setSelectedSceneDetail(updated);
    await loadScenes(currentProject.id);
  };

  const handleConfirmScene = async () => {
    if (!currentProject || !selectedSceneId) return;
    const confirmed = await api.confirmScene(currentProject.id, selectedSceneId);
    setSelectedSceneDetail(confirmed);
    await loadScenes(currentProject.id);
  };

  const handleAddEntity = async (entityType: string, data: any) => {
    if (!currentProject || !selectedSceneId) return;
    await api.addEntity(currentProject.id, selectedSceneId, entityType, data);
    const refreshed = await api.getSceneDetail(currentProject.id, selectedSceneId);
    setSelectedSceneDetail(refreshed);
    await loadScenes(currentProject.id);
  };

  const handleDeleteEntity = async (entityType: string, entityId: string) => {
    if (!currentProject || !selectedSceneId) return;
    await api.deleteEntity(currentProject.id, selectedSceneId, entityType, entityId);
    const refreshed = await api.getSceneDetail(currentProject.id, selectedSceneId);
    setSelectedSceneDetail(refreshed);
    await loadScenes(currentProject.id);
  };

  const handleExportJson = () => {
    if (!currentProject) return;
    window.open(api.getExportJsonUrl(currentProject.id), '_blank');
  };

  const handleExportCsv = () => {
    if (!currentProject) return;
    window.location.href = api.getExportCsvUrl(currentProject.id);
  };

  const handleExportPdf = () => {
    if (!currentProject) return;
    window.open(api.getExportPdfUrl(currentProject.id), '_blank');
  };

  // Next/Prev navigation
  const currentIndex = scenes.findIndex((s) => s.id === selectedSceneId);
  const handlePrev = () => {
    if (currentIndex > 0) setSelectedSceneId(scenes[currentIndex - 1].id);
  };
  const handleNext = () => {
    if (currentIndex >= 0 && currentIndex < scenes.length - 1) setSelectedSceneId(scenes[currentIndex + 1].id);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Header
        currentProject={currentProject}
        projects={projects}
        activeTab={activeTab}
        onTabChange={(tab) => {
          setActiveTab(tab);
          // If leaving scene detail, reset selection
          if (tab !== 'breakdown') {
            setSelectedSceneId(null);
            setSelectedSceneDetail(null);
          }
        }}
        onSelectProject={(id) => {
          const found = projects.find((p) => p.id === id);
          if (found) setCurrentProject(found);
        }}
        onOpenCreateProject={() => setIsCreateOpen(true)}
        onOpenUpload={() => setIsUploadOpen(true)}
        onAnalyze={handleStartAnalysis}
        isAnalyzing={currentJob?.status === 'ANALYZING' || currentJob?.status === 'PENDING'}
        onSeedDemo={handleSeedDemo}
        isSeedingDemo={isSeedingDemo}
        onExportJson={handleExportJson}
        onExportCsv={handleExportCsv}
        onExportPdf={handleExportPdf}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6">
        {projects.length === 0 ? (
          <div className="max-w-md mx-auto my-20 p-8 rounded-3xl bg-slate-900 border border-slate-800 text-center shadow-2xl">
            <div className="p-3.5 rounded-2xl bg-cyan-500/10 text-cyan-400 w-fit mx-auto mb-4">
              <Film className="w-8 h-8" />
            </div>
            <h2 className="text-lg font-bold text-white mb-2">Welcome to ScriptBreakdown V2</h2>
            <p className="text-xs text-slate-400 mb-6 leading-relaxed">
              Create a film project and upload a screenplay to perform automated breakdown and discrete mathematical production schedule optimization.
            </p>
            <button
              onClick={() => setIsCreateOpen(true)}
              className="px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-xs transition shadow-lg shadow-cyan-500/20"
            >
              Create First Project
            </button>
          </div>
        ) : (
          <>
            {currentProject && (
              <ProjectStatsBar stats={currentProject.stats} projectName={currentProject.name} />
            )}

            {/* View Switching */}
            {activeTab === 'breakdown' && (
              scenes.length === 0 ? (
                <div className="p-12 rounded-2xl bg-slate-900/40 border border-slate-800 text-center">
                  <UploadCloud className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                  <h3 className="text-base font-semibold text-slate-200 mb-1">No Screenplay Uploaded Yet</h3>
                  <p className="text-xs text-slate-400 max-w-sm mx-auto mb-5">
                    Upload a PDF, DOCX, or TXT screenplay for "{currentProject?.name}" to detect scenes and run AI production breakdown.
                  </p>
                  <button
                    onClick={() => setIsUploadOpen(true)}
                    className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
                  >
                    Upload Screenplay Now
                  </button>
                </div>
              ) : selectedSceneDetail ? (
                <SceneDetailView
                  scene={selectedSceneDetail}
                  onClose={() => {
                    setSelectedSceneId(null);
                    setSelectedSceneDetail(null);
                  }}
                  onUpdate={handleUpdateScene}
                  onConfirm={handleConfirmScene}
                  onAddEntity={handleAddEntity}
                  onDeleteEntity={handleDeleteEntity}
                  onPrevScene={handlePrev}
                  onNextScene={handleNext}
                  hasPrev={currentIndex > 0}
                  hasNext={currentIndex >= 0 && currentIndex < scenes.length - 1}
                />
              ) : (
                <SceneTable
                  scenes={scenes}
                  onSelectScene={(id) => setSelectedSceneId(id)}
                  selectedSceneId={selectedSceneId}
                />
              )
            )}

            {currentProject && activeTab === 'cast' && (
              <CastManager projectId={currentProject.id} />
            )}

            {currentProject && activeTab === 'crew' && (
              <CrewManager projectId={currentProject.id} />
            )}

            {currentProject && activeTab === 'locations' && (
              <LocationManager projectId={currentProject.id} />
            )}

            {currentProject && activeTab === 'schedule' && (
              <ScheduleDashboard projectId={currentProject.id} />
            )}
          </>
        )}
      </main>

      {/* Modals */}
      <CreateProjectModal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        onCreate={handleCreateProject}
      />

      {currentProject && (
        <UploadScreenplayModal
          isOpen={isUploadOpen}
          onClose={() => setIsUploadOpen(false)}
          onUpload={handleUploadScreenplay}
          projectName={currentProject.name}
        />
      )}

      <ProcessingModal
        job={currentJob}
        onClose={() => setIsProcessingOpen(false)}
      />
    </div>
  );
}

