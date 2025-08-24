import { useTasks } from "../../TaskContext";
import TaskItem from "./TaskItem";

export default function TaskList({ onEdit }) {
  const { tasks, updateTask, deleteTask, stopTask, startTask, assignUser } = useTasks();

  if (!tasks.length) return <p className="text-gray-500">No tasks found</p>;
  return (
    <div className="space-y-4">
      {tasks.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          onEdit={() => onEdit(task)}
          onDelete={deleteTask}
          stopTask={stopTask}
          startTask={startTask}
          assignUser={assignUser}
        />
      ))}
    </div>
  );
}
