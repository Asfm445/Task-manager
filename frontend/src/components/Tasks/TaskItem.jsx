import React from "react";
import { Edit2, Trash2, Clock, Hourglass, CheckCircle } from "lucide-react";

const statusStyles = {
  completed: "bg-green-100 text-green-700",
  in_progress: "bg-yellow-100 text-yellow-700",
  pending: "bg-gray-100 text-gray-700",
};

const statusIcons = {
  completed: <CheckCircle className="inline w-4 h-4 mr-1 text-green-500" />,
  in_progress: <Hourglass className="inline w-4 h-4 mr-1 text-yellow-500" />,
  pending: <Clock className="inline w-4 h-4 mr-1 text-gray-500" />,
};

export default function TaskItem({ task, onEdit, onDelete }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow border">
      <div className="flex justify-between items-center">
        <h2 className="font-bold">Task #{task.id}</h2>
        <span className={`flex items-center px-2 py-1 rounded ${statusStyles[task.status]}`}>
          {statusIcons[task.status]}
          {task.status.replace("_", " ")}
        </span>
      </div>
      <p className="text-gray-600">{task.description}</p>
      <div className="text-sm text-gray-500 mt-2 flex gap-3">
        <span>Due: {task.end_date && new Date(task.end_date).toLocaleDateString()}</span>
        <span>Est: {task.estimated_hr}h</span>
        <span>Done: {task.done_hr}h</span>
        <span>Repetitive: {task.is_repititive ? "Yes" : "No"}</span>
        {task.main_task_id && <span>Main Task: #{task.main_task_id}</span>}
      </div>
      <div className="flex gap-2 mt-3">
        <button onClick={() => onEdit(task)} className="bg-yellow-400 text-white px-3 py-1 rounded flex items-center gap-1">
          <Edit2 size={14} /> Edit
        </button>
        <button onClick={() => onDelete(task.id)} className="bg-red-500 text-white px-3 py-1 rounded flex items-center gap-1">
          <Trash2 size={14} /> Delete
        </button>
      </div>
    </div>
  );
}
