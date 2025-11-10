# StudyBuddy iOS Conversion Plan

**Document Version**: 1.0
**Created**: 2025-11-10
**Status**: Planning Phase
**Target**: iOS 17.0+ (iPhone and iPad)

---

## Executive Summary

This document outlines the high-level strategy for converting the StudyBuddy web application (React + FastAPI) into a native iOS mobile application. The conversion will leverage the existing backend infrastructure while building a new native iOS frontend that provides an enhanced mobile-first experience with offline capabilities, push notifications, and native iOS integrations.

**Key Goals:**
- Maintain 100% feature parity with web version
- Leverage existing FastAPI backend with minimal modifications
- Build native iOS UI with SwiftUI for optimal performance
- Add mobile-specific features (offline mode, push notifications, Face ID)
- Ensure seamless data synchronization across platforms

---

## Current Architecture Assessment

### Web Application Stack
```
Frontend:  React 19 + TypeScript + Vite
Backend:   FastAPI (Python 3.11+) + Pydantic v2
Database:  PostgreSQL (Supabase)
AI:        OpenAI GPT-4 for question generation
Auth:      Token-based (bearer tokens)
Hosting:   Render.com
```

### Core Features
1. **Authentication**: Email/password with bearer token validation
2. **Child Management**: CRUD operations for child profiles with grade tracking
3. **Adaptive Practice Sessions**:
   - Subject/topic/subtopic selection
   - Dynamic difficulty adjustment based on performance
   - Real-time question delivery with immediate feedback
4. **Progress Tracking**: Accuracy metrics, streaks, subject-level breakdowns
5. **AI Question Generation**: OpenAI-powered with fallback to seeded questions
6. **Standards Alignment**: Eureka Math + Common Core standards

### API Endpoints (Existing)
```
/auth/signup              POST    Create parent account
/auth/login               POST    Authenticate parent
/children                 GET     List children
/children                 POST    Create child profile
/children/{id}            PUT     Update child profile
/children/{id}            DELETE  Remove child profile
/questions/fetch          POST    Fetch adaptive questions
/attempts                 POST    Log question attempts
/progress/{child_id}      GET     Retrieve progress stats
/standards                GET     Fetch standards reference
/admin/generate           POST    Generate question batches
/sessions                 GET     Get session history
/quiz/*                   *       Quiz mode endpoints
```

### What Works Well (Reusable)
✅ **Backend API** - RESTful design, well-documented, stateless
✅ **Data Models** - Pydantic schemas map cleanly to Swift structs
✅ **Authentication** - Token-based auth works perfectly with mobile
✅ **Business Logic** - Adaptive difficulty, question picking, progress tracking
✅ **Database** - Supabase works identically for mobile clients

### What Needs Rethinking
⚠️ **Frontend** - Complete rebuild with SwiftUI
⚠️ **Offline Mode** - Web has no offline support; iOS should cache content
⚠️ **Push Notifications** - Not applicable to web; critical for mobile engagement
⚠️ **Local Storage** - Web uses localStorage; iOS needs Core Data or SwiftData
⚠️ **Session Management** - Mobile apps need more robust background handling

---

## iOS Architecture Proposal

### Technology Stack

#### Frontend (Native iOS)
```
Language:       Swift 6.0+
UI Framework:   SwiftUI (iOS 17+)
Navigation:     NavigationStack + Routing
State:          Observation framework (@Observable)
Networking:     URLSession + async/await
Storage:        SwiftData (iOS 17+) for local persistence
Security:       Keychain for token storage
Auth:           Face ID / Touch ID support
```

#### Backend (Existing - Minimal Changes)
```
API:            FastAPI (no changes to core endpoints)
New Features:   Push notification service (APNs integration)
                Webhook for real-time updates (optional)
```

### Architectural Patterns

#### 1. **MVVM + Repository Pattern**
```
View Layer:         SwiftUI Views (stateless, declarative)
ViewModel Layer:    @Observable ViewModels (state management)
Repository Layer:   Network + Local data sources
Service Layer:      API client, auth, storage services
```

