// src/App.jsx
import React from "react";
import PlanPage from "./pages/Plans";
import Sidebar from "./components/Sidebar";
import { Routes, Route, Navigate } from "react-router-dom";
import Tasks from "./pages/Tasks";
import Header from "./components/Header";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ProtectedRoute from "./components/ProtectedRoute";


export default function App() {
  return (
    <>
      <Header></Header>
      <Routes>
        <Route path="/plans" element={<ProtectedRoute>
          <PlanPage />
        </ProtectedRoute>} />
        <Route path="/tasks" element={<ProtectedRoute><Tasks /></ProtectedRoute> } />
        <Route path="/" element={<Navigate to="/plans" />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>

    </>
  );
}
