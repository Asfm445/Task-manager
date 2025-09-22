import { Hourglass, PlusCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { useTasks } from "../TaskContext";
import Header from "../components/Header";
import TaskForm from "../components/Tasks/TaskForm";
import TaskList from "../components/Tasks/TaskList";

export default function Tasks() {
  const { createTask, updateTask, deleteTask, loading, error, searchTasks } = useTasks();
  const [showForm, setShowForm] = useState(false);
  const [editTask, setEditTask] = useState(null);
  const [message, setMessage] = useState("");

  // search UI state
  const [search, setSearch] = useState("");
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    if (typeof searchTasks !== "function") return;
    setIsSearching(true);
    const id = setTimeout(async () => {
      try {
        await searchTasks(search.trim()); // backend-powered search via TaskProvider
      } finally {
        setIsSearching(false);
      }
    }, 350); // debounce
    return () => clearTimeout(id);
  }, [search, searchTasks]);

  if (loading) return (
    <>
      <Header></Header>
      <div className="flex justify-center items-center py-16 text-blue-600">
        <Hourglass className="animate-pulse mr-2" /> Loading tasks...
      </div>
    </>
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

  const clearSearch = () => setSearch("");

  return (
    <>
      <Header></Header>
      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* Page header / actions */}
        <div className="flex items-center justify-between mb-6 gap-3">
          <div className="flex items-center gap-3">
            <div className="px-2.5 py-1 rounded-lg bg-blue-50 text-blue-700 border border-blue-100 shadow-sm">
              <Hourglass className="w-4 h-4" />
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-gray-900">
              Tasks
            </h1>
          </div>

          <div className="flex items-center gap-2">
            {/* Search bar */}
            <div className="hidden sm:flex items-center bg-white border border-gray-200 rounded-lg shadow-sm px-3 py-2 w-64">
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-gray-400 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m21 21-4.3-4.3m0 0A7.5 7.5 0 1 0 5 5a7.5 7.5 0 0 0 11.7 11.7Z" />
              </svg>
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search tasks..."
                className="w-full outline-none text-sm"
              />
              {isSearching && <span className="ml-2 text-xs text-blue-600">Searching...</span>}
              {search && (
                <button
                  onClick={clearSearch}
                  className="ml-2 text-gray-400 hover:text-gray-600"
                  title="Clear"
                >
                  ×
                </button>
              )}
            </div>

            <button
              onClick={() => setShowForm(true)}
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-4 py-2 rounded-lg shadow-sm transition-colors"
            >
              <PlusCircle className="w-5 h-5" /> New Task
            </button>
          </div>
        </div>

        {/* Mobile search */}
        <div className="sm:hidden mb-4">
          <div className="flex items-center bg-white border border-gray-200 rounded-lg shadow-sm px-3 py-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-gray-400 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m21 21-4.3-4.3m0 0A7.5 7.5 0 1 0 5 5a7.5 7.5 0 0 0 11.7 11.7Z" />
            </svg>
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search tasks..."
              className="w-full outline-none text-sm"
            />
            {isSearching && <span className="ml-2 text-xs text-blue-600">...</span>}
            {search && (
              <button
                onClick={clearSearch}
                className="ml-2 text-gray-400 hover:text-gray-600"
                title="Clear"
              >
                ×
              </button>
            )}
          </div>
        </div>

        {/* Messages */}
        {message && (
          <div className="mb-4 text-green-800 bg-green-50 border border-green-200 rounded-lg px-4 py-3 shadow-sm">
            {message}
          </div>
        )}
        {error && (
          <div className="mb-4 text-red-800 bg-red-50 border border-red-200 rounded-lg px-4 py-3 shadow-sm">
            {error?.response?.data?.detail || error.message}
          </div>
        )}

        {/* Forms */}
        {showForm && (
          <div className="mb-6 bg-white rounded-xl border border-gray-200 shadow p-4">
            <TaskForm onSubmit={handleCreate} onCancel={() => setShowForm(false)} />
          </div>
        )}
        {editTask && (
          <div className="mb-6 bg-white rounded-xl border border-gray-200 shadow p-4">
            <TaskForm initialData={editTask} onSubmit={handleUpdate} onCancel={() => setEditTask(null)} />
          </div>
        )}

        {/* Task list in a card */}
        <div className="bg-white rounded-xl border border-gray-200 shadow">
          <div className="px-4 py-3 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-800">Your Tasks</h2>
          </div>
          <div className="p-2 md:p-3">
            <TaskList onEdit={setEditTask} onDelete={handleDelete} />
          </div>
        </div>
      </div>

      {/* Floating action (mobile) */}
      {!showForm && !editTask && (
        <button
          onClick={() => setShowForm(true)}
          className="fixed bottom-6 right-6 md:hidden bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg p-4 transition-colors"
          aria-label="Create new task"
        >
          <PlusCircle className="w-6 h-6" />
        </button>
      )}
    </>
  );
}