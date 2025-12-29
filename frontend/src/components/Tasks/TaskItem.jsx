import {
  Calendar, CheckCircle2, Clock, Edit3, MoreVertical,
  Pause, Play, Trash2, UserPlus, StopCircle, ArrowRight
} from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { useTaskMutations } from "../../hooks/useTasksData";

const statusConfig = {
  completed: {
    bg: "bg-green-100",
    text: "text-green-700",
    border: "border-green-200",
    icon: CheckCircle2,
    label: "Completed"
  },
  in_progress: {
    bg: "bg-blue-100",
    text: "text-blue-700",
    border: "border-blue-200",
    icon: Clock,
    label: "In Progress"
  },
  pending: {
    bg: "bg-gray-100",
    text: "text-gray-600",
    border: "border-gray-200",
    icon: Clock, // Keeping clock for pending
    label: "Pending"
  },
  stopped: {
    bg: "bg-red-100",
    text: "text-red-700",
    border: "border-red-200",
    icon: StopCircle,
    label: "Stopped"
  },
};

export default function TaskItem({ task, onEdit }) {
  const { toggleTask, deleteTask, assignUser } = useTaskMutations();
  const [email, setEmail] = useState("");
  const [isAssigning, setIsAssigning] = useState(false);
  const [showAssignForm, setShowAssignForm] = useState(false);
  const [isActionLoading, setIsActionLoading] = useState(false);

  const status = statusConfig[task.status] || statusConfig.pending;
  const StatusIcon = status.icon;

  const handleToggle = async (stop) => {
    setIsActionLoading(true);
    try {
      await toggleTask({ id: task.id, stop });
    } catch (err) {
      console.error("Failed to toggle task:", err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this task?")) return;
    setIsActionLoading(true);
    try {
      await deleteTask(task.id);
    } catch (err) {
      console.error("Failed to delete task:", err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleAssign = async (e) => {
    e.preventDefault();
    setIsAssigning(true);
    try {
      await assignUser({ taskId: task.id, email });
      setEmail("");
      setShowAssignForm(false);
    } catch (err) {
      alert("Failed to assign user.");
    } finally {
      setIsAssigning(false);
    }
  };

  const formatDate = (date) => new Date(date).toLocaleDateString("en-US", { month: "short", day: "numeric" });

  return (
    <div className="group relative bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md hover:border-blue-200 transition-all duration-300 flex flex-col h-full">
      {/* Card Header & Status */}
      <div className="p-5 flex-1">
        <div className="flex justify-between items-start mb-3">
          <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${status.bg} ${status.text} ${status.border}`}>
            <StatusIcon className="w-3.5 h-3.5" />
            {status.label}
          </div>
          {task.is_repititive && (
            <span className="text-xs font-medium text-purple-600 bg-purple-50 px-2 py-1 rounded-md border border-purple-100">
              Repetitive
            </span>
          )}
        </div>

        <Link to={`/tasks/${task.id}`} className="block group-hover:text-blue-600 transition-colors">
          <h3 className="font-bold text-gray-900 text-lg mb-2 line-clamp-2 leading-tight">
            {task.description}
          </h3>
        </Link>

        <div className="text-sm text-gray-500 mb-4 font-mono">#{task.id}</div>

        {/* Mini Grid Metrics */}
        <div className="grid grid-cols-2 gap-3 text-sm text-gray-600 mb-4">
          <div className="bg-gray-50 p-2 rounded-lg">
            <span className="block text-xs text-gray-400 font-medium uppercase tracking-wider mb-0.5">Est.</span>
            <span className="font-semibold text-gray-900">{task.estimated_hr}h</span>
          </div>
          <div className={`p-2 rounded-lg ${task.done_hr > task.estimated_hr ? "bg-red-50 text-red-700" : "bg-blue-50 text-blue-700"}`}>
            <span className="block text-xs opacity-70 font-medium uppercase tracking-wider mb-0.5">Done</span>
            <span className="font-semibold">{task.done_hr}h</span>
          </div>
          {task.start_date && (
            <div className="bg-gray-50 p-2 rounded-lg col-span-2 flex justify-between items-center">
              <span className="text-xs text-gray-400 font-medium uppercase tracking-wider">Timeline</span>
              <span className="font-medium text-gray-700">
                {formatDate(task.start_date)}
                {task.end_date && <span className="text-gray-400 mx-1">→</span>}
                {task.end_date && formatDate(task.end_date)}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Action Footer */}
      <div className="p-4 border-t border-gray-100 bg-gray-50/50 rounded-b-xl flex items-center justify-between gap-2">
        <div className="flex gap-1">
          <Link
            to={`/tasks/${task.id}`}
            className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            title="View Details"
          >
            <ArrowRight className="w-4 h-4" />
          </Link>

          <button
            onClick={() => onEdit(task)}
            className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            title="Edit Task"
          >
            <Edit3 className="w-4 h-4" />
          </button>

          <button
            onClick={() => setShowAssignForm(!showAssignForm)}
            className={`p-2 rounded-lg transition-colors ${showAssignForm ? "bg-indigo-50 text-indigo-600" : "text-gray-500 hover:text-indigo-600 hover:bg-indigo-50"}`}
            title="Assign User"
          >
            <UserPlus className="w-4 h-4" />
          </button>

          <button
            onClick={handleDelete}
            disabled={isActionLoading}
            className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors disabled:opacity-50"
            title="Delete Task"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>

        {task.is_repititive && (
          <button
            onClick={() => handleToggle(!task.is_stopped)}
            disabled={isActionLoading}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all shadow-sm ${task.is_stopped
              ? "bg-green-600 hover:bg-green-700 text-white"
              : "bg-white text-gray-700 border border-gray-200 hover:bg-gray-50"
              }`}
          >
            {task.is_stopped ? <Play className="w-3.5 h-3.5 fill-current" /> : <Pause className="w-3.5 h-3.5 fill-current" />}
            {task.is_stopped ? "RESUME" : "STOP"}
          </button>
        )}
      </div>

      {/* Assign Popover (Inline) */}
      {showAssignForm && (
        <div className="absolute bottom-16 left-4 right-4 bg-white p-3 rounded-xl shadow-xl border border-gray-200 z-10 animate-in fade-in slide-in-from-bottom-2">
          <form onSubmit={handleAssign} className="flex gap-2">
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="Assignee email..."
              autoFocus
              className="flex-1 px-3 py-1.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />
            <button
              disabled={isAssigning}
              className="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-xs font-bold hover:bg-blue-700 transition-colors"
            >
              Add
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
