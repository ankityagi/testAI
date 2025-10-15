# StudyBuddy User Guide

## Overview
StudyBuddy is an adaptive learning platform that provides Common Core-aligned practice questions for K-12 students. The system uses AI-generated questions and intelligent difficulty progression to create personalized learning experiences.

---

## User Capabilities

### 1. Authentication & Account Management

#### Sign Up
- Create a parent account with email and password
- Password must be at least 6 characters
- Email validation is enforced

#### Log In
- Sign in with registered email and password
- Session persists across browser sessions
- Secure token-based authentication

#### Log Out
- End current session
- Clears authentication token

---

### 2. Child Profile Management

#### Add a Child
- **Name**: Required field
- **Grade**: Optional, 0-12 (K-12)
- **ZIP Code**: Optional, for future location-based features

#### View Children
- See all children associated with parent account
- Display shows: Name, Grade, ZIP code
- Visual indicator for selected child

#### Edit Child
- Update name, grade, or ZIP code
- Changes saved immediately

#### Delete Child
- Remove child profile
- **Warning**: All progress history is permanently deleted
- Confirmation required before deletion

#### Select Active Child
- Click "Select" button to make child active
- Only one child can be active at a time
- Active child highlighted in the list

---

### 3. Practice Sessions

#### Subject Selection
- **Available Subjects**:
  - Math
  - Reading
  - Science
  - Writing

#### Topic Selection
- **Dropdown populated based on**:
  - Selected subject
  - Child's grade level
- **Option**: "Random" - System auto-selects appropriate topic
- **Examples**:
  - Grade 3 Math: multiplication, division, fractions, geometry, measurement
  - Grade 1 Reading: phonics, comprehension, vocabulary, main idea

#### Subtopic Selection
- **Dropdown populated based on**:
  - Selected subject
  - Selected topic
  - Child's grade level
- **Option**: "Random" - System intelligently selects next subtopic
- **Smart Selection Algorithm**:
  - Prioritizes subtopics with more unseen questions
  - Follows pedagogical sequence order
- **Examples** (Grade 3 Math - Multiplication):
  - Introduction to Multiplication Facts (2s, 5s, and 10s)
  - Understanding Multiplication as Repeated Addition
  - Using Arrays to Represent Multiplication

#### Question Answering
- **Question Display**:
  - Question stem (main question text)
  - Multiple choice options (typically 4 choices)
  - Subject, topic, subtopic metadata
  - Difficulty level indicator (easy, medium, hard)
  - Question ID (first 8 characters, for debugging)

- **Interaction**:
  - Click any option to submit answer
  - Buttons disable immediately after click to prevent double-submission
  - Auto-advance to next question after 1.5 seconds

- **Feedback**:
  - **Correct Answer**: "Nice work! That answer is correct."
  - **Wrong Answer**: "Keep practicing! The correct answer was [correct answer]."

#### Adaptive Difficulty

The system automatically adjusts difficulty based on performance:

| Performance Level | Criteria | Question Difficulty Order |
|------------------|----------|---------------------------|
| **New Student** | No previous attempts | Easy → Medium |
| **Struggling** | < 60% accuracy | Easy only |
| **Good Performance** | ≥ 80% accuracy | Easy → Medium → Hard |
| **High Performance** | ≥ 95% accuracy AND ≥ 10 attempts | Medium → Hard → Easy |

**Key Features**:
- Performance calculated across ALL subjects/topics
- Real-time adjustment after each question
- Questions randomized to prevent repetition
- Only correct answers mark questions as "seen"

---

### 4. Progress Tracking

#### Overall Statistics
- **Total Questions Attempted**: Lifetime count
- **Correct Answers**: Total correct
- **Accuracy Percentage**: Overall accuracy rate
- **Current Streak**: Consecutive correct answers

#### Subject-Specific Breakdown
For each subject attempted:
- Number of correct answers
- Total questions attempted
- Accuracy percentage

#### Progress Updates
- Real-time updates after each question
- Visual display of statistics
- Streak tracking encourages consistency

---

### 5. Standards Reference

#### Browse Standards
- View Common Core standards
- Organized by:
  - Subject
  - Grade level
  - Domain and sub-domain
  - Standard reference code

#### Standard Details
- Standard title
- Full description
- Alignment with curriculum

---

### 6. Question Bank & AI Generation

#### Hybrid Question System

**Seeded Questions**:
- Pre-loaded, curriculum-aligned questions
- Quality-controlled content
- Diverse difficulty levels

**AI-Generated Questions**:
- **Automatic Generation**:
  - Triggers when inventory drops below 10 questions for a subtopic
  - Background generation maintains buffer
  - Instant generation if no questions available
- **Quality Features**:
  - Common Core aligned
  - Grade-appropriate
  - Includes rationale/explanation
  - Deduplication prevents repeats

