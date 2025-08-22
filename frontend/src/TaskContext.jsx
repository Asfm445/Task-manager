import { createContext, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "./api"; // your axios instance
import { checkIsAuthorized } from "./authorize"; // Adjust the import based on your project structure


export const TaskContext = createContext();

export const TaskProvider = ({ children }) => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const fetchTasks = async () => {
    setLoading(true);
    setError(null);
    try{
      const isAuthorized = await checkIsAuthorized();
      if (!isAuthorized) {
      navigate("/login");
      }
    } catch(err){
      console.error("Authorization check failed:", err);
      setError(err);
      return;
    }
    try {
      const res = await api.get("/tasks");
      setTasks(res.data || []);
    } catch (err) {
      setError(err);
      console.error("Error fetching tasks:", err);
    } finally {
      setLoading(false);
    }
  };

  const createTask = async (payload) => {
    setError(null);
     try{
      const isAuthorized = await checkIsAuthorized();
      if (!isAuthorized) {
      navigate("/login");
      }
    } catch(err){
      console.error("Authorization check failed:", err);
      setError(err);
      return;
    }
    try {
      const res = await api.post("/tasks", payload);
      setTasks((prev) => [...prev, res.data]);
      return res.data;
    } catch (err) {
      setError(err);
      console.error("Error creating task:", err);
      throw err;
    }
  };

  const updateTask = async (id, taskData) => {
    setError(null);
     try{
      const isAuthorized = await checkIsAuthorized();
      if (!isAuthorized) {
      navigate("/login");
      }
    } catch(err){
      console.error("Authorization check failed:", err);
      setError(err);
      return;
    }
    try {
      const { done_hr, ...payload } = taskData; // exclude done_hr
      const res = await api.patch(`/tasks/${id}`, payload);
      setTasks((prev) => prev.map((task) => (task.id === id ? res.data : task)));
      return res.data;
    } catch (err) {
      setError(err);
      console.error("Error updating task:", err);
      throw err;
    }
  };

  const deleteTask = async (id) => {
    setError(null);
     try{
      const isAuthorized = await checkIsAuthorized();
      if (!isAuthorized) {
      navigate("/login");
      }
    } catch(err){
      console.error("Authorization check failed:", err);
      setError(err);
      return;
    }
    try {
      await api.delete(`tasks/${id}`);
      setTasks((prev) => prev.filter((t) => t.id !== id));
    } catch (err) {
      setError(err);
      console.error("Error deleting task:", err);
      throw err;
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  return (
    <TaskContext.Provider value={{ tasks, loading, error, fetchTasks, createTask, updateTask, deleteTask }}>
      {children}
    </TaskContext.Provider>
  );
};

export const useTasks = () => useContext(TaskContext);