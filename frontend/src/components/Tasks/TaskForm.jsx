import React, { useEffect, useState } from "react";
import { useTasks } from "../../TaskContext";
import TimePicker from "../TimePicker";

export default function TaskForm({ initialData = null, onCancel, onSubmit }) {
  const { tasks } = useTasks();

  const emptyForm = {
    description: "",
    start_date: "",
    start_time: "",
    status: "pending",
    end_date: "",
    end_time: "",
    estimated_hr: "",
    is_repititive: false,
    main_task_id: "",
  };

  const [form, setForm] = useState(emptyForm);

  useEffect(() => {
    if (initialData) {
      // Pre-fill form for edit
      const start = initialData.start_date ? new Date(initialData.start_date) : null;
      const end = initialData.end_date ? new Date(initialData.end_date) : null;
      setForm({
        description: initialData.description || "",
        status: initialData.status || "pending",
        start_date: start ? start.toISOString().slice(0, 10) : "",
        start_time: start ? start.toTimeString().slice(0, 5) : "",
        end_date: end ? end.toISOString().slice(0, 10) : "",
        end_time: end ? end.toTimeString().slice(0, 5) : "",
        estimated_hr: initialData.estimated_hr ?? "",
        is_repititive: !!initialData.is_repititive,
        main_task_id: initialData.main_task_id || "",
      });
    } else {
      setForm(emptyForm);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleStartTimeChange = (date) => {
    if (date) {
      const formatted = date.toTimeString().slice(0, 5); // "HH:mm"
      setForm((prev) => ({ ...prev, start_time: formatted }));
    }
  };

  const handleEndTimeChange = (date) => {
    if (date) {
      const formatted = date.toTimeString().slice(0, 5); // "HH:mm"
      setForm((prev) => ({ ...prev, end_time: formatted }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const payload = {
      description: form.description,
      status: form.status,
      is_repititive: !!form.is_repititive,
    };

    // Combine date + time into ISO when both present
    if (form.start_date && form.start_time) {
      payload.start_date = new Date(`${form.start_date}T${form.start_time}`).toISOString();
    }
    if (form.end_date && form.end_time) {
      payload.end_date = new Date(`${form.end_date}T${form.end_time}`).toISOString();
    }

    // Only include estimated_hr if provided
    if (form.estimated_hr !== "" && form.estimated_hr !== null && form.estimated_hr !== undefined) {
      payload.estimated_hr = Number(form.estimated_hr);
    }

    // Main task id
    if (form.main_task_id) {
      payload.main_task_id = Number(form.main_task_id);
    }

    onSubmit(payload);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-5 bg-blue-50 p-6 rounded-lg border border-blue-200 shadow"
    >
      {/* Description */}
      <div>
        <label htmlFor="description" className="block font-semibold mb-1 text-gray-700">
          Description <span className="text-red-500">*</span>
        </label>
        <input
          id="description"
          type="text"
          name="description"
          placeholder="Task description"
          value={form.description}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>

      {/* Status */}
      <div>
        <label htmlFor="status" className="block font-semibold mb-1 text-gray-700">
          Status <span className="text-red-500">*</span>
        </label>
        <select
          id="status"
          name="status"
          value={form.status}
          onChange={handleChange}
          className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="pending">Pending</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {/* Start Date + Time */}
      <div className="flex gap-3">
        <div className="flex-1">
          <label htmlFor="start_date" className="block font-semibold mb-1 text-gray-700">
            Start Date
          </label>
          <input
            id="start_date"
            type="date"
            name="start_date"
            value={form.start_date}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>
        <div className="flex-1">
          <label htmlFor="start_time" className="block font-semibold mb-1 text-gray-700">
            Start Time
          </label>
          <TimePicker value={form.start_time} onChange={handleStartTimeChange} />
        </div>
      </div>

      {/* End Date + Time */}
      <div className="flex gap-3">
        <div className="flex-1">
          <label htmlFor="end_date" className="block font-semibold mb-1 text-gray-700">
            End Date
          </label>
          <input
            id="end_date"
            type="date"
            name="end_date"
            value={form.end_date}
            onChange={handleChange}
            className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>
        <div className="flex-1">
          <label htmlFor="end_time" className="block font-semibold mb-1 text-gray-700">
            End Time
          </label>
          <TimePicker value={form.end_time} onChange={handleEndTimeChange} />
        </div>
      </div>

      {/* Estimated Hours */}
      <div>
        <label htmlFor="estimated_hr" className="block font-semibold mb-1 text-gray-700">
          Estimated Hours
        </label>
        <input
          id="estimated_hr"
          type="number"
          name="estimated_hr"
          value={form.estimated_hr}
          onChange={handleChange}
          min="0"
          placeholder="0"
          className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>

      {/* Repetitive */}
      <div className="flex items-center gap-3">
        <input
          id="is_repititive"
          type="checkbox"
          name="is_repititive"
          checked={form.is_repititive}
          onChange={handleChange}
          className="w-4 h-4"
        />
        <label htmlFor="is_repititive" className="font-semibold text-gray-700">
          Repetitive Task
        </label>
      </div>

      {/* Main Task */}
      <div>
        <label htmlFor="main_task_id" className="block font-semibold mb-1 text-gray-700">
          Main Task (Optional)
        </label>
        <select
          id="main_task_id"
          name="main_task_id"
          value={form.main_task_id}
          onChange={handleChange}
          className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
        >
          <option value="">No Main Task</option>
          {tasks.map((t) => (
            <option key={t.id} value={t.id}>
              #{t.id} - {t.description}
            </option>
          ))}
        </select>
      </div>

      {/* Buttons */}
      <div className="flex gap-3 mt-4">
        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold shadow transition"
        >
          Save
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="bg-gray-400 hover:bg-gray-500 text-white px-6 py-2 rounded-lg font-semibold shadow transition"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
