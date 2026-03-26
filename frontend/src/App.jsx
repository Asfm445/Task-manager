// src/App.jsx
import { Navigate, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import DatePlanAnalytics from "./pages/DatePlanAnalytics";
import ProtectedRoute from "./components/ProtectedRoute";
import ForgotPassword from "./pages/ForgotPassword";
import Home from "./pages/Home";
import Login from "./pages/Login";
import PlanPage from "./pages/Plans";
import Register from "./pages/Register";
import ResetPassword from "./pages/ResetPassword";
import TaskAnalyticsDashboard from "./pages/TaskAnalytics";
import TaskDetail from "./pages/TaskDetail";
import Tasks from "./pages/Tasks";
import VerifyEmail from "./pages/VerifyEmail";
import { TaskProvider } from "./TaskContext";

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TaskProvider>
        <Routes>
          <Route path="/plans" element={<ProtectedRoute><PlanPage /></ProtectedRoute>} />
          <Route path="/tasks" element={<ProtectedRoute><Tasks /></ProtectedRoute>} />
          <Route path="/tasks/:id" element={<ProtectedRoute><TaskDetail /></ProtectedRoute>} />
          <Route path="/" element={<Home />} />
          <Route path="/home" element={<Home />} />
          <Route path="/date-analytics" element={<DatePlanAnalytics />} />
          <Route path="/task-analytics" element={<TaskAnalyticsDashboard />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/auth/reset-password" element={<ResetPassword />} />
          <Route path="/auth/forgot-password" element={<ForgotPassword />} />
          <Route path="/auth/verify-email" element={<VerifyEmail />} />
        </Routes>
      </TaskProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
