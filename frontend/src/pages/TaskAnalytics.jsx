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
import { useEffect, useState } from 'react';
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

// Mock data based on your provided information
const mockTasks = [
  { id: 1, description: "correct some issue with task-manager project", end_date: "2025-09-01 18:16:00+00", estimated_hr: 1, done_hr: 1, is_repititive: false, status: "completed", start_date: "2025-09-01 17:21:00+00", main_task_id: null, owner_id: 1, is_stopped: false },
  { id: 2, description: "set up vm kali linux and find a way for cyber", end_date: "2025-09-01 19:26:00+00", estimated_hr: 1, done_hr: 1, is_repititive: false, status: "completed", start_date: "2025-09-01 18:26:00+00", main_task_id: null, owner_id: 1, is_stopped: false },
  { id: 6, description: "creating needed virtual machines", end_date: "2025-09-03 08:55:00+00", estimated_hr: 2, done_hr: 2.45, is_repititive: false, status: "completed", start_date: "2025-09-03 06:30:00+00", main_task_id: null, owner_id: 1, is_stopped: false },
  { id: 8, description: "Plan for phase 2", end_date: "2025-09-07 00:31:00+00", estimated_hr: 1, done_hr: 1, is_repititive: false, status: "completed", start_date: "2025-09-06 19:36:00+00", main_task_id: 7, owner_id: 1, is_stopped: false },
  { id: 10, description: "Array and Matrix", end_date: "2025-10-07 05:52:00+00", estimated_hr: 8, done_hr: 2, is_repititive: false, status: "in_progress", start_date: "2025-09-07 05:57:00+00", main_task_id: 9, owner_id: 1, is_stopped: false },
  { id: 11, description: "DFS and Union Find", end_date: "2025-10-21 13:59:00+00", estimated_hr: 19, done_hr: 3.48, is_repititive: false, status: "in_progress", start_date: "2025-09-07 14:10:00+00", main_task_id: 9, owner_id: 1, is_stopped: false },
  { id: 12, description: "stack and que", end_date: "2025-11-07 08:12:00+00", estimated_hr: 15, done_hr: 0, is_repititive: false, status: "in_progress", start_date: "2025-09-09 07:17:00+00", main_task_id: 9, owner_id: 1, is_stopped: false },
  { id: 5, description: "Random Forest", end_date: "2025-09-02 14:30:00+00", estimated_hr: 2, done_hr: 2.23, is_repititive: false, status: "completed", start_date: "2025-09-02 12:16:00+00", main_task_id: 4, owner_id: 1, is_stopped: false },
  { id: 4, description: "ML", end_date: "2025-11-02 13:12:00+00", estimated_hr: 64, done_hr: 2, is_repititive: false, status: "in_progress", start_date: "2025-09-02 12:17:00+00", main_task_id: null, owner_id: 1, is_stopped: false },
  { id: 14, description: "correct some issue with task_manager project", end_date: "2025-09-09 20:22:00+00", estimated_hr: 2, done_hr: 0, is_repititive: false, status: "pending", start_date: "2025-09-09 10:27:00+00", main_task_id: null, owner_id: 1, is_stopped: false },
  { id: 9, description: "DSA practice", end_date: "2025-11-21 21:42:00+00", estimated_hr: 240, done_hr: 0, is_repititive: false, status: "pending", start_date: "2025-09-07 20:42:00+00", main_task_id: null, owner_id: 1, is_stopped: false },
  { id: 7, description: "ML phase 2", end_date: "2025-09-21 19:27:00+00", estimated_hr: 16, done_hr: 1, is_repititive: false, status: "in_progress", start_date: "2025-09-07 19:27:00+00", main_task_id: 4, owner_id: 1, is_stopped: false },
];

const mockTimeLogs = [
  { id: 1, end_time: "14:18:00", start_time: "13:18:00", task_id: 1, plan_id: 1, done: true },
  { id: 2, end_time: "15:34:00", start_time: "14:34:00", task_id: 2, plan_id: 1, done: true },
  { id: 4, end_time: "04:56:00", start_time: "02:29:00", task_id: 6, plan_id: 3, done: true },
  { id: 5, end_time: "16:35:00", start_time: "15:35:00", task_id: 8, plan_id: 4, done: true },
  { id: 6, end_time: "03:54:00", start_time: "01:54:00", task_id: 10, plan_id: 5, done: true },
  { id: 7, end_time: "11:30:00", start_time: "10:01:00", task_id: 11, plan_id: 5, done: true },
  { id: 8, end_time: "04:03:00", start_time: "02:03:00", task_id: 11, plan_id: 6, done: true },
  { id: 10, end_time: "05:26:00", start_time: "03:26:00", task_id: 12, plan_id: 7, done: false },
];

