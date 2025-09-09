// src/App.jsx
import { Navigate, Route, Routes } from "react-router-dom";
import TimeLogAnalytics from "./components/Plans/DatePlanAnalytics";
import ProtectedRoute from "./components/ProtectedRoute";
import ForgotPassword from "./pages/ForgotPassword";
import Login from "./pages/Login";
import PlanPage from "./pages/Plans";
import Register from "./pages/Register";
import ResetPassword from "./pages/ResetPassword";
import TaskAnalyticsDashboard from "./pages/TaskAnalytics";
import TaskDetail from "./pages/TaskDetail";
import Tasks from "./pages/Tasks";
import VerifyEmail from "./pages/VerifyEmail";
import { TaskProvider } from "./TaskContext";

export default function App() {
  return (
    <>
      <Routes>
        {/* <TaskProvider */}
        <Route path="/plans" element={<ProtectedRoute>
          <TaskProvider><PlanPage /></TaskProvider>
        </ProtectedRoute>} />
        <Route path="/tasks" element={<ProtectedRoute> <TaskProvider><Tasks /></TaskProvider></ProtectedRoute> } />
        <Route path="/tasks/:id" element={<ProtectedRoute><TaskDetail /></ProtectedRoute> } />
        <Route path="/" element={<Navigate to="/plans" />} />
        <Route path="/date-analytics" element={<TimeLogAnalytics></TimeLogAnalytics>} />
        <Route path="/task-analytics" element={<TaskAnalyticsDashboard></TaskAnalyticsDashboard>} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/auth/reset-password" element={<ResetPassword />} />
        <Route path="/auth/forgot-password" element={<ForgotPassword />} />
        <Route path="/auth/verify-email" element={<VerifyEmail />} />
      </Routes>

    </>
  );
}
