import { Calendar, CalendarDays, Clock, Target, TrendingUp, Zap } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import {
    Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart,
    ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts';

// Mock data
const mockTimeLogs = [
  { id: 1, date: '2025-09-01', start_time: '13:18:00', end_time: '14:18:00', description: 'correct some issue with task-manager project' },
  { id: 2, date: '2025-09-01', start_time: '14:34:00', end_time: '15:34:00', description: 'set up vm kali linux and find a way for cyber' },
  { id: 3, date: '2025-09-03', start_time: '02:29:00', end_time: '04:56:00', description: 'creating needed virtual machines' },
  { id: 4, date: '2025-09-06', start_time: '15:35:00', end_time: '16:35:00', description: 'Plan for phase 2' },
  { id: 5, date: '2025-09-07', start_time: '01:54:00', end_time: '03:54:00', description: 'Array and Matrix' },
  { id: 6, date: '2025-09-07', start_time: '10:01:00', end_time: '11:30:00', description: 'DFS and Union Find' },
  { id: 7, date: '2025-09-08', start_time: '02:03:00', end_time: '04:03:00', description: 'DFS and Union Find' },
  { id: 8, date: '2025-09-09', start_time: '03:26:00', end_time: '05:26:00', description: 'stack and queue' }
];

// Helper: format date
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
};

// Helper: generate calendar heatmap data
const generateCalendarData = (logs, year, month) => {
  const daysInMonth = new Date(year, month, 0).getDate();
  const calendarData = Array.from({ length: daysInMonth }, (_, i) => {
    const day = i + 1;
    const dateString = `${year}-${month.toString().padStart(2,'0')}-${day.toString().padStart(2,'0')}`;
    return { date: dateString, hours: 0, formattedDate: formatDate(dateString) };
  });

  logs.forEach(log => {
    const [logYear, logMonth, logDay] = log.date.split('-').map(Number);
    if (logYear === year && logMonth === month) {
      const start = new Date(`2000-01-01T${log.start_time}`);
      const end = new Date(`2000-01-01T${log.end_time}`);
      const duration = (end - start) / (1000 * 60 * 60); // in hours
      const entry = calendarData[logDay - 1];
      if (entry) entry.hours += duration;
    }
  });

  return calendarData;
};

// Helper: calculate stats
const calculateStats = (logs) => {
  const dailyStats = {};
  const topicStats = {};
  let totalMinutes = 0;

  logs.forEach(log => {
    const start = new Date(`2000-01-01T${log.start_time}`);
    const end = new Date(`2000-01-01T${log.end_time}`);
    const duration = (end - start) / (1000 * 60);
    totalMinutes += duration;

    dailyStats[log.date] = (dailyStats[log.date] || 0) + duration;

    const topic = log.description.split(' ')[0];
    topicStats[topic] = (topicStats[topic] || 0) + duration;
  });

  const dailyData = Object.entries(dailyStats).map(([date, minutes]) => ({
    date,
    minutes,
    hours: (minutes/60).toFixed(1),
    formattedDate: formatDate(date)
  }));

  const topicData = Object.entries(topicStats).map(([topic, minutes]) => ({
    topic,
    minutes,
    hours: (minutes/60).toFixed(1)
  }));

  return {
    totalHours: (totalMinutes / 60).toFixed(1),
    averagePerDay: (totalMinutes / Object.keys(dailyStats).length / 60).toFixed(1),
    averageSession: (totalMinutes / logs.length / 60).toFixed(1),
    totalSessions: logs.length,
    totalDays: Object.keys(dailyStats).length,
    dailyData,
    topicData
  };
};

// Heatmap color
const getHeatmapColor = (hours) => {
  if (hours === 0) return 'bg-gray-100';
  if (hours < 1) return 'bg-green-100';
  if (hours < 2) return 'bg-green-200';
  if (hours < 4) return 'bg-green-300';
  if (hours < 6) return 'bg-green-400';
  return 'bg-green-500 text-white';
};

// --- Subcomponents ---
const SummaryCards = ({ stats }) => (
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <div className="bg-white rounded-xl shadow p-6 flex flex-col items-center">
      <div className="p-3 bg-blue-100 rounded-full mb-4"><Clock className="w-6 h-6 text-blue-600" /></div>
      <h3 className="text-lg font-semibold text-gray-700">Total Hours</h3>
      <p className="text-3xl font-bold text-gray-900">{stats.totalHours}h</p>
    </div>
    <div className="bg-white rounded-xl shadow p-6 flex flex-col items-center">
      <div className="p-3 bg-green-100 rounded-full mb-4"><Calendar className="w-6 h-6 text-green-600" /></div>
      <h3 className="text-lg font-semibold text-gray-700">Days Tracked</h3>
      <p className="text-3xl font-bold text-gray-900">{stats.totalDays}</p>
    </div>
    <div className="bg-white rounded-xl shadow p-6 flex flex-col items-center">
      <div className="p-3 bg-purple-100 rounded-full mb-4"><TrendingUp className="w-6 h-6 text-purple-600" /></div>
      <h3 className="text-lg font-semibold text-gray-700">Avg Per Day</h3>
      <p className="text-3xl font-bold text-gray-900">{stats.averagePerDay}h</p>
    </div>
    <div className="bg-white rounded-xl shadow p-6 flex flex-col items-center">
      <div className="p-3 bg-orange-100 rounded-full mb-4"><Zap className="w-6 h-6 text-orange-600" /></div>
      <h3 className="text-lg font-semibold text-gray-700">Avg Session</h3>
      <p className="text-3xl font-bold text-gray-900">{stats.averageSession}h</p>
    </div>
  </div>
);

