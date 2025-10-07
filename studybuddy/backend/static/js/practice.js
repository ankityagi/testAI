const subjectSelect = document.getElementById('subject-select');
const fetchButton = document.getElementById('fetch-question-btn');
const topicInput = document.getElementById('topic-input');
const questionCard = document.getElementById('question-card');
const questionTopic = document.getElementById('question-topic');
const questionStem = document.getElementById('question-stem');
const optionsList = document.getElementById('question-options');
const feedbackEl = document.getElementById('practice-feedback');
const emptyStateEl = document.getElementById('practice-empty');

export const setupPracticeUI = ({ apiClient, onAttemptLogged }) => {
  let currentChildId = null;
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

  const renderQuestion = (question) => {
    currentQuestion = question;
    optionsList.textContent = '';
    questionStem.textContent = question.stem;
    questionTopic.textContent = `${question.subject.toUpperCase()} • ${question.topic || 'General'} • ${question.difficulty || 'adaptive'}`;
    question.options.forEach((option) => {
      const listItem = document.createElement('li');
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = option;
      button.addEventListener('click', () => submitAttempt(option));
      listItem.appendChild(button);
      optionsList.appendChild(listItem);
    });
    feedbackEl.textContent = '';
    questionCard.hidden = false;
    emptyStateEl.hidden = true;
  };

  const submitAttempt = async (selection) => {
    if (!currentQuestion || !currentChildId || submitting) {
      return;
    }
    submitting = true;
    try {
      const payload = {
        child_id: currentChildId,
        question_id: currentQuestion.id,
        selected: selection,
        time_spent_ms: Math.floor(Math.random() * 4000) + 1000,
      };
      const result = await apiClient.submitAttempt(payload);
      feedbackEl.textContent = result.correct
        ? 'Nice work! That answer is correct.'
        : `Keep practicing! The correct answer was ${result.expected}.`;
      onAttemptLogged();
    } catch (error) {
      feedbackEl.textContent = error.message || 'Unable to record attempt.';
    } finally {
      submitting = false;
    }
  };

  const fetchQuestion = async () => {
    if (!currentChildId) {
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
      const topicValue = topicInput.value.trim();
      if (topicValue.length) {
        requestPayload.topic = topicValue;
      }
      const response = await apiClient.fetchQuestions(requestPayload);
      if (!response.questions?.length) {
        feedbackEl.textContent = 'No questions available right now. Try another subject.';
        return;
      }
      renderQuestion(response.questions[0]);
      feedbackEl.textContent = 'Pick the best answer to continue the streak!';
    } catch (error) {
      feedbackEl.textContent = error.message || 'Unable to fetch questions.';
    }
  };

  fetchButton.addEventListener('click', fetchQuestion);

  return {
    onChildSelected(childId) {
      currentChildId = childId;
      if (!childId) {
        reset();
        return;
      }
      emptyStateEl.textContent = 'Press “Fetch questions” to start practicing.';
      emptyStateEl.hidden = false;
      questionCard.hidden = true;
      feedbackEl.textContent = '';
    },
  };
};
