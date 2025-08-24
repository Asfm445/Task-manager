import { ArrowLeft, BarChart3, Shield, Timer, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../api";
import Header from "../components/Header";

export default function TaskDetail() {
  const { id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.get(`/tasks/analytics/${id}`);
        setData(res.data);
      } catch (e) {
        setError(e);
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [id]);

  if (loading) return <div className="p-6 text-lg text-blue-600 animate-pulse">Loading analytics...</div>;
  if (error) return <div className="p-6 text-red-600">{error?.response?.data?.detail || error.message}</div>;
  if (!data) return null;

  const { task, analytics } = data;
  const cm = analytics?.completion_metrics || {};
  const te = analytics?.time_efficiency || {};
  const pt = analytics?.progress_trends || {};
  const pi = analytics?.performance_indicators || {};
  const sa = analytics?.status_analysis || {};
  const ta = analytics?.time_analysis || {};
  const sum = analytics?.summary || {};

  return (
   <>
    <Header></Header>
     <div className="max-w-4xl mx-auto p-4 space-y-8">
      <div className="flex items-center gap-3 mb-2">
        <Link to="/tasks" className="text-blue-600 flex items-center gap-1 hover:underline hover:text-blue-800 transition">
          <ArrowLeft size={18}/> Back
        </Link>
        <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight">
          Task <span className="text-blue-700">#{task.id}</span> Analytics
        </h1>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-2xl p-5 shadow-lg hover:shadow-xl transition">
          <div className="flex items-center gap-2 text-blue-600 font-semibold mb-2"><BarChart3/> Completion</div>
          <div className="text-4xl font-extrabold text-blue-800">{cm.progress_percentage ?? cm.completion_rate ?? 0}%</div>
          <div className="text-sm text-gray-700 mt-2">Done <span className="font-bold">{cm.done_hours ?? 0}h</span> / Est <span className="font-bold">{cm.estimated_hours ?? 0}h</span></div>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-2xl p-5 shadow-lg hover:shadow-xl transition">
          <div className="flex items-center gap-2 text-green-600 font-semibold mb-2"><TrendingUp/> Efficiency</div>
          <div className="text-4xl font-extrabold text-green-800">{te.efficiency_score ?? 0}%</div>
          <div className="text-sm text-gray-700 mt-2">Avg <span className="font-bold">{te.avg_hours_per_cycle ?? 0}h</span> per cycle</div>
        </div>
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-2xl p-5 shadow-lg hover:shadow-xl transition">
          <div className="flex items-center gap-2 text-purple-600 font-semibold mb-2"><Timer/> Time</div>
          <div className="text-4xl font-extrabold text-purple-800">{ta.time_spent_hours ?? 0}h</div>
          <div className="text-sm text-gray-700 mt-2">Remaining <span className="font-bold">{ta.time_remaining_hours ?? 0}h</span> <span className="italic">({ta.deadline_status})</span></div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow hover:shadow-md transition">
          <h2 className="font-semibold mb-2 flex items-center gap-2 text-blue-700"><TrendingUp/> Trend</h2>
          <p className="text-gray-700 mb-1">Trend: <span className="font-bold">{pt.trend || "N/A"}</span></p>
          <p className="text-gray-700 mb-1">Consistency: <span className="font-bold">{pt.consistency_score ?? 0}%</span></p>
          <p className="text-gray-700 mb-1">Improvement: <span className="font-bold">{pt.improvement_rate ?? 0}%</span></p>
          {pt.recent_performance && (
            <div className="mt-2 text-sm text-gray-600">Recent performance: <span className="font-mono">{pt.recent_performance.join(", ")}h</span></div>
          )}
        </div>
        <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow hover:shadow-md transition">
          <h2 className="font-semibold mb-2 flex items-center gap-2 text-purple-700"><Shield/> Performance</h2>
          <p className="text-gray-700 mb-1">Productivity: <span className="font-bold">{pi.productivity_score ?? 0}%</span></p>
          <p className="text-gray-700 mb-1">Reliability: <span className="font-bold">{pi.reliability_score ?? 0}%</span></p>
          <p className="text-gray-700 mb-1">Quality: <span className="font-bold">{pi.quality_score ?? 0}%</span></p>
          <p className="text-gray-700 mb-1">Overall: <span className="font-bold">{pi.overall_performance ?? 0}%</span></p>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow hover:shadow-md transition">
        <h2 className="font-semibold mb-2 text-blue-700">Status</h2>
        <div className="text-gray-700 grid md:grid-cols-3 gap-2 text-sm">
          <div><span className="font-bold">Current:</span> {sa.current_status}</div>
          <div><span className="font-bold">Health:</span> {sa.status_health}</div>
          <div><span className="font-bold">Changes:</span> {sa.status_changes}</div>
          <div><span className="font-bold">Stopped:</span> {sa.is_stopped ? "Yes" : "No"}</div>
          <div><span className="font-bold">Repetitive:</span> {sa.is_repetitive ? "Yes" : "No"}</div>
          <div><span className="font-bold">Stop frequency:</span> {sa.stop_frequency}</div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow hover:shadow-md transition">
        <h2 className="font-semibold mb-2 text-blue-700">Summary</h2>
        <div className="text-gray-800 text-lg font-bold mb-1">Grade: {sum.grade}</div>
        <div className="text-gray-600 mb-2">Overall score: {sum.overall_score}</div>
        {Array.isArray(sum.recommendations) && sum.recommendations.length > 0 && (
          <ul className="list-disc ml-6 mt-2 text-gray-700">
            {sum.recommendations.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
   </>
  );
}
