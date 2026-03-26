import { format } from "date-fns";
import { useState } from "react";
import Header from "../components/Header";
import AddTimeLogForm from "../components/Plans/AddTimeLogForm";
import DateNavigator from "../components/Plans/DateNavigator";
import TimeLogItem from "../components/Plans/TimeLogItem";
import { usePlansQuery, usePlanMutations, useAllTasksQuery } from "../hooks/useTasksData";

export default function PlanPage() {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ start: "", end: "", task_id: "" });

  const dateKey = format(selectedDate, "yyyy-MM-dd");

  const { data: planData, isLoading: plansLoading } = usePlansQuery(dateKey);
  const { data: allTasks, isLoading: tasksLoading } = useAllTasksQuery();
  const { addLog, markSuccess, deleteLog } = usePlanMutations();

  const [isSubmitting, setIsSubmitting] = useState(false);

  const logs = planData?.times || [];
  const planId = planData?.id;

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
    if (!form.start || !form.end || !form.task_id || !planId) return;

    setIsSubmitting(true);
    try {
      const payload = {
        task_id: parseInt(form.task_id, 10),
        start_time: form.start.length === 5 ? `${form.start}:00` : form.start,
        end_time: form.end.length === 5 ? `${form.end}:00` : form.end,
        plan_id: planId,
        description: form.description,
      };
      await addLog(payload);
      setForm({ start: "", end: "", task_id: "" });
      setShowForm(false);
    } catch (err) {
      console.error("Failed to add log:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleMarkSuccess = async (timelog_id) => {
    try {
      await markSuccess(timelog_id);
    } catch (err) {
      console.error("Failed to mark success:", err);
    }
  };

  const handleDeleteLog = async (timelog_id) => {
    try {
      await deleteLog(timelog_id);
    } catch (err) {
      console.error("Failed to delete log:", err);
    }
  };

  return (
    <>
      <Header />
      <div className="bg-gray-50 min-h-[calc(100vh-64px)]">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <DateNavigator selectedDate={selectedDate} setSelectedDate={setSelectedDate} />

          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 md:p-8 mt-6">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  <span className="inline-block w-2.5 h-2.5 bg-blue-600 rounded-full shadow-sm" />
                  Time Logs
                </h3>
                <p className="text-sm text-gray-500 mt-1">Manage your daily activity</p>
              </div>
              <button
                onClick={() => setShowForm((v) => !v)}
                className={`px-4 py-2 rounded-lg font-semibold shadow-sm transition-all ${showForm
                  ? "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  : "bg-blue-600 text-white hover:bg-blue-700 hover:shadow-md"
                  }`}
              >
                {showForm ? "Cancel" : "+ Add Entry"}
              </button>
            </div>

            {showForm && (
              <div className="mb-8 p-4 bg-gray-50 rounded-xl border border-gray-200 animate-in fade-in slide-in-from-top-2">
                <AddTimeLogForm
                  form={form}
                  setForm={setForm}
                  tasks={allTasks || []}
                  loading={isSubmitting}
                  onSubmit={handleAddLog}
                />
              </div>
            )}

            {plansLoading ? (
              <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mb-3"></div>
                <p className="text-sm">Loading logs...</p>
              </div>
            ) : logs.length === 0 ? (
              <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                <div className="text-4xl mb-3">📝</div>
                <h4 className="text-gray-900 font-medium mb-1">No logs for this day</h4>
                <p className="text-gray-500 text-sm">
                  Click <span className="text-blue-600 font-semibold">Add Entry</span> to start tracking time.
                </p>
              </div>
            ) : (
              <ul className="space-y-4">
                {logs.map((log) => (
                  <TimeLogItem
                    key={log.id || log.start_time}
                    log={log}
                    formatTime={formatTime}
                    getDuration={getDuration}
                    onDone={handleMarkSuccess}
                    onDelete={handleDeleteLog}
                  />
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
