import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "./components/ui/sonner";
import { AuthProvider } from "./context/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Layout } from "./components/Layout";

// Pages
import { LoginPage } from "./pages/LoginPage";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LandingPage } from "./pages/LandingPage";
import { ProjectsPage } from "./pages/ProjectsPage";
import { ProjectDetailPage } from "./pages/ProjectDetailPage";
import { AdminUsersPage } from "./pages/AdminUsersPage";
import { SettingsPage } from "./pages/SettingsPage";
import { DiaryPage } from "./pages/DiaryPage";
import { GalleryPage } from "./pages/GalleryPage";
import { BlogPage } from "./pages/BlogPage";
import { LibraryPage } from "./pages/LibraryPage";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <DashboardPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Projects */}
          <Route
            path="/projects"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProjectsPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:projectId"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProjectDetailPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Project Features */}
          <Route
            path="/projects/:projectId/diary"
            element={
              <ProtectedRoute>
                <Layout>
                  <DiaryPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:projectId/gallery"
            element={
              <ProtectedRoute>
                <Layout>
                  <GalleryPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:projectId/blog"
            element={
              <ProtectedRoute>
                <Layout>
                  <BlogPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:projectId/library"
            element={
              <ProtectedRoute>
                <Layout>
                  <LibraryPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:projectId/tasks"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProjectDetailPage />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects/:projectId/routines"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProjectDetailPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Calendar - Placeholder */}
          <Route
            path="/calendar"
            element={
              <ProtectedRoute>
                <Layout>
                  <DashboardPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Settings */}
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Layout>
                  <SettingsPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Admin Routes */}
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute adminOnly>
                <Layout>
                  <AdminUsersPage />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Catch all - redirect to landing */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" />
    </AuthProvider>
  );
}

export default App;
