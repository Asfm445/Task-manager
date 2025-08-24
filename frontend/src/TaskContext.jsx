import { createContext, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./api"; // your axios instance
import { checkIsAuthorized } from "./authorize";

export const TaskContext = createContext();

export const TaskProvider = ({ children }) => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Helper to ensure user is authorized before any request
  const ensureAuthorized = async () => {
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
  };

  const fetchTasks = async () => {
    setLoading(true);
    setError(null);

    if (!(await ensureAuthorized())) {
      setLoading(false);
      return;
    }

    try {
      const res = await api.get("/tasks");
      setTasks(res.data || []);
    } catch (err) {
      console.error("Error fetching tasks:", err);
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  const createTask = async (payload) => {
    setError(null);
    console.log(payload)

    if (!(await ensureAuthorized())) return;

    try {
      const res = await api.post("/tasks", payload);
      console.log(payload)
      setTasks((prev) => [...prev, res.data]);
      return res.data;
    } catch (err) {
      console.error("Error creating task:", err);
      setError(err);
      throw err;
    }
  };

  const updateTask = async (id, taskData) => {
    setError(null);

    if (!(await ensureAuthorized())) return;

    try {
      const { done_hr, ...payload } = taskData; // exclude done_hr
      const res = await api.patch(`/tasks/${id}`, payload);
      setTasks((prev) => prev.map((task) => (task.id === id ? res.data : task)));
      return res.data;
    } catch (err) {
      console.error("Error updating task:", err);
      setError(err);
      throw err;
    }
  };

  const deleteTask = async (id) => {
    setError(null);

    if (!(await ensureAuthorized())) return;

    try {
      await api.delete(`/tasks/${id}`);
      setTasks((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      console.error("Error deleting task:", err);
      setError(err);
      throw err;
    }
  };

  const stopTask = async (id) => {
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
  };

  const startTask = async (id) => {
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
  };

  const assignUser = async (taskId, email) => {
    setError(null);
    if (!(await ensureAuthorized())) return;
    try {
      await api.post(`/tasks/assign/${taskId}`, {assignee_email: email });
      // Optionally, you can refetch tasks or update the assigned user in state if your backend returns updated task data
      await fetchTasks();
    } catch (err) {
      setError(err);
      throw err;
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  return (
    <TaskContext.Provider
      value={{
        tasks,
        loading,
        error,
        fetchTasks,
        createTask,
        updateTask,
        deleteTask,
        stopTask,
        startTask,
        assignUser, // <-- add here
      }}
    >
      {children}
    </TaskContext.Provider>
  );
};

export const useTasks = () => useContext(TaskContext);