#### 2. **Offline-First Architecture**
```
┌─────────────────┐
│   SwiftUI View  │
└────────┬────────┘
         │
┌────────▼────────┐
│   ViewModel     │  (Publishes UI state)
└────────┬────────┘
         │
┌────────▼────────┐
│   Repository    │  (Coordinates data sources)
└────┬───────┬────┘
     │       │
┌────▼───┐  │  ┌────▼────────┐
│ Local  │  │  │   Remote    │
│ (Cache)│◄─┴──│  (FastAPI)  │
└────────┘     └─────────────┘
```

#### 3. **Data Synchronization Strategy**
- **Write-through**: Optimistic updates to local cache, background sync to server
- **Read strategy**: Check local cache first, fetch from API if stale
- **Conflict resolution**: Server wins (last-write-wins)
- **Sync triggers**: App launch, foreground transition, manual refresh

---

## Development Phases

### Phase 0: Foundation & Setup (2-3 weeks)
**Goal**: Set up iOS project structure, networking, and authentication

#### Deliverables
- [ ] Create Xcode project with SwiftUI + iOS 17 target
- [ ] Set up project structure (MVVM folders, dependency injection)
- [ ] Implement API client layer with URLSession
- [ ] Create Swift models matching Pydantic schemas
- [ ] Build authentication service (login, signup, token management)
- [ ] Implement Keychain storage for secure token persistence
- [ ] Add Face ID / Touch ID biometric authentication
- [ ] Create reusable UI components library (Button, Card, Input, etc.)

#### Key Files
```
StudyBuddyApp/
  App/
    StudyBuddyApp.swift              # App entry point
    AppEnvironment.swift             # Dependency injection
  Models/
    Parent.swift                      # User model
    Child.swift                       # Child profile
    Question.swift                    # Question data
    Progress.swift                    # Progress tracking
  Services/
    APIClient.swift                   # Network layer
    AuthService.swift                 # Authentication
    KeychainService.swift             # Secure storage
  Repositories/
    AuthRepository.swift
    ChildRepository.swift
  ViewModels/
    AuthViewModel.swift
  Views/
    Auth/
      LoginView.swift
      SignupView.swift
  Resources/
    Assets.xcassets
```

#### API Requirements
- ✅ No backend changes needed
- Document API response formats for Swift codegen

---

### Phase 1: Core Features - Child Management (2-3 weeks)
**Goal**: Implement child profile CRUD operations with local caching

#### Deliverables
- [ ] Implement SwiftData schema for local child storage
- [ ] Build ChildRepository with offline-first logic
- [ ] Create ChildrenListView (equivalent to ChildrenPanel)
- [ ] Create AddChildView and EditChildView forms
- [ ] Implement pull-to-refresh and optimistic updates
- [ ] Add grade picker with visual design
- [ ] Implement child profile deletion with confirmation
- [ ] Add empty state illustrations

#### Key Screens
```
ChildrenListView
├── Navigation bar with "Add" button
├── List of child cards (name, grade, avatar)
├── Swipe actions (edit, delete)
└── Empty state with call-to-action

AddChildView (Sheet)
├── Name input field
├── Grade picker (K-12)
├── Birthdate picker (optional)
├── ZIP code input (optional)
└── Save/Cancel buttons
```

#### API Endpoints Used
- `GET /children` - Fetch all children
- `POST /children` - Create child
- `PUT /children/{id}` - Update child
- `DELETE /children/{id}` - Delete child

---

### Phase 2: Practice Sessions - Question Flow (3-4 weeks)
**Goal**: Build adaptive practice session with real-time question delivery

#### Deliverables
- [ ] Implement QuestionRepository with caching
- [ ] Build quiz setup flow (subject/topic/subtopic selection)
- [ ] Create PracticeSessionView (question display)
- [ ] Implement answer selection with visual feedback
- [ ] Add progress indicator (X of Y questions)
- [ ] Build answer submission and validation
- [ ] Create immediate feedback modal (correct/incorrect)
- [ ] Implement session completion flow
- [ ] Add question prefetching for smooth UX
- [ ] Cache questions for offline practice

#### Key Screens
```
QuizSetupView
├── Child selector (if multiple children)
├── Subject picker (Math, ELA, Science, etc.)
├── Topic dropdown
├── Subtopic dropdown
└── "Start Practice" button

PracticeSessionView
├── Progress indicator (3/10)
├── Question stem (LaTeX support if needed)
├── Answer options (A, B, C, D)
├── Submit button
└── Skip button (optional)

FeedbackModal (overlay)
├── Correct/Incorrect indicator
├── Explanation/rationale
├── "Next Question" button
└── "End Session" button
```

