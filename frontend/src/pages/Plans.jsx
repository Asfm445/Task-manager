import React, { useState, useEffect } from "react";
import { format, addDays, subDays } from "date-fns";
import api from "../api"; // <-- import your axios instance here

export default function PlanPage() {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showForm, setShowForm] = useState(false);
  const [logs, setLogs] = useState([]);
  const [form, setForm] = useState({
    start: "",
    end: "",
    task: "",
  });

  const dateKey = format(selectedDate, "yyyy-MM-dd");

 useEffect(() => {
  const fetchLogs = async () => {
    try {
      console.log("Sending to backend:", { date: dateKey });
      const res = await api.post("plans/", { date: dateKey }); // POST with { date: 'yyyy-MM-dd' }
      console.log("Fetched data for", dateKey, res.data);
      setLogs(res.data.times || []);
    } catch (err) {
      console.error("Failed to fetch logs:", err);
      setLogs([]);
    }
  };

  fetchLogs();
}, [dateKey]);


  const goToYesterday = () => setSelectedDate((prev) => subDays(prev, 1));
  const goToTomorrow = () => setSelectedDate((prev) => addDays(prev, 1));

 // Helper: format raw time string "HH:mm:ss.xxx" => "HH:mm"
const formatTime = (timeStr) => {
  if (!timeStr) return "";
  const parts = timeStr.split(":");
  if (parts.length < 2) return timeStr; // fallback
  return `${parts[0].padStart(2, "0")}:${parts[1].padStart(2, "0")}`;
};

// Calculate duration between start and end times (ignore seconds)
const getDuration = (start, end) => {
  if (!start || !end) return "";

  // Extract hours and minutes as numbers
  const [sh, sm] = start.split(":").map(Number);
  const [eh, em] = end.split(":").map(Number);

  let duration = eh * 60 + em - (sh * 60 + sm);
  if (duration < 0) duration = 0; // no negative durations

  const hours = Math.floor(duration / 60);
  const minutes = duration % 60;

  return `${hours}h ${minutes}m`;
};



  const handleFormChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAddLog = (e) => {
    e.preventDefault();
    if (!form.start || !form.end || !form.task) return;
    console.log("Submitting time log for", dateKey, form);
    setForm({ start: "", end: "", task: "" });
    setShowForm(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100">
      <main className="max-w-3xl mx-auto py-12 px-4">
        {/* ... your existing UI code for date navigation and logs display ... */}
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
                  <input
                    type="text"
                    name="task"
                    value={form.task}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 rounded border border-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
                    placeholder="Task description"
                    required
                  />
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
      {formatTime(log.start_time)} <span className="mx-1 text-gray-400">–</span>{" "}
      {formatTime(log.end_time)}
    </span>
    <span className="text-sm text-blue-600 font-semibold bg-blue-100 px-3 py-1 rounded-full">
      {getDuration(log.start_time, log.end_time)}
    </span>

    </div>
    <span className="mt-2 md:mt-0 text-sm text-gray-700 font-medium">
      Task:{" "}
      <span className="text-blue-700">
        {log.task?.description || log.task || log.task_id || "No description"}
      </span>
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
