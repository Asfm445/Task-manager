import {
  ArrowLeft, Calendar, CheckCircle2, Clock, ListTodo,
  Repeat, TrendingUp, Users, AlertCircle, BarChart3,
  Play, Pause, Edit, Trash2
} from "lucide-react";
import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { useTaskQuery, useTaskMutations, useProgressQuery } from "../hooks/useTasksData";
import Header from "../components/Header";

export default function TaskDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("overview");

  const [page, setPage] = useState(0);
  const limit = 20;

  const { data, isLoading, isError, error } = useTaskQuery(id);
  const { toggleTask, deleteTask } = useTaskMutations();
  const {
    data: progressData,
    isLoading: isProgressLoading
  } = useProgressQuery({ taskId: id, skip: page * limit, limit });

  if (isLoading) {
    return (
      <>
        <Header />
        <div className="flex justify-center items-center py-20">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading task details...</p>
          </div>
        </div>
      </>
    );
  }

  if (isError || !data?.task) {
    return (
      <>
        <Header />
        <div className="max-w-4xl mx-auto p-6">
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
            <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-3" />
            <p className="text-red-800 font-semibold">
              {error?.response?.data?.detail || "Task not found"}
            </p>
            <Link to="/tasks" className="text-blue-600 hover:underline mt-4 inline-block">
              ← Back to tasks
            </Link>
          </div>
        </div>
      </>
    );
  }

  const { task, analytics } = data;
  const progressEntries = progressData?.data || [];
  const totalProgress = progressData?.total || 0;
  const totalPages = Math.ceil(totalProgress / limit);

  const handleToggleTask = async () => {
    try {
      await toggleTask({ id, stop: !task.is_stopped });
    } catch (e) {
      alert(e.response?.data?.detail || "Failed to toggle task");
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this task?")) return;
    try {
      await deleteTask(id);
    } catch (e) {
      alert(e.response?.data?.detail || "Failed to delete task");
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: "bg-yellow-100 text-yellow-800 border-yellow-200",
      in_progress: "bg-blue-100 text-blue-800 border-blue-200",
      completed: "bg-green-100 text-green-800 border-green-200",
      stopped: "bg-red-100 text-red-800 border-red-200"
    };
    return colors[status] || "bg-gray-100 text-gray-800 border-gray-200";
  };

  const formatDate = (dateString) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  return (
    <>
      <Header />
      <div className="max-w-6xl mx-auto px-4 py-6">
        {/* Header content and tabs (same as before but using data from hook) */}
        <div className="mb-6">
          <Link
            to="/tasks"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-blue-600 mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to tasks</span>
          </Link>

          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <h1 className="text-3xl font-extrabold text-gray-900 mb-2">
                {task.description}
              </h1>
              <div className="flex flex-wrap items-center gap-3">
                <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getStatusColor(task.status)}`}>
                  {task.status.replace("_", " ")}
                </span>
                {task.is_repititive && (
                  <span className="px-3 py-1 rounded-full text-sm font-semibold bg-purple-100 text-purple-800 border border-purple-200 flex items-center gap-1">
                    <Repeat className="w-3 h-3" />
                    Repetitive
                  </span>
                )}
                {task.is_stopped && (
                  <span className="px-3 py-1 rounded-full text-sm font-semibold bg-red-100 text-red-800 border border-red-200">
                    Stopped
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              {task.is_repititive && (
                <button
                  onClick={handleToggleTask}
                  className={`px-4 py-2 rounded-lg font-semibold transition-all flex items-center gap-2 ${task.is_stopped
                    ? "bg-green-600 hover:bg-green-700 text-white"
                    : "bg-yellow-600 hover:bg-yellow-700 text-white"
                    }`}
                >
                  {task.is_stopped ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                  {task.is_stopped ? "Resume" : "Stop"}
                </button>
              )}
              <button
                onClick={() => navigate(`/tasks`)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-all flex items-center gap-2"
              >
                <Edit className="w-4 h-4" />
                Edit
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition-all flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <div className="flex gap-4">
            {["overview", "subtasks", "progress", "analytics"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 font-semibold border-b-2 transition-colors ${activeTab === tab
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-600 hover:text-gray-900"
                  }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            <div className="grid md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-xl p-5">
                <div className="flex items-center gap-2 text-blue-600 mb-2">
                  <Clock className="w-5 h-5" />
                  <span className="font-semibold">Progress</span>
                </div>
                <div className="text-3xl font-bold text-blue-900">
                  {task.estimated_hr > 0 ? Math.round((task.done_hr / task.estimated_hr) * 100) : 0}%
                </div>
                <div className="text-sm text-gray-700 mt-1">
                  {task.done_hr}h / {task.estimated_hr}h
                </div>
              </div>

              <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-xl p-5">
                <div className="flex items-center gap-2 text-green-600 mb-2">
                  <Calendar className="w-5 h-5" />
                  <span className="font-semibold">Start Date</span>
                </div>
                <div className="text-sm font-semibold text-green-900">
                  {formatDate(task.start_date)}
                </div>
              </div>

              <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-xl p-5">
                <div className="flex items-center gap-2 text-purple-600 mb-2">
                  <Calendar className="w-5 h-5" />
                  <span className="font-semibold">End Date</span>
                </div>
                <div className="text-sm font-semibold text-purple-900">
                  {formatDate(task.end_date)}
                </div>
              </div>

              <div className="bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 rounded-xl p-5">
                <div className="flex items-center gap-2 text-orange-600 mb-2">
                  <Users className="w-5 h-5" />
                  <span className="font-semibold">Assigned</span>
                </div>
                <div className="text-3xl font-bold text-orange-900">
                  {task.assignees?.length || 0}
                </div>
                <div className="text-sm text-gray-700 mt-1">team members</div>
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Task Details</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-semibold text-gray-600">Task ID</label>
                  <p className="text-gray-900">#{task.id}</p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">Owner ID</label>
                  <p className="text-gray-900">#{task.owner_id}</p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">Estimated Hours</label>
                  <p className="text-gray-900">{task.estimated_hr} hours</p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">Completed Hours</label>
                  <p className="text-gray-900">{task.done_hr} hours</p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">Main Task</label>
                  <p className="text-gray-900">
                    {task.main_task_id ? `#${task.main_task_id}` : "None (Main Task)"}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-semibold text-gray-600">Type</label>
                  <p className="text-gray-900">
                    {task.is_repititive ? "Repetitive Task" : "One-time Task"}
                  </p>
                </div>
              </div>
            </div>

            {task.assignees && task.assignees.length > 0 && (
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Assigned Team Members
                </h2>
                <div className="flex flex-wrap gap-3">
                  {task.assignees.map((userId) => (
                    <div
                      key={userId}
                      className="px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg flex items-center gap-2"
                    >
                      <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
                        {userId.toString().slice(0, 2)}
                      </div>
                      <span className="font-semibold text-gray-900">User #{userId}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "subtasks" && (
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <ListTodo className="w-5 h-5" />
              Subtasks
            </h2>
            {task.subtasks && task.subtasks.length > 0 ? (
              <div className="space-y-3">
                {task.subtasks.map((subtask) => (
                  <div
                    key={subtask.id}
                    className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">{subtask.description}</h3>
                        <div className="flex items-center gap-3 mt-2 text-sm text-gray-600">
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${getStatusColor(subtask.status)}`}>
                            {subtask.status}
                          </span>
                          <span>{subtask.done_hr}h / {subtask.estimated_hr}h</span>
                        </div>
                      </div>
                      <Link
                        to={`/tasks/${subtask.id}`}
                        className="text-blue-600 hover:text-blue-700 font-semibold text-sm"
                      >
                        View →
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No subtasks for this task</p>
            )}
          </div>
        )}

        {activeTab === "progress" && (
          <div className="bg-white border border-gray-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Progress History
              </h2>
              {task.is_repititive && (
                <span className="text-sm font-medium text-gray-500">
                  Total Records: {totalProgress}
                </span>
              )}
            </div>

            {task.is_repititive ? (
              isProgressLoading ? (
                <div className="flex justify-center py-12">
                  <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                </div>
              ) : progressEntries.length > 0 ? (
                <div className="space-y-4">
                  <div className="space-y-3">
                    {progressEntries.map((entry, index) => (
                      <div
                        key={index}
                        className="p-4 border border-gray-100 rounded-xl hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-bold text-gray-900">
                                Cycle {totalProgress - (page * limit + index)}
                              </span>
                              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${getStatusColor(entry.status)} shadow-sm border`}>
                                {entry.status.replace("_", " ")}
                              </span>
                            </div>
                            <div className="text-sm text-gray-500 flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {formatDate(entry.start_date)}
                              <span className="mx-1">→</span>
                              {formatDate(entry.end_date)}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="flex items-center gap-1 text-gray-900 font-bold">
                              <Clock className="w-3 h-3 text-blue-500" />
                              {entry.done_hr}h
                              <span className="text-gray-400 font-normal">/</span>
                              <span className="text-gray-500 font-medium">{entry.estimated_hr}h</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {totalPages > 1 && (
                    <div className="flex justify-center items-center gap-4 mt-6">
                      <button
                        onClick={() => setPage(p => Math.max(0, p - 1))}
                        disabled={page === 0}
                        className="px-4 py-2 bg-white border border-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                      >
                        Previous
                      </button>

                      <span className="text-sm font-medium text-gray-600">
                        Page {page + 1} of {totalPages}
                      </span>

                      <button
                        onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
                        disabled={page >= totalPages - 1}
                        className="px-4 py-2 bg-white border border-gray-200 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                      >
                        Next
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                  <BarChart3 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">No progress history recorded yet</p>
                </div>
              )
            ) : (
              <div className="text-center py-12 bg-gray-50 rounded-xl border border-dashed border-gray-200">
                <Repeat className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">
                  Progress tracking is only available for repetitive tasks
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === "analytics" && (
          <div className="space-y-6">
            {analytics ? (
              <>
                <div className="grid md:grid-cols-2 gap-6 mb-6">
                  {/* Completion Rate Card */}
                  <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2 text-blue-600">
                        <BarChart3 className="w-5 h-5" />
                        <h3 className="font-semibold text-lg">Completion Rate</h3>
                      </div>
                      <span className="text-2xl font-bold text-blue-900">
                        {analytics.completion_metrics?.completion_rate || 0}%
                      </span>
                    </div>

                    {/* Visual Bar for Completion Rate */}
                    <div className="w-full bg-gray-100 rounded-full h-4 mb-2 overflow-hidden">
                      <div
                        className="bg-blue-600 h-4 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(analytics.completion_metrics?.completion_rate || 0, 100)}%` }}
                      ></div>
                    </div>
                    <p className="text-sm text-gray-500 text-right">Target: 100%</p>
                  </div>

                  {/* Standard Completion vs Estimated Card */}
                  <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2 text-purple-600">
                        <Clock className="w-5 h-5" />
                        <h3 className="font-semibold text-lg">Standard Time</h3>
                      </div>
                      <span className="text-2xl font-bold text-purple-900">
                        {data.standard_completion_hr ? data.standard_completion_hr.toFixed(1) : "N/A"}h
                      </span>
                    </div>

                    {data.standard_completion_hr && (
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="font-medium text-gray-700">Estimated</span>
                            <span className="font-bold">{task.estimated_hr}h</span>
                          </div>
                          <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                            <div
                              className="bg-gray-400 h-2.5 rounded-full"
                              style={{ width: '100%' }} // Relative baseline
                            ></div>
                          </div>
                        </div>

                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span className="font-medium text-purple-700">Standard (Avg)</span>
                            <span className="font-bold text-purple-700">{data.standard_completion_hr.toFixed(1)}h</span>
                          </div>
                          <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                            <div
                              className={`h-2.5 rounded-full ${data.standard_completion_hr > task.estimated_hr ? 'bg-red-500' : 'bg-green-500'}`}
                              style={{ width: `${Math.min((data.standard_completion_hr / (task.estimated_hr || 1)) * 100, 100)}%` }}
                            ></div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {data.standard_completion_hr > task.estimated_hr
                              ? "Standard time is higher than estimated (Task might be complex)"
                              : "Standard time is lower than estimated (Good performance)"}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-xl p-5">
                    <div className="flex items-center gap-2 text-green-600 mb-2">
                      <TrendingUp className="w-5 h-5" />
                      <span className="font-semibold">Efficiency</span>
                    </div>
                    <div className="text-3xl font-bold text-green-900">
                      {analytics.time_efficiency?.efficiency_score || 0}%
                    </div>
                    <p className="text-sm text-green-800 mt-1">
                      {analytics.time_efficiency?.status}
                    </p>
                  </div>

                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-xl p-5">
                    <div className="flex items-center gap-2 text-purple-600 mb-2">
                      <CheckCircle2 className="w-5 h-5" />
                      <span className="font-semibold">Grade</span>
                    </div>
                    <div className="text-3xl font-bold text-purple-900">
                      {analytics.summary?.grade || "N/A"}
                    </div>
                  </div>
                </div>

                {analytics.summary?.recommendations && analytics.summary.recommendations.length > 0 && (
                  <div className="bg-white border border-gray-200 rounded-xl p-6 mt-6">
                    <h2 className="text-xl font-bold text-gray-900 mb-4">Recommendations</h2>
                    <ul className="space-y-2">
                      {analytics.summary.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start gap-2 text-gray-700">
                          <CheckCircle2 className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            ) : (
              <div className="bg-white border border-gray-200 rounded-xl p-6 text-center">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-500">Analytics not available for this task</p>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}