#### API Endpoints Used
- `POST /questions/fetch` - Fetch questions with adaptive difficulty
- `POST /attempts` - Log answer attempts
- `GET /standards` - Display aligned standards

#### Offline Considerations
- Cache last 50 questions per subject per child
- Pre-fetch questions when online for offline use
- Queue attempts locally, sync when connection restored

---

### Phase 3: Progress Tracking & Analytics (2 weeks)
**Goal**: Display comprehensive progress metrics and historical data

#### Deliverables
- [ ] Implement ProgressRepository with local aggregation
- [ ] Build ProgressDashboardView (equivalent to ProgressPanel)
- [ ] Create subject-level breakdown views
- [ ] Add accuracy percentage displays with visual indicators
- [ ] Implement streak tracking (current/best)
- [ ] Build session history list
- [ ] Create detailed session view (review questions)
- [ ] Add charts/graphs for progress over time
- [ ] Implement pull-to-refresh for latest data

#### Key Screens
```
ProgressDashboardView
├── Overall Stats Card
│   ├── Total accuracy percentage
│   ├── Current streak
│   └── Questions answered count
├── Subject Breakdown (List)
│   ├── Math: 85% | 42 questions
│   ├── ELA: 92% | 38 questions
│   └── Science: 78% | 25 questions
└── Session History (Timeline)
    └── [Date] Math | 8/10 correct

SessionDetailView
├── Session metadata (date, duration, subject)
├── Question list with correctness indicators
└── Option to retry missed questions
```

#### API Endpoints Used
- `GET /progress/{child_id}` - Fetch progress stats
- `GET /sessions` - Fetch session history

---

### Phase 4: Mobile-Specific Enhancements (2-3 weeks)
**Goal**: Add features that differentiate mobile from web

#### Deliverables
- [ ] **Push Notifications**
  - Daily practice reminders
  - Streak maintenance alerts
  - New question availability notifications
  - Achievement unlocks
- [ ] **Widgets** (iOS Home Screen)
  - Current streak widget
  - Quick start practice widget
- [ ] **Shortcuts Integration**
  - Siri shortcuts for "Start practice session"
- [ ] **Haptic Feedback**
  - Correct answer: success haptic
  - Incorrect answer: error haptic
  - Session complete: notification haptic
- [ ] **Accessibility**
  - VoiceOver support for all screens
  - Dynamic Type support
  - High contrast mode
- [ ] **Share Sheet**
  - Share progress reports with parents
  - Export session results as PDF

#### Backend Changes Required
```python
# New endpoint for push notification registration
POST /devices/register
{
  "device_token": "APNs token",
  "parent_id": "uuid",
  "preferences": {
    "daily_reminder": true,
    "streak_alerts": true
  }
}

# New notification service
studybuddy/backend/services/notifications.py
- send_push_notification()
- schedule_daily_reminder()
- send_streak_alert()
```

---

### Phase 5: Offline Mode & Sync (2 weeks)
**Goal**: Robust offline support with intelligent sync

#### Deliverables
- [ ] Implement comprehensive caching strategy
- [ ] Build sync queue for offline actions
- [ ] Create conflict resolution logic
- [ ] Add network status monitoring
- [ ] Display offline indicator in UI
- [ ] Implement background refresh (BGTaskScheduler)
- [ ] Add manual sync button
- [ ] Handle auth token expiration gracefully

#### Sync Strategy
```
Actions to Queue Offline:
- Create/Update/Delete child profiles
- Submit question attempts
- Update child grades

Sync Priority:
1. Authentication (refresh token if expired)
2. Child profile changes (CUD operations)
3. Question attempts (bulk submission)
4. Fetch latest questions/progress

Error Handling:
- Retry with exponential backoff
- Show sync status in Settings
- Allow user to clear failed items
```

---

### Phase 6: Polish & App Store Prep (2-3 weeks)
**Goal**: Production-ready app with App Store assets

#### Deliverables
- [ ] **UI Polish**
  - Smooth animations and transitions
  - Loading states for all async operations
  - Error states with retry actions
  - Empty states with helpful illustrations
- [ ] **Onboarding Flow**
  - Welcome screens explaining features
  - Permission requests (notifications, Face ID)
  - Quick start tutorial
- [ ] **Settings Screen**
  - Account management
  - Child profiles shortcut
  - Notification preferences
  - About/Help/Privacy Policy
  - Logout option
- [ ] **App Store Assets**
  - App icon (1024x1024)
  - Screenshots (iPhone and iPad)
  - Privacy nutrition label
  - App description and keywords
  - Promotional text
- [ ] **Testing**
  - Unit tests for ViewModels and Services
  - UI tests for critical flows (XCTest)
  - TestFlight beta testing
- [ ] **Performance Optimization**
  - Image caching and optimization
  - Launch time optimization
  - Memory profiling
  - Battery usage analysis

---

## Key Technical Considerations

### 1. Authentication & Security

#### Token Management
```swift
// Store token in Keychain, not UserDefaults
KeychainService.shared.save(token, for: "auth_token")

// Biometric unlock
let context = LAContext()
context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics) { success, error in
    if success {
        // Unlock app and fetch token
    }
}
```

#### Token Refresh Strategy
- Check token expiration on app foreground
- Refresh proactively before expiration
- Gracefully handle 401 responses and re-authenticate

### 2. Offline Data Storage

#### SwiftData Models
```swift
@Model
final class Child {
    @Attribute(.unique) var id: String
    var name: String
    var grade: Int?
    var birthdate: Date?
    var parentId: String
    var syncStatus: SyncStatus // .synced, .pending, .failed
    var lastModified: Date
}

@Model
final class CachedQuestion {
    @Attribute(.unique) var id: String
    var subject: String
    var topic: String?
    var subtopic: String?
    var stem: String
    var options: [String]
    var correctAnswer: String
    var cachedAt: Date
    var childId: String
}

@Model
final class PendingAttempt {
    var questionId: String
    var childId: String
    var selectedAnswer: String
    var isCorrect: Bool
    var timestamp: Date
    var syncStatus: SyncStatus
}
```

#### Cache Invalidation
- Questions: 7-day TTL
- Progress data: 1-hour TTL
- Child profiles: Persist until deleted, sync on change

### 3. Network Layer

#### API Client Implementation
```swift
actor APIClient {
    private let baseURL = "https://api.studybuddy.com"
    private let session: URLSession

    func request<T: Decodable>(
        _ endpoint: Endpoint,
        as type: T.Type
    ) async throws -> T {
        var request = URLRequest(url: endpoint.url)
        request.httpMethod = endpoint.method.rawValue

        // Add auth token
        if let token = KeychainService.shared.getToken() {
            request.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.httpError(httpResponse.statusCode)
        }

        return try JSONDecoder().decode(T.self, from: data)
    }
}
```

### 4. State Management

#### Observable ViewModels
```swift
@Observable
final class PracticeViewModel {
    private let repository: QuestionRepository

    var questions: [Question] = []
    var currentQuestionIndex = 0
    var answers: [String: String] = [:]
    var isLoading = false
    var errorMessage: String?

    @MainActor
    func fetchQuestions(for child: Child, subject: String) async {
        isLoading = true
        defer { isLoading = false }

        do {
            questions = try await repository.fetchQuestions(
                childId: child.id,
                subject: subject,
                limit: 10
            )
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    @MainActor
    func submitAnswer(_ answer: String) async {
        let question = questions[currentQuestionIndex]
        answers[question.id] = answer

        do {
            try await repository.logAttempt(
                questionId: question.id,
                childId: currentChildId,
                answer: answer,
                isCorrect: answer == question.correctAnswer
            )
            currentQuestionIndex += 1
        } catch {
            errorMessage = "Failed to submit answer"
        }
    }
}
```

### 5. Push Notifications

#### Backend Setup (Python/FastAPI)
```python
# Install APNs library
# pip install aioapns

from aioapns import APNs, NotificationRequest

async def send_practice_reminder(device_token: str, child_name: str):
    apns = APNs(
        key="path/to/key.p8",
        key_id="KEY_ID",
        team_id="TEAM_ID",
        topic="com.studybuddy.app",
        use_sandbox=False
    )

    notification = NotificationRequest(
        device_token=device_token,
        message={
            "aps": {
                "alert": {
                    "title": "Practice Time!",
                    "body": f"Help {child_name} keep their streak alive!"
                },
                "sound": "default",
                "badge": 1
            },
            "type": "practice_reminder"
        }
    )

    await apns.send_notification(notification)
```

#### iOS Setup
```swift
// Register for notifications
UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge])

// Handle device token
func application(
    _ application: UIApplication,
    didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
) {
    let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
    Task {
        try await APIClient.shared.registerDevice(token: token)
    }
}
```

---

## API Modifications Required

### New Endpoints

#### 1. Device Registration (Push Notifications)
```
POST /devices/register
Authorization: Bearer <token>

Request:
{
  "device_token": "apns_token_string",
  "platform": "ios",
  "preferences": {
    "daily_reminder": true,
    "streak_alerts": true,
    "new_questions": false
  }
}

Response: 204 No Content
```

#### 2. Batch Sync Endpoint (Optional Optimization)
```
POST /sync/batch
Authorization: Bearer <token>

Request:
{
  "since": "2025-11-10T12:00:00Z",
  "entities": ["children", "attempts", "progress"]
}

Response:
{
  "children": [...],
  "attempts": [...],
  "progress": {...},
  "server_timestamp": "2025-11-10T12:05:00Z"
}
```

### Existing Endpoints - Modifications

#### 1. Add Pagination Support
```
GET /children?limit=20&offset=0
GET /sessions?child_id=<id>&limit=50&offset=0
```

#### 2. Add Field Filtering (Optional)
```
GET /progress/{child_id}?fields=overall_accuracy,streak,subject_breakdown
```

#### 3. Return Timestamps
Ensure all responses include `updated_at` or `last_modified` timestamps for sync logic.

---

## Testing Strategy

### Unit Tests
```
Target: 80% code coverage

Test Coverage:
- ViewModels: All business logic and state transitions
- Repositories: Network + local data source coordination
- Services: Authentication, API client, storage
- Models: Data transformations and validation
```

### UI Tests
```
Critical Flows to Test:
✓ Signup and login
✓ Add child profile
✓ Start practice session
✓ Answer questions and get feedback
✓ View progress dashboard
✓ Offline mode behavior
✓ Sync after reconnection
```

### Manual Testing
```
Devices:
- iPhone SE (small screen)
- iPhone 15 Pro (standard)
- iPad Air (tablet)

iOS Versions:
- iOS 17.0 (minimum)
- iOS 18.x (latest)

Scenarios:
- Fresh install
- Offline usage
- Background app refresh
- Push notification delivery
- Token expiration handling
- Low battery mode
```

### Beta Testing (TestFlight)
```
Audience:
- Internal team (5-10 users)
- Parent beta testers (20-30 users)

Duration: 2-3 weeks

Feedback Collection:
- In-app feedback form
- TestFlight feedback
- Analytics (Crashlytics)
```

---

## Deployment Strategy

### Development Environment
```
API: Development Render instance (dev.studybuddy.com)
Database: Supabase development project
Push: APNs Sandbox
```

### Staging Environment
```
API: Staging Render instance (staging.studybuddy.com)
Database: Supabase staging project
Push: APNs Sandbox
TestFlight: Internal testing
```

### Production Environment
```
API: Production Render instance (api.studybuddy.com)
Database: Supabase production project
Push: APNs Production
App Store: Public release
```

### CI/CD Pipeline
```
1. Code pushed to GitHub
2. GitHub Actions runs:
   - Swift linter (SwiftLint)
   - Unit tests (XCTest)
   - Build for testing
3. On release branch:
   - Build archive
   - Upload to TestFlight
4. Manual promotion to App Store
```

### App Store Submission Checklist
- [ ] App Privacy Policy URL
- [ ] Support URL
- [ ] Age rating (4+)
- [ ] Categories (Education, Kids)
- [ ] Keywords and description
- [ ] Screenshots (5.5", 6.5", 6.7" + iPad)
- [ ] App preview video (optional)
- [ ] COPPA compliance review
- [ ] Export compliance documentation

---

## Timeline & Resource Estimation

### Development Timeline
```
Phase 0: Foundation & Setup           2-3 weeks
Phase 1: Child Management             2-3 weeks
Phase 2: Practice Sessions            3-4 weeks
Phase 3: Progress Tracking            2 weeks
Phase 4: Mobile Enhancements          2-3 weeks
Phase 5: Offline Mode & Sync          2 weeks
Phase 6: Polish & App Store Prep      2-3 weeks
────────────────────────────────────────────────
Total:                                15-20 weeks
```

### Team Requirements
```
Core Team:
- 1 Senior iOS Developer (SwiftUI, iOS SDK)
- 1 Backend Developer (Python/FastAPI - for push notifications)
- 1 UI/UX Designer (iOS Human Interface Guidelines)
- 1 QA Engineer (TestFlight, manual testing)

Part-time:
- Product Manager (prioritization, App Store submission)
- DevOps Engineer (CI/CD setup)
```

### Infrastructure Costs
```
Monthly Costs:
- Apple Developer Program: $99/year (~$8/month)
- TestFlight: Included in Developer Program
- Push Notification Service: Free (APNs)
- Additional Render instance (optional): $7-25/month
- Total: ~$15-35/month additional to existing infrastructure
```

---

## Risk Assessment & Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SwiftData stability issues | Medium | High | Have Core Data fallback plan |
| API rate limiting on mobile | Low | Medium | Implement exponential backoff |
| Offline sync conflicts | Medium | Medium | Server-wins strategy documented |
| Push notification delivery | Low | Low | Provide in-app fallback reminders |
| App Store rejection | Low | High | Follow HIG strictly, legal review |

### Product Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Feature parity delays | Medium | Medium | MVP-first approach, iterate |
| User adoption low | Medium | High | Soft launch, marketing plan |
| Performance on older devices | Low | Medium | Test on iPhone SE, optimize |
| COPPA compliance issues | Low | High | Legal review before submission |

---

## Success Metrics

### Development KPIs
- Code coverage: >80%
- Crash-free rate: >99.5%
- App launch time: <2 seconds
- TestFlight builds: Weekly cadence

### Product KPIs (Post-Launch)
- App Store rating: >4.5 stars
- Daily active users: Track engagement
- Session completion rate: >80%
- Offline usage: >20% of sessions
- Push notification opt-in: >60%

---

## Future Considerations (Post-V1)

### Phase 7: iPad Optimization
- Split-view layouts
- Pencil support for math problems
- Multi-child dashboard

### Phase 8: Gamification
- Achievement badges
- Leaderboards (family-only)
- Avatar customization
- Reward system

### Phase 9: Parent Dashboard
- Email reports
- Progress insights
- Weak area identification
- Curriculum recommendations

### Phase 10: watchOS Companion
- Quick practice sessions (5 questions)
- Streak tracking
- Reminder complications

---

## Appendix

### A. Glossary
- **APNs**: Apple Push Notification service
- **SwiftData**: Apple's modern persistence framework (iOS 17+)
- **MVVM**: Model-View-ViewModel architectural pattern
- **Repository Pattern**: Abstraction layer for data access
- **TestFlight**: Apple's beta testing platform

### B. References
- [iOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui)
- [SwiftData Documentation](https://developer.apple.com/documentation/swiftdata)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)

### C. Key Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-11-10 | Use SwiftUI over UIKit | Modern, declarative, less boilerplate |
| 2025-11-10 | Use SwiftData over Core Data | iOS 17+ target, simpler API, future-proof |
| 2025-11-10 | Reuse existing FastAPI backend | Proven, stable, minimal changes needed |
| 2025-11-10 | Offline-first architecture | Better UX, works in low connectivity |

---

## Next Steps

### Immediate Actions (Week 1)
1. ✅ Create this plan document
2. ⏳ Review and approve plan with stakeholders
3. ⏳ Set up Xcode project with initial structure
4. ⏳ Create GitHub repository for iOS app
5. ⏳ Set up Apple Developer account and App Store Connect
6. ⏳ Design initial UI mockups for core screens
7. ⏳ Create iOS branch in backend repo for API modifications
8. ⏳ Schedule kickoff meeting with iOS development team

### Phase 0 Kickoff (Week 2)
- Implement networking layer and models
- Build authentication flow
- Set up CI/CD pipeline
- Begin UI component library

---

**Document Ownership**: Engineering Team
**Review Cycle**: Bi-weekly during development
**Approval Required**: Product Manager, CTO, Lead iOS Developer
