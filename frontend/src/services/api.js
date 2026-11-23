import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const advisoryApi = {
  // Generate advisory
  generateAdvisory: async (data) => {
    const res = await api.post('/advisory/generate', data);
    return res.data;
  },

  // Get single advisory
  getAdvisory: async (requestId) => {
    const res = await api.get(`/advisory/${requestId}`);
    return res.data;
  },

  // Download PDF
  getAdvisoryPdfUrl: (requestId) => `/api/advisory/${requestId}/pdf`,

  // Agent statuses
  getAgentsStatus: async (requestId) => {
    const res = await api.get(`/agents/status/${requestId}`);
    return res.data;
  },

  // Blackboard entries
  getBlackboardEntries: async (requestId) => {
    const res = await api.get(`/blackboard/${requestId}`);
    return res.data;
  },

  // History
  getHistory: async () => {
    const res = await api.get('/history');
    return res.data;
  },

  // Dashboard Stats
  getDashboardStats: async () => {
    const res = await api.get('/history/stats');
    return res.data;
  },

  // Delete advisory
  deleteAdvisory: async (requestId) => {
    const res = await api.delete(`/history/${requestId}`);
    return res.data;
  },

  // Schemes
  getSchemes: async () => {
    const res = await api.get('/schemes');
    return res.data;
  },

  searchSchemes: async (query) => {
    const res = await api.get(`/schemes/search?q=${encodeURIComponent(query)}`);
    return res.data;
  },

  // Health
  getHealth: async () => {
    const res = await api.get('/health');
    return res.data;
  },
};

export default api;
