import { useEffect, useState } from "react";
import { useAllTasksQuery } from "../../hooks/useTasksData";
import TimePicker from "../TimePicker";

export default function TaskForm({ initialData = null, onCancel, onSubmit }) {
  const { data: allTasks = [] } = useAllTasksQuery();

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
  const [errors, setErrors] = useState({});
  const [backendError, setBackendError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const getNowTime = () => new Date().toTimeString().slice(0, 5);

  useEffect(() => {
    if (initialData) {
      const start = initialData.start_date ? new Date(initialData.start_date) : null;
      const end = initialData.end_date ? new Date(initialData.end_date) : null;
      setForm({
        description: initialData.description || "",
        status: initialData.status || "pending",
        start_date: start ? start.toISOString().slice(0, 10) : "",
        start_time: start ? start.toTimeString().slice(0, 5) : getNowTime(),
        end_date: end ? end.toISOString().slice(0, 10) : "",
        end_time: end ? end.toTimeString().slice(0, 5) : getNowTime(),
        estimated_hr: initialData.estimated_hr ?? "",
        is_repititive: !!initialData.is_repititive,
        main_task_id: initialData.main_task_id || "",
      });
    } else {
      setForm({
        ...emptyForm,
        start_time: getNowTime(),
        end_time: getNowTime(),
      });
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
      setForm((prev) => ({ ...prev, start_time: date.toTimeString().slice(0, 5) }));
    }
  };

  const handleEndTimeChange = (date) => {
    if (date) {
      setForm((prev) => ({ ...prev, end_time: date.toTimeString().slice(0, 5) }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = {};
    setBackendError("");
    setIsSubmitting(true);

    if (!form.description.trim()) newErrors.description = "Description is required.";
    if (form.start_date && !form.start_time) newErrors.start_time = "Start time is required.";
    if (form.end_date && !form.end_time) newErrors.end_time = "End time is required.";
    if (form.estimated_hr < 0) newErrors.estimated_hr = "Hours cannot be negative.";

    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) {
      setIsSubmitting(false);
      return;
    }

    const payload = {
      description: form.description,
      status: form.status,
      is_repititive: !!form.is_repititive,
    };

    if (form.start_date && form.start_time) {
      payload.start_date = new Date(`${form.start_date}T${form.start_time}`).toISOString();
    }
    if (form.end_date && form.end_time) {
      payload.end_date = new Date(`${form.end_date}T${form.end_time}`).toISOString();
    }
    if (form.estimated_hr !== "") {
      payload.estimated_hr = Number(form.estimated_hr);
    }
    if (form.main_task_id) {
      payload.main_task_id = Number(form.main_task_id);
    }

    try {
      await onSubmit(payload);
    } catch (err) {
      setBackendError(err.response?.data?.detail || err.message || "Something went wrong.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-6 p-6 bg-white rounded-xl border border-gray-100"
    >
      {backendError && (
        <div className="bg-red-50 text-red-700 px-4 py-2 rounded-lg text-sm font-medium border border-red-100 text-center">
          {backendError}
        </div>
      )}

      {/* Description */}
      <div>
        <label className="block text-sm font-bold mb-1 text-gray-700">Description</label>
        <input
          type="text"
          name="description"
          value={form.description}
          onChange={handleChange}
          required
          disabled={isSubmitting}
          placeholder="What needs to be done?"
          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition disabled:bg-gray-50"
        />
        {errors.description && <p className="text-xs text-red-500 mt-1">{errors.description}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-bold mb-1 text-gray-700">Status</label>
          <select
            name="status"
            value={form.status}
            onChange={handleChange}
            disabled={isSubmitting}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition disabled:bg-gray-50"
          >
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-bold mb-1 text-gray-700">Estimated Hours</label>
          <input
            type="number"
            name="estimated_hr"
            value={form.estimated_hr}
            onChange={handleChange}
            min="0"
            disabled={isSubmitting}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition disabled:bg-gray-50"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-bold mb-1 text-gray-700">Start Date</label>
          <input
            type="date"
            name="start_date"
            value={form.start_date}
            onChange={handleChange}
            disabled={isSubmitting}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition disabled:bg-gray-50"
          />
        </div>
        <div>
          <label className="block text-sm font-bold mb-1 text-gray-700">Start Time</label>
          <TimePicker value={form.start_time} onChange={handleStartTimeChange} disabled={isSubmitting} />
        </div>
        <div>
          <label className="block text-sm font-bold mb-1 text-gray-700">End Date</label>
          <input
            type="date"
            name="end_date"
            value={form.end_date}
            onChange={handleChange}
            disabled={isSubmitting}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition disabled:bg-gray-50"
          />
        </div>
        <div>
          <label className="block text-sm font-bold mb-1 text-gray-700">End Time</label>
          <TimePicker value={form.end_time} onChange={handleEndTimeChange} disabled={isSubmitting} />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="is_repititive"
          name="is_repititive"
          checked={form.is_repititive}
          onChange={handleChange}
          disabled={isSubmitting}
          className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500"
        />
        <label htmlFor="is_repititive" className="text-sm font-bold text-gray-700">Repetitive Task</label>
      </div>

      <div>
        <label className="block text-sm font-bold mb-1 text-gray-700">Main Task (Optional)</label>
        <select
          name="main_task_id"
          value={form.main_task_id}
          onChange={handleChange}
          disabled={isSubmitting}
          className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition disabled:bg-gray-50"
        >
          <option value="">No Main Task</option>
          {allTasks.filter(t => t.id !== initialData?.id).map((t) => (
            <option key={t.id} value={t.id}>
              #{t.id} - {t.description}
            </option>
          ))}
        </select>
      </div>

      <div className="flex gap-3 justify-end mt-4">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting}
            className="px-6 py-2 rounded-lg font-bold text-gray-600 hover:bg-gray-50 transition"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-6 py-2 rounded-lg font-bold bg-blue-600 text-white hover:bg-blue-700 shadow-md transition disabled:opacity-50"
        >
          {isSubmitting ? "Saving..." : "Save Task"}
        </button>
      </div>
    </form>
  );
}