const summaryEl = document.getElementById('progress-summary');
const subjectsEl = document.getElementById('progress-subjects');
const standardsEl = document.getElementById('standards-list');

export const setupHistoryUI = ({ apiClient }) => {
  let cachedStandards = null;

  const clearProgress = () => {
    summaryEl.textContent = '';
    subjectsEl.textContent = '';
    const empty = document.createElement('p');
    empty.className = 'muted';
    empty.textContent = 'Start a session to see progress here.';
    subjectsEl.appendChild(empty);
  };

  const renderSummary = (progress) => {
    summaryEl.textContent = '';
    const metrics = [
      { label: 'Attempted', value: progress.attempted },
      { label: 'Correct', value: progress.correct },
      { label: 'Accuracy', value: `${Math.round(progress.accuracy * 100)}%` },
      { label: 'Current streak', value: progress.current_streak },
    ];
    metrics.forEach((metric) => {
      const term = document.createElement('dt');
      term.textContent = metric.label;
      const definition = document.createElement('dd');
      definition.textContent = metric.value;
      summaryEl.append(term, definition);
    });
  };

  const renderSubjects = (progress) => {
    subjectsEl.textContent = '';
    const entries = Object.entries(progress.by_subject || {});
    if (!entries.length) {
      const empty = document.createElement('li');
      empty.className = 'muted';
      empty.textContent = 'No subject history yet.';
      subjectsEl.appendChild(empty);
      return;
    }
    entries.forEach(([subject, stats]) => {
      const item = document.createElement('li');
      const title = document.createElement('strong');
      title.textContent = subject;
      const details = document.createElement('p');
      details.className = 'muted';
      const accuracy = stats.total ? Math.round((stats.accuracy || 0) * 100) : 0;
      details.textContent = `${stats.correct}/${stats.total} correct • ${accuracy}% accuracy`;
      item.append(title, details);
      subjectsEl.appendChild(item);
    });
  };

  const renderStandards = (standards) => {
    standardsEl.textContent = '';
    standards.forEach((standard) => {
      const item = document.createElement('li');
      const heading = document.createElement('h3');
      heading.textContent = `${standard.subject.toUpperCase()} • ${standard.standard_ref}`;
      const badge = document.createElement('p');
      badge.className = 'muted';
      const scope = [standard.grade ? `Grade ${standard.grade}` : null, standard.domain, standard.sub_domain]
        .filter(Boolean)
        .join(' • ');
      badge.textContent = scope;
      const description = document.createElement('p');
      description.textContent = standard.description || 'No description provided yet.';
      item.append(heading, badge, description);
      standardsEl.appendChild(item);
    });
  };

  const loadStandards = async () => {
    if (cachedStandards) {
      return;
    }
    try {
      const standards = await apiClient.getStandards();
      cachedStandards = standards;
      renderStandards(standards);
    } catch (error) {
      standardsEl.textContent = '';
      const warning = document.createElement('li');
      warning.className = 'muted';
      warning.textContent = error.message || 'Unable to load standards.';
      standardsEl.appendChild(warning);
    }
  };

  clearProgress();

  return {
    async onChildSelected(childId) {
      if (!childId) {
        clearProgress();
        return;
      }
      try {
        const progress = await apiClient.getProgress(childId);
        renderSummary(progress);
        renderSubjects(progress);
      } catch (error) {
        summaryEl.textContent = '';
        subjectsEl.textContent = '';
        const issue = document.createElement('li');
        issue.className = 'muted';
        issue.textContent = error.message || 'Unable to load progress.';
        subjectsEl.appendChild(issue);
      }
    },

    async loadStandards() {
      await loadStandards();
    },
  };
};
