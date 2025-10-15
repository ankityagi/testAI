const subjectSelect = document.getElementById('subject-select');
const fetchButton = document.getElementById('fetch-question-btn');
const topicSelect = document.getElementById('topic-select');
const subtopicSelect = document.getElementById('subtopic-select');
const questionCard = document.getElementById('question-card');
const questionTopic = document.getElementById('question-topic');
const questionStem = document.getElementById('question-stem');
const optionsList = document.getElementById('question-options');
const feedbackEl = document.getElementById('practice-feedback');
const emptyStateEl = document.getElementById('practice-empty');

export const setupPracticeUI = ({ apiClient, onAttemptLogged }) => {
  let currentChildId = null;
  let currentChild = null;
  let currentQuestion = null;
  let submitting = false;

  const reset = () => {
    currentQuestion = null;
    optionsList.textContent = '';
    questionStem.textContent = '';
    questionTopic.textContent = '';
    feedbackEl.textContent = '';
    questionCard.hidden = true;
    emptyStateEl.hidden = false;
    emptyStateEl.textContent = 'Select a child to begin.';
  };

  const renderQuestion = (question, selectedSubtopic) => {
    console.log('[PRACTICE] ========== RENDERING NEW QUESTION ==========');
    console.log('[PRACTICE] Question details:', {
      id: question.id,
      stem: question.stem,
      hash: question.hash,
      difficulty: question.difficulty,
      selectedSubtopic,
      fullQuestion: question
    });

    currentQuestion = question;

    // Clear and update stem
    questionStem.textContent = '';
    questionStem.textContent = question.stem;

    // Clear and rebuild options
    optionsList.textContent = '';
    question.options.forEach((option, index) => {
      const listItem = document.createElement('li');
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = option;
      button.addEventListener('click', () => submitAttempt(option));
      listItem.appendChild(button);
      optionsList.appendChild(listItem);
      console.log(`[PRACTICE] Added option ${index + 1}: ${option}`);
    });

    // Update metadata
    const subtopicText = selectedSubtopic ? ` • ${selectedSubtopic}` : '';
    const questionIdText = question.id ? ` • ID: ${question.id.substring(0, 8)}` : '';
    questionTopic.textContent = `${question.subject.toUpperCase()} • ${question.topic || 'General'}${subtopicText} • ${question.difficulty || 'adaptive'}${questionIdText}`;

    feedbackEl.textContent = '';
    questionCard.hidden = false;
    emptyStateEl.hidden = true;

    console.log('[PRACTICE] Question render complete');
    console.log('[PRACTICE] ==========================================');
  };

  const submitAttempt = async (selection) => {
    if (!currentQuestion || !currentChildId || submitting) {
      console.log('[PRACTICE] Submit blocked:', { currentQuestion: !!currentQuestion, currentChildId, submitting });
      return;
    }
    submitting = true;

    // Disable all option buttons immediately
    const optionButtons = optionsList.querySelectorAll('button');
    optionButtons.forEach(btn => btn.disabled = true);

    try {
      const payload = {
        child_id: currentChildId,
        question_id: currentQuestion.id,
        selected: selection,
        time_spent_ms: Math.floor(Math.random() * 4000) + 1000,
      };
      console.log('[PRACTICE] Submitting attempt:', payload);
      const result = await apiClient.submitAttempt(payload);
      console.log('[PRACTICE] Attempt result:', result);
      feedbackEl.textContent = result.correct
        ? 'Nice work! That answer is correct.'
        : `Keep practicing! The correct answer was ${result.expected}.`;
      onAttemptLogged();

      // Auto-fetch next question after a short delay
      setTimeout(async () => {
        submitting = true; // Prevent double-clicks during auto-fetch
        try {
          console.log('[PRACTICE] Auto-fetching next question...');
          const nextResponse = await fetchQuestion();
          console.log('[PRACTICE] Auto-fetch complete:', nextResponse);
        } catch (error) {
          console.error('[PRACTICE] Error fetching next question:', error);
          feedbackEl.textContent = error.message || 'Unable to fetch next question.';
        } finally {
          submitting = false;
        }
      }, 1500);
    } catch (error) {
      console.error('[PRACTICE] Error submitting attempt:', error);
      feedbackEl.textContent = error.message || 'Unable to record attempt.';
      // Re-enable buttons if submission failed
      optionButtons.forEach(btn => btn.disabled = false);
      submitting = false;
    }
  };

  const loadTopics = async () => {
    if (!currentChild) {
      console.log('[PRACTICE] No currentChild, skipping topic load');
      return;
    }
    const subject = subjectSelect.value;
    const grade = currentChild.grade;

    console.log('[PRACTICE] Loading topics:', { subject, grade });

    if (!grade && grade !== 0) {
      console.warn('[PRACTICE] Child has no grade set, cannot load topics');
      topicSelect.innerHTML = '<option value="">Random</option>';
      subtopicSelect.innerHTML = '<option value="">Random</option>';
      return;
    }

    try {
      const response = await apiClient.getTopics(subject, grade);
      const topics = response.topics || [];
      console.log(`[PRACTICE] Loaded ${topics.length} topics`);

      // Clear and rebuild topic dropdown
      topicSelect.innerHTML = '<option value="">Random</option>';
      topics.forEach(t => {
        const option = document.createElement('option');
        option.value = t.topic;
        option.textContent = t.topic;
        topicSelect.appendChild(option);
      });

      // Load subtopics for the first/selected topic
      await loadSubtopics();
    } catch (error) {
      console.error('[PRACTICE] Error loading topics:', error);
      topicSelect.innerHTML = '<option value="">Random</option>';
      subtopicSelect.innerHTML = '<option value="">Random</option>';
    }
  };

  const loadSubtopics = async () => {
    if (!currentChild) {
      console.log('[PRACTICE] No currentChild, skipping subtopic load');
      return;
    }
    const subject = subjectSelect.value;
    const grade = currentChild.grade;
    const topic = topicSelect.value || null;

    console.log('[PRACTICE] Loading subtopics:', { subject, grade, topic });

    if (!grade && grade !== 0) {
      console.warn('[PRACTICE] Child has no grade set, cannot load subtopics');
      subtopicSelect.innerHTML = '<option value="">Random</option>';
      return;
    }

    try {
      const response = await apiClient.getSubtopics(subject, grade, topic);
      const subtopics = response.subtopics || [];
      console.log(`[PRACTICE] Loaded ${subtopics.length} subtopics`);

      // Clear and rebuild subtopic dropdown
      subtopicSelect.innerHTML = '<option value="">Random</option>';
      subtopics.forEach(st => {
        const option = document.createElement('option');
        option.value = st.subtopic;
        option.textContent = st.subtopic;
        subtopicSelect.appendChild(option);
      });
    } catch (error) {
      console.error('[PRACTICE] Error loading subtopics:', error);
      // Keep the "Random" option if loading fails
      subtopicSelect.innerHTML = '<option value="">Random</option>';
    }
  };

  const fetchQuestion = async () => {
    if (!currentChildId) {
      console.log('[PRACTICE] No child selected');
      feedbackEl.textContent = 'Select a child before starting a session.';
      return;
    }
    feedbackEl.textContent = 'Fetching questions…';
    try {
      const requestPayload = {
        child_id: currentChildId,
        subject: subjectSelect.value,
        limit: 1,
      };
      const topicValue = topicSelect.value;
      if (topicValue) {
        requestPayload.topic = topicValue;
      }
      const subtopicValue = subtopicSelect.value;
      if (subtopicValue) {
        requestPayload.subtopic = subtopicValue;
      }
      console.log('[PRACTICE] Fetching questions with payload:', requestPayload);
      const response = await apiClient.fetchQuestions(requestPayload);
      console.log('[PRACTICE] Received response:', response);
      console.log('[PRACTICE] Response has', response.questions?.length || 0, 'questions');
      if (!response.questions?.length) {
        console.error('[PRACTICE] ❌ NO QUESTIONS IN RESPONSE!');
        console.error('[PRACTICE] Full response:', JSON.stringify(response));
        feedbackEl.textContent = 'No questions available right now. Try another subject.';
        return null;
      }
      console.log('[PRACTICE] ✓ About to render question from response');
      renderQuestion(response.questions[0], response.selected_subtopic);
      feedbackEl.textContent = 'Pick the best answer to continue the streak!';
      return response;
    } catch (error) {
      console.error('[PRACTICE] Error in fetchQuestion:', error);
      feedbackEl.textContent = error.message || 'Unable to fetch questions.';
      throw error; // Re-throw so caller can handle
    }
  };

  fetchButton.addEventListener('click', fetchQuestion);

  // Reload topics when subject changes
  subjectSelect.addEventListener('change', loadTopics);

  // Reload subtopics when topic changes
  topicSelect.addEventListener('change', loadSubtopics);

  return {
    onChildSelected(childId, child) {
      currentChildId = childId;
      currentChild = child;
      if (!childId) {
        reset();
        return;
      }
      emptyStateEl.textContent = 'Press "Fetch questions" to start practicing.';
      emptyStateEl.hidden = false;
      questionCard.hidden = true;
      feedbackEl.textContent = '';

      // Load topics and subtopics for the current selection
      loadTopics();
    },
  };
};
