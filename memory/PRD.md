# Self-Sufficient Life - Product Requirements Document

## Overview
A full-stack application to help users setup and maintain a self-sufficient lifestyle, with project management, diaries, galleries, blogs, libraries, task management, and daily routines.

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

## Code Architecture (After Refactoring - Jan 2026)
```
/app/
├── docker-compose.yml
├── DOCKER.md
├── backend/
│   ├── server.py           # Main FastAPI app entry point (~80 lines)
│   ├── config.py           # Configuration and database connection
│   ├── models/             # Pydantic models
│   │   ├── __init__.py, auth.py, project.py, diary.py, gallery.py,
│   │   └── blog.py, library.py, task.py, routine.py, public.py
│   ├── routes/             # API route handlers
│   │   ├── __init__.py, auth.py, admin.py, projects.py, diary.py,
│   │   └── gallery.py, blog.py, library.py, tasks.py, routines.py,
│   │       public.py, dashboard.py, health.py
│   ├── services/           # Business logic helpers
│   │   └── __init__.py, auth.py, email.py, project.py
│   ├── daily_reminders.py  # Cron job script
│   └── Dockerfile, requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.js, config.js, utils.js
│   │   ├── components/
│   │   │   ├── ShareButton.jsx    # Social sharing component
│   │   │   └── ...
│   │   ├── context/, hooks/, pages/
│   ├── public/, Dockerfile, package.json
└── memory/PRD.md
```

## Completed Features ✅

### Core Features (Original Requirements)
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

### Recent Updates (Jan 16-17, 2026)

#### Watermark Removed ✅
- Removed emergent-main.js script from index.html

#### Backend Refactoring ✅
- Split 2100+ line monolithic server.py into modular structure
- Created separate models/, routes/, services/ directories

#### Image Display Fix ✅
- Created `/api/files/{path}` endpoint with proper CORS headers
- Created `getImageUrl()` utility in frontend for URL transformation
- Added `CORSStaticFilesMiddleware` for static files CORS support
- Fixed image display on: Landing page, Projects page, Project detail, Gallery, Dashboard

#### Social Sharing Features ✅
- **ShareButton component**: Dropdown with Twitter/X, Facebook, LinkedIn, Email, Copy Link
- **ShareIcons component**: Compact inline sharing icons
- Added to:
  - Public project pages (Share button in header)
  - Landing page project cards (Share icons)
  - Blog/Library entry cards (Share icons)

#### Gallery Image Modal ✅ (Jan 17, 2026)
- Click on gallery images to view in fullscreen modal
- Features:
  - Large image display with dark overlay background
  - Filename and image counter (e.g., "1 of 5")
  - Download button to save image
  - Close button (X) and click outside to close
  - Previous/Next navigation arrows (when multiple images)
  - Thumbnail strip at bottom for quick navigation
  - Keyboard navigation: Arrow keys (left/right), Escape to close
- Works on both secure Gallery page and public project Gallery tab

#### Private Gallery Image Security ✅ (Jan 17, 2026)
- Images in private folders are now protected from anonymous access
- Access control checks:
  - Image folder's `is_public` flag
  - User authentication via token (query param or header)
  - Project ownership verification
- Token passed via query parameter for `<img>` tag compatibility
- Public folder/project images remain accessible to everyone

#### Financial Module ✅ (Jan 22, 2026)
- **Global finance tracking** with project filtering
- **Accounts** (per project): bank, cash, crypto, asset types with starting balance support
- **Categories** (per project): income, expense, investment with default seeding
- **Transactions**: Full CRUD with income/expense tracking, savings goal attachment
- **Savings Goals**: Track savings progress with target amounts and linked transactions
- **Analytics**:
  - Project Dashboard: Income, expenses, investments, net balance, burn rate
  - Monthly Overview: By project and category breakdowns
  - Runway Calculator: Liquid cash, burn rate, months remaining, safety threshold warning
- **API Endpoints**: 
  - `/api/finance/accounts` - Account CRUD (with starting_balance)
  - `/api/finance/categories` - Category CRUD + seeding
  - `/api/finance/transactions` - Transaction CRUD
  - `/api/finance/savings-goals` - Savings goals CRUD
  - `/api/finance/dashboard/{project_id}` - Project summary
  - `/api/finance/monthly?month=YYYY-MM` - Monthly overview
  - `/api/finance/runway` - Runway calculation
- **Frontend**: 6-tab interface (Transactions, Accounts, Savings, Budget, Monthly, Runway)
- EUR currency only

#### Budgeting System ✅ (Jan 23, 2026)
- **Replaced old Recurring Transactions** with a more powerful Expense Periods system
- **Expense Periods**: Time-bound budget periods (e.g., "2026", "First Year on Farm")
  - Define start and end months (YYYY-MM format)
  - Contains Expected Items (budgeted income/expenses)
  - Shows monthly income, expenses, and net totals
- **Expected Items**: Budget line items within periods
  - Types: income or expense
  - Frequencies: monthly, yearly, or one-time
  - Optional category assignment for automatic transaction matching
- **Budget vs Actual Comparison**: Monthly view showing
  - Expected vs actual income/expenses/profit
  - Individual budget item matching with actual transactions
  - Unbudgeted transactions list
  - Status indicators (matched/unmatched)
- **API Endpoints**:
  - `/api/budget/periods` - Expense period CRUD
  - `/api/budget/items` - Expected item CRUD
  - `/api/budget/comparison?month=YYYY-MM` - Monthly budget comparison
- **Old recurring transactions system removed** (endpoints and UI deprecated)

#### Transaction Import ✅ (Jan 23, 2026)
- **Multi-step import wizard** for bulk transaction import
- **Supported formats**: CSV, OFX (Open Financial Exchange), QFX (Quicken)
- **CSV column mapping**: User-configurable mapping for date, amount, description columns
- **Date format support**: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, DD.MM.YYYY
- **Amount parsing**: Handles various formats (1234.56, 1,234.56, 1.234,56)
- **Transaction preview**: Preview imported transactions with checkboxes for selective import
- **Batch import**: Assign project, account, and default category to all imported transactions
- **API Endpoints**:
  - `POST /api/finance/import/preview/csv` - Parse CSV and return preview
  - `POST /api/finance/import/preview/ofx` - Parse OFX/QFX and return preview
  - `POST /api/finance/import/confirm` - Confirm and save imported transactions
  - `GET /api/finance/import/sample-csv` - Get sample CSV format

#### Simplified Editor & Blog Image Attachments ✅ (Jan 17, 2026)
- Replaced RichTextEditor with SimpleEditor (no embedded images)
- SimpleEditor features:
  - Headings (H1, H2, H3)
  - Text formatting (Bold, Italic, Underline, Strikethrough)
  - Text color picker (20 preset colors)
  - Lists (bullet, numbered) and blockquotes
  - Text alignment (left, center, right)
  - Links
  - Undo/Redo
- Blog entries now support attached images (separate from content)
- New endpoints: POST/DELETE `/api/projects/{id}/blog/{entry_id}/images`
- Images stored in `/uploads/blog/{project_id}/{entry_id}/`
- Blog model updated with `images` array field
- **Diary & Library pages also updated to use SimpleEditor**

#### CORS Fix for Cross-Origin Uploads ✅ (Jan 17, 2026)
- Implemented `CORSAllMiddleware` custom middleware in server.py
- Handles OPTIONS preflight requests with proper headers
- All responses include CORS headers for cross-origin access
- Verified working with cross-origin requests from different domains

#### Maximum Upload Image Size (5MB) ✅ (Jan 17, 2026)
- Added `MAX_UPLOAD_SIZE` (5MB) constant in config.py
- Backend validates file size on all image upload endpoints:
  - Project image upload (`/api/projects/{id}/image`)
  - Gallery image upload (`/api/projects/{id}/gallery/images`)
  - Blog image upload (`/api/projects/{id}/blog/{entry_id}/images`)
- Returns HTTP 413 with clear error message for oversized files
- New `/api/config` endpoint exposes max upload size to frontend
- Frontend validation in `utils.js`: `validateImageFile()`, `getMaxUploadSizeMB()`
- Upload dialogs display "Supported: JPEG, PNG, GIF, WEBP (max 5MB)"
- Error toast displayed immediately when user selects oversized file

## Key API Endpoints
- **Auth**: `/api/auth/{login, forgot-password, reset-password, me, settings, change-password}`
- **Admin**: `/api/admin/users` (CRUD)
- **Projects**: `/api/projects` (CRUD with image upload)
- **Diary**: `/api/projects/{id}/diary` (CRUD)
- **Gallery**: `/api/projects/{id}/gallery/{folders, images}` (CRUD)
- **Blog**: `/api/projects/{id}/blog` (CRUD) + `/blog/{entry_id}/images` (image attachments)
- **Library**: `/api/projects/{id}/library/{folders, entries}` (CRUD)
- **Tasks**: `/api/projects/{id}/tasks` (CRUD)
- **Routines**: `/api/projects/{id}/routines/{startup, shutdown}` (CRUD + complete)
- **Dashboard**: `/api/dashboard/{data, all-tasks}`
- **Public**: `/api/public/{projects, users/{id}/profile}`
- **Files**: `/api/files/{path}` - Serves files with access control (supports `?token=` for auth)
- **Health**: `/api/health`
- **Config**: `/api/config` - Returns app configuration (max_upload_size_mb, max_upload_size_bytes, allowed_image_types)

## Test Credentials
- **Admin Email**: admin@selfsufficient.app
- **Admin Password**: admin123

## Test Reports
- `/app/test_reports/iteration_10.json` - Backend refactoring tests (33 passed)
- `/app/test_reports/iteration_11.json` - Image fix & sharing tests (29 passed)
- `/app/test_reports/iteration_12.json` - CORS, max upload size, SimpleEditor tests (all passed)
- `/app/test_reports/iteration_13.json` - Finance module tests
- `/app/test_reports/iteration_14.json` - Budget system tests (100% passed)
- `/app/test_reports/iteration_15.json` - Transaction Import tests (100% passed)
- `/app/tests/test_image_and_sharing.py` - Pytest test suite
- `/app/tests/test_upload_size_and_cors.py` - CORS and upload size tests

## Future Enhancements (Backlog)
1. Export/import functionality for projects
2. Mobile app version
3. Analytics dashboard for content views
4. Multi-language support
5. Two-factor authentication
6. Project collaboration features

## Documentation
- `/app/DOCKER.md` - Docker setup and deployment guide
- `/app/.env.example` - Environment variables template