// Generate mock analytics data
const generateAnalyticsData = () => {
  return {
    completionRate: [
      { date: '2025-09-01', total_tasks: 5, completed_tasks: 3, completion_rate: 60 },
      { date: '2025-09-02', total_tasks: 7, completed_tasks: 5, completion_rate: 71 },
      { date: '2025-09-03', total_tasks: 6, completed_tasks: 4, completion_rate: 67 },
      { date: '2025-09-04', total_tasks: 8, completed_tasks: 6, completion_rate: 75 },
      { date: '2025-09-05', total_tasks: 4, completed_tasks: 3, completion_rate: 75 },
      { date: '2025-09-06', total_tasks: 9, completed_tasks: 7, completion_rate: 78 },
      { date: '2025-09-07', total_tasks: 7, completed_tasks: 5, completion_rate: 71 },
    ],
    timeAllocation: [
      { category: 'Machine Learning', estimated_hours: 20, actual_hours: 15 },
      { category: 'Algorithms', estimated_hours: 15, actual_hours: 12 },
      { category: 'Project Work', estimated_hours: 8, actual_hours: 6 },
      { category: 'Infrastructure', estimated_hours: 5, actual_hours: 4 },
      { category: 'Planning', estimated_hours: 3, actual_hours: 2 },
      { category: 'Other', estimated_hours: 10, actual_hours: 8 },
    ],
    userProductivity: [
      { username: 'You', completed_tasks: 12, total_hours: 25, efficiency: 85 },
      { username: 'Team Member 1', completed_tasks: 8, total_hours: 18, efficiency: 78 },
      { username: 'Team Member 2', completed_tasks: 10, total_hours: 22, efficiency: 82 },
    ],
    dailyUtilization: [
      { date: '2025-09-01', hours: 6.5 },
      { date: '2025-09-02', hours: 7.2 },
      { date: '2025-09-03', hours: 5.8 },
      { date: '2025-09-04', hours: 8.1 },
      { date: '2025-09-05', hours: 6.3 },
      { date: '2025-09-06', hours: 7.5 },
      { date: '2025-09-07', hours: 6.9 },
    ]
  };
};

const TaskAnalyticsDashboard = () => {
  const [tasks, setTasks] = useState([]);
  const [timeLogs, setTimeLogs] = useState([]);
  const [timeRange, setTimeRange] = useState('7days');
  const [loading, setLoading] = useState(true);
  const [analyticsData, setAnalyticsData] = useState({
    completionRate: [],
    timeAllocation: [],
    userProductivity: [],
    dailyUtilization: []
  });

  useEffect(() => {
    // Simulate API fetch
    const fetchData = async () => {
      setLoading(true);
      try {
        // Using mock data for demonstration
        setTimeout(() => {
          setTasks(mockTasks);
          setTimeLogs(mockTimeLogs);
          setAnalyticsData(generateAnalyticsData());
          setLoading(false);
        }, 800);
      } catch (error) {
        console.error('Failed to fetch data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Calculate statistics
  const calculateStats = () => {
    if (tasks.length === 0) return {};
    
    // Status distribution
    const statusCount = {
      completed: 0,
      in_progress: 0,
      pending: 0
    };
    
    // Estimated vs actual time
    let totalEstimated = 0;
    let totalActual = 0;
    let totalCompletedEstimated = 0;
    let totalCompletedActual = 0;
    
    // Categorize tasks
    const categories = {};
    
    tasks.forEach(task => {
      // Count status
      statusCount[task.status] = (statusCount[task.status] || 0) + 1;
      
      // Sum estimated and actual hours
      totalEstimated += task.estimated_hr;
      totalActual += task.done_hr;
      
      if (task.status === 'completed') {
        totalCompletedEstimated += task.estimated_hr;
        totalCompletedActual += task.done_hr;
      }
      
      // Categorize by description keywords
      const desc = task.description.toLowerCase();
      let category = 'Other';
      
      if (desc.includes('ml') || desc.includes('random forest')) category = 'Machine Learning';
      else if (desc.includes('dsa') || desc.includes('array') || desc.includes('matrix') || 
               desc.includes('dfs') || desc.includes('stack') || desc.includes('que')) category = 'Algorithms';
      else if (desc.includes('task') || desc.includes('project')) category = 'Project Work';
      else if (desc.includes('vm') || desc.includes('kali') || desc.includes('linux')) category = 'Infrastructure';
      else if (desc.includes('plan')) category = 'Planning';
      
      categories[category] = (categories[category] || 0) + 1;
    });
    
    // Accuracy for completed tasks
    const accuracy = totalCompletedEstimated > 0 
      ? (totalCompletedActual / totalCompletedEstimated) * 100 
      : 0;
    
    // Overdue tasks (end_date is in the past but status is not completed)
    const now = new Date();
    const overdueTasks = tasks.filter(task => {
      if (task.status === 'completed') return false;
      const endDate = new Date(task.end_date);
      return endDate < now;
    });
    
    // Format data for charts
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
      totalTasks: tasks.length,
      statusCount,
      totalEstimated,
      totalActual,
      accuracy: accuracy.toFixed(1),
      overdueTasks: overdueTasks.length,
      statusData,
      categoryData,
      efficiency: totalEstimated > 0 ? ((totalActual / totalEstimated) * 100).toFixed(1) : 0
    };
  };

  const stats = calculateStats();

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
                <LineChart data={analyticsData.completionRate}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`${value}%`, 'Completion Rate']} />
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
                <BarChart data={analyticsData.timeAllocation}>
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
                <BarChart data={analyticsData.dailyUtilization}>
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
                <BarChart data={analyticsData.userProductivity}>
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
                {tasks.map(task => {
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