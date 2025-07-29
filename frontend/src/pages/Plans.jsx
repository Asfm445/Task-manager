// src/pages/PlanPage.jsx
import React, { useState } from "react";
import { Link } from "react-router-dom";
import { format, addDays, subDays } from "date-fns";

const mockTimeLogs = {
  "2025-07-20": [
    { start: "08:00", end: "10:00", task: "Fix bug #432" },
    { start: "14:00", end: "16:00", task: "Design login page" },
  ],
  "2025-07-21": [{ start: "09:00", end: "12:00", task: "Code review PR #108" }],
  "2025-07-22": [{ start: "11:00", end: "13:30", task: "Write documentation" }],
};

const mockTasks = [
  "Fix bug #432",
  "Design login page",
  "Code review PR #108",
  "Write documentation",
];

export default function PlanPage() {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showForm, setShowForm] = useState(false);
  const [logsByDate, setLogsByDate] = useState(mockTimeLogs);
  const [form, setForm] = useState({
    start: "",
    end: "",
    task: mockTasks[0],
  });

  const dateKey = format(selectedDate, "yyyy-MM-dd");
  const logs = logsByDate[dateKey] || [];

  const goToYesterday = () => setSelectedDate((prev) => subDays(prev, 1));
  const goToTomorrow = () => setSelectedDate((prev) => addDays(prev, 1));

  const getDuration = (start, end) => {
    const [sh, sm] = start.split(":").map(Number);
    const [eh, em] = end.split(":").map(Number);
    const duration = eh * 60 + em - (sh * 60 + sm);
    return `${Math.floor(duration / 60)}h ${duration % 60}m`;
  };

  const handleFormChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAddLog = (e) => {
    e.preventDefault();
    if (!form.start || !form.end || !form.task) return;
    setLogsByDate((prev) => ({
      ...prev,
      [dateKey]: [...(prev[dateKey] || []), { ...form }],
    }));
    setForm({ start: "", end: "", task: mockTasks[0] });
    setShowForm(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100">
      {/* Main content */}
      <main className="max-w-3xl mx-auto py-12 px-4">
        <div className="flex items-center justify-between mb-8">
          <button
            onClick={goToYesterday}
            className="flex items-center gap-1 text-gray-600 hover:text-blue-700 font-medium px-3 py-2 rounded transition-colors hover:bg-blue-100"
          >
            <span className="text-lg">⬅</span> Yesterday
          </button>
          <h2 className="text-2xl font-bold text-blue-700 tracking-tight shadow-sm px-4 py-2 rounded bg-white/80">
            {format(selectedDate, "MMMM dd, yyyy")}
          </h2>
          <button
            onClick={goToTomorrow}
            className="flex items-center gap-1 text-gray-600 hover:text-blue-700 font-medium px-3 py-2 rounded transition-colors hover:bg-blue-100"
          >
            Tomorrow <span className="text-lg">➡</span>
          </button>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8 border border-blue-100">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-blue-600 flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-blue-400 rounded-full" />
              Time Logs
            </h3>
            <button
              onClick={() => setShowForm((v) => !v)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold shadow transition"
            >
              {showForm ? "Cancel" : "Add New"}
            </button>
          </div>

          {showForm && (
            <form
              onSubmit={handleAddLog}
              className="mb-8 bg-blue-50 rounded-lg p-6 border border-blue-200 shadow flex flex-col gap-4"
            >
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-blue-700 mb-1">
                    Start Time
                  </label>
                  <input
                    type="time"
                    name="start"
                    value={form.start}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 rounded border border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
                    required
                  />
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-medium text-blue-700 mb-1">
                    End Time
                  </label>
                  <input
                    type="time"
                    name="end"
                    value={form.end}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 rounded border border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
                    required
                  />
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-medium text-blue-700 mb-1">
                    Task
                  </label>
                  <select
                    name="task"
                    value={form.task}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 rounded border border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
                    required
                  >
                    {mockTasks.map((task, idx) => (
                      <option key={idx} value={task}>
                        {task}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <button
                type="submit"
                className="self-end bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold shadow transition"
              >
                Add Log
              </button>
            </form>
          )}

          {logs.length === 0 ? (
            <p className="text-gray-400 text-center py-8">
              No logs for this day.{" "}
              <span className="font-medium text-blue-500">
                Add one to start!
              </span>
            </p>
          ) : (
            <ul className="space-y-4">
              {logs.map((log, i) => (
                <li
                  key={i}
                  className="flex flex-col md:flex-row md:justify-between md:items-center bg-blue-50 rounded-lg px-5 py-3 border border-blue-100 shadow-sm hover:bg-blue-100 transition"
                >
                  <div className="flex items-center gap-4">
                    <span className="font-mono text-lg text-blue-800">
                      {log.start} <span className="mx-1 text-gray-400">–</span>{" "}
                      {log.end}
                    </span>
                    <span className="text-sm text-blue-600 font-semibold bg-blue-100 px-3 py-1 rounded-full">
                      {getDuration(log.start, log.end)}
                    </span>
                  </div>
                  <span className="mt-2 md:mt-0 text-sm text-gray-700 font-medium">
                    Task: <span className="text-blue-700">{log.task}</span>
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  );
}
