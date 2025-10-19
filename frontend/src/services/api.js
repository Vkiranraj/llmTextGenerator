import axios from 'axios';

const API_BASE = ''; // Use relative URLs since nginx will proxy

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const jobService = {
  // Get all jobs
  getJobs: async () => {
    const response = await api.get('/jobs/');
    return response.data;
  },

  // Create a new job
  createJob: async (url, email = null) => {
    const response = await api.post('/jobs/', { url, email });
    return response.data;
  },

  // Get a specific job
  getJob: async (jobId) => {
    const response = await api.get(`/jobs/${jobId}`);
    return response.data;
  },

  // Get job progress
  getJobProgress: async (jobId) => {
    const response = await api.get(`/jobs/${jobId}/progress`);
    return response.data;
  },

  // Download job content
  downloadJob: (jobId) => {
    return `${API_BASE}/jobs/${jobId}/download`;
  },
};

export default api;
