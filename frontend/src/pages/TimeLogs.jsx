// src/pages/TimeLogs.jsx
import React from "react";

const mockLogs = [
  { id: 1, task: "Fix bug #432", hours: 3, date: "2025-07-19" },
  { id: 2, task: "Login UI", hours: 2, date: "2025-07-18" },
  { id: 3, task: "API docs", hours: 1.5, date: "2025-07-17" },
];

export default function TimeLogs() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Time Logs</h1>
      <table className="w-full table-auto bg-white shadow rounded-xl">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-4 py-2 text-left">Task</th>
            <th className="px-4 py-2 text-left">Hours</th>
            <th className="px-4 py-2 text-left">Date</th>
          </tr>
        </thead>
        <tbody>
          {mockLogs.map((log) => (
            <div className="bg-white p-4 rounded shadow w-full md:w-2/3">
              <h2 className="font-bold text-lg mb-2">Time Logs</h2>
              <ul className="space-y-2">
                <li className="border p-2 rounded">
                  08:00 - 12:00 → Build Frontend (4h)
                </li>
                <li className="border p-2 rounded">
                  13:00 - 15:00 → Fix Login Bug (2h)
                </li>
              </ul>
            </div>
          ))}
        </tbody>
      </table>
    </div>
  );
}
