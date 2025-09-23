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
import { useEffect, useMemo, useState } from 'react';
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
import { useTasks } from '../TaskContext'; // Import useTasks

// Remove mock data
// const mockTasks = [ ... ];
// const mockTimeLogs = [ ... ];
// const generateAnalyticsData = () => { ... };

const TaskAnalyticsDashboard = () => {
  const { fetchAllTasksForAnalytics, loading, error } = useTasks(); // Use the hook
  const [allTasksAnalytics, setAllTasksAnalytics] = useState([]);
  const [timeRange, setTimeRange] = useState('7days');
  // The loading state is now managed by useTasks, so we can remove the local loading state
  // const [loading, setLoading] = useState(true);
  const [chartData, setChartData] = useState({
    completionRate: [],
    timeAllocation: [],
    userProductivity: [],
    dailyUtilization: []
  });

  // 1. Initialize stats as a state variable with default values
  // const [stats, setStats] = useState({
  //   totalTasks: 0,
  //   statusCount: { completed: 0, in_progress: 0, pending: 0 },
  //   totalEstimated: 0,
  //   totalActual: 0,
  //   accuracy: "0.0",
  //   overdueTasks: 0,
  //   statusData: [],
  //   categoryData: [],
  //   efficiency: "0.0"
  // });

  useEffect(() => {
    const getAnalytics = async () => {
      // The loading state is managed by useTasks
      // setLoading(true);
      try {
        console.log("naking request here")
        const data = await fetchAllTasksForAnalytics();
        setAllTasksAnalytics(data);
      } catch (e) {
        console.error('Failed to fetch analytics data', e);
      } finally {
        // setLoading(false);
      }
    };
    getAnalytics();
  }, []); // Add fetchAllTasksForAnalytics to dependency array

  useEffect(() => {
    if (allTasksAnalytics.length > 0) {
      const { completionRate, timeAllocation, userProductivity, dailyUtilization } = processAnalyticsData(allTasksAnalytics);
      setChartData({
        completionRate,
        timeAllocation,
        userProductivity,
        dailyUtilization
      });
    }
  }, [allTasksAnalytics]);

  // 2. Add a new useEffect to recalculate stats when allTasksAnalytics changes
  // useEffect(() => {
  //   setStats(calculateStats());
  // }, [allTasksAnalytics]);

  const processAnalyticsData = (data) => {
    const completionRateMap = {};
    const timeAllocationMap = {};
    const userProductivityMap = {};
    const dailyUtilizationMap = {};

    let totalCompletedTasks = 0;
    let totalTasksCount = data.length;

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
        totalCompletedTasks++;
      }

      // Time Allocation
      const category = analytics.summary.key_insights[2].split(': ')[1]; // Extract category from summary
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

    // Finalize completion rate
    const completionRate = Object.keys(completionRateMap).map(date => {
      const entry = completionRateMap[date];
      return {
        date,
        total_tasks: entry.total_tasks,
        completed_tasks: entry.completed_tasks,
        completion_rate: (entry.completed_tasks / entry.total_tasks) * 100
      };
    }).sort((a, b) => new Date(a.date) - new Date(b.date));

    // Finalize time allocation
    const timeAllocation = Object.keys(timeAllocationMap).map(category => ({
      category,
      estimated_hours: timeAllocationMap[category].estimated_hours,
      actual_hours: timeAllocationMap[category].actual_hours
    }));

    // Finalize user productivity
    const userProductivity = Object.keys(userProductivityMap).map(username => {
      const entry = userProductivityMap[username];
      const totalEstimatedForUser = data.reduce((sum, item) => item.task.owner_id === 1 ? sum + item.task.estimated_hr : sum, 0); // Assuming user_id 1 is "You"
      return {
        username,
        completed_tasks: entry.completed_tasks,
        total_hours: entry.total_hours,
        efficiency: totalEstimatedForUser > 0 ? (entry.total_hours / totalEstimatedForUser) * 100 : 0
      };
    });

    // Finalize daily utilization
    const dailyUtilization = Object.keys(dailyUtilizationMap).map(date => ({
      date,
      hours: dailyUtilizationMap[date].hours
    })).sort((a, b) => new Date(a.date) - new Date(b.date));

    return { completionRate, timeAllocation, userProductivity, dailyUtilization };
  };

  const calculateStats = () => {
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

    // Status distribution
    const statusCount = {
      completed: 0,
      in_progress: 0,
      pending: 0
    };

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

      const category = item.analytics.summary.key_insights[2].split(': ')[1];
      categories[category] = (categories[category] || 0) + 1;
    });

    const accuracy = totalCompletedEstimated > 0
      ? (totalCompletedActual / totalCompletedEstimated) * 100
      : 0;

    const now = new Date();
    const overdueTasks = allTasksAnalytics.filter(item => {
      if (item.task.status === 'completed') return false;
      const endDate = new Date(item.task.end_date);
      return endDate < now;
    });

    const statusData = Object.keys(statusCount).map(status => ({
      name: status.replace('_', ' ').toUpperCase(),
      value: statusCount[status],
      color: status === 'completed' ? '#10B981' : status === 'in_progress' ? '#3B82F6' : '#F59E0B'
    }));

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
  };

  // Use useMemo to memoize the stats object
  const stats = useMemo(() => calculateStats(), [allTasksAnalytics]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <Header />
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Task Analytics Dashboard</h1>
        <p className="text-gray-600 mb-8">Comprehensive analysis of your tasks and productivity</p>
        
        {/* Time Range Selector */}
        <div className="mb-6 flex justify-end">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7days">Last 7 Days</option>
            <option value="30days">Last 30 Days</option>
            <option value="90days">Last 90 Days</option>
          </select>
        </div>
        
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow p-6 flex flex-col">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-700">Total Tasks</h3>
                <p className="text-3xl font-bold text-gray-900">{stats.totalTasks}</p>
              </div>
              <div className="p-3 bg-blue-100 rounded-full">
                <Target className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-4 text-sm text-gray-500">
              <span className="flex items-center"><div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div> Completed: {stats.statusCount.completed || 0}</span>
              <span className="flex items-center"><div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div> In Progress: {stats.statusCount.in_progress || 0}</span>
              <span className="flex items-center"><div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div> Pending: {stats.statusCount.pending || 0}</span>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow p-6 flex flex-col">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-700">Time Investment</h3>
                <p className="text-3xl font-bold text-gray-900">{stats.totalActual}h</p>
                <p className="text-sm text-gray-500">of {stats.totalEstimated}h estimated</p>
              </div>
              <div className="p-3 bg-green-100 rounded-full">
                <Clock className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  className="bg-green-600 h-2.5 rounded-full" 
                  style={{ width: `${stats.efficiency > 100 ? 100 : stats.efficiency}%` }}
                ></div>
              </div>
              <p className="text-xs mt-1 text-gray-500">{stats.efficiency}% of estimated time used</p>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow p-6 flex flex-col">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-700">Estimation Accuracy</h3>
                <p className="text-3xl font-bold text-gray-900">{stats.accuracy}%</p>
              </div>
              <div className="p-3 bg-purple-100 rounded-full">
                <TrendingUp className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <p className="text-sm mt-4 text-gray-500">
              For completed tasks, your time estimates were {stats.accuracy > 100 ? 'over' : 'under'} by {Math.abs(100 - stats.accuracy).toFixed(1)}%
            </p>
          </div>
          
          <div className="bg-white rounded-xl shadow p-6 flex flex-col">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-700">Overdue Tasks</h3>
                <p className="text-3xl font-bold text-gray-900">{stats.overdueTasks}</p>
              </div>
              <div className="p-3 bg-red-100 rounded-full">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
            </div>
            <p className="text-sm mt-4 text-gray-500">
              {stats.overdueTasks > 0 
                ? 'Consider reprioritizing these tasks' 
                : 'Great! You have no overdue tasks'}
            </p>
          </div>
        </div>
        
        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Status Distribution */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <PieChartIcon className="w-5 h-5 mr-2 text-blue-600" />
              Task Status Distribution
            </h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats.statusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {stats.statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          {/* Category Distribution */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Target className="w-5 h-5 mr-2 text-green-600" />
              Tasks by Category
            </h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.categoryData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" name="Tasks" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Completion Rate Chart */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
              Task Completion Rate
            </h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData.completionRate}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value.toFixed(1)}%`, 'Completion Rate']} />
                  <Line type="monotone" dataKey="completion_rate" stroke="#8884d8" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          {/* Time Allocation Chart */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Clock className="w-5 h-5 mr-2 text-green-600" />
              Time Allocation by Category
            </h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData.timeAllocation}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="actual_hours" name="Actual Hours" fill="#82ca9d" />
                  <Bar dataKey="estimated_hours" name="Estimated Hours" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Daily Utilization Chart */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Calendar className="w-5 h-5 mr-2 text-purple-600" />
              Daily Time Utilization
            </h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData.dailyUtilization}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="hours" name="Hours Worked" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* User Productivity Chart */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
              <Users className="w-5 h-5 mr-2 text-orange-600" />
              User Productivity
            </h2>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData.userProductivity}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="username" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="completed_tasks" name="Completed Tasks" fill="#3b82f6" />
                  <Bar dataKey="efficiency" name="Efficiency %" fill="#10B981" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
        
        {/* Task List */}
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Task Details</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Task</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estimated</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actual</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Due Date</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {allTasksAnalytics.map(item => {
                  const task = item.task;
                  const dueDate = new Date(task.end_date);
                  const now = new Date();
                  const isOverdue = dueDate < now && task.status !== 'completed';
                  
                  const statusIcon = task.status === 'completed' 
                    ? <CheckCircle className="w-4 h-4 text-green-500" /> 
                    : task.status === 'in_progress' 
                    ? <PlayCircle className="w-4 h-4 text-blue-500" /> 
                    : <PauseCircle className="w-4 h-4 text-yellow-500" />;
                  
                  const statusText = task.status.replace('_', ' ').toUpperCase();
                  
                  return (
                    <tr key={task.id} className={isOverdue ? 'bg-red-50' : ''}>
                      <td className="px-6 py-4 text-sm text-gray-900">{task.description}</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{task.estimated_hr}h</td>
                      <td className="px-6 py-4 text-sm text-gray-900">{task.done_hr}h</td>
                      <td className="px-6 py-4 text-sm text-gray-900 flex items-center">
                        {statusIcon}
                        <span className="ml-1">{statusText}</span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {dueDate.toLocaleDateString()}
                        {isOverdue && <span className="ml-2 text-xs text-red-500">(Overdue)</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskAnalyticsDashboard;