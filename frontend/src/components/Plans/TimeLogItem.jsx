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
    <li className="bg-blue-50 rounded-xl p-4 border border-blue-100 shadow-md hover:bg-blue-100 transition-all duration-150">
      {/* Top Row - Time and Duration */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-3">
          <span className="font-mono text-base sm:text-lg text-blue-800 font-medium">
            {formatTime(log.start_time)} <span className="mx-1 text-gray-400">–</span>{" "}
            {formatTime(log.end_time)}
          </span>
          <span className="text-xs sm:text-sm text-blue-700 font-bold bg-blue-200 px-2 py-1 rounded-full shadow">
            {getDuration(log.start_time, log.end_time)}
          </span>
        </div>
        
        {/* Status indicator for mobile */}
        {done && (
          <span className="sm:hidden flex items-center gap-1 text-green-600 font-semibold text-sm">
            <CheckCircle className="w-4 h-4" /> Completed
          </span>
        )}
      </div>
      
      {/* Bottom Row - Task and Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex-1 min-w-0">
          <span className="text-sm text-gray-700 font-medium block mb-1 sm:mb-0 sm:inline">
            Task:{" "}
          </span>
          <span className="text-blue-700 font-semibold text-sm sm:text-base truncate block sm:inline">
            {log.task?.description || log.task || log.task_id}
          </span>
        </div>
        
        <div className="flex items-center gap-2 self-end sm:self-auto">
          {done ? (
            <span className="hidden sm:flex items-center gap-1 text-green-600 font-semibold text-sm">
              <CheckCircle className="w-4 h-4" /> Completed
            </span>
          ) : (
            <button
              onClick={handleMarkDone}
              className="bg-green-500 hover:bg-green-600 text-white px-3 py-1.5 rounded-lg text-xs sm:text-sm font-semibold shadow transition disabled:opacity-60 flex items-center gap-1"
              title="Mark as Done"
              disabled={loading}
            >
              <CheckCircle className="w-3 h-3 sm:w-4 sm:h-4" />
              <span className="hidden xs:inline">{loading ? "Marking..." : "Done"}</span>
            </button>
          )}
          
          <button
            onClick={handleDelete}
            className="bg-red-500 hover:bg-red-600 text-white px-3 py-1.5 rounded-lg text-xs sm:text-sm font-semibold shadow transition disabled:opacity-60 flex items-center gap-1"
            title="Delete Time Log"
            disabled={deleting}
          >
            <Trash2 className="w-3 h-3 sm:w-4 sm:h-4" />
            <span className="hidden xs:inline">{deleting ? "Deleting..." : "Delete"}</span>
          </button>
        </div>
      </div>
    </li>
  );
}