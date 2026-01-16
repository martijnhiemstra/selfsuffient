# Self-Sufficient Lifestyle App - PRD

## Original Problem Statement
Build an application to help users setup a self-sufficient lifestyle with:
- User authentication (login, forgot password - no registration)
- Projects (name, description 5000 chars, image, public/private)
- Diary entries per project (title, datetime, story 10000 chars, search/sort)
- Gallery with recursive folders and images
- Blog (public/private entries, public viewing page, view tracking)
- Library (folders, entries, public/private)
- Tasks with calendar (month/week/day view, drag-drop, recurring)
- Startup/Shutdown daily task lists with completion tracking
- Public landing page with view tracking
- Rich HTML editor for descriptions

## User Personas
1. **Homesteader** - Primary user managing self-sufficiency projects
2. **Admin** - User management, system configuration
3. **Public Visitor** - Views public projects, blogs, library entries

## Core Requirements (Static)
- No user registration - admin creates users
- JWT authentication with bcrypt
- MongoDB database
- FastAPI backend, React frontend
- Responsive design with nature/organic theme
- Rich text editing (TipTap)

## What's Been Implemented

### Phase 1 - Core Infrastructure ✅
- [x] JWT Authentication (login, logout, forgot/reset password)
- [x] Admin user seeding (admin@selfsufficient.app / admin123)
- [x] Protected routes & Auth context
- [x] Landing page, Login page, Forgot/Reset password pages
- [x] Dashboard layout with bento grid
- [x] Responsive navigation
- [x] Design system (Playfair Display, DM Sans, earthy colors)

### Phase 2 - Project Management ✅
- [x] Projects CRUD (name, description, public/private)
- [x] Project image upload
- [x] Projects listing with search/sort
- [x] Project detail page with feature cards
- [x] Admin user management (create, list, delete)
- [x] Settings page with password change

### Phase 3 - Content Features ✅
- [x] Diary entries with rich text (TipTap)
- [x] Gallery with folders and image uploads
- [x] Blog (public/private entries)
- [x] Library with folders and entries

### Phase 4 - Task Management ✅
- [x] Tasks & Calendar (month/week/day view)
- [x] Task recurring options (daily, weekly, monthly, yearly)
- [x] Startup/Shutdown daily task lists with completion tracking

### Phase 5 - Calendar Interactivity & Public URLs (2026-01-16) ✅
- [x] Click-to-edit tasks on calendar (opens Edit Task dialog)
- [x] Drag-and-drop to reschedule non-recurring tasks
- [x] Task deletion with confirmation dialog
- [x] User-specific public URLs (/public/user/:userId)
- [x] Public Site nav link opens user's profile in new tab

### Phase 6 - Docker, Email & Advanced Features (2026-01-16) ✅
- [x] Docker + Docker Compose support with environment configuration
- [x] SMTP email service (SSL on port 465) for password reset
- [x] Configurable APP_NAME and APP_URL from environment
- [x] Recursive folder navigation for Gallery (breadcrumbs, subfolders)
- [x] Recursive folder navigation for Library (breadcrumbs, subfolders)
- [x] View counts displayed on Blog and Library entries
- [x] Enhanced search in descriptions (Blog, Library, Diary)
- [x] Light green (#f0f7f0) background for authenticated section
- [x] Custom landing page background image

### Phase 7 - Daily Reminders & UI Improvements (2026-01-16) ✅
- [x] Renamed "Startup" to "Start of Day Items" throughout the app
- [x] Renamed "Shutdown" to "End of Day Items" throughout the app
- [x] Added `daily_reminders` property to user profile
- [x] Settings page has Daily Reminders toggle with description
- [x] Daily reminder email template with Start of Day → Tasks → End of Day order
- [x] Cron integrated into backend container (no separate service)
- [x] View counts show "0 views" explicitly on public project pages

### Phase 8 - Public Gallery & Search/Sort (2026-01-16) ✅
- [x] Added `is_public` property to gallery folders
- [x] Gallery folder creation dialog has "Make Public" toggle
- [x] Gallery folders display Globe icon badge when public
- [x] Public project page has Gallery tab showing public folders
- [x] Public project page Blog tab has search and sort
- [x] Public project page Library tab has search and sort
- [x] Public project page Gallery tab has search and sort
- [x] GET /api/public/projects/{id}/gallery returns only public folders

## Environment Configuration
See `/app/.env.example` for all options:
- `APP_NAME` - Application name displayed throughout
- `APP_URL` - Frontend URL for email links
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` - Email settings
- `SMTP_FROM_EMAIL`, `SMTP_FROM_NAME` - Sender configuration

## Tech Stack
- Backend: FastAPI, Motor (MongoDB async), PyJWT, bcrypt, smtplib (SSL)
- Frontend: React, TailwindCSS, Shadcn/UI, React Router, TipTap
- Database: MongoDB
- Design: Playfair Display + DM Sans fonts, earthy green theme
- Containerization: Docker, Docker Compose

## Key API Endpoints
- `/api/auth/{login, logout, forgot-password, reset-password}`
- `/api/auth/settings` (PUT) - Update user settings (daily_reminders)
- `/api/config` - Get app configuration
- `/api/cron/send-daily-reminders` (POST) - Send daily reminder emails
- `/api/projects/...` (CRUD)
- `/api/projects/{project_id}/{diary, blog, library, tasks, routines}`
- `/api/projects/{project_id}/gallery/folders/{folderId}/path` - Breadcrumb path
- `/api/projects/{project_id}/library/folders/{folderId}/path` - Breadcrumb path
- `/api/public/projects` - List all public projects
- `/api/public/users/{user_id}/profile` - Get user's public profile
- `/api/public/projects/{project_id}/blog/{entry_id}` - Increments view count
- `/api/public/projects/{project_id}/library/entries/{entry_id}` - Increments view count
- `/api/dashboard/today` - Dashboard data

## Test Credentials
- Email: admin@selfsufficient.app
- Password: admin123

## Notes
- Password reset emails sent via SMTP SSL (port 465) when configured
- If SMTP not configured, reset tokens logged to console (dev mode)
- Recursive folders support unlimited nesting depth
- View counts increment on public page access

## All Features Complete ✅
All original requirements from the problem statement have been implemented.
