


import { useEffect, useState } from "react";

export default function AddTimeLogForm({ form, setForm, tasks, loading, onSubmit }) {
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredTasks, setFilteredTasks] = useState(tasks);

  const handleFormChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  // Filter tasks based on search term
  useEffect(() => {
    if (searchTerm.trim() === "") {
      setFilteredTasks(tasks);
    } else {
      const filtered = tasks.filter(task => 
        task.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredTasks(filtered);
    }
  }, [searchTerm, tasks]);

  return (
    <form
      onSubmit={onSubmit}
      className="mb-8 bg-blue-50 rounded-lg p-6 border border-blue-200 shadow flex flex-col gap-4"
    >
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-blue-700 mb-1">Start Time</label>
          <input
            type="time"
            name="start"
            value={form.start}
            onChange={handleFormChange}
            disabled={loading}
            className="w-full px-3 py-2 rounded border border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:bg-gray-100 disabled:cursor-not-allowed"
            required
          />
        </div>
        <div className="flex-1">
          <label className="block text-sm font-medium text-blue-700 mb-1">End Time</label>
          <input
            type="time"
            name="end"
            value={form.end}
            onChange={handleFormChange}
            disabled={loading}
            className="w-full px-3 py-2 rounded border border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:bg-gray-100 disabled:cursor-not-allowed"
            required
          />
        </div>
        <div className="flex-1">
          <label className="block text-sm font-medium text-blue-700 mb-1">Task</label>
          <input
            type="text"
            placeholder="Search tasks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 rounded border border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400 mb-2"
            disabled={loading}
          />
          <select
            name="task_id"
            value={form.task_id}
            onChange={handleFormChange}
            className="w-full px-3 py-2 rounded border border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:bg-gray-100 disabled:cursor-not-allowed"
            required
            disabled={loading}
          >
            <option value="">Select task</option>
            {filteredTasks.map((task) => (
              <option key={task.id} value={task.id}>
                {task.description || `Task ${task.id}`}
              </option>
            ))}
          </select>
        </div>
      </div>
      <button
        type="submit"
        disabled={loading}
        className="self-end bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold shadow transition disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-600 flex items-center justify-center gap-2 min-w-[120px]"
      >
        {loading ? (
          <>
            <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Adding...
          </>
        ) : (
          "Add Log"
        )}
      </button>
    </form>
  );
}