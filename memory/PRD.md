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
│   ├── server.py           # Main FastAPI app entry point (~60 lines)
│   ├── config.py           # Configuration and database connection
│   ├── models/             # Pydantic models
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── project.py
│   │   ├── diary.py
│   │   ├── gallery.py
│   │   ├── blog.py
│   │   ├── library.py
│   │   ├── task.py
│   │   ├── routine.py
│   │   └── public.py
│   ├── routes/             # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── projects.py
│   │   ├── diary.py
│   │   ├── gallery.py
│   │   ├── blog.py
│   │   ├── library.py
│   │   ├── tasks.py
│   │   ├── routines.py
│   │   ├── public.py
│   │   ├── dashboard.py
│   │   └── health.py
│   ├── services/           # Business logic helpers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── email.py
│   │   └── project.py
│   ├── daily_reminders.py  # Cron job script
│   ├── entrypoint.sh
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── config.js
│   │   ├── components/
│   │   ├── context/
│   │   ├── hooks/
│   │   └── pages/
│   ├── public/
│   ├── Dockerfile
│   └── package.json
└── memory/
    └── PRD.md
```

## Key Database Collections
- `users`: id, email, hashed_password, name, is_admin, daily_reminders
- `projects`: id, user_id, name, description, image, is_public
- `diary_entries`: id, project_id, title, story, entry_datetime
- `blog_entries`: id, project_id, title, description, is_public, views
- `library_folders`: id, project_id, parent_id, name
- `library_entries`: id, project_id, folder_id, title, description, is_public, views
- `gallery_folders`: id, project_id, parent_id, name, is_public
- `gallery_images`: id, project_id, folder_id, filename, url
- `tasks`: id, project_id, title, description, task_datetime, is_all_day, recurrence
- `routine_tasks`: id, project_id, routine_type, title, description, order
- `routine_completions`: id, task_id, completed_date
- `password_resets`: id, user_id, token, expires_at, used

## Key API Endpoints
- **Auth**: `/api/auth/{login, forgot-password, reset-password, me, settings, change-password}`
- **Admin**: `/api/admin/users` (CRUD)
- **Projects**: `/api/projects` (CRUD with image upload)
- **Diary**: `/api/projects/{id}/diary` (CRUD)
- **Gallery**: `/api/projects/{id}/gallery/{folders, images}` (CRUD)
- **Blog**: `/api/projects/{id}/blog` (CRUD)
- **Library**: `/api/projects/{id}/library/{folders, entries}` (CRUD)
- **Tasks**: `/api/projects/{id}/tasks` (CRUD)
- **Routines**: `/api/projects/{id}/routines/{startup, shutdown}` (CRUD + complete/uncomplete)
- **Dashboard**: `/api/dashboard/{data, all-tasks}`
- **Public**: `/api/public/{projects, users/{id}/profile}`
- **Health**: `/api/health`

## Completed Features ✅
All original requirements have been implemented:

1. **Authentication** ✅
   - JWT-based login/logout
   - Password reset via SMTP email
   - User settings management

2. **Projects** ✅
   - Full CRUD with image upload
   - Public/private visibility
   - Search and sort functionality

3. **Diary** ✅
   - Searchable/sortable entries
   - Date-based organization

4. **Gallery** ✅
   - Recursive folder structure
   - Public folders support
   - Breadcrumb navigation
   - Image upload and management

5. **Blog** ✅
   - Public/private entries
   - View count tracking
   - Search and sort

6. **Library** ✅
   - Recursive folders
   - Public/private entries
   - View count tracking
   - Breadcrumb navigation

7. **Tasks & Calendar** ✅
   - Month/week/day views
   - Drag-and-drop support
   - Click-to-edit functionality
   - Recurrence options

8. **Daily Routines** ✅
   - "Start of Day" items
   - "End of Day" items
   - Completion tracking per day

9. **Public Site** ✅
   - Landing page with public projects
   - User-specific public profiles (`/public/user/:userId`)
   - Public project pages with Blog, Library, Gallery tabs

10. **User Dashboard** ✅
    - Today's tasks display
    - Incomplete routines display
    - Quick access to projects

11. **Daily Reminders** ✅
    - Opt-in email notifications
    - Secure cron job implementation

12. **Docker Containerization** ✅
    - Docker Compose setup
    - Auto admin user seeding
    - Production-ready configuration

## Recent Updates (Jan 16, 2026)
- **Watermark Removed**: Removed emergent-main.js script from index.html
- **Backend Refactoring**: Split monolithic server.py (2100+ lines) into modular structure:
  - Created `config.py` for configuration
  - Created `models/` folder with separate model files
  - Created `routes/` folder with separate route files  
  - Created `services/` folder for business logic
- **Dashboard API Fix**: Updated frontend to use correct endpoint `/api/dashboard/data`
- **All Tests Passing**: 33 backend tests + frontend tests all passing

## Test Credentials
- **Admin Email**: admin@selfsufficient.app
- **Admin Password**: admin123

## Future Enhancements (Backlog)
1. Social sharing features for public content
2. Export/import functionality for projects
3. Mobile app version
4. Analytics dashboard for content views
5. Multi-language support
6. Two-factor authentication
7. Project collaboration features

## Documentation
- `/app/DOCKER.md` - Docker setup and deployment guide
- `/app/.env.example` - Environment variables template
