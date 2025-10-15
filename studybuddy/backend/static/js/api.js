const BASE_URL = window.location.origin;
const TOKEN_KEY = 'studybuddy.token';
const PARENT_KEY = 'studybuddy.parent';

let accessToken = window.localStorage.getItem(TOKEN_KEY) || '';

const serializeBody = (body) => {
  if (!body) {
    return undefined;
  }
  return JSON.stringify(body);
};

const parseError = async (response) => {
  try {
    const data = await response.json();
    return data.detail || response.statusText;
  } catch (error) {
    return response.statusText;
  }
};

const handleUnauthorised = () => {
  apiClient.setToken('');
  apiClient.storeParent(null);
};

const request = async (path, { method = 'GET', body } = {}) => {
  const headers = { Accept: 'application/json' };
  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }
  if (accessToken) {
    headers.Authorization = `Bearer ${accessToken}`;
  }
  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: serializeBody(body),
  });
  if (response.status === 204) {
    return null;
  }
  if (!response.ok) {
    if (response.status === 401) {
      handleUnauthorised();
    }
    const message = await parseError(response);
    throw new Error(message || 'Unexpected error');
  }
  try {
    return await response.json();
  } catch (error) {
    return null;
  }
};

export const apiClient = {
  setToken(token) {
    accessToken = token || '';
    if (token) {
      window.localStorage.setItem(TOKEN_KEY, token);
    } else {
      window.localStorage.removeItem(TOKEN_KEY);
    }
  },

  getToken() {
    return accessToken;
  },

  storeParent(parent) {
    if (parent) {
      window.localStorage.setItem(PARENT_KEY, JSON.stringify(parent));
    } else {
      window.localStorage.removeItem(PARENT_KEY);
    }
  },

  getStoredParent() {
    const raw = window.localStorage.getItem(PARENT_KEY);
    if (!raw) {
      return null;
    }
    try {
      return JSON.parse(raw);
    } catch (error) {
      return null;
    }
  },

  async health() {
    return request('/healthz');
  },

  async signup(credentials) {
    const payload = await request('/auth/signup', {method: 'POST', body: credentials});
    this.setToken(payload.access_token);
    this.storeParent(payload.parent);
    return payload;
  },

  async login(credentials) {
    const payload = await request('/auth/login', {method: 'POST', body: credentials});
    this.setToken(payload.access_token);
    this.storeParent(payload.parent);
    return payload;
  },

  logout() {
    this.setToken('');
    this.storeParent(null);
  },

  async listChildren() {
    return request('/children');
  },

  async createChild(data) {
    return request('/children', {method: 'POST', body: data});
  },

  async updateChild(childId, data) {
    return request(`/children/${childId}`, {method: 'PATCH', body: data});
  },

  async deleteChild(childId) {
    await request(`/children/${childId}`, {method: 'DELETE'});
  },

  async getTopics(subject, grade) {
    const params = new URLSearchParams({ subject, grade: grade.toString() });
    return request(`/questions/topics?${params.toString()}`);
  },

  async getSubtopics(subject, grade, topic = null) {
    const params = new URLSearchParams({ subject, grade: grade.toString() });
    if (topic) {
      params.append('topic', topic);
    }
    return request(`/questions/subtopics?${params.toString()}`);
  },

  async fetchQuestions(payload) {
    return request('/questions/fetch', {method: 'POST', body: payload});
  },

  async submitAttempt(payload) {
    return request('/attempts', {method: 'POST', body: payload});
  },

  async getProgress(childId) {
    return request(`/progress/${childId}`);
  },

  async getStandards() {
    return request('/standards');
  },
};
