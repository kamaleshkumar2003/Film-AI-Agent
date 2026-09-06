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
};
