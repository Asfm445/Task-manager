import React, { createContext, useState, useEffect, useContext } from "react";
import api from "./api"; // your axios instance

export const TaskContext = createContext();

export const TaskProvider = ({ children }) => {
  const [tasks, setTasks] = useState([]);

  const fetchTasks = async () => {
    try {
      const res = await api.get("/tasks");
      setTasks(res.data);
    } catch (err) {
      console.error("Error fetching tasks:", err);
    }
  };

  const createTask = async (payload) => {
    try {
      // const payload = {
      //   description: formData.description,
      //   end_date: new Date(formData.end_date).toISOString(),
      //   status: formData.status,
      //   estimated_hr: Number(formData.estimated_hr), // ensure string
      //   is_repititive: formData.is_repititive,
      //   main_task_id: formData.main_task_id || null,
      //   };
      //   if(formData.startDate){
      //       payload.start_date = new Date(formData.startDate).toISOString();
      //   }
      //   console.log(payload)
      const res = await api.post("/tasks", payload);
      setTasks((prev) => [...prev, res.data]);
    } catch (err) {
      console.error("Error creating task:", err);
    }
  };

  const updateTask = async (id, taskData) => {
    try {
      const { done_hr, ...payload } = taskData; // exclude done_hr
      const res = await api.patch(`/tasks/${id}`, payload);
      setTasks((prev) =>
        prev.map((task) => (task.id === id ? res.data : task))
      );
    } catch (err) {
      console.error("Error updating task:", err);
    }
  };
  const deleteTask = async (id) => {
    await api.delete(`tasks/${id}`);
    setTasks(prev => prev.filter(t => t.id !== id));
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  return (
    <TaskContext.Provider value={{ tasks, createTask, updateTask, deleteTask }}>
      {children}
    </TaskContext.Provider>
  );
};

export const useTasks = () => useContext(TaskContext);