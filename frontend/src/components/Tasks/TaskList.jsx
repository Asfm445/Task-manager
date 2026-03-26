import TaskItem from "./TaskItem";

export default function TaskList({ onEdit, tasks }) {
  if (!tasks.length) return <p className="text-center text-gray-500 py-8">No tasks found</p>;

  return (
    <div className="space-y-4">
      {tasks.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          onEdit={() => onEdit(task)}
        />
      ))}
    </div>
  );
}
