import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth/AuthContext';
import { ProtectedRoute } from './auth/ProtectedRoute';
import { DashboardLayout } from './components/layout/DashboardLayout';
import { ThemeProvider } from './context/ThemeContext';
import { VignexIntroScreen } from './components/common/VignexIntroScreen';

import LoginPage from './pages/LoginPage';
import StudentDashboard from './pages/StudentDashboard';
import StudentAcademicsPage from './pages/StudentAcademicsPage';
import StudentCareerPage from './pages/StudentCareerPage';
import ReportIssuePage from './pages/ReportIssuePage';
import MyComplaintsPage from './pages/MyComplaintsPage';
import CaseDetailPage from './pages/CaseDetailPage';
import StudentProfilePage from './pages/StudentProfilePage';

import FacultyDashboard from './pages/FacultyDashboard';
import FacultyCasesPage from './pages/FacultyCasesPage';
import FacultyDepartmentIssuesPage from './pages/FacultyDepartmentIssuesPage';
import FacultyCaseDetailPage from './pages/FacultyCaseDetailPage';
import { FacultyAcademicPage } from './pages/FacultyAcademicPage';
import FacultyProfilePage from './pages/FacultyProfilePage';

import ManagementDashboard from './pages/ManagementDashboard';
import ManagementCampusIssuesPage from './pages/ManagementCampusIssuesPage';
import ManagementCaseDetailPage from './pages/ManagementCaseDetailPage';
import ManagementSimulationsPage from './pages/ManagementSimulationsPage';
import { ManagementAcademicPage } from './pages/ManagementAcademicPage';
import ManagementOpportunityIntakePage from './pages/ManagementOpportunityIntakePage';
import ManagementProfilePage from './pages/ManagementProfilePage';
import AskVignexPage from './pages/AskVignexPage';
import PlaceholderPage from './pages/PlaceholderPage';
import FacultyFeedbackPage from './pages/FacultyFeedbackPage';
import ChangePasswordPage from './pages/ChangePasswordPage';

const HomeRedirect: React.FC = () => {
  const { user } = useAuth();
  if (user?.role) {
    if (user.must_change_password) {
      return <Navigate to="/change-password" replace />;
    }
    return <Navigate to={`/${user.role}`} replace />;
  }
  return <Navigate to="/login" replace />;
};

const AppContent: React.FC = () => {
  const [showIntro, setShowIntro] = useState<boolean>(() => {
    return !sessionStorage.getItem('vignex_intro_completed');
  });

  const handleIntroComplete = () => {
    sessionStorage.setItem('vignex_intro_completed', 'true');
    setShowIntro(false);
  };

  return (
    <>
      {showIntro && <VignexIntroScreen onComplete={handleIntroComplete} />}
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/change-password" element={<ChangePasswordPage />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            {/* Student Routes */}
            <Route element={<ProtectedRoute allowedRoles={['student']} />}>
              <Route path="/student" element={<StudentDashboard />} />
              <Route path="/student/academics" element={<StudentAcademicsPage />} />
              <Route path="/student/career" element={<StudentCareerPage />} />
              <Route path="/student/ask-vignex" element={<AskVignexPage />} />
              <Route path="/student/ask-vignai" element={<AskVignexPage />} />
              <Route path="/student/report" element={<ReportIssuePage />} />
              <Route path="/student/complaints" element={<MyComplaintsPage />} />
              <Route path="/student/complaints/:caseId" element={<CaseDetailPage />} />
              <Route path="/student/profile" element={<StudentProfilePage />} />
            </Route>

            {/* Faculty Routes */}
            <Route element={<ProtectedRoute allowedRoles={['faculty']} />}>
              <Route path="/faculty" element={<FacultyDashboard />} />
              <Route path="/faculty/academic-intelligence" element={<FacultyAcademicPage />} />
              <Route path="/faculty/ask-vignex" element={<AskVignexPage />} />
              <Route path="/faculty/ask-vignai" element={<AskVignexPage />} />
              <Route path="/faculty/department-issues" element={<FacultyDepartmentIssuesPage />} />
              <Route path="/faculty/cases" element={<FacultyCasesPage />} />
              <Route path="/faculty/cases/:caseId" element={<FacultyCaseDetailPage />} />
              <Route
                path="/faculty/insights"
                element={
                  <PlaceholderPage
                    title="Faculty AI Insights"
                    badgeText="Faculty Workspace"
                    description="AI-generated summaries and sentiment trends for department complaints."
                  />
                }
              />
              <Route path="/faculty/feedback" element={<FacultyFeedbackPage />} />
              <Route path="/faculty/profile" element={<FacultyProfilePage />} />
            </Route>

            {/* Management Routes */}
            <Route element={<ProtectedRoute allowedRoles={['management']} />}>
              <Route path="/management" element={<ManagementDashboard />} />
              <Route path="/management/intelligence" element={<ManagementDashboard />} />
              <Route path="/management/academic-intelligence" element={<ManagementAcademicPage />} />
              <Route path="/management/campus-issues" element={<ManagementCampusIssuesPage />} />
              <Route path="/management/campus-issues/:caseId" element={<ManagementCaseDetailPage />} />
              <Route path="/management/issues" element={<ManagementCampusIssuesPage />} />
              <Route path="/management/issues/:caseId" element={<ManagementCaseDetailPage />} />
              <Route
                path="/management/analytics"
                element={
                  <PlaceholderPage
                    title="Campus Analytics"
                    badgeText="Management Console"
                    description="Cross-department operational metrics, resolution rates, and trend analytics."
                  />
                }
              />
              <Route
                path="/management/ai-insights"
                element={
                  <PlaceholderPage
                    title="AI Insights & Emerging Issues"
                    badgeText="Management Console"
                    description="Machine-learning powered cluster detection, duplicate complaints, and root-cause analysis."
                  />
                }
              />
              <Route path="/management/ask-vignex" element={<AskVignexPage />} />
              <Route path="/management/ask-vignai" element={<AskVignexPage />} />
              <Route path="/management/simulations" element={<ManagementSimulationsPage />} />
              <Route path="/management/what-if" element={<ManagementSimulationsPage />} />
              <Route path="/management/opportunity-intake" element={<ManagementOpportunityIntakePage />} />
              <Route path="/management/profile" element={<ManagementProfilePage />} />
            </Route>

            {/* Universal Shared AI Assistant Routes */}
            <Route path="/ask-vignex" element={<AskVignexPage />} />
            <Route path="/ask-vignai" element={<AskVignexPage />} />
          </Route>

          <Route path="/" element={<HomeRedirect />} />
        </Route>

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </>
  );
};

import { ToastProvider } from './components/ui/Toast';

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <ToastProvider>
          <AuthProvider>
            <AppContent />
          </AuthProvider>
        </ToastProvider>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;

