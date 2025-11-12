# Topic Loading Logic Analysis

## Overview
Analysis of how topics are loaded and displayed in the Quiz Setup Modal, identifying cases where no topics may be shown to the user.

## The Flow

### 1. User Opens Quiz Modal
- User clicks "Start Quiz" button
- QuizSetupModal component mounts
- Default subject: `"Mathematics"`

### 2. Standards Loading Triggered
```typescript
useEffect(() => {
  if (!selectedChild || !subject) return;

  const loadStandards = async () => {
    const data = await standardsService.list(subject, selectedChild.grade);
    setStandards(data || []);
  };

  loadStandards();
}, [subject, selectedChild]);
```

### 3. API Call
```
GET /standards?subject=Mathematics&grade=3
```

### 4. Backend Processing
```python
# Normalize subject name
subject_normalized = "mathematics"

# Map to database format
subject_mappings = {
    'mathematics': 'math',
    'english language arts': 'reading',
    'ela': 'reading',
}
search_subject = "math"  # Mapped!

# Filter standards
standards = [s for s in standards if s.get('subject', '').lower() == 'math']
standards = [s for s in standards if s.get('grade') == 3]
```

### 5. Frontend Topic Extraction
```typescript
const safeStandards = Array.isArray(standards) ? standards : [];
const topics = Array.from(
  new Set(safeStandards.map((s) => s.domain).filter(Boolean))
) as string[];
```

### 6. UI Display
```typescript
{topics.length > 0 ? (
  <select>
    <option value="">Select a topic</option>
    {topics.map(t => <option key={t} value={t}>{t}</option>)}
  </select>
) : (
  <p>No topics available for this subject and grade</p>
)}
```

---

## Cases Where No Topics Are Shown

### ❌ Case 1: Subject Name Mismatch
**Before Fix:**
- Frontend: `subject="Mathematics"`
- Database: `subject="math"`
- Match: `"mathematics" == "math"` → **FALSE**
- Result: 0 standards returned

**After Fix:**
- Subject mapping: `"Mathematics" → "math"`
- Match: `"math" == "math"` → **TRUE**
- Result: Standards returned ✅

### ❌ Case 2: No Standards for Grade
**Scenario:** Child is grade 5, but only grade 1-3 standards exist
```python
# Child grade: 5
# Available grades: [1, 2, 3]
# Filter: s.get('grade') == 5
# Result: Empty array
```

**User sees:**
> "No topics available for this subject and grade"

**Solution:** Need to seed standards for all grades (K-12)

### ❌ Case 3: Domain Field is Null/Empty
**Scenario:** Standards exist but `domain` field is missing
```javascript
// Standard: { subject: 'math', grade: 3, domain: null }
// After filter(Boolean): domain is filtered out
// Result: Empty topics array
```

**User sees:**
> "No topics available for this subject and grade"

**Solution:** Ensure all standards have populated `domain` field

### ❌ Case 4: Empty Standards Database
**Scenario:** Repository returns empty array
```python
standards = repo.list_standards()  # Returns []
```

**User sees:**
> "No topics available for this subject and grade"

**Solution:** Run database seed scripts

### ❌ Case 5: API Call Fails
**Scenario:** Network error or backend down
```typescript
catch (err) {
  setStandardsError('Failed to load topics');
  setStandards([]); // Empty array
}
```

**User sees:**
> Error message: "Failed to load topics"

### ❌ Case 6: No Child Selected
**Scenario:** User hasn't added/selected a child yet
```typescript
if (!selectedChild || !subject) return; // Exit early
```

**User sees:**
> "Select a topic" dropdown remains but loads forever

**Solution:** Dashboard should require child before showing "Start Quiz"

### ⚠️ Case 7: Standards for Subject but Not Grade
**Scenario:** Math standards exist for grades 1-6, child is grade 7
```python
# Subject filter: ✅ Returns math standards
# Grade filter: ❌ Filters out all (no grade 7)
# Result: Empty array
```

**User sees:**
> "No topics available for this subject and grade"

**Partial Fix:** Show "No topics for grade X" instead of generic message

---

## Testing Checklist

- [ ] Test with "Mathematics" → should show math topics
- [ ] Test with "English Language Arts" → should show reading topics
- [ ] Test with grade 1 child → should show grade 1 topics
- [ ] Test with grade 12 child → should show appropriate message if no standards
- [ ] Test with no child selected → should not attempt to load
- [ ] Test with backend down → should show error message
- [ ] Test subject switching → should reload topics for new subject
- [ ] Test grade switching (by changing child) → should reload topics

---

## Data Requirements

### Standards Database Must Have:
1. ✅ `subject` field populated (lowercase: 'math', 'reading', 'science', 'social studies')
2. ✅ `grade` field populated (0-12)
3. ✅ `domain` field populated (becomes "topic" in UI)
4. ⚠️ `sub_domain` field (optional, becomes "subtopic")

### Current Data Status:
- Total standards: 2
- Subjects: 'math', 'reading'
- Grades: [1]
- Domains: ['Operations & Algebraic Thinking']

**Action Required:** Seed more standards for grades 1-12 across all subjects

---

## Fix Summary

### ✅ Fixed Issues:
1. Subject name mapping ('Mathematics' → 'math')
2. Defensive type checking (Array.isArray)
3. Error handling sets empty array

### ⚠️ Remaining Issues:
1. Limited standards data (only grade 1)
2. Generic error messages
3. No feedback when grade has no standards

### 📋 Future Improvements:
1. Better error messages: "No topics available for Mathematics grade 7"
2. Fallback to nearest grade if exact grade not found
3. Show "Coming soon" message for unsupported subjects
4. Preload standards on app init to detect data issues early
