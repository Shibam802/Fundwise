const BASE_URL = 'http://localhost:8000';

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export const api = {
  listUsers: () => request('/api/users'),
  getUser: (id) => request(`/api/users/${id}`),
  listFunds: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/api/funds${qs ? `?${qs}` : ''}`);
  },
  listStocks: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/api/stocks${qs ? `?${qs}` : ''}`);
  },
  getItem: (id) => request(`/api/items/${id}`),
  getRecommendations: (userId, topN = 10) =>
    request(`/api/recommendations/${userId}?top_n=${topN}`),
  getSimilarInvestors: (userId, topN = 5) =>
    request(`/api/similar-investors/${userId}?top_n=${topN}`),
  getPortfolio: (userId) => request(`/api/portfolio/${userId}`),
  computeRiskProfile: (answers) =>
    request('/api/risk-profile', { method: 'POST', body: JSON.stringify(answers) }),
  logInteraction: (payload) =>
    request('/api/interactions', { method: 'POST', body: JSON.stringify(payload) }),
  getCategories: () => request('/api/categories'),
};
