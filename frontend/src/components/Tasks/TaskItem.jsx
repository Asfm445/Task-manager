import { CheckCircle, Clock, Edit2, Hourglass, PauseCircle, PlayCircle, Trash2, UserPlus } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

const statusStyles = {
  completed: "bg-gradient-to-r from-green-400 to-green-200 text-green-900 shadow-sm",
  in_progress: "bg-gradient-to-r from-yellow-300 to-yellow-100 text-yellow-900 shadow-sm",
  pending: "bg-gradient-to-r from-gray-300 to-gray-100 text-gray-800 shadow-sm",
  stopped: "bg-gradient-to-r from-red-300 to-red-100 text-red-900 shadow-sm",
};

const statusIcons = {
  completed: <CheckCircle className="inline w-4 h-4 mr-1 text-green-600" />,
  in_progress: <Hourglass className="inline w-4 h-4 mr-1 text-yellow-600 animate-spin" />,
  pending: <Clock className="inline w-4 h-4 mr-1 text-gray-600" />,
  stopped: <PauseCircle className="inline w-4 h-4 mr-1 text-red-600" />,
};

export default function TaskItem({ task, onEdit, onDelete, stopTask, startTask, assignUser }) {
  const [actionLoading, setActionLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [showAssignForm, setShowAssignForm] = useState(false);

  const handleStop = async () => {
    setActionLoading(true);
    try {
      await stopTask(task.id);
    } catch (err) {
      console.error("Failed to stop task:", err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleStart = async () => {
    setActionLoading(true);
    try {
      await startTask(task.id);
    } catch (err) {
      console.error("Failed to start task:", err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleAssign = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await assignUser(task.id, email);
      alert("User assigned!");
      setEmail("");
      setShowAssignForm(false);
    } catch (err) {
      alert("Failed to assign user.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-100 hover:shadow-xl hover:scale-[1.02] transition-all duration-200">
      <div className="flex justify-between items-center mb-3">
        <h2 className="font-bold text-xl text-gray-900 tracking-tight">
          Task <span className="text-blue-600">#{task.id}</span>
        </h2>
        <span
          className={`flex items-center gap-1 px-4 py-1 rounded-full text-sm font-semibold ${statusStyles[task.status]} transition-all`}
        >
          {statusIcons[task.status]}
          <span className="capitalize">{task.status.replace("_", " ")}</span>
        </span>
      </div>
      <p className="text-gray-700 mb-4 text-base">{task.description}</p>

      <div className="text-sm text-gray-600 mb-4 grid grid-cols-2 sm:grid-cols-3 gap-y-2 gap-x-4">
        {task.start_date && (
          <span>
            <span className="font-medium text-gray-800">Start:</span>{" "}
            {new Date(task.start_date).toLocaleString(undefined, {
              year: "numeric",
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
        )}
        {task.end_date && (
          <span>
            <span className="font-medium text-gray-800">Due:</span>{" "}
            {new Date(task.end_date).toLocaleString(undefined, {
              year: "numeric",
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </span>
        )}
        {task.estimated_hr !== undefined && (
          <span>
            <span className="font-medium text-gray-800">Est:</span> {task.estimated_hr}h
          </span>
        )}
        {task.done_hr !== undefined && (
          <span>
            <span className="font-medium text-gray-800">Done:</span> {task.done_hr}h
          </span>
        )}
        <span>
          <span className="font-medium text-gray-800">Repetitive:</span>{" "}
          {task.is_repititive ? "Yes" : "No"}
        </span>
        {task.main_task_id && (
          <span>
            <span className="font-medium text-gray-800">Main Task:</span> #{task.main_task_id}
          </span>
        )}
      </div>

      <div className="flex flex-wrap gap-3 justify-end mt-2">
        <Link
          to={`/tasks/${task.id}`}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-colors shadow-sm text-sm md:text-base"
          title="View Task"
        >
          View
        </Link>
        <button
          onClick={() => onEdit(task)}
          className="bg-yellow-400 hover:bg-yellow-500 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-colors shadow-sm text-sm md:text-base"
          title="Edit Task"
        >
          <Edit2 size={16} /> Edit
        </button>
        <button
          onClick={() => onDelete(task.id)}
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-colors shadow-sm text-sm md:text-base"
          title="Delete Task"
        >
          <Trash2 size={16} /> Delete
        </button>
        <button
          onClick={() => setShowAssignForm((v) => !v)}
          className="bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-colors shadow-sm text-sm md:text-base"
          title="Assign User"
        >
          <UserPlus size={16} /> Assign User
        </button>
        {task.is_repititive && (
          !task.is_stopped ? (
            <button
              onClick={handleStop}
              className="bg-red-400 hover:bg-red-500 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-colors shadow-sm text-sm md:text-base"
              title="Stop Task"
              disabled={actionLoading}
            >
              <PauseCircle size={16} /> {actionLoading ? "Stopping..." : "Stop"}
            </button>
          ) : (
            <button
              onClick={handleStart}
              className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg font-semibold flex items-center gap-2 transition-colors shadow-sm text-sm md:text-base"
              title="Start Task"
              disabled={actionLoading}
            >
              <PlayCircle size={16} /> {actionLoading ? "Starting..." : "Start"}
            </button>
          )
        )}
      </div>

      {showAssignForm && (
        <form onSubmit={handleAssign} className="flex gap-2 items-center mt-4">
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            placeholder="User email"
            required
            className="px-3 py-2 border rounded-lg"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold"
          >
            {loading ? "Assigning..." : "Assign"}
          </button>
          <button
            type="button"
            onClick={() => setShowAssignForm(false)}
            className="bg-gray-200 text-gray-800 px-3 py-2 rounded-lg font-semibold"
          >
            Cancel
          </button>
        </form>
      )}
    </div>
  );
}
