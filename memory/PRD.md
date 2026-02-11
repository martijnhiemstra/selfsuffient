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
│   │   └── import_transactions.py # Transaction imports
│   └── services/           # Business logic helpers
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── components/
│   │   │   └── PWAInstallPrompt.jsx  # PWA install prompt
│   │   ├── serviceWorkerRegistration.js  # PWA service worker
│   │   └── pages/
│   │       ├── ChecklistsPage.jsx    # Nested under projects
│   │       └── FinancePage.jsx       # Full budgeting system
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
- Splash screen on load
- Standalone display mode

## Recent Bug Fixes
- **Gallery Upload Bug** (Feb 11, 2026) - Fixed issue where images uploaded in a subfolder appeared in root. Changed `folder_id` parameter from query param to Form field.
- **App Tagline** (Feb 11, 2026) - Updated from "self-sufficient living" to "sustainable, earthly living"

## Upcoming Tasks (P0-P1)
1. (P1) Cleanup obsolete `recurring_transactions` database collection
2. (P1) Transaction Import - Duplicate detection enhancement
3. (P1) Project export/import functionality

## Future/Backlog Tasks (P2)
1. Full mobile app (React Native or Capacitor)
2. Multi-language support
3. Two-factor authentication (2FA)
4. Project collaboration features

## Test Credentials
- **Email:** admin@selfsufficient.app
- **Password:** admin123

## Key API Endpoints
- **Checklists:** `/api/checklists`, `/api/checklists/{id}`, `/api/checklist-items/{id}`
- **Finance:** `/api/finance/accounts`, `/api/finance/transactions`, `/api/finance/savings-goals`
- **Import:** `/api/import/preview`, `/api/import/confirm`
- **Google Calendar:** `/api/google-calendar/auth`, `/api/google-calendar/sync`
