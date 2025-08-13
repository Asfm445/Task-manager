export default function AddTimeLogForm({ form, setForm, tasks, loading, onSubmit }) {
  const handleFormChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

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
            className="w-full px-3 py-2 rounded border border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
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
            className="w-full px-3 py-2 rounded border border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
            required
          />
        </div>
        <div className="flex-1">
          <label className="block text-sm font-medium text-blue-700 mb-1">Task</label>
          <select
            name="task_id"
            value={form.task_id}
            onChange={handleFormChange}
            className="w-full px-3 py-2 rounded border border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
            required
            disabled={loading}
          >
            <option value="">Select task</option>
            {tasks.map((task) => (
              <option key={task.id} value={task.id}>
                {task.description || `Task ${task.id}`}
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
  );
}
