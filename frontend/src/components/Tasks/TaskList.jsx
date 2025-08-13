import React from "react";
import TaskItem from "./TaskItem";

export default function TaskList({ tasks, onEdit, onDelete }) {
  if (!tasks.length) return <p className="text-gray-500">No tasks found</p>;
  return (
    <div className="space-y-4">
      {tasks.map(task => (
        <TaskItem key={task.id} task={task} onEdit={onEdit} onDelete={onDelete} />
      ))}
    </div>
  );
}
