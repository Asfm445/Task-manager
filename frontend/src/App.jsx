// src/App.jsx
import React from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Header from "./components/Header";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import PlanPage from "./pages/Plans";
import Register from "./pages/Register";
import TaskDetail from "./pages/TaskDetail";
import Tasks from "./pages/Tasks";


export default function App() {
  return (
    <>
      <Header></Header>
      <Routes>
        <Route path="/plans" element={<ProtectedRoute>
          <PlanPage />
        </ProtectedRoute>} />
        <Route path="/tasks" element={<ProtectedRoute><Tasks /></ProtectedRoute> } />
        <Route path="/tasks/:id" element={<ProtectedRoute><TaskDetail /></ProtectedRoute> } />
        <Route path="/" element={<Navigate to="/plans" />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>

    </>
  );
}
