# Quiz Mode Progressive Rollout Guide

This document outlines the progressive rollout strategy for Quiz Mode, including internal testing (dogfooding), monitoring, and staged deployment.

## Feature Flag

Quiz Mode can be enabled or disabled using the `ENABLE_QUIZ_MODE` environment variable:

```bash
# Enable Quiz Mode (default)
ENABLE_QUIZ_MODE=1

# Disable Quiz Mode (for staged rollout or maintenance)
ENABLE_QUIZ_MODE=0
```

When disabled, all quiz endpoints return HTTP 503 (Service Unavailable) with the message:
> "Quiz Mode is currently disabled for maintenance. Please try again later."

## Phase 1: Internal Testing (Dogfooding)

### Prerequisites
- Backend deployed with `ENABLE_QUIZ_MODE=1`
- Frontend deployed with quiz UI components
- Monitoring and logging infrastructure in place
- At least 3 internal testers identified

### Testing Checklist

**Setup & Access**
- [ ] Verify quiz feature flag is enabled
- [ ] Confirm "Start Quiz" button visible on Dashboard
- [ ] Confirm active quiz badge displays correctly

**Quiz Creation Flow**
- [ ] Create quiz with default settings (10 questions, 10 minutes)
- [ ] Create quiz with minimum settings (5 questions, 5 minutes)
- [ ] Create quiz with maximum settings (30 questions, 120 minutes)
- [ ] Test custom difficulty mix (e.g., 50% hard, 50% medium)
- [ ] Verify cannot create duplicate active quiz (409 Conflict)

**Quiz Taking Flow**
- [ ] All questions visible on single page
- [ ] Can select answers for any question in any order
- [ ] Timer counts down correctly
- [ ] Timer syncs with backend (reload page to verify)
- [ ] Submit button works and shows confirmation
- [ ] Auto-submit triggers at 00:00
- [ ] Cannot interact with quiz after submission

**Results & Feedback**
- [ ] Score calculated correctly
- [ ] Incorrect items display with explanations
- [ ] Feedback modal appears after 2 seconds
- [ ] Can submit feedback with ratings and comments
- [ ] Can skip feedback without blocking
- [ ] Quiz history displays in ProgressPanel "Quizzes" tab

**Edge Cases**
- [ ] Network interruption during quiz (reload recovers state)
- [ ] Multiple tabs open (state syncs correctly)
- [ ] Expired quiz submission (410 Gone)
- [ ] Already submitted quiz resubmission (400 Bad Request)
- [ ] Question bank exhaustion (appropriate error message)

**Performance**
- [ ] Quiz loads in <2 seconds (20 questions)
- [ ] Submission processes in <1 second (20 answers)
- [ ] No UI freezing during answer selection
- [ ] Timer updates smoothly every second

**User Feedback Collection**
- [ ] At least 10 quizzes completed per tester
- [ ] Collect feedback on:
  - Was duration appropriate?
  - Were questions fair?
  - Overall rating (1-5 stars)
  - Free-form comments

### Success Criteria
- Zero critical bugs (data loss, crashes, auth bypass)
- 90%+ of users rate quiz mode 4+ stars
- Average duration rating: "just_right" (not too short or too long)
- Average fairness rating: "appropriate" (not too easy or too hard)
- Performance within targets (<2s create, <1s submit)

## Phase 2: Monitoring & Metrics

### Log Filtering

Quiz-related logs use structured prefixes for easy filtering:

**Quiz Operations**
```bash
# Filter all quiz logs
grep "\[QUIZ\]" /var/log/app.log

# Filter quiz creation
grep "\[QUIZ\] Creating quiz" /var/log/app.log

# Filter quiz submission
grep "\[QUIZ\] Submitting quiz" /var/log/app.log
grep "\[QUIZ\] Quiz .* graded" /var/log/app.log
```

**User Feedback**
```bash
# Filter all feedback
grep "\[QUIZ_FEEDBACK\]" /var/log/app.log

# Example output:
# [QUIZ_FEEDBACK] session_id=abc123 duration=just_right fairness=appropriate rating=5 has_comments=true
# [QUIZ_FEEDBACK] session_id=abc123 comments=Great experience! Questions were challenging but fair.
```

