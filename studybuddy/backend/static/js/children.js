const listEl = document.getElementById('children-list');
const formEl = document.getElementById('child-form');
const nameInput = document.getElementById('child-name');
const gradeInput = document.getElementById('child-grade');
const zipInput = document.getElementById('child-zip');
const feedbackEl = document.getElementById('child-feedback');

export const setupChildrenUI = ({ apiClient, onChildrenUpdated, onChildSelected }) => {
  let currentChildren = [];
  let selectedId = null;

  const showFeedback = (message) => {
    feedbackEl.textContent = message;
  };

  const renderEmpty = () => {
    const item = document.createElement('li');
    item.className = 'muted';
    item.textContent = 'No children yet. Add a learner above.';
    listEl.replaceChildren(item);
  };

  const highlight = (childId) => {
    selectedId = childId;
    Array.from(listEl.children).forEach((node) => {
      if (!(node instanceof HTMLElement)) {
        return;
      }
      node.classList.toggle('active', node.dataset.childId === childId);
    });
  };

  const handleSelect = (childId) => {
    highlight(childId);
    onChildSelected(childId);
  };

  const createActionButton = (label, handler) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'ghost';
    button.textContent = label;
    button.addEventListener('click', handler);
    return button;
  };

  const renderChildren = (children) => {
    currentChildren = children;
    if (!children.length) {
      renderEmpty();
      return;
    }
    listEl.textContent = '';
    children.forEach((child) => {
      const item = document.createElement('li');
      item.dataset.childId = child.id;

      const details = document.createElement('div');
      details.style.display = 'grid';
      details.style.gap = '0.15rem';
      const title = document.createElement('strong');
      title.textContent = child.name;
      const meta = document.createElement('span');
      meta.className = 'muted';
      const gradeLabel = child.grade === null || child.grade === undefined ? '—' : `Grade ${child.grade}`;
      meta.textContent = `${gradeLabel} • ${child.zip || 'ZIP n/a'}`;
      details.append(title, meta);

      const actions = document.createElement('div');
      actions.className = 'child-actions';

      const selectBtn = createActionButton('Select', () => handleSelect(child.id));
      const editBtn = createActionButton('Edit', async () => {
        const nextName = window.prompt('Child name', child.name);
        if (nextName === null) {
          return;
        }
        const nextGradeInput = window.prompt('Grade (0-12)', child.grade !== null ? String(child.grade) : '');
        if (nextGradeInput === null) {
          return;
        }
        const nextZip = window.prompt('ZIP (optional)', child.zip || '');
        if (nextZip === null) {
          return;
        }
        const payload = {};
        const trimmedName = nextName.trim();
        if (trimmedName && trimmedName !== child.name) {
          payload.name = trimmedName;
        }
        const trimmedGrade = nextGradeInput.trim();
        if (trimmedGrade.length) {
          const parsed = Number(trimmedGrade);
          if (Number.isNaN(parsed) || parsed < 0 || parsed > 12) {
            showFeedback('Grade must be a number between 0 and 12.');
            return;
          }
          payload.grade = parsed;
        } else if (child.grade !== null && child.grade !== undefined) {
          payload.grade = null;
        }
        const trimmedZip = nextZip.trim();
        if (trimmedZip !== child.zip && trimmedZip.length) {
          payload.zip = trimmedZip;
        } else if (!trimmedZip.length && child.zip) {
          payload.zip = null;
        }
        if (!Object.keys(payload).length) {
          showFeedback('No changes to save.');
          return;
        }
        try {
          await apiClient.updateChild(child.id, payload);
          showFeedback('Child updated.');
          await refresh();
        } catch (error) {
          showFeedback(error.message || 'Unable to update child.');
        }
      });
      const deleteBtn = createActionButton('Remove', async () => {
        const confirmed = window.confirm(`Remove ${child.name}? Progress history will be cleared.`);
        if (!confirmed) {
          return;
        }
        try {
          await apiClient.deleteChild(child.id);
          showFeedback('Child removed.');
          await refresh();
        } catch (error) {
          showFeedback(error.message || 'Unable to remove child.');
        }
      });
      actions.append(selectBtn, editBtn, deleteBtn);
      item.append(details, actions);
      if (child.id === selectedId) {
        item.classList.add('active');
      }
      listEl.appendChild(item);
    });
  };

  const refresh = async () => {
    try {
      const children = await apiClient.listChildren();
      renderChildren(children);
      onChildrenUpdated(children);
    } catch (error) {
      showFeedback(error.message || 'Unable to load children.');
      renderEmpty();
    }
  };

  formEl.addEventListener('submit', async (event) => {
    event.preventDefault();
    const name = nameInput.value.trim();
    const gradeValue = gradeInput.value.trim();
    const zipValue = zipInput.value.trim();
    const payload = { name };
    if (gradeValue.length) {
      const parsed = Number(gradeValue);
      if (Number.isNaN(parsed) || parsed < 0 || parsed > 12) {
        showFeedback('Grade must be a number between 0 and 12.');
        return;
      }
      payload.grade = parsed;
    }
    if (zipValue.length) {
      payload.zip = zipValue;
    }
    try {
      await apiClient.createChild(payload);
      showFeedback('Child added.');
      formEl.reset();
      await refresh();
    } catch (error) {
      showFeedback(error.message || 'Unable to add child.');
    }
  });

  return {
    refresh,
    highlight,
  };
};
