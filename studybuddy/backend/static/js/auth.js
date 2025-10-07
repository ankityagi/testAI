import { apiClient } from './api.js';
import { setupChildrenUI } from './children.js';
import { setupPracticeUI } from './practice.js';
import { setupHistoryUI } from './history.js';

const authSection = document.getElementById('auth-section');
const appSection = document.getElementById('app-section');
const authForm = document.getElementById('auth-form');
const authTitle = document.getElementById('auth-title');
const authSubtitle = document.getElementById('auth-subtitle');
const authError = document.getElementById('auth-error');
const loginTab = document.getElementById('auth-tab-login');
const signupTab = document.getElementById('auth-tab-signup');
const authSubmit = document.getElementById('auth-submit');
const emailInput = document.getElementById('auth-email');
const passwordInput = document.getElementById('auth-password');
const logoutButton = document.getElementById('logout-btn');
const parentEmail = document.getElementById('parent-email');
const childCount = document.getElementById('child-count');

const state = {
  parent: null,
  children: [],
  selectedChildId: null,
};

let mode = 'login';
let childrenUI;
let practiceUI;
let historyUI;

const setMode = (nextMode) => {
  mode = nextMode;
  const isSignup = mode === 'signup';
  authTitle.textContent = isSignup ? 'Create your account' : 'Welcome back';
  authSubtitle.textContent = isSignup
    ? 'Sign up to start assigning personalised quizzes.'
    : 'Log in to pick up where you left off.';
  authSubmit.textContent = isSignup ? 'Sign up' : 'Log in';
  passwordInput.setAttribute('autocomplete', isSignup ? 'new-password' : 'current-password');
  authError.hidden = true;
  authError.textContent = '';
  passwordInput.value = '';
  loginTab.classList.toggle('active', !isSignup);
  signupTab.classList.toggle('active', isSignup);
  loginTab.setAttribute('aria-selected', String(!isSignup));
  signupTab.setAttribute('aria-selected', String(isSignup));
};

const setParentInfo = (parent) => {
  state.parent = parent;
  parentEmail.textContent = parent.email;
};

const resetDashboard = () => {
  state.parent = null;
  state.children = [];
  state.selectedChildId = null;
  childCount.textContent = '';
  parentEmail.textContent = '';
};

const showDashboard = () => {
  authSection.hidden = true;
  appSection.hidden = false;
};

const showAuth = () => {
  appSection.hidden = true;
  authSection.hidden = false;
  resetDashboard();
};

const updateChildCount = () => {
  if (!state.children.length) {
    childCount.textContent = 'No children yet';
    return;
  }
  const label = state.children.length === 1 ? 'child' : 'children';
  childCount.textContent = `${state.children.length} ${label}`;
};

const handleChildrenUpdated = (children) => {
  state.children = children;
  updateChildCount();
  if (!children.length) {
    state.selectedChildId = null;
    practiceUI.onChildSelected(null);
    historyUI.onChildSelected(null);
    return;
  }
  const exists = children.some((child) => child.id === state.selectedChildId);
  if (!exists) {
    state.selectedChildId = children[0].id;
    practiceUI.onChildSelected(state.selectedChildId);
    historyUI.onChildSelected(state.selectedChildId);
    childrenUI.highlight(state.selectedChildId);
  }
};

const handleChildSelected = (childId) => {
  state.selectedChildId = childId;
  practiceUI.onChildSelected(childId);
  historyUI.onChildSelected(childId);
};

historyUI = setupHistoryUI({
  apiClient,
});

practiceUI = setupPracticeUI({
  apiClient,
  onAttemptLogged: () => {
    if (state.selectedChildId) {
      historyUI.onChildSelected(state.selectedChildId);
    }
  },
});

childrenUI = setupChildrenUI({
  apiClient,
  onChildrenUpdated: handleChildrenUpdated,
  onChildSelected: handleChildSelected,
});

const handleAuthSuccess = async (payload) => {
  setParentInfo(payload.parent);
  await childrenUI.refresh();
  updateChildCount();
  await historyUI.loadStandards();
  showDashboard();
  if (state.children.length) {
    const childId = state.children[0].id;
    state.selectedChildId = childId;
    childrenUI.highlight(childId);
    practiceUI.onChildSelected(childId);
    historyUI.onChildSelected(childId);
  }
};

authForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  authSubmit.disabled = true;
  authError.hidden = true;
  authError.textContent = '';
  try {
    const credentials = {
      email: emailInput.value.trim(),
      password: passwordInput.value,
    };
    const payload = mode === 'signup'
      ? await apiClient.signup(credentials)
      : await apiClient.login(credentials);
    await handleAuthSuccess(payload);
  } catch (error) {
    authError.hidden = false;
    authError.textContent = error.message || 'Unable to authenticate.';
  } finally {
    authSubmit.disabled = false;
  }
});

loginTab.addEventListener('click', () => {
  if (mode !== 'login') {
    setMode('login');
    emailInput.focus();
  }
});

signupTab.addEventListener('click', () => {
  if (mode !== 'signup') {
    setMode('signup');
    emailInput.focus();
  }
});

logoutButton.addEventListener('click', () => {
  apiClient.logout();
  setMode('login');
  showAuth();
});

const boot = async () => {
  const storedParent = apiClient.getStoredParent();
  const storedToken = apiClient.getToken();
  if (!storedToken || !storedParent) {
    return;
  }
  try {
    setParentInfo(storedParent);
    await childrenUI.refresh();
    updateChildCount();
    await historyUI.loadStandards();
    showDashboard();
    if (state.children.length) {
      const childId = state.selectedChildId || state.children[0].id;
      state.selectedChildId = childId;
      childrenUI.highlight(childId);
      practiceUI.onChildSelected(childId);
      historyUI.onChildSelected(childId);
    }
  } catch (error) {
    apiClient.logout();
    showAuth();
  }
};

setMode('login');
boot();
