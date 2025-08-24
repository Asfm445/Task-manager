import { format } from "date-fns";
import { useEffect, useState } from "react";
import api from "../api";
import Header from "../components/Header";
import AddTimeLogForm from "../components/Plans/AddTimeLogForm";
import DateNavigator from "../components/Plans/DateNavigator";
import TimeLogItem from "../components/Plans/TimeLogItem";
import { useTasks } from "../TaskContext";

export default function PlanPage() {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showForm, setShowForm] = useState(false);
  const [logs, setLogs] = useState([]);
  const [plan, setPlan] = useState({});
  const { tasks, loading } = useTasks();

  const [form, setForm] = useState({ start: "", end: "", task_id: "" });
  const dateKey = format(selectedDate, "yyyy-MM-dd");

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await api.post("plans/", { date: dateKey });
        setPlan(res.data);
        setLogs(res.data.times || []);
      } catch (err) {
        console.error("Failed to fetch logs:", err);
        setLogs([]);
      }
    };
    fetchLogs();
  }, [dateKey]);

  const formatTime = (timeStr) => {
    if (!timeStr) return "";
    const parts = timeStr.split(":");
    if (parts.length < 2) return timeStr;
    return `${parts[0].padStart(2, "0")}:${parts[1].padStart(2, "0")}`;
  };

  const getDuration = (start, end) => {
    if (!start || !end) return "";
    const [sh, sm] = start.split(":").map(Number);
    const [eh, em] = end.split(":").map(Number);
    let duration = eh * 60 + em - (sh * 60 + sm);
    if (duration < 0) duration = 0;
    const hours = Math.floor(duration / 60);
    const minutes = duration % 60;
    return `${hours}h ${minutes}m`;
  };

  const handleAddLog = async (e) => {
    e.preventDefault();
    if (!form.start || !form.end || !form.task_id) return;
    try {
      const payload = {
        task_id: parseInt(form.task_id, 10),
        start_time: form.start.length === 5 ? `${form.start}:00` : form.start,
        end_time: form.end.length === 5 ? `${form.end}:00` : form.end,
        plan_id: plan.id,
      };
      await api.post("plans/timelog", payload);
      setForm({ start: "", end: "", task_id: "" });
      setShowForm(false);

      const res = await api.post("plans/", { date: dateKey });
      setLogs(res.data.times || []);
    } catch (err) {
      console.error("Failed to add log:", err);
    }
  };

  const handleMarkSuccess = async (timelog_id) => {
    try {
      await api.get(`plans/timelog/done/${timelog_id}`);
      // const res = await api.post("plans/", { date: dateKey });
      // setLogs(res.data.times || []);
    } catch (err) {
      console.error("Failed to mark success:", err);
    }
  };

  const handleDeleteLog = async (timelog_id) => {
    try {
      await api.delete(`plans/timelog/${timelog_id}`);
      setLogs((prev) => prev.filter((log) => log.id !== timelog_id));
    } catch (err) {
      console.error("Failed to delete log:", err);
    }
  };

  return (
    <>
      <Header></Header>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-gray-100">
      <main className="max-w-3xl mx-auto py-12 px-4">
        <DateNavigator selectedDate={selectedDate} setSelectedDate={setSelectedDate} />

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
            <AddTimeLogForm form={form} setForm={setForm} tasks={tasks} loading={loading} onSubmit={handleAddLog} />
          )}

          {logs.length === 0 ? (
            <p className="text-gray-400 text-center py-8">
              No logs for this day. <span className="font-medium text-blue-500">Add one to start!</span>
            </p>
          ) : (
            <ul className="space-y-4">
              {logs.map((log) => (
                <TimeLogItem
                  key={log.id || log.start_time}
                  log={log}
                  formatTime={formatTime}
                  getDuration={getDuration}
                  onMarkSuccess={handleMarkSuccess}
                  onDeleteLog={handleDeleteLog}
                />
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
    </>
  );
}
