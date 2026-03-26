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
            const res = await api.get(`/tasks/${id}`);
            // Backend returns: { task, progress, standard_completion_hr, curr_completion_rate }
            const data = res.data;
            const { task, curr_completion_rate } = data;

            // --- Derive Analytics Client-Side ---

            // 1. Completion Metrics
            // curr_completion_rate is a float (e.g. 0.5 for 50%)
            const completion_rate = Math.round((curr_completion_rate || 0) * 100);

            const completion_metrics = {
                completion_rate,
                time_spent: task.done_hr,
                estimated_time: task.estimated_hr
            };

            // 2. Time Efficiency
            let efficiency_score = 100;
            if (task.done_hr > 0) {
                // Efficiency = (Estimated / Actual) * 100
                efficiency_score = Math.round((task.estimated_hr / task.done_hr) * 100);
            } else if (task.estimated_hr === 0) {
                efficiency_score = 100; // undefined efficiency, assume ok
            } else {
                // done_hr is 0 but estimated > 0.
                // Technically efficiency is infinite (haven't spent time yet), 
                // but for display let's default to 100 until they start.
                efficiency_score = 100;
            }

            let efficiency_status = "On Track";
            if (efficiency_score >= 110) efficiency_status = "Efficient";
            else if (efficiency_score < 80) efficiency_status = "Inefficient";

            // 3. Analytics Summary (Grade & Recommendations)
            let grade = "B";
            if (efficiency_score >= 120) grade = "S";
            else if (efficiency_score >= 90) grade = "A";
            else if (efficiency_score >= 70) grade = "B";
            else grade = "C";

            const recommendations = [];
            if (data.ai_recommendation) {
                if (data.ai_recommendation.feedback) {
                    recommendations.push(data.ai_recommendation.feedback);
                }
                if (data.ai_recommendation.recommendations) {
                    // If it's a string that looks like a list, we could split it, 
                    // but for now let's just push it.
                    recommendations.push(data.ai_recommendation.recommendations);
                }
            }

            if (efficiency_score < 70) {
                recommendations.push("Task is taking longer than expected. Consider breaking it down.");
                recommendations.push("Review blockers with the team.");
            } else if (efficiency_score > 150) {
                recommendations.push("Task estimated time might be too generous.");
            }

            const endDate = new Date(task.end_date);
            const now = new Date();
            if (completion_rate < 50 && endDate < now) {
                recommendations.push("Task is overdue and less than halfway done. Prioritize immediately.");
            } else if (completion_rate === 100) {
                recommendations.push("Task completed! Good job.");
            }

            if (recommendations.length === 0) {
                recommendations.push("Keep up the good work!");
            }

            return {
                task: task,
                analytics: {
                    completion_metrics,
                    time_efficiency: {
                        efficiency_score,
                        status: efficiency_status
                    },
                    summary: {
                        grade,
                        recommendations
                    }
                },
                // Pass through other backend data if needed
                progress: data.progress,
                standard_completion_hr: data.standard_completion_hr,
                curr_completion_rate: data.curr_completion_rate
            };
        },
        enabled: !!id,
        staleTime: 1000 * 60 * 5,
    });
};

/**
 * Hook for fetching task progress with infinite scrolling
 */
export const useProgressQuery = ({ taskId, skip = 0, limit = 20 }) => {
    return useQuery({
        queryKey: ["task-progress", taskId, { skip, limit }],
        queryFn: async () => {
            const res = await api.get(`/tasks/progress/${taskId}`, {
                params: { skip, limit }
            });
            return res.data; // { total, data }
        },
        enabled: !!taskId,
        placeholderData: (previousData) => previousData,
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
            mutationFn: ({ id, stop }) => {
                const endpoint = stop ? `/tasks/stop/${id}` : `/tasks/start/${id}`;
                return api.post(endpoint, {});
            },
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
