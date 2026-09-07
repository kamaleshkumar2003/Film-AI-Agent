import axios from 'axios';
import { Project, SceneSummary, SceneDetail, JobResponse } from '../types';

const API_BASE = '/api';

export const api = {
  // Projects
  getProjects: async (): Promise<Project[]> => {
    const res = await axios.get(`${API_BASE}/projects`);
    return res.data;
  },

  getProject: async (projectId: string): Promise<Project> => {
    const res = await axios.get(`${API_BASE}/projects/${projectId}`);
    return res.data;
  },

  createProject: async (data: {
    name: string;
    production_type: string;
    description?: string;
    director?: string;
    production_company?: string;
  }): Promise<Project> => {
    const res = await axios.post(`${API_BASE}/projects`, data);
    return res.data;
  },

  uploadScreenplay: async (projectId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await axios.post(`${API_BASE}/projects/${projectId}/screenplay`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  },

  startAnalysis: async (projectId: string): Promise<JobResponse> => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/analyze`);
    return res.data;
  },

  reanalyzeProject: async (projectId: string): Promise<JobResponse> => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/reanalyze`);
    return res.data;
  },

  // Jobs
  getJobStatus: async (jobId: string): Promise<JobResponse> => {
    const res = await axios.get(`${API_BASE}/jobs/${jobId}`);
    return res.data;
  },

  // Scenes
  getScenes: async (
    projectId: string,
    filters?: {
      int_ext?: string;
      day_night?: string;
      weather_sensitivity?: string;
      location?: string;
      character?: string;
    }
  ): Promise<SceneSummary[]> => {
    const res = await axios.get(`${API_BASE}/projects/${projectId}/scenes`, { params: filters });
    return res.data;
  },

  getSceneDetail: async (projectId: string, sceneId: string): Promise<SceneDetail> => {
    const res = await axios.get(`${API_BASE}/projects/${projectId}/scenes/${sceneId}`);
    return res.data;
  },

  updateScene: async (projectId: string, sceneId: string, data: Partial<SceneDetail>): Promise<SceneDetail> => {
    const res = await axios.put(`${API_BASE}/projects/${projectId}/scenes/${sceneId}`, data);
    return res.data;
  },

  confirmScene: async (projectId: string, sceneId: string): Promise<SceneDetail> => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/scenes/${sceneId}/confirm`);
    return res.data;
  },

  addEntity: async (projectId: string, sceneId: string, entityType: string, data: any) => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/scenes/${sceneId}/entities`, {
      entity_type: entityType,
      data
    });
    return res.data;
  },

  deleteEntity: async (projectId: string, sceneId: string, entityType: string, entityId: string) => {
    const res = await axios.delete(`${API_BASE}/projects/${projectId}/scenes/${sceneId}/entities/${entityType}/${entityId}`);
    return res.data;
  },

  // Exports
  getExportJsonUrl: (projectId: string) => `${API_BASE}/projects/${projectId}/export/json`,
  getExportCsvUrl: (projectId: string) => `${API_BASE}/projects/${projectId}/export/csv`,

  // ==========================================
  // V2 API METHODS: CAST & CREW
  // ==========================================
  getCast: async (projectId: string) => {
    const res = await axios.get(`${API_BASE}/projects/${projectId}/cast`);
    return res.data;
  },

  createCastMember: async (projectId: string, data: any) => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/cast`, data);
    return res.data;
  },

  deleteCastMember: async (projectId: string, castId: string) => {
    const res = await axios.delete(`${API_BASE}/projects/${projectId}/cast/${castId}`);
    return res.data;
  },

  setCastAvailability: async (projectId: string, castId: string, data: any) => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/cast/${castId}/availability`, data);
    return res.data;
  },

  getCrew: async (projectId: string) => {
    const res = await axios.get(`${API_BASE}/projects/${projectId}/crew`);
    return res.data;
  },

  createCrewMember: async (projectId: string, data: any) => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/crew`, data);
    return res.data;
  },

  deleteCrewMember: async (projectId: string, crewId: string) => {
    const res = await axios.delete(`${API_BASE}/projects/${projectId}/crew/${crewId}`);
    return res.data;
  },

  setCrewAvailability: async (projectId: string, crewId: string, data: any) => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/crew/${crewId}/availability`, data);
    return res.data;
  },

  // ==========================================
  // V2 API METHODS: LOCATIONS & TRAVEL
  // ==========================================
  getLocations: async (projectId: string) => {
    const res = await axios.get(`${API_BASE}/projects/${projectId}/locations`);
    return res.data;
  },

  createLocation: async (projectId: string, data: any) => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/locations`, data);
    return res.data;
  },

  deleteLocation: async (projectId: string, locId: string) => {
    const res = await axios.delete(`${API_BASE}/projects/${projectId}/locations/${locId}`);
    return res.data;
  },

  setLocationAvailability: async (projectId: string, locId: string, data: any) => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/locations/${locId}/availability`, data);
    return res.data;
  },

  getTravelMatrix: async (projectId: string) => {
    const res = await axios.get(`${API_BASE}/projects/${projectId}/locations/travel-matrix`);
    return res.data;
  },

  updateTravelMatrix: async (projectId: string, items: any[]) => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/locations/travel-matrix`, items);
    return res.data;
  },

  // ==========================================
  // V2 API METHODS: SCHEDULING & OPTIMIZATION
  // ==========================================
  getProductionConfig: async (projectId: string) => {
    const res = await axios.get(`${API_BASE}/projects/${projectId}/schedule/production-config`);
    return res.data;
  },

  updateProductionConfig: async (projectId: string, data: any) => {
    const res = await axios.put(`${API_BASE}/projects/${projectId}/schedule/production-config`, data);
    return res.data;
  },

  generateSchedule: async (projectId: string, data: any) => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/schedule/generate`, data);
    return res.data;
  },

  getScheduleVersions: async (projectId: string) => {
    const res = await axios.get(`${API_BASE}/projects/${projectId}/schedule/versions`);
    return res.data;
  },

  getScheduleVersion: async (projectId: string, versionId: string) => {
    const res = await axios.get(`${API_BASE}/projects/${projectId}/schedule/versions/${versionId}`);
    return res.data;
  },

  moveScheduleItem: async (projectId: string, versionId: string, itemId: string, data: any) => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/schedule/versions/${versionId}/move-item?item_id=${itemId}`, data);
    return res.data;
  },

  lockScene: async (projectId: string, data: any) => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/schedule/lock-scene`, data);
    return res.data;
  },

  runWhatIf: async (projectId: string, data: any) => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/schedule/what-if`, data);
    return res.data;
  },

  seedDemoData: async (projectId: string) => {
    const res = await axios.post(`${API_BASE}/projects/${projectId}/schedule/demo-seed`);
    return res.data;
  },

  getExportPdfUrl: (projectId: string, versionId?: string) => {
    return versionId
      ? `${API_BASE}/projects/${projectId}/schedule/export/pdf?version_id=${versionId}`
      : `${API_BASE}/projects/${projectId}/schedule/export/pdf`;
  },
};

