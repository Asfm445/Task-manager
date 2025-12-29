import {
  AlertCircle,
  Calendar,
  CheckCircle,
  Clock,
  PauseCircle,
  PieChart as PieChartIcon,
  PlayCircle,
  Target,
  TrendingUp,
  Users
} from 'lucide-react';
import { useMemo, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';
import Header from '../components/Header';
import { useAllTasksAnalyticsQuery } from '../hooks/useTasksData';

const TaskAnalyticsDashboard = () => {
  const { data: allTasksAnalytics = [], isLoading, isError } = useAllTasksAnalyticsQuery();
  const [timeRange, setTimeRange] = useState('7days');

  const processAnalyticsData = (data) => {
    const completionRateMap = {};
    const timeAllocationMap = {};
    const userProductivityMap = {};
    const dailyUtilizationMap = {};

    data.forEach(item => {
      const task = item.task;
      const analytics = item.analytics;

      // Completion Rate
      const startDate = new Date(task.start_date).toISOString().split('T')[0];
      if (!completionRateMap[startDate]) {
        completionRateMap[startDate] = { total_tasks: 0, completed_tasks: 0, completion_rate: 0 };
      }
      completionRateMap[startDate].total_tasks++;
      if (task.status === 'completed') {
        completionRateMap[startDate].completed_tasks++;
      }

      // Time Allocation
      const category = analytics.summary.key_insights[2]?.split(': ')[1] || 'General';
      if (!timeAllocationMap[category]) {
        timeAllocationMap[category] = { estimated_hours: 0, actual_hours: 0 };
      }
      timeAllocationMap[category].estimated_hours += task.estimated_hr;
      timeAllocationMap[category].actual_hours += task.done_hr;

      // User Productivity (simplified for single user)
      if (!userProductivityMap['You']) {
        userProductivityMap['You'] = { completed_tasks: 0, total_hours: 0, efficiency: 0 };
      }
      if (task.status === 'completed') {
        userProductivityMap['You'].completed_tasks++;
      }
      userProductivityMap['You'].total_hours += task.done_hr;

      // Daily Utilization
      if (analytics.time_analysis && analytics.time_analysis.start_date) {
        const taskDate = new Date(analytics.time_analysis.start_date).toISOString().split('T')[0];
        if (!dailyUtilizationMap[taskDate]) {
          dailyUtilizationMap[taskDate] = { hours: 0 };
        }
        dailyUtilizationMap[taskDate].hours += analytics.time_analysis.time_spent_hours;
      }
    });

    const completionRate = Object.keys(completionRateMap).map(date => {
      const entry = completionRateMap[date];
      return {
        date,
        total_tasks: entry.total_tasks,
        completed_tasks: entry.completed_tasks,
        completion_rate: (entry.completed_tasks / entry.total_tasks) * 100
      };
    }).sort((a, b) => new Date(a.date) - new Date(b.date));

    const timeAllocation = Object.keys(timeAllocationMap).map(category => ({
      category,
      estimated_hours: timeAllocationMap[category].estimated_hours,
      actual_hours: timeAllocationMap[category].actual_hours
    }));

    const userProductivity = Object.keys(userProductivityMap).map(username => {
      const entry = userProductivityMap[username];
      const totalEstimatedForUser = data.reduce((sum, item) => sum + item.task.estimated_hr, 0);
      return {
        username,
        completed_tasks: entry.completed_tasks,
        total_hours: entry.total_hours,
        efficiency: totalEstimatedForUser > 0 ? (entry.total_hours / totalEstimatedForUser) * 100 : 0
      };
    });

    const dailyUtilization = Object.keys(dailyUtilizationMap).map(date => ({
      date,
      hours: dailyUtilizationMap[date].hours
    })).sort((a, b) => new Date(a.date) - new Date(b.date));

    return { completionRate, timeAllocation, userProductivity, dailyUtilization };
  };

  const chartData = useMemo(() => processAnalyticsData(allTasksAnalytics), [allTasksAnalytics]);

  const stats = useMemo(() => {
    if (allTasksAnalytics.length === 0) return {
      totalTasks: 0,
      statusCount: { completed: 0, in_progress: 0, pending: 0 },
      totalEstimated: 0,
      totalActual: 0,
      accuracy: "0.0",
      overdueTasks: 0,
      statusData: [],
      categoryData: [],
      efficiency: "0.0"
    };

    const statusCount = { completed: 0, in_progress: 0, pending: 0 };
    let totalEstimated = 0;
    let totalActual = 0;
    let totalCompletedEstimated = 0;
    let totalCompletedActual = 0;
    const categories = {};

    allTasksAnalytics.forEach(item => {
      const task = item.task;
      statusCount[task.status] = (statusCount[task.status] || 0) + 1;
      totalEstimated += task.estimated_hr;
      totalActual += task.done_hr;

      if (task.status === 'completed') {
        totalCompletedEstimated += task.estimated_hr;
        totalCompletedActual += task.done_hr;
      }

      const category = item.analytics.summary.key_insights[2]?.split(': ')[1] || 'General';
      categories[category] = (categories[category] || 0) + 1;
    });

    const accuracy = totalCompletedEstimated > 0 ? (totalCompletedActual / totalCompletedEstimated) * 100 : 0;
    const now = new Date();
    const overdueTasks = allTasksAnalytics.filter(item => {
      if (item.task.status === 'completed') return false;
      return new Date(item.task.end_date) < now;
    });

    const statusData = [
      { name: 'COMPLETED', value: statusCount.completed, color: '#10B981' },
      { name: 'IN PROGRESS', value: statusCount.in_progress, color: '#3B82F6' },
      { name: 'PENDING', value: statusCount.pending, color: '#F59E0B' }
    ].filter(s => s.value > 0);

    const categoryData = Object.keys(categories).map(category => ({
      name: category,
      value: categories[category]
    }));

    return {
      totalTasks: allTasksAnalytics.length,
      statusCount,
      totalEstimated,
      totalActual,
      accuracy: accuracy.toFixed(1),
      overdueTasks: overdueTasks.length,
      statusData,
      categoryData,
      efficiency: totalEstimated > 0 ? ((totalActual / totalEstimated) * 100).toFixed(1) : "0.0"
    };
  }, [allTasksAnalytics]);

  if (isLoading) {
    return (
      <>
        <Header />
        <div className="flex justify-center items-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      </>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <Header />
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Task Analytics Dashboard</h1>
        <p className="text-gray-600 mb-8">Comprehensive analysis of your tasks and productivity</p>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase">Total Tasks</h3>
                <p className="text-2xl font-bold text-gray-900">{stats.totalTasks}</p>
              </div>
              <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                <Target size={20} />
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase">Hours Invested</h3>
                <p className="text-2xl font-bold text-gray-900">{stats.totalActual}h</p>
              </div>
              <div className="p-2 bg-green-100 rounded-lg text-green-600">
                <Clock size={20} />
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase">Est. Accuracy</h3>
                <p className="text-2xl font-bold text-gray-900">{stats.accuracy}%</p>
              </div>
              <div className="p-2 bg-purple-100 rounded-lg text-purple-600">
                <TrendingUp size={20} />
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase">Overdue</h3>
                <p className="text-2xl font-bold text-gray-900 text-red-600">{stats.overdueTasks}</p>
              </div>
              <div className="p-2 bg-red-100 rounded-lg text-red-600">
                <AlertCircle size={20} />
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Status Pie Chart */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-bold text-gray-800 mb-6 flex items-center gap-2">
              <PieChartIcon size={20} className="text-blue-500" /> Status Distribution
            </h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats.statusData}
                    cx="50%" cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {stats.statusData.map((entry, index) => (
                      <Cell key={index} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Time Utilization Line Chart */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-bold text-gray-800 mb-6 flex items-center gap-2">
              <Calendar size={20} className="text-purple-500" /> Daily Utilization
            </h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData.dailyUtilization}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" hide />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="hours" stroke="#8b5cf6" strokeWidth={3} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Task List Table */}
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <div className="p-6 border-b border-gray-100">
            <h2 className="text-lg font-bold text-gray-800">Recent Task Activity</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 text-left">
                <tr>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Task</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Hours (A/E)</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-4 text-xs font-bold text-gray-500 uppercase">Due Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {allTasksAnalytics.slice(0, 10).map(item => (
                  <tr key={item.task.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{item.task.description}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{item.task.done_hr} / {item.task.estimated_hr}h</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold uppercase ${item.task.status === 'completed' ? 'bg-green-100 text-green-700' :
                          item.task.status === 'in_progress' ? 'bg-blue-100 text-blue-700' : 'bg-yellow-100 text-yellow-700'
                        }`}>
                        {item.task.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">{new Date(item.task.end_date).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskAnalyticsDashboard;