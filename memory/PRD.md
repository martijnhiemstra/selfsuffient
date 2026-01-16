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

## Prioritized Backlog

### P0 (Critical) - DONE
- [x] All core features implemented

### P1 (High) - IN PROGRESS
- [ ] Recursive folder structure for Gallery and Library (folders can contain sub-folders)
- [ ] Real password reset with email service integration

### P2 (Medium)
- [ ] View counts displayed on public blog/library entries
- [ ] Enhanced search (search within description fields, not just titles)
- [ ] Multi-image upload for gallery

### P3 (Low)
- [ ] Email notifications for password reset
- [ ] Sorting preferences persistence across sessions

## Tech Stack
- Backend: FastAPI, Motor (MongoDB async), PyJWT, bcrypt
- Frontend: React, TailwindCSS, Shadcn/UI, React Router, TipTap
- Database: MongoDB
- Design: Playfair Display + DM Sans fonts, earthy green theme

## Key API Endpoints
- `/api/auth/{login, logout, forgot-password, reset-password}`
- `/api/projects/...` (CRUD)
- `/api/projects/{project_id}/{diary, blog, library, tasks, routines}`
- `/api/public/projects` - List all public projects
- `/api/public/users/{user_id}/profile` - Get user's public profile
- `/api/dashboard/today` - Dashboard data

## Test Credentials
- Email: admin@selfsufficient.app
- Password: admin123

## Notes
- Password recovery is currently MOCKED (generates token but doesn't send email)
- Recursive folders exist in schema but UI navigation needs enhancement
