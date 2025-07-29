import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { Menu, X } from "lucide-react";

const navStyle = ({ isActive }) =>
  `block px-4 py-2 rounded-md font-medium ${
    isActive ? "bg-blue-600 text-white" : "text-gray-700 hover:bg-gray-200"
  }`;

export default function Sidebar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* 🔹 Top Navbar (Mobile Only) */}
      <div className="md:hidden fixed top-0 left-0 right-0 bg-white shadow px-4 py-3 z-40 flex items-center justify-between">
        <button onClick={() => setIsOpen(true)}>
          <Menu className="w-6 h-6 text-gray-700" />
        </button>
        <h2 className="text-lg font-semibold">Dashboard</h2>
        <div className="w-6 h-6" /> {/* Spacer */}
      </div>

      {/* 🔹 Static Sidebar (Desktop Only) */}
      <aside className="hidden md:block fixed left-0 top-0 h-screen w-64 bg-white border-r p-4 z-30">
        <h2 className="text-xl font-bold mb-4">Dashboard</h2>
        <nav className="space-y-2">
          <NavLink to="/tasks" className={navStyle}>
            Tasks
          </NavLink>
          <NavLink to="/plans" className={navStyle}>
            Plans
          </NavLink>
          <NavLink to="/timelogs" className={navStyle}>
            Time Logs
          </NavLink>
        </nav>
      </aside>

      {/* 🔹 Drawer Sidebar (Mobile Only) */}
      {isOpen && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          {/* Overlay */}
          <div
            className="absolute inset-0 bg-black bg-opacity-40"
            onClick={() => setIsOpen(false)}
          />
          {/* Sidebar Drawer */}
          <div className="relative w-64 h-full bg-white p-4 z-50 shadow">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Dashboard</h2>
              <button onClick={() => setIsOpen(false)}>
                <X className="w-6 h-6 text-gray-700" />
              </button>
            </div>
            <nav className="space-y-2">
              <NavLink
                to="/tasks"
                className={navStyle}
                onClick={() => setIsOpen(false)}
              >
                Tasks
              </NavLink>
              <NavLink
                to="/plans"
                className={navStyle}
                onClick={() => setIsOpen(false)}
              >
                Plans
              </NavLink>
              <NavLink
                to="/timelogs"
                className={navStyle}
                onClick={() => setIsOpen(false)}
              >
                Time Logs
              </NavLink>
            </nav>
          </div>
        </div>
      )}
    </>
  );
}