**Selection & Grading**
```bash
# Filter question selection logs
grep "\[PICKER\]" /var/log/app.log

# Filter grading logs (none currently, grading is inline)
```

### Key Metrics to Track

**Usage Metrics**
- Total quiz sessions created (per day/week)
- Quiz completions vs. expirations (completion rate)
- Average quiz duration (compare to configured duration)
- Questions per quiz (distribution: 5, 10, 15, 20, 25, 30)
- Popular subjects/topics for quiz mode

**Performance Metrics**
- P50, P95, P99 latency for `/quiz/sessions` (create)
- P50, P95, P99 latency for `/quiz/sessions/{id}/submit` (submit)
- Error rates by endpoint (target: <1%)
- 503 Service Unavailable count (when feature flag disabled)

**Quality Metrics**
- Average quiz score by grade level
- Average quiz score by subject
- Question bank exhaustion frequency (insufficient questions)
- Feedback ratings distribution:
  - Duration: too_short / just_right / too_long
  - Fairness: too_easy / appropriate / too_hard
  - Overall: 1-5 stars (target: avg ≥4.0)

**Error Monitoring**
- Quiz creation failures (400, 409, 500)
- Quiz submission failures (400, 410, 500)
- Question selection errors ("Insufficient questions available")
- OpenAI API failures (if generation fallback triggered)

### Alert Thresholds