#### Question Inventory Management
- **Per-Subtopic Buffer**: System maintains minimum 10 questions per subtopic
- **Proactive Restocking**: Background tasks generate questions asynchronously
- **Smart Deduplication**: Hash-based system prevents duplicate questions

---

### 7. Session Flow

#### Typical User Journey

1. **Login/Signup**
   - Parent creates account or logs in
   - Dashboard appears with children list

2. **Child Management**
   - Add child if first time
   - Set grade level for accurate question selection
   - Select active child

3. **Start Practice**
   - Subject selection (Math, Reading, Science, Writing)
   - Topic selection (grade-appropriate options appear)
   - Subtopic selection (fine-grained focus area)
   - Click "Fetch questions"

4. **Answer Questions**
   - Read question and options
   - Click answer
   - View immediate feedback
   - Auto-advance to next question (1.5s delay)
   - Continue practice session

5. **Monitor Progress**
   - View real-time statistics
   - Track accuracy and streaks
   - See subject-specific performance

---

## Technical Features (User-Visible)

### Smart Question Selection
- Never shows same question twice if answered correctly
- Randomized question order prevents patterns
- Subtopic progression follows educational best practices

### Session Persistence
- Login state saved across browser sessions
- Selected child remembered
- Progress tracked continuously

### Error Handling
- Clear error messages for failed operations
- Graceful fallbacks when questions unavailable
- Network error handling

### Performance
- Fast question loading (< 1 second typical)
- Background AI generation doesn't block user
- Efficient database queries

---

## User Interface Components

### Dashboard Layout

**Header Section**:
- Logged in as: [parent email]
- Child count display
- Logout button

**Children Panel**:
- List of all children
- Add child form (inline)
- Edit/Delete/Select buttons for each child
- Visual highlight for selected child

**Practice Session Panel**:
- Subject dropdown
- Topic dropdown (dynamically populated)
- Subtopic dropdown (dynamically populated)
- "Fetch questions" button
- Question card (when active):
  - Question metadata (subject, topic, subtopic, difficulty, ID)
  - Question stem
  - Answer options
  - Feedback message

**Progress Panel**:
- Overall statistics summary
- Subject-specific breakdown
- Visual indicators for performance

**Standards Reference Panel**:
- Browsable Common Core standards
- Filterable by grade/subject

---

## Data & Privacy

### What's Stored
- Parent email and hashed password
- Child profiles (name, grade, ZIP)
- Question attempts (question ID, answer, correctness, time)
- Seen questions (only correct answers)
- Session tokens

### What's NOT Stored
- Plain-text passwords
- Personal identifying information beyond email
- Question content viewed (only IDs)

---

## Best Practices for Users

### For Optimal Learning

1. **Set Accurate Grade Levels**
   - Ensures age-appropriate questions
   - Enables proper topic selection

2. **Use Topic/Subtopic Selection**
   - Target specific learning areas
   - Follow school curriculum
   - Use "Random" for mixed review

3. **Monitor Progress Regularly**
   - Track accuracy trends
   - Identify struggling subjects
   - Celebrate streaks

4. **Encourage Repeated Practice**
   - Wrong answers don't mark questions as "seen"
   - Students can retry until mastery
   - Adaptive difficulty ensures appropriate challenge

### For Parents

1. **Multiple Children**
   - Each child has independent progress tracking
   - Switch between children easily
   - Separate question history

2. **Grade Transitions**
   - Update child's grade as they advance
   - New topics automatically become available
   - Previous progress retained

3. **Subject Focus**
   - Use for targeted practice (e.g., "multiplication only")
   - Supplement homework or test prep
   - General review with random selection

---

## Future Enhancements (Roadmap)

*Note: These are planned features, not currently available*

- Performance reports and analytics
- Custom question sets
- Time-based challenges
- Achievement badges
- Parent-teacher progress sharing
- Offline mode
- Mobile app

---

## Troubleshooting

### "No questions available"
- **Cause**: Question bank empty for specific subtopic/grade
- **Solution**: Try different subtopic or use "Random" selection

### Questions repeating after wrong answers
- **Expected Behavior**: Questions only marked as "seen" when answered correctly
- **Purpose**: Allows mastery through repetition

### Can't see topics/subtopics
- **Check**: Child has grade level set
- **Check**: Selected subject has content for that grade
- **Solution**: Refresh page or select different subject

### Progress not updating
- **Check**: Correct child is selected
- **Solution**: Log out and log back in

---

## Contact & Support

For issues, feedback, or questions:
- GitHub Issues: [Repository Link]
- Email: [Support Email]

---

## Version Information

**Current Version**: 1.0
**Last Updated**: 2025-01-15
**Database**: PostgreSQL (Supabase)
**AI Model**: OpenAI GPT-4
**Framework**: FastAPI + Vanilla JavaScript
