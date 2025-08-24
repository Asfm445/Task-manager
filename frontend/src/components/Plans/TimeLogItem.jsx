import { CheckCircle, Trash2 } from "lucide-react";
import { useState } from "react";
import api from "../../api";

export default function TimeLogItem({ log, formatTime, getDuration, onDone, onDelete }) {
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(log.done);
  const [deleting, setDeleting] = useState(false);

  const handleMarkDone = async () => {
    setLoading(true);
    try {
      await api.get(`/plans/timelog/done/${log.id}`);
      setDone(true);
      if (onDone) onDone(log.id);
    } catch (err) {
      console.error("Failed to mark as done:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await api.delete(`/plans/timelog/${log.id}`);
      if (onDelete) onDelete(log.id);
    } catch (err) {
      console.error("Failed to delete timelog:", err);
    } finally {
      setDeleting(false);
    }
  };

  return (
    <li className="flex flex-col md:flex-row md:justify-between md:items-center bg-blue-50 rounded-xl px-6 py-4 border border-blue-100 shadow-md hover:bg-blue-100 transition-all duration-150">
      <div className="flex items-center gap-5">
        <span className="font-mono text-lg text-blue-800">
          {formatTime(log.start_time)} <span className="mx-1 text-gray-400">–</span>{" "}
          {formatTime(log.end_time)}
        </span>
        <span className="text-sm text-blue-700 font-bold bg-blue-100 px-4 py-1 rounded-full shadow">
          {getDuration(log.start_time, log.end_time)}
        </span>
      </div>
      <div className="flex items-center gap-4 mt-3 md:mt-0">
        <span className="text-sm text-gray-700 font-medium">
          Task: <span className="text-blue-700 font-semibold">{log.task?.description || log.task || log.task_id}</span>
        </span>
        {done ? (
          <span className="flex items-center gap-1 text-green-600 font-semibold">
            <CheckCircle className="w-5 h-5" /> Done
          </span>
        ) : (
          <button
            onClick={handleMarkDone}
            className="bg-green-500 hover:bg-green-600 text-white px-4 py-1 rounded-lg text-sm font-semibold shadow transition disabled:opacity-60"
            title="Mark as Done"
            disabled={loading}
          >
            {loading ? "Marking..." : "Mark Done"}
          </button>
        )}
        <button
          onClick={handleDelete}
          className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded-lg text-sm font-semibold shadow transition disabled:opacity-60 flex items-center gap-1"
          title="Delete Time Log"
          disabled={deleting}
        >
          <Trash2 className="w-4 h-4" />
          {deleting ? "Deleting..." : "Delete"}
        </button>
      </div>
    </li>
  );
}

// Example parent component
// import { useState } from "react";
// import TimeLogItem from "./TimeLogItem";

// function TimeLogList({ logs }) {
//   const [timeLogs, setTimeLogs] = useState(logs);

//   const handleDelete = (id) => {
//     setTimeLogs((prev) => prev.filter((log) => log.id !== id));
//   };

//   return (
//     <ul>
//       {timeLogs.map((log) => (
//         <TimeLogItem
//           key={log.id}
//           log={log}
//           formatTime={...}
//           getDuration={...}
//           onDelete={handleDelete}
//         />
//       ))}
//     </ul>
//   );
// }
