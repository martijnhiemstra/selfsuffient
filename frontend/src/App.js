import "@/App.css";
import { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "./components/ui/sonner";
import { AuthProvider } from "./context/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { Layout } from "./components/Layout";
import { PWAInstallPrompt } from "./components/PWAInstallPrompt";
import { fetchAppConfig } from "./utils";

// Pages
import { LoginPage } from "./pages/LoginPage";
import { ForgotPasswordPage } from "./pages/ForgotPasswordPage";
import { ResetPasswordPage } from "./pages/ResetPasswordPage";
import { DashboardPage } from "./pages/DashboardPage";
import { LandingPage } from "./pages/LandingPage";
import { PublicProjectPage } from "./pages/PublicProjectPage";
import { PublicUserPage } from "./pages/PublicUserPage";
import { ProjectsPage } from "./pages/ProjectsPage";
import { ProjectDetailPage } from "./pages/ProjectDetailPage";
import { AdminUsersPage } from "./pages/AdminUsersPage";
import { SettingsPage } from "./pages/SettingsPage";
import { DiaryPage } from "./pages/DiaryPage";
import { GalleryPage } from "./pages/GalleryPage";
import { BlogPage } from "./pages/BlogPage";
import { LibraryPage } from "./pages/LibraryPage";
import { TasksPage } from "./pages/TasksPage";
import { RoutinesPage } from "./pages/RoutinesPage";
import { CalendarPage } from "./pages/CalendarPage";
import { MyPublicSitePage } from "./pages/MyPublicSitePage";
import { FinancePage } from "./pages/FinancePage";
import { ChecklistsPage } from "./pages/ChecklistsPage";

function App() {
  // Fetch app config on mount to get max upload size
  useEffect(() => {
    fetchAppConfig();
  }, []);

  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/public/project/:projectId" element={<PublicProjectPage />} />
          <Route path="/public/user/:userId" element={<PublicUserPage />} />

          {/* Protected Routes */}
          <Route path="/dashboard" element={<ProtectedRoute><Layout><DashboardPage /></Layout></ProtectedRoute>} />

          {/* Projects */}
          <Route path="/projects" element={<ProtectedRoute><Layout><ProjectsPage /></Layout></ProtectedRoute>} />
          <Route path="/projects/:projectId" element={<ProtectedRoute><Layout><ProjectDetailPage /></Layout></ProtectedRoute>} />

          {/* Project Features */}
          <Route path="/projects/:projectId/diary" element={<ProtectedRoute><Layout><DiaryPage /></Layout></ProtectedRoute>} />
          <Route path="/projects/:projectId/gallery" element={<ProtectedRoute><Layout><GalleryPage /></Layout></ProtectedRoute>} />
          <Route path="/projects/:projectId/blog" element={<ProtectedRoute><Layout><BlogPage /></Layout></ProtectedRoute>} />
          <Route path="/projects/:projectId/library" element={<ProtectedRoute><Layout><LibraryPage /></Layout></ProtectedRoute>} />
          <Route path="/projects/:projectId/tasks" element={<ProtectedRoute><Layout><TasksPage /></Layout></ProtectedRoute>} />
          <Route path="/projects/:projectId/routines" element={<ProtectedRoute><Layout><RoutinesPage /></Layout></ProtectedRoute>} />

          {/* Calendar */}
          <Route path="/calendar" element={<ProtectedRoute><Layout><CalendarPage /></Layout></ProtectedRoute>} />

          {/* Finance */}
          <Route path="/finance" element={<ProtectedRoute><Layout><FinancePage /></Layout></ProtectedRoute>} />

          {/* Checklists - within project context */}
          <Route path="/projects/:projectId/checklists" element={<ProtectedRoute><Layout><ChecklistsPage /></Layout></ProtectedRoute>} />

          {/* My Public Site */}
          <Route path="/my-public-site" element={<ProtectedRoute><Layout><MyPublicSitePage /></Layout></ProtectedRoute>} />

          {/* Settings */}
          <Route path="/settings" element={<ProtectedRoute><Layout><SettingsPage /></Layout></ProtectedRoute>} />

          {/* Admin Routes */}
          <Route path="/admin/users" element={<ProtectedRoute adminOnly><Layout><AdminUsersPage /></Layout></ProtectedRoute>} />

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" />
    </AuthProvider>
  );
}

export default App;
