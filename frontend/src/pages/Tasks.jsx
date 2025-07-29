// src/pages/Tasks.jsx
import React from "react";
import { CheckCircle, Clock, Hourglass } from "lucide-react";

const mockTasks = [
  {
    id: 1,
    title: "Fix bug #432",
    status: "In Progress",
    due: "2025-07-23",
    description: "Resolve the critical bug in the payment module.",
    hours: "3h",
    assignee: "Alice",
  },
  {
    id: 2,
    title: "Code review PR #108",
    status: "Pending",
    due: "2025-07-21",
    description: "Review the pull request for the new dashboard.",
    hours: "1h",
    assignee: "Bob",
  },
  {
    id: 3,
    title: "Design login page",
    status: "Completed",
    due: "2025-07-18",
    description: "Create a modern login page UI.",
    hours: "5h",
    assignee: "Charlie",
  },
];

const statusStyles = {
  Completed: "bg-green-100 text-green-700",
  "In Progress": "bg-yellow-100 text-yellow-700",
  Pending: "bg-gray-100 text-gray-700",
};

const statusIcons = {
  Completed: <CheckCircle className="inline w-4 h-4 mr-1 text-green-500" />,
  "In Progress": <Hourglass className="inline w-4 h-4 mr-1 text-yellow-500" />,
  Pending: <Clock className="inline w-4 h-4 mr-1 text-gray-500" />,
};

export default function Tasks() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-extrabold mb-8 text-blue-700 flex items-center gap-2">
        <Hourglass className="w-7 h-7 text-blue-500" />
        Tasks
      </h1>
      <div className="space-y-6">
        {mockTasks.map((task) => (
          <div
            key={task.id}
            className="bg-white p-6 rounded-xl shadow flex flex-col gap-2 border border-gray-100 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between">
              <h2 className="font-bold text-xl text-gray-800">{task.title}</h2>
              <span
                className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${
                  statusStyles[task.status]
                }`}
              >
                {statusIcons[task.status]}
                {task.status}
              </span>
            </div>
            <p className="text-gray-500 mb-2">{task.description}</p>
            <div className="flex flex-wrap gap-4 text-sm text-gray-600">
              <span>
                <b>Due:</b>{" "}
                <span className="text-blue-600 font-semibold">
                  {new Date(task.due).toLocaleDateString()}
                </span>
              </span>
              <span>
                <b>Assignee:</b> {task.assignee}
              </span>
              <span>
                <b>Est. Time:</b> {task.hours}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