const CalendarHeatmap = ({ calendarData }) => (
  <div className="bg-white rounded-xl shadow p-6 mb-8">
    <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
      <CalendarDays className="w-5 h-5 mr-2 text-blue-600" />Work Calendar
    </h2>
    <div className="grid grid-cols-7 gap-2">
      {['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].map(day => (
        <div key={day} className="text-center font-medium text-gray-500 py-2">{day}</div>
      ))}
      {calendarData.map(day => {
        const dayNumber = new Date(day.date).getDate();
        return (
          <div
            key={day.date}
            className={`h-12 rounded-lg flex flex-col items-center justify-center ${getHeatmapColor(day.hours)}`}
            title={`${day.formattedDate}: ${day.hours.toFixed(1)} hours`}
          >
            <span className="text-xs font-medium">{dayNumber}</span>
            {day.hours > 0 && <span className="text-xs mt-1">{day.hours.toFixed(1)}h</span>}
          </div>
        );
      })}
    </div>
    <div className="flex justify-between mt-4 text-sm text-gray-500">
      <span>Less</span>
      <div className="flex space-x-1">
        <div className="w-4 h-4 bg-gray-100"></div>
        <div className="w-4 h-4 bg-green-100"></div>
        <div className="w-4 h-4 bg-green-200"></div>
        <div className="w-4 h-4 bg-green-300"></div>
        <div className="w-4 h-4 bg-green-400"></div>
        <div className="w-4 h-4 bg-green-500"></div>
      </div>
      <span>More</span>
    </div>
  </div>
);

const DailyBarChart = ({ dailyData }) => (
  <div className="bg-white rounded-xl shadow p-6">
    <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
      <CalendarDays className="w-5 h-5 mr-2 text-blue-600" />Time Distribution by Date
    </h2>
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={dailyData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="formattedDate" angle={-45} textAnchor="end" height={60} />
          <YAxis label={{ value: 'Hours', angle: -90, position: 'insideLeft' }} />
          <Tooltip formatter={(value) => [`${value} hours`, 'Duration']} />
          <Legend />
          <Bar dataKey="hours" name="Hours" fill="#3b82f6" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  </div>
);

const TopicPieChart = ({ topicData }) => {
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];
  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
        <Target className="w-5 h-5 mr-2 text-green-600" />Time by Topic
      </h2>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={topicData}
              cx="50%" cy="50%"
              labelLine={false}
              label={({ topic, hours }) => `${topic}: ${hours}h`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="hours"
              nameKey="topic"
            >
              {topicData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value) => [`${value} hours`, 'Duration']} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

const TimeLogTable = ({ logs }) => (
  <div className="bg-white rounded-xl shadow p-6">
    <h2 className="text-xl font-semibold text-gray-800 mb-4">Time Log Details</h2>
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {['Date','Start Time','End Time','Duration','Description'].map(h => (
              <th key={h} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {logs.map(log => {
            const start = new Date(`2000-01-01T${log.start_time}`);
            const end = new Date(`2000-01-01T${log.end_time}`);
            const duration = (end - start) / (1000 * 60);
            const hours = Math.floor(duration / 60);
            const minutes = duration % 60;

            return (
              <tr key={log.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{formatDate(log.date)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{log.start_time.substring(0,5)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{log.end_time.substring(0,5)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{hours}h {minutes}m</td>
                <td className="px-6 py-4 text-sm text-gray-900">{log.description}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  </div>
);

// --- Main Component ---
const TimeLogAnalytics = () => {
  const [timeLogs, setTimeLogs] = useState([]);
  const [selectedMonth, setSelectedMonth] = useState(9);
  const [selectedYear, setSelectedYear] = useState(2025);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setTimeout(() => {
        setTimeLogs(mockTimeLogs);
        setLoading(false);
      }, 800);
    };
    fetchData();
  }, []);

  const calendarData = useMemo(() => generateCalendarData(timeLogs, selectedYear, selectedMonth), [timeLogs, selectedYear, selectedMonth]);
  const stats = useMemo(() => calculateStats(timeLogs), [timeLogs]);

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  );

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Time Log Analytics</h1>
        <p className="text-gray-600 mb-8">Analyze your productivity patterns and time distribution</p>

        <SummaryCards stats={stats} />
        <CalendarHeatmap calendarData={calendarData} />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <DailyBarChart dailyData={stats.dailyData} />
          <TopicPieChart topicData={stats.topicData} />
        </div>
        <TimeLogTable logs={timeLogs} />
      </div>
    </div>
  );
};

export default TimeLogAnalytics;
