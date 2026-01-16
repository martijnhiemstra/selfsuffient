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

### Phase 1 - Core Infrastructure (2026-01-16) ✅
- [x] JWT Authentication (login, logout, forgot/reset password)
- [x] Admin user seeding (admin@selfsufficient.app / admin123)
- [x] Protected routes
- [x] Auth context
- [x] Landing page (public)
- [x] Login page
- [x] Forgot/Reset password pages
- [x] Dashboard layout with bento grid
- [x] Responsive navigation
- [x] Design system (Playfair Display, DM Sans, earthy colors)

### Phase 2 - Project Management (2026-01-16) ✅
- [x] Projects CRUD (name, description, public/private)
- [x] Project image upload
- [x] Projects listing with search/sort
- [x] Project detail page with feature cards
- [x] Admin user management (create, list, delete)
- [x] Settings page with password change

## Prioritized Backlog

### P0 (Critical)
- [x] Projects CRUD
- [x] Project image upload
- [x] Admin user management

### P1 (High)
- [ ] Diary entries
- [ ] Gallery with recursive folders
- [ ] Blog (public/private)
- [ ] Library

### P2 (Medium)
- [ ] Tasks & Calendar
- [ ] Startup/Shutdown lists
- [ ] Public project view
- [ ] View tracking

### P3 (Low)
- [ ] Rich text editor integration
- [ ] Email notifications for password reset
- [ ] Sorting preferences persistence

## Tech Stack
- Backend: FastAPI, Motor (MongoDB async), PyJWT, bcrypt
- Frontend: React, TailwindCSS, Shadcn/UI, React Router
- Database: MongoDB
- Design: Playfair Display + DM Sans fonts, earthy green theme

## Next Tasks
1. Create Project model and CRUD endpoints
2. Implement image upload for projects
3. Build ProjectsListPage and ProjectDetailPage
4. Add admin user management panel
