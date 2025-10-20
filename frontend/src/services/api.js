import axios from 'axios';

// Get API base URL from environment variable, fallback to relative URLs for nginx proxy
const API_BASE = process.env.REACT_APP_API_BASE_URL || '';

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
  createJob: async (url) => {
    const response = await api.post('/jobs/', { url });
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