**Critical Alerts** (immediate action required)
- Error rate >5% on any quiz endpoint
- P95 latency >5 seconds for quiz creation
- P95 latency >3 seconds for quiz submission
- Database connection failures
- Auth bypass detected (child doesn't belong to parent)

**Warning Alerts** (investigate within 24h)
- Error rate >2% on any quiz endpoint
- Completion rate <70% (high abandonment)
- Average feedback rating <3.5 stars
- Question bank exhaustion >10 times per day
- OpenAI API usage spike (>50 requests per day)

### Monitoring Commands

**Real-time Monitoring**
```bash
# Watch quiz creation in real-time
tail -f /var/log/app.log | grep "\[QUIZ\]"

# Watch feedback submissions
tail -f /var/log/app.log | grep "\[QUIZ_FEEDBACK\]"

# Watch errors
tail -f /var/log/app.log | grep "ERROR.*quiz"
```

**Daily Summary**
```bash
# Count quiz sessions created today
grep "\[QUIZ\] Created session" /var/log/app.log | grep "$(date +%Y-%m-%d)" | wc -l

# Count quiz submissions today
grep "\[QUIZ\] Quiz .* graded" /var/log/app.log | grep "$(date +%Y-%m-%d)" | wc -l

# Average feedback rating today
grep "\[QUIZ_FEEDBACK\].*rating=" /var/log/app.log | grep "$(date +%Y-%m-%d)" | \
  sed 's/.*rating=\([0-9]\).*/\1/' | awk '{sum+=$1; count++} END {print sum/count}'

# Duration feedback distribution
grep "\[QUIZ_FEEDBACK\].*duration=" /var/log/app.log | grep "$(date +%Y-%m-%d)" | \
  sed 's/.*duration=\([a-z_]*\).*/\1/' | sort | uniq -c
```

**Error Analysis**
```bash
# Count errors by type
grep "ERROR.*quiz" /var/log/app.log | grep "$(date +%Y-%m-%d)" | \
  sed 's/.*HTTPException(status_code=\([0-9]*\).*/\1/' | sort | uniq -c

# Find slow requests (>2s)
grep "\[QUIZ\]" /var/log/app.log | grep "$(date +%Y-%m-%d)" | \
  grep -E "took [2-9][0-9]{3}ms|took [0-9]{5,}ms"
```

## Phase 3: Staged Rollout

### Stage 1: Limited Beta (Week 1)
- Enable for 10% of users (via feature flag or user segment)
- Monitor error rates and performance daily
- Collect feedback from beta users
- Fix any critical bugs before expanding

**Validation Gates**
- No critical bugs reported
- Error rate <2%
- Average feedback rating ≥4.0
- Performance within targets

### Stage 2: Expanded Beta (Week 2)
- Enable for 50% of users
- Continue monitoring metrics
- Tune default settings based on feedback:
  - Adjust default duration if >30% say "too_short" or "too_long"
  - Adjust difficulty mix if >30% say "too_easy" or "too_hard"
- Update documentation with learnings

**Validation Gates**
- No new critical bugs
- Error rate <1.5%
- Completion rate ≥75%
- User satisfaction maintained (≥4.0 avg)

### Stage 3: Full Rollout (Week 3)
- Enable for 100% of users
- Update documentation and guides
- Announce feature publicly
- Monitor for 1 week before considering stable

**Validation Gates**
- Error rate <1%
- Performance stable
- User satisfaction maintained
- Support ticket volume manageable

## Phase 4: Continuous Improvement

### Feedback-Driven Tuning

**If feedback shows "duration too_short" >30%**
```bash
# Analysis
grep "duration=too_short" /var/log/app.log | wc -l

# Action: Increase default duration in .env.example
# Default: 600 seconds → 900 seconds (10 min → 15 min)
```

**If feedback shows "questions too_easy" >30%**
```bash
# Analysis
grep "fairness=too_easy" /var/log/app.log | wc -l

# Action: Adjust default difficulty mix in .env.example
# Default: 30% easy, 50% medium, 20% hard
# Adjusted: 20% easy, 50% medium, 30% hard
```

### A/B Testing Opportunities
- Test different default difficulty mixes by grade level
- Test different timer display styles (countdown vs. elapsed)
- Test feedback modal timing (immediate vs. 2s delay vs. 5s delay)
- Test question ordering (random vs. difficulty-sorted)

### Feature Enhancements (Post-Rollout)
- [ ] Quiz history export (PDF reports)
- [ ] Quiz scheduling (schedule quiz for specific date/time)
- [ ] Multiplayer quiz mode (compete with siblings)
- [ ] Quiz templates (save frequently used configurations)
- [ ] Adaptive quizzes (adjust difficulty mid-quiz based on performance)

## Rollback Plan

### When to Rollback
- Critical bug causing data loss or auth bypass
- Error rate >10% sustained for >15 minutes
- Database corruption or migration failure
- Widespread user complaints or negative feedback

### Rollback Procedure

**Immediate Rollback (Disable Feature)**
```bash
# Set feature flag to 0 (all quiz endpoints return 503)
export ENABLE_QUIZ_MODE=0

# Restart backend
systemctl restart studybuddy-backend

# Verify rollback
curl -i http://localhost:8000/quiz/sessions/
# Should return: 503 Service Unavailable
```

**Data Preservation**
- Quiz sessions table remains intact (no data loss)
- Users can still view historical quiz results
- New quiz creation disabled until issue resolved

**Communication**
- Update status page: "Quiz Mode temporarily disabled for maintenance"
- Notify users via in-app banner (if feature flag API exists)
- Provide ETA for resolution

### Post-Rollback Investigation
1. Review error logs for root cause
2. Reproduce bug in staging environment
3. Fix and test thoroughly
4. Deploy fix to staging
5. Re-enable for internal testers (dogfooding)
6. Re-enable for 10% of users (beta)
7. Monitor closely before full re-rollout

## Success Metrics (3 Months Post-Launch)

**Adoption**
- 50%+ of active users have tried quiz mode
- 20%+ of active users use quiz mode weekly
- Average 2+ quizzes per active user per week

**Quality**
- Average feedback rating ≥4.2 stars
- Completion rate ≥80%
- Error rate <0.5%
- P95 latency <1.5s for creation, <0.8s for submission

**Engagement**
- Users who try quiz mode have 20%+ higher overall engagement
- Quiz mode users complete 30%+ more practice questions overall
- Positive correlation between quiz usage and learning outcomes

## References

- Feature Implementation: `CLAUDE_PLAN_QUIZ`
- API Documentation: `USAGE_FILE.md` (Quiz Mode section)
- Environment Configuration: `.env.example`
- Backend Routes: `studybuddy/backend/routes/quiz.py`
- Frontend Components: `src/ui/web/src/pages/Quiz*.tsx`
- Monitoring Setup: This document (ROLLOUT_QUIZ_MODE.md)
