// src/App.jsx
import React from "react";
import PlanPage from "./pages/Plans";
import Sidebar from "./components/Sidebar";
import { Routes, Route, Navigate } from "react-router-dom";
import Tasks from "./pages/Tasks";
import Header from "./components/Header";

export default function App() {
  return (
    <>
      <Header></Header>
      <Routes>
        <Route path="/plans" element={<PlanPage />} />
        <Route path="/tasks" element={<Tasks />} />
        <Route path="/" element={<Navigate to="/plans" />} />
      </Routes>
    </>
  );
}
