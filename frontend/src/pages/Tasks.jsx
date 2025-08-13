import React, { useState } from "react";
import { PlusCircle, Hourglass } from "lucide-react";
import { useTasks } from "../TaskContext";
import TaskForm from "../components/Tasks/TaskForm";
import TaskList from "../components/Tasks/TaskList";

export default function Tasks() {
  const { tasks, loading, createTask, updateTask, deleteTask } = useTasks();
  const [showForm, setShowForm] = useState(false);
  const [editTask, setEditTask] = useState(null);

  if (loading) return <p>Loading...</p>;

  const handleCreate = async (data) => {
    await createTask(data);
    setShowForm(false);
  };

  const handleUpdate = async (data) => {
    await updateTask(editTask.id, data);
    setEditTask(null);
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Hourglass /> Tasks
        </h1>
        <button onClick={() => setShowForm(true)} className="bg-blue-600 text-white px-4 py-2 rounded flex items-center gap-1">
          <PlusCircle /> New Task
        </button>
      </div>

      {showForm && <TaskForm onSubmit={handleCreate} onCancel={() => setShowForm(false)} />}
      {editTask && <TaskForm initialData={editTask} onSubmit={handleUpdate} onCancel={() => setEditTask(null)} />}

      <TaskList tasks={tasks} onEdit={setEditTask} onDelete={deleteTask} />
    </div>
  );
}
