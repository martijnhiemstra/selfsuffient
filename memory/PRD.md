# Earthly Life - Product Requirements Document

## Overview
A full-stack application to help users setup and maintain a sustainable, self-sufficient lifestyle, with project management, diaries, galleries, blogs, libraries, task management, daily routines, and financial tracking.

## Original Problem Statement
Build an application that helps users setup a self-sufficient lifestyle with:
- User authentication (Login and forgot password, no registration)
- Projects with name, description, image, public/private settings
- Diary with searchable/sortable entries per project
- Gallery with recursive folders and searchable/sortable images
- Blog with public/private entries and view counts
- Library with recursive folders and public/private entries
- HTML editor for all description fields
- Calendar with month/week/day views, recurrence, and drag-and-drop
- Daily startup and shutdown task lists
- Public landing page showing public projects, blogs, and libraries
- User dashboard showing undone routines and today's tasks
- Daily reminder emails (opt-in)
- Docker containerization

## Tech Stack
- **Frontend**: React, React Router, Axios, Tailwind CSS, Shadcn/UI, TipTap editor
- **Backend**: FastAPI, MongoDB (motor), Pydantic, JWT authentication
- **Containerization**: Docker, Docker Compose
- **Scheduled Tasks**: Cron (inside backend container)

## Code Architecture
```
/app/
├── backend/
│   ├── server.py           # Main FastAPI app entry point
│   ├── config.py           # Configuration and database connection
│   ├── models/             # Pydantic models
│   ├── routes/             # API route handlers
│   │   ├── checklist.py    # Project checklists
│   │   ├── gallery.py      # Gallery with folder support
│   │   ├── google_calendar.py # Google Calendar sync
│   │   ├── import_transactions.py # Transaction imports with AI
│   │   └── openai_settings.py # NEW: User OpenAI API key management
│   └── services/
│       ├── google_calendar.py
│       └── openai_analyzer.py  # NEW: AI transaction analysis
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── components/
│   │   │   └── PWAInstallPrompt.jsx  # PWA install prompt
│   │   ├── serviceWorkerRegistration.js  # PWA service worker
│   │   └── pages/
│   │       ├── ChecklistsPage.jsx    # Nested under projects
│   │       ├── FinancePage.jsx       # Full budgeting + AI import
│   │       └── SettingsPage.jsx      # OpenAI API key config
│   └── public/
│       ├── manifest.json      # PWA manifest
│       ├── service-worker.js  # Service worker for offline
│       └── icons/             # PWA icons (72-512px)
└── memory/PRD.md
```

## Completed Features ✅

### Core Features
1. **Authentication** ✅ - JWT login, password reset via SMTP
2. **Projects** ✅ - Full CRUD with image upload, public/private
3. **Diary** ✅ - Searchable/sortable entries
4. **Gallery** ✅ - Recursive folders, public support, breadcrumbs
5. **Blog** ✅ - Public/private entries, view counts
6. **Library** ✅ - Recursive folders, public/private, view counts
7. **Tasks & Calendar** ✅ - Drag-and-drop, recurrence
8. **Daily Routines** ✅ - Start/End of Day items with tracking
9. **Public Site** ✅ - Landing page, user profiles, project pages
10. **Dashboard** ✅ - Today's tasks, incomplete routines
11. **Daily Reminders** ✅ - Opt-in email via cron
12. **Docker** ✅ - Full containerization

### Financial Module ✅
- Account management (multiple accounts with balances)
- Transaction tracking (income/expenses with categories)
- Savings goals with progress tracking
- Expense Periods with budgeting
- Budget comparison view
- Monthly overview with category breakdown
- Financial runway calculation
- Transaction import (CSV, OFX, QFX files)

### AI Transaction Analysis ✅ - Feb 13, 2026
- **User-provided OpenAI API keys** - Each user configures their own key in Settings
- **Model selection** - GPT-4o-mini, GPT-4o, GPT-4-turbo, GPT-3.5-turbo
- **During import preview**, users can click "Analyze with AI" to:
  - Auto-categorize transactions (income/expense, category)
  - Detect recurring transactions (subscriptions, bills, salary)
  - Flag unusual amounts compared to historical patterns
- **Encrypted storage** of API keys per user
- **Test key** functionality to validate before saving

### Project Checklists ✅
- Reusable checklists within projects
- Checklist items with toggle completion
- Progress tracking (completed/total)
- Reset functionality
- Nested route: `/projects/:projectId/checklists`

### Google Calendar Integration ✅
- User-provided OAuth credentials
- One-way sync (tasks/routines to Google Calendar)
- Stored per-user credentials

