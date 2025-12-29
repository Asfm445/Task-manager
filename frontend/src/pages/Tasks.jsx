import { Hourglass, PlusCircle } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useTasks } from "../TaskContext";
import Header from "../components/Header";
import TaskForm from "../components/Tasks/TaskForm";
import TaskList from "../components/Tasks/TaskList";

export default function Tasks() {
  const {
    tasks,
    loading,
    loadingMore,
    error,
    pagination,
    fetchTasks,
    loadMoreTasks,
    resetTasks,
    createTask
  } = useTasks();

  const [showForm, setShowForm] = useState(false);
  const [editTask, setEditTask] = useState(null);
  const [message, setMessage] = useState("");

  // search and filter UI state
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("uncompleted");

  const observerRef = useRef(null);
  const lastTaskRef = useCallback(
    (node) => {
      if (loadingMore) return;
      if (observerRef.current) observerRef.current.disconnect();

      observerRef.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && pagination.hasMore) {
          loadMoreTasks();
        }
      });

      if (node) observerRef.current.observe(node);
    },
    [loadingMore, pagination.hasMore, loadMoreTasks]
  );

  // Fetch tasks when filterStatus or searchTerm changes
  useEffect(() => {
    const fetchData = async () => {
      resetTasks();
      await fetchTasks({ 
        reset: true, 
        currentFilterStatus: filterStatus, 
        currentSearchTerm: searchTerm 
      });
    };

    fetchData();
  }, [filterStatus]); // Only depend on filterStatus

  // Debounced search effect
  useEffect(() => {
    const id = setTimeout(() => {
      const fetchData = async () => {
        resetTasks();
        await fetchTasks({ 
          reset: true, 
          currentFilterStatus: filterStatus, 
          currentSearchTerm: searchTerm 
        });
      };

      fetchData();
    }, 350);

    return () => clearTimeout(id);
  }, [searchTerm]); // Only depend on searchTerm

  if (loading && !loadingMore)
    return (
      <>
        <Header></Header>
        <div className="flex justify-center items-center py-16 text-blue-600">
          <Hourglass className="animate-pulse mr-2" /> Loading tasks...
        </div>
      </>
    );

  const handleCreate = async (data) => {
    try {
      let res=await createTask(data);
      setMessage("Task created successfully");
      setShowForm(false);
      setTimeout(() => setMessage(""), 2000);
    } catch (_) {}
  };

  const handleUpdate = async (data) => {
    try {
      await fetchTasks.updateTask(editTask.id, data);
      setMessage("Task updated successfully");
      setEditTask(null);
      setTimeout(() => setMessage(""), 2000);
    } catch (_) {}
  };

  const handleDelete = async (id) => {
    try {
      await fetchTasks.deleteTask(id);
      setMessage("Task deleted");
      setTimeout(() => setMessage(""), 1500);
    } catch (_) {}
  };

  const clearSearch = () => setSearchTerm("");

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
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search tasks..."
                className="w-full outline-none text-sm"
              />
              {loadingMore && <span className="ml-2 text-xs text-blue-600">Searching...</span>}
              {searchTerm && (
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
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search tasks..."
              className="w-full outline-none text-sm"
            />
            {loadingMore && <span className="ml-2 text-xs text-blue-600">...</span>}
            {searchTerm && (
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

        {/* Status filters */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setFilterStatus("uncompleted")}
            className={`px-3 py-1 rounded-lg text-sm font-medium ${
              filterStatus === "uncompleted"
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            Uncompleted
          </button>
          <button
            onClick={() => setFilterStatus("completed")}
            className={`px-3 py-1 rounded-lg text-sm font-medium ${
              filterStatus === "completed"
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            Completed
          </button>
          <button
            onClick={() => setFilterStatus("all")}
            className={`px-3 py-1 rounded-lg text-sm font-medium ${
              filterStatus === "all"
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            All
          </button>
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
            <h2 className="text-lg font-semibold text-gray-800">Your Tasks ({pagination.total})</h2>
          </div>
          <div className="p-2 md:p-3">
            <TaskList onEdit={setEditTask} onDelete={handleDelete} tasks={tasks} />
            {loadingMore && (
              <div className="flex justify-center items-center py-4 text-blue-600">
                <Hourglass className="animate-pulse mr-2" /> Loading more tasks...
              </div>
            )}
            <div ref={lastTaskRef} style={{ height: "1px" }} /> {/* Observer target */}
            {!pagination.hasMore && !loadingMore && tasks.length > 0 && (
              <p className="text-center text-gray-500 py-4">No more tasks to load.</p>
            )}
            {tasks.length === 0 && !loading && !loadingMore && (
              <p className="text-gray-500 text-center py-4">No tasks found.</p>
            )}
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