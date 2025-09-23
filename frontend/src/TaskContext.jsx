import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./api";
import { checkIsAuthorized } from "./authorize";

export const TaskContext = createContext();

export const TaskProvider = ({ children }) => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 20,
    total: 0,
    hasMore: true
  });
  const navigate = useNavigate();

  // Helper to ensure user is authorized before any request
  const ensureAuthorized = useCallback(async () => {
    try {
      const authorized = await checkIsAuthorized();
      if (!authorized) {
        navigate("/login");
        return false;
      }
      return true;
    } catch (err) {
      console.error("Authorization check failed:", err);
      setError(err);
      navigate("/login");
      return false;
    }
  }, [navigate]);

  // Enhanced fetchTasks that accepts parameters
  const fetchTasks = useCallback(async (options = {}) => {
    const {
      reset = true,
      currentFilterStatus = "uncompleted",
      currentSearchTerm = "",
      skip = null,
      limit = null
    } = options;
    
    setLoading(true);
    setError(null);

    if (!(await ensureAuthorized())) {
      setLoading(false);
      return;
    }

    try {
      const currentSkip = skip !== null ? skip : (reset ? 0 : pagination.skip);
      const currentLimit = limit !== null ? limit : pagination.limit;

      const params = {
        skip: currentSkip,
        limit: currentLimit,
        search_name: currentSearchTerm || undefined,
      };
      
      // Backend expects 'uncompleted' or 'completed' to be true/false
      if (currentFilterStatus === "completed") {
          params.completed = true;
      } else if (currentFilterStatus === "uncompleted") {
          params.uncompleted = true;
      }

      const res = await api.get("/tasks", { params });
      const { tasks: newTasks, total } = res.data;

      setTasks((prev) => (reset ? newTasks : [...prev, ...newTasks]));
      setPagination((prev) => ({
        ...prev,
        skip: reset ? newTasks.length : prev.skip + newTasks.length,
        total,
        hasMore: newTasks.length === currentLimit,
      }));
    } catch (err) {
      console.error("Error fetching tasks:", err);
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [pagination.limit, pagination.skip, ensureAuthorized]);

  // Load more tasks for infinite scroll
  const loadMoreTasks = useCallback(async () => {
    if (loadingMore || !pagination.hasMore) return;

    setLoadingMore(true);
    setError(null);

    if (!(await ensureAuthorized())) {
      setLoadingMore(false);
      return;
    }

    try {
      const params = {
        skip: pagination.skip,
        limit: pagination.limit,
      };

      const res = await api.get("/tasks", { params });
      const { tasks: newTasks, total } = res.data;

      setTasks((prev) => [...prev, ...newTasks]);
      setPagination((prev) => ({
        ...prev,
        skip: prev.skip + newTasks.length,
        total,
        hasMore: newTasks.length === pagination.limit,
      }));
    } catch (err) {
      console.error("Error loading more tasks:", err);
      setError(err);
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore, pagination.hasMore, pagination.skip, pagination.limit, ensureAuthorized]);

  // Search tasks - now just an alias for fetchTasks with search parameters
  const searchTasks = useCallback(async (options = {}) => {
    return fetchTasks(options);
  }, [fetchTasks]);

  // Create task logic
  const createTask = useCallback(async (payload) => {
    setError(null);
    if (!(await ensureAuthorized())) return;

    try {
      const res = await api.post("/tasks", payload);
      setTasks((prev) => [res.data, ...prev]);
      setPagination((prev) => ({
        ...prev,
        total: prev.total + 1,
        skip: prev.skip + 1,
      }));
      return res.data;
    } catch (err) {
      console.error("Error creating task:", err);
      setError(err);
      throw err;
    }
  }, [ensureAuthorized]);

  // Update task logic
  const updateTask = useCallback(async (id, taskData) => {
    setError(null);
    if (!(await ensureAuthorized())) return;

    try {
      const { done_hr, ...payload } = taskData;
      const res = await api.patch(`/tasks/${id}`, payload);
      setTasks((prev) => prev.map((task) => (task.id === id ? res.data : task)));
      return res.data;
    } catch (err) {
      console.error("Error updating task:", err);
      setError(err);
      throw err;
    }
  }, [ensureAuthorized]);

  // Delete task logic
  const deleteTask = useCallback(async (id) => {
    setError(null);
    if (!(await ensureAuthorized())) return;

    try {
      await api.delete(`/tasks/${id}`);
      setTasks((prev) => prev.filter((t) => t.id !== id));
      setPagination((prev) => ({
        ...prev,
        total: Math.max(0, prev.total - 1),
        skip: Math.max(0, prev.skip - 1),
      }));
    } catch (err) {
      console.error("Error deleting task:", err);
      setError(err);
      throw err;
    }
  }, [ensureAuthorized]);

  // Stop task logic
  const stopTask = useCallback(async (id) => {
    setError(null);
    if (!(await ensureAuthorized())) return;
    try {
      await api.post(`/tasks/stop/${id}`);
      setTasks((prev) =>
        prev.map((task) =>
          task.id === id ? { ...task, is_stopped: true, status: "stopped" } : task
        )
      );
    } catch (err) {
      setError(err);
      throw err;
    }
  }, [ensureAuthorized]);

  // Start task logic
  const startTask = useCallback(async (id) => {
    setError(null);
    if (!(await ensureAuthorized())) return;
    try {
      await api.post(`/tasks/start/${id}`);
      setTasks((prev) =>
        prev.map((task) =>
          task.id === id ? { ...task, is_stopped: false, status: "in_progress" } : task
        )
      );
    } catch (err) {
      setError(err);
      throw err;
    }
  }, [ensureAuthorized]);

  // Assign user to task logic
  const assignUser = useCallback(async (taskId, email) => {
    setError(null);
    if (!(await ensureAuthorized())) return;
    try {
      await api.post(`/tasks/assign/${taskId}`, { assignee_email: email });
      await fetchTasks({ reset: true }); // Refetch tasks to ensure we have the latest data
    } catch (err) {
      setError(err);
      throw err;
    }
  }, [ensureAuthorized, fetchTasks]);

  // Fetch all tasks for analytics
  const fetchAllTasksForAnalytics = useCallback(async () => {
    setLoading(true);
    setError(null);
    if (!(await ensureAuthorized())) {
      setLoading(false);
      return [];
    }
    try {
      const res = await api.get("/tasks/all/task/analytics");
      return res.data || [];
    } catch (err) {
      console.error("Error fetching all tasks for analytics:", err);
      setError(err);
      return [];
    } finally {
      setLoading(false);
    }
  }, [ensureAuthorized]);

  // Reset tasks and pagination
  const resetTasks = useCallback(() => {
    setTasks([]);
    setPagination({
      skip: 0,
      limit: 20,
      total: 0,
      hasMore: true,
    });
  }, []);

  // Initial data fetch
  useEffect(() => {
    fetchTasks({ reset: true });
  }, []); // Empty dependency array - only run on mount

  return (
    <TaskContext.Provider
      value={{
        tasks,
        loading,
        loadingMore,
        error,
        pagination,
        fetchTasks,
        loadMoreTasks,
        searchTasks,
        createTask,
        updateTask,
        deleteTask,
        stopTask,
        startTask,
        assignUser,
        fetchAllTasksForAnalytics,
        resetTasks,
      }}
    >
      {children}
    </TaskContext.Provider>
  );
};

export const useTasks = () => useContext(TaskContext);