### Progressive Web App (PWA) ✅ - Feb 11, 2026
- Web app manifest with app info and icons
- Service worker for offline caching
- Multiple icon sizes (72px - 512px)
- Apple touch icon support
- Install prompt component

## Recent Bug Fixes
- **Gallery Upload Bug** (Feb 11, 2026) - Fixed folder_id not being passed during subfolder uploads
- **Google Libraries Missing** (Feb 13, 2026) - Added google-api-python-client and related packages to requirements.txt

### AI Garden Designer - Feb 15, 2026
- **Phase 1 (Canvas):** Interactive Konva.js drawing tool with configurable grid scale, snap-to-grid, polygon closure detection, real-time measurements (area, perimeter)
- **Phase 2 (Input Form):** GPS coordinates, wind direction, garden goal selection, plant preferences, existing features, custom notes
- **Phase 3 (AI Generation):** Backend service using user's OpenAI API key. Frontend integrates generate button with loading state, error handling (API key missing), and full results display: design summary, sun/wind/climate analysis, plant list table, garden zones, planting tips, seasonal tasks
- **Phase 4 (Visual Output):** Renders AI-generated plants as colored circles on the Konva canvas at suggested coordinates, with name labels. Garden zones shown as semi-transparent dashed polygons. Color-coded legend by category with counts. Toggle show/hide overlay. "View on Canvas" button from results switches to canvas view.

### GitHub Actions CI/CD - Mar 15, 2026
- GitHub Actions workflow for building and pushing Docker images to GitHub Container Registry (ghcr.io)
- Triggers on push and pull requests to `main` and `development` branches
- Builds two separate images: backend (FastAPI) and frontend (React/Nginx)
- Tagging: branch name (`main`/`development`) + `latest` + short SHA. PRs get `pr-{number}` tag
- Docker layer caching via GitHub Actions cache for fast builds
- Backend Dockerfile: runtime env vars for DB, SMTP, JWT, etc.
- Frontend Dockerfile: build-time ARGs for `REACT_APP_BACKEND_URL`

### Settings & Admin Restructure - Mar 16, 2026
- **Settings page** split into 4 tabs: Profile (info + password), Notifications (daily reminders), Calendar (Google Calendar sync), AI (renamed from "AI Transaction Analysis" to "AI Settings")
- Calendar and AI tabs lazy-load data only when selected
- **New Admin page** (`/admin`) with 2 tabs: Email Configuration, User Management
- Admin page only visible to admin users via dropdown menu
- User Management tab lazy-loads user list only when selected
- Removed standalone Manage Users page; consolidated into Admin page

### Centralized Image Uploader & Library Images - Apr 5, 2026
- **ImageUploader component** (`/app/frontend/src/components/ImageUploader.jsx`): Reusable dialog with client-side crop (react-image-crop) + resize/compress (browser-image-compression, ~80% JPEG quality)
  - Cover mode (project covers): forced 3:2 aspect ratio crop, max 1200px
  - Free mode (gallery/blog/library): optional free-form crop, configurable max width
- Integrated into: ProjectDetailPage (cover), GalleryPage (1920px), BlogPage (1600px), LibraryPage (1600px)
- **Library image support**: New backend endpoints for upload/delete images on library entries, `library_images` MongoDB collection, images shown inline on entry cards

### Expense Periods Search & Bug Fix - Mar 24, 2026
- Added date range search (From/To month) to Expense Periods tab with Clear button and result counter
- Fixed update bug: period name and totals now immediately reflect after editing (added await to fetch calls)

### Garden Designer Disabled - Mar 24, 2026
- Disabled Garden Designer page: route and import commented out in App.js, link removed from project detail
- Code preserved in GardenDesignerPage.jsx for future re-enablement

## Upcoming Tasks (P0-P1)
1. (P1) PWA refinement and offline capabilities
3. (P1) Project export/import functionality

## Future/Backlog Tasks (P2)
1. Update app tagline to align with "Earthly Life"
2. Full mobile app (React Native or Capacitor)
3. Multi-language support
4. Two-factor authentication (2FA)
5. Project collaboration features
6. Frontend linting warnings cleanup

## Test Credentials
- **Email:** admin@selfsufficient.app
- **Password:** admin123

## Key API Endpoints
- **OpenAI Settings:** `/api/openai/settings` (GET/POST/DELETE), `/api/openai/test`, `/api/openai/models`
- **AI Import Analysis:** `/api/finance/import/analyze`
- **Checklists:** `/api/checklists`, `/api/checklists/{id}`
- **Finance:** `/api/finance/accounts`, `/api/finance/transactions`
- **Import:** `/api/finance/import/preview`, `/api/finance/import/confirm`
- **Google Calendar:** `/api/google-calendar/auth`, `/api/google-calendar/sync`
