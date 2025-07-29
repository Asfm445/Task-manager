import React from "react";

const tasks = [
  {
    id: 1,
    title: "Finish API integration",
    description: "Connect backend Go API",
    status: "In Progress",
    dueDate: "2025-07-25",
  },
  {
    id: 2,
    title: "Write unit tests",
    description: "Test services",
    status: "Completed",
    dueDate: "2025-07-22",
  },
  {
    id: 3,
    title: "Fix login bug",
    description: "Fix JWT expiration",
    status: "Pending",
    dueDate: "2025-07-21",
  },
];

const plans = [
  {
    id: 1,
    name: "Finish MVP",
    description: "Must-have features before July 28",
    dueDate: "2025-07-28",
  },
  {
    id: 2,
    name: "Polish UI/UX",
    description: "Refactor and improve layout",
    dueDate: "2025-07-30",
  },
];

const timeLogs = [
  { id: 1, task: "API Integration", date: "2025-07-20", hours: 2.5 },
  { id: 2, task: "Fix login bug", date: "2025-07-19", hours: 1 },
  { id: 3, task: "UI Polish", date: "2025-07-18", hours: 3 },
];

const getStatusColor = (status) => {
  switch (status) {
    case "Completed":
      return "bg-green-100 text-green-700";
    case "In Progress":
      return "bg-yellow-100 text-yellow-700";
    case "Pending":
      return "bg-red-100 text-red-700";
    default:
      return "bg-gray-100 text-gray-700";
  }
};

export default function Dashboard() {
  return (
    <div className="space-y-10">
      <h2 className="text-2xl font-bold text-gray-800">Dashboard</h2>

      {/* Tasks */}
      <section>
        <h3 className="text-xl font-semibold mb-3">Tasks</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {tasks.map((task) => (
            <div key={task.id} className="bg-white rounded-xl shadow p-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-semibold">{task.title}</h4>
                <span
                  className={`text-xs px-2 py-1 rounded-full ${getStatusColor(
                    task.status
                  )}`}
                >
                  {task.status}
                </span>
              </div>
              <p className="text-gray-600 text-sm">{task.description}</p>
              <p className="mt-2 text-xs text-gray-500">Due: {task.dueDate}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Plans */}
      <section>
        <h3 className="text-xl font-semibold mb-3">Plans</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className="bg-blue-50 border border-blue-200 rounded-xl p-4 shadow-sm"
            >
              <h4 className="font-semibold text-blue-800">{plan.name}</h4>
              <p className="text-sm text-blue-700">{plan.description}</p>
              <p className="mt-1 text-xs text-blue-500">Due: {plan.dueDate}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Time Logs */}
      <section>
        <h3 className="text-xl font-semibold mb-3">Time Logs</h3>
        <div className="bg-white rounded-xl shadow overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-700">
            <thead className="bg-gray-100 text-gray-600 uppercase text-xs">
              <tr>
                <th className="px-4 py-2">Task</th>
                <th className="px-4 py-2">Date</th>
                <th className="px-4 py-2">Hours</th>
              </tr>
            </thead>
            <tbody>
              {timeLogs.map((log) => (
                <tr key={log.id} className="border-t">
                  <td className="px-4 py-2">{log.task}</td>
                  <td className="px-4 py-2">{log.date}</td>
                  <td className="px-4 py-2">{log.hours} hrs</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
