import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from "@tanstack/react-query";
import api from "../api";
import { useNavigate } from "react-router-dom";

/**
 * Hook for fetching multiple tasks with infinite scrolling
 */
export const useTasksInfiniteQuery = (options = {}) => {
    const { searchTerm = "", filterStatus = "uncompleted" } = options;

    return useInfiniteQuery({
        queryKey: ["tasks", { searchTerm, filterStatus }],
        queryFn: async ({ pageParam = 0 }) => {
            const params = {
                skip: pageParam,
                limit: 20,
                search_name: searchTerm || undefined,
            };

            if (filterStatus === "completed") {
                params.completed = true;
            } else if (filterStatus === "uncompleted") {
                params.uncompleted = true;
            }

            const res = await api.get("/tasks", { params });
            return res.data;
        },
        getNextPageParam: (lastPage, allPages) => {
            const loadedCount = allPages.reduce((acc, page) => acc + page.tasks.length, 0);
            return loadedCount < lastPage.total ? loadedCount : undefined;
        },
    });
};

/**
 * Simpler query for when we just need all tasks
 */
export const useAllTasksQuery = () => {
    return useQuery({
        queryKey: ["tasks", "all"],
        queryFn: async () => {
            const res = await api.get("/tasks", { params: { limit: 100 } });
            return res.data.tasks || [];
        }
    });
};

/**
 * Hook for fetching all tasks for analytics
 */
export const useAllTasksAnalyticsQuery = () => {
    return useQuery({
        queryKey: ["tasks", "analytics", "all"],
        queryFn: async () => {
            const res = await api.get("/tasks/all/task/analytics");
            return res.data || [];
        }
    });
};

/**
 * Hook for fetching a single task with its analytics and progress
 */
export const useTaskQuery = (id) => {
    return useQuery({
        queryKey: ["task", id],
        queryFn: async () => {
            const [taskRes, analyticsRes] = await Promise.all([
                api.get(`/tasks/${id}`),
                api.get(`/tasks/analytics/${id}`).catch(() => ({ data: { analytics: null } })),
            ]);

            return {
                task: taskRes.data,
                analytics: analyticsRes.data.analytics,
            };
        },
        enabled: !!id,
        staleTime: 1000 * 60 * 5,
    });
};

/**
 * Hook for fetching task progress with infinite scrolling
 */
export const useProgressInfiniteQuery = (taskId) => {
    return useInfiniteQuery({
        queryKey: ["task-progress", taskId],
        queryFn: async ({ pageParam = 0 }) => {
            const res = await api.get(`/tasks/progress/${taskId}`, {
                params: { skip: pageParam, limit: 10 }
            });
            return res.data; // { total, data }
        },
        getNextPageParam: (lastPage, allPages) => {
            const loadedCount = allPages.reduce((acc, page) => acc + page.data.length, 0);
            return loadedCount < lastPage.total ? loadedCount : undefined;
        },
        enabled: !!taskId,
    });
};

/**
 * Hook for Plans (Time Logs)
 */
export const usePlansQuery = (dateKey) => {
    return useQuery({
        queryKey: ["plans", dateKey],
        queryFn: async () => {
            const res = await api.post("plans/", { date: dateKey });
            return res.data;
        },
        enabled: !!dateKey,
    });
};

/**
 * Mutations
 */
export const useTaskMutations = () => {
    const queryClient = useQueryClient();
    const navigate = useNavigate();

    return {
        createTask: useMutation({
            mutationFn: (payload) => api.post("/tasks", payload),
            onSuccess: () => queryClient.invalidateQueries(["tasks"]),
        }).mutateAsync,

        updateTask: useMutation({
            mutationFn: ({ id, payload }) => api.patch(`/tasks/${id}`, payload),
            onSuccess: (res, { id }) => {
                queryClient.invalidateQueries(["tasks"]);
                queryClient.invalidateQueries(["task", id]);
            },
        }).mutateAsync,

        deleteTask: useMutation({
            mutationFn: (id) => api.delete(`/tasks/${id}`),
            onSuccess: () => {
                queryClient.invalidateQueries(["tasks"]);
                navigate("/tasks");
            },
        }).mutateAsync,

        toggleTask: useMutation({
            mutationFn: ({ id, stop }) => api.post(`/tasks/${id}/toggle`, { stop }),
            onSuccess: (res, { id }) => {
                queryClient.invalidateQueries(["tasks"]);
                queryClient.invalidateQueries(["task", id]);
            },
        }).mutateAsync,

        assignUser: useMutation({
            mutationFn: ({ taskId, email }) => api.post(`/tasks/assign/${taskId}`, { assignee_email: email }),
            onSuccess: (res, { taskId }) => {
                queryClient.invalidateQueries(["tasks"]);
                queryClient.invalidateQueries(["task", taskId]);
            },
        }).mutateAsync,
    };
};

export const usePlanMutations = () => {
    const queryClient = useQueryClient();

    return {
        addLog: useMutation({
            mutationFn: (payload) => api.post("plans/timelog", payload),
            onSuccess: () => queryClient.invalidateQueries(["plans"]),
        }).mutateAsync,

        markSuccess: useMutation({
            mutationFn: (timelog_id) => api.get(`plans/timelog/done/${timelog_id}`),
            onSuccess: () => queryClient.invalidateQueries(["plans"]),
        }).mutateAsync,

        deleteLog: useMutation({
            mutationFn: (timelog_id) => api.delete(`plans/timelog/${timelog_id}`),
            onSuccess: () => queryClient.invalidateQueries(["plans"]),
        }).mutateAsync,
    };
};
