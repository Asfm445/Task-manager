import { useEffect, useState } from "react";
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
  const [errors, setErrors] = useState({});
  const [backendError, setBackendError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false); // ✅ Loading state

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
    setIsSubmitting(true); // ✅ Start loading

    // Frontend validation
    if (!form.description.trim()) newErrors.description = "Description is required.";
    if (form.start_date && !form.start_time) newErrors.start_time = "Start time is required when start date is set.";
    if (form.end_date && !form.end_time) newErrors.end_time = "End time is required when end date is set.";
    if (form.estimated_hr < 0) newErrors.estimated_hr = "Estimated hours cannot be negative.";

    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) {
      setIsSubmitting(false); // ✅ Stop loading if validation fails
      return;
    }

    // Build payload
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
    if (form.estimated_hr !== "" && form.estimated_hr !== null && form.estimated_hr !== undefined) {
      payload.estimated_hr = Number(form.estimated_hr);
    }
    if (form.main_task_id) {
      payload.main_task_id = Number(form.main_task_id);
    }

    try {
      await onSubmit(payload);
      // ✅ If onSubmit succeeds, the parent component should handle closing the form
    } catch (err) {
      const msg = err.response?.data?.message || err.message || "Something went wrong.";
      setBackendError(msg);
    } finally {
      setIsSubmitting(false); // ✅ Always stop loading regardless of success/error
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-7 p-8 bg-white rounded-2xl shadow-2xl border border-gray-100 max-w-xl mx-auto"
    >
      {/* Backend Error Notification */}
      {backendError && (
        <div className="bg-red-100 text-red-700 px-4 py-2 rounded-lg text-center font-medium">
          {backendError}
        </div>
      )}

      {/* Description */}
      <div>
        <label htmlFor="description" className="block font-semibold mb-2 text-gray-800">
          Description <span className="text-red-500">*</span>
        </label>
        <input
          id="description"
          type="text"
          name="description"
          value={form.description}
          onChange={handleChange}
          required
          disabled={isSubmitting} // ✅ Disable during submission
          placeholder="Enter a brief task description"
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        {errors.description && <p className="text-sm text-red-500 mt-1">{errors.description}</p>}
      </div>

      {/* Status */}
      <div>
        <label htmlFor="status" className="block font-semibold mb-2 text-gray-800">
          Status
        </label>
        <select
          id="status"
          name="status"
          value={form.status}
          onChange={handleChange}
          disabled={isSubmitting} // ✅ Disable during submission
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          <option value="pending">Pending</option>
          <option value="in_progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {/* Start & End Date/Time */}
      <div className="grid grid-cols-2 gap-5">
        <div>
          <label htmlFor="start_date" className="block font-semibold mb-2 text-gray-800">Start Date</label>
          <input
            type="date"
            name="start_date"
            value={form.start_date}
            onChange={handleChange}
            disabled={isSubmitting} // ✅ Disable during submission
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
        </div>
        <div>
          <label htmlFor="start_time" className="block font-semibold mb-2 text-gray-800">Start Time</label>
          <TimePicker 
            value={form.start_time} 
            onChange={handleStartTimeChange} 
            disabled={isSubmitting} // ✅ Pass disabled prop to TimePicker
          />
          {errors.start_time && <p className="text-sm text-red-500 mt-1">{errors.start_time}</p>}
        </div>
        <div>
          <label htmlFor="end_date" className="block font-semibold mb-2 text-gray-800">End Date</label>
          <input
            type="date"
            name="end_date"
            value={form.end_date}
            onChange={handleChange}
            disabled={isSubmitting} // ✅ Disable during submission
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition disabled:bg-gray-100 disabled:cursor-not-allowed"
          />
        </div>
        <div>
          <label htmlFor="end_time" className="block font-semibold mb-2 text-gray-800">End Time</label>
          <TimePicker 
            value={form.end_time} 
            onChange={handleEndTimeChange} 
            disabled={isSubmitting} // ✅ Pass disabled prop to TimePicker
          />
          {errors.end_time && <p className="text-sm text-red-500 mt-1">{errors.end_time}</p>}
        </div>
      </div>

      {/* Estimated Hours */}
      <div>
        <label htmlFor="estimated_hr" className="block font-semibold mb-2 text-gray-800">Estimated Hours</label>
        <input
          type="number"
          name="estimated_hr"
          value={form.estimated_hr}
          onChange={handleChange}
          min="0"
          disabled={isSubmitting} // ✅ Disable during submission
          placeholder="e.g. 2"
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
        {errors.estimated_hr && <p className="text-sm text-red-500 mt-1">{errors.estimated_hr}</p>}
      </div>

      {/* Repetitive */}
      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          name="is_repititive"
          checked={form.is_repititive}
          onChange={handleChange}
          disabled={isSubmitting} // ✅ Disable during submission
          className="w-5 h-5 accent-blue-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <label className="font-semibold text-gray-800">Repetitive Task</label>
      </div>

      {/* Main Task */}
      <div>
        <label htmlFor="main_task_id" className="block font-semibold mb-2 text-gray-800">Main Task (Optional)</label>
        <select
          id="main_task_id"
          name="main_task_id"
          value={form.main_task_id}
          onChange={handleChange}
          disabled={isSubmitting} // ✅ Disable during submission
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition disabled:bg-gray-100 disabled:cursor-not-allowed"
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
      <div className="flex gap-4 mt-6 justify-end">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSubmitting} // ✅ Disable during submission
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-2 rounded-lg font-semibold shadow transition disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-200"
            title="Cancel"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={isSubmitting} // ✅ Disable during submission
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-semibold shadow transition disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-600 flex items-center justify-center gap-2"
          title="Save Task"
        >
          {isSubmitting ? (
            <>
              <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Saving...
            </>
          ) : (
            "Save"
          )}
        </button>
      </div>
    </form>
  );
}