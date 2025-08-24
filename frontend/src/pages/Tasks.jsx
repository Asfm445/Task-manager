import { Hourglass, PlusCircle } from "lucide-react";
import { useState } from "react";
import { useTasks } from "../TaskContext";
import Header from "../components/Header";
import TaskForm from "../components/Tasks/TaskForm";
import TaskList from "../components/Tasks/TaskList";

export default function Tasks() {
  const { createTask, updateTask, deleteTask, loading, error } = useTasks();
  const [showForm, setShowForm] = useState(false);
  const [editTask, setEditTask] = useState(null);
  const [message, setMessage] = useState("");

  if (loading) return (
    <div className="flex justify-center items-center py-10 text-blue-600">
      <Hourglass className="animate-pulse" /> Loading tasks...
    </div>
  );

  const handleCreate = async (data) => {
    try {
      await createTask(data);
      setMessage("Task created successfully");
      setShowForm(false);
      setTimeout(() => setMessage(""), 2000);
    } catch (_) {}
  };

  const handleUpdate = async (data) => {
    try {
      await updateTask(editTask.id, data);
      setMessage("Task updated successfully");
      setEditTask(null);
      setTimeout(() => setMessage(""), 2000);
    } catch (_) {}
  };

  const handleDelete = async (id) => {
    try {
      await deleteTask(id);
      setMessage("Task deleted");
      setTimeout(() => setMessage(""), 1500);
    } catch (_) {}
  };

  return (
    <>
      <Header></Header>
      <div className="max-w-2xl mx-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Hourglass /> Tasks
        </h1>
        <button onClick={() => setShowForm(true)} className="bg-blue-600 text-white px-4 py-2 rounded flex items-center gap-1">
          <PlusCircle /> New Task
        </button>
      </div>

      {message && <div className="mb-3 text-green-700 bg-green-50 border border-green-200 rounded px-3 py-2">{message}</div>}
      {error && <div className="mb-3 text-red-700 bg-red-50 border border-red-200 rounded px-3 py-2">{error?.response?.data?.detail || error.message}</div>}

      {showForm && <TaskForm onSubmit={handleCreate} onCancel={() => setShowForm(false)} />}
      {editTask && <TaskForm initialData={editTask} onSubmit={handleUpdate} onCancel={() => setEditTask(null)} />}

      <TaskList onEdit={setEditTask} />
    </div>
    </>
  );
}
