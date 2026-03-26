import { Hourglass, PlusCircle } from "lucide-react";
import { useCallback, useMemo, useRef, useState } from "react";
import { useTaskUI } from "../TaskContext";
import { useTasksInfiniteQuery, useTaskMutations } from "../hooks/useTasksData";
import Header from "../components/Header";
import TaskItem from "../components/Tasks/TaskItem";
import TaskForm from "../components/Tasks/TaskForm";

export default function Tasks() {
  const { searchTerm, setSearchTerm, filterStatus, setFilterStatus } = useTaskUI();

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isError,
    error,
    refetch
  } = useTasksInfiniteQuery({ searchTerm, filterStatus });

  const { createTask, updateTask, deleteTask } = useTaskMutations();

  const [showForm, setShowForm] = useState(false);
  const [editTask, setEditTask] = useState(null);
  const [message, setMessage] = useState("");

  const observerRef = useRef(null);
  const lastTaskRef = useCallback(
    (node) => {
      if (isLoading || isFetchingNextPage) return;
      if (observerRef.current) observerRef.current.disconnect();

      observerRef.current = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && hasNextPage) {
          fetchNextPage();
        }
      });

      if (node) observerRef.current.observe(node);
    },
    [isLoading, isFetchingNextPage, hasNextPage, fetchNextPage]
  );

  const tasks = useMemo(() => {
    return data?.pages.flatMap((page) => page.tasks) || [];
  }, [data]);

  const totalTasks = data?.pages[0]?.total || 0;

  if (isLoading)
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
      await createTask(data);
      setMessage("Task created successfully");
      setShowForm(false);
      setTimeout(() => setMessage(""), 2000);
    } catch (_) { }
  };

  const handleUpdate = async (data) => {
    try {
      await updateTask({ id: editTask.id, payload: data });
      setMessage("Task updated successfully");
      setEditTask(null);
      setTimeout(() => setMessage(""), 2000);
    } catch (_) { }
  };

  const handleDelete = async (id) => {
    try {
      await deleteTask(id);
      setMessage("Task deleted");
      setTimeout(() => setMessage(""), 1500);
    } catch (_) { }
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
              {isFetchingNextPage && <span className="ml-2 text-xs text-blue-600">...</span>}
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

        {/* Status filters */}
        <div className="flex gap-2 mb-4">
          {["uncompleted", "completed", "all"].map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-3 py-1 rounded-lg text-sm font-medium capitalize ${filterStatus === status
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
            >
              {status}
            </button>
          ))}
        </div>

        {/* Messages */}
        {message && (
          <div className="mb-4 text-green-800 bg-green-50 border border-green-200 rounded-lg px-4 py-3 shadow-sm">
            {message}
          </div>
        )}
        {isError && (
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

        {/* Task Grid */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded-md text-sm">
                {totalTasks}
              </span>
              Tasks Available
            </h2>
            <div className="text-sm text-gray-500">
              Showing {tasks.length} of {totalTasks}
            </div>
          </div>

          {tasks.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {tasks.map((task) => (
                <div key={task.id} ref={lastTaskRef}>
                  <TaskItem task={task} onEdit={setEditTask} /> {/* TaskItem is now a card */}
                </div>
              ))}
            </div>
          ) : (
            !isLoading && (
              <div className="text-center py-20 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-full shadow-sm mb-4">
                  <Hourglass className="w-8 h-8 text-gray-300" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">No tasks found</h3>
                <p className="text-gray-500 max-w-sm mx-auto">
                  {searchTerm ? `No results for "${searchTerm}"` : "Get started by creating your first task!"}
                </p>
                {!searchTerm && (
                  <button
                    onClick={() => setShowForm(true)}
                    className="mt-4 text-blue-600 font-semibold hover:text-blue-700"
                  >
                    + Create Task
                  </button>
                )}
              </div>
            )
          )}

          {isFetchingNextPage && (
            <div className="flex justify-center items-center py-8">
              <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}

          {!hasNextPage && tasks.length > 0 && (
            <div className="text-center py-8 text-gray-400 text-sm font-medium uppercase tracking-widest">
              All tasks loaded
            </div>
          )}
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