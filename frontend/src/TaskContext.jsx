import { createContext, useContext, useState, useMemo } from "react";

export const TaskContext = createContext();

export const TaskProvider = ({ children }) => {
  // Global UI state for tasks
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("uncompleted");
  const [pagination, setPagination] = useState({
    page: 0,
    pageSize: 20
  });

  const value = useMemo(() => ({
    searchTerm,
    setSearchTerm,
    filterStatus,
    setFilterStatus,
    pagination,
    setPagination
  }), [searchTerm, filterStatus, pagination]);

  return (
    <TaskContext.Provider value={value}>
      {children}
    </TaskContext.Provider>
  );
};

export const useTaskUI = () => {
  const context = useContext(TaskContext);
  if (!context) {
    throw new Error("useTaskUI must be used within a TaskProvider");
  }
  return context;
};

// Hook for backward compatibility
export const useTasks = useTaskUI;