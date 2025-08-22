import { ArrowLeft, BarChart3, Shield, Timer, TrendingUp } from "lucide-react";
import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../api";

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

  if (loading) return <div className="p-6">Loading analytics...</div>;
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
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/tasks" className="text-blue-600 flex items-center gap-1"><ArrowLeft size={16}/> Back</Link>
        <h1 className="text-2xl font-bold">Task #{task.id} Analytics</h1>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-white border rounded-lg p-4 shadow">
          <div className="flex items-center gap-2 text-blue-600"><BarChart3/> Completion</div>
          <div className="text-3xl font-bold">{cm.progress_percentage ?? cm.completion_rate ?? 0}%</div>
          <div className="text-sm text-gray-600">Done {cm.done_hours ?? 0}h / Est {cm.estimated_hours ?? 0}h</div>
        </div>
        <div className="bg-white border rounded-lg p-4 shadow">
          <div className="flex items-center gap-2 text-green-600"><TrendingUp/> Efficiency</div>
          <div className="text-3xl font-bold">{te.efficiency_score ?? 0}%</div>
          <div className="text-sm text-gray-600">Avg {te.avg_hours_per_cycle ?? 0}h per cycle</div>
        </div>
        <div className="bg-white border rounded-lg p-4 shadow">
          <div className="flex items-center gap-2 text-purple-600"><Timer/> Time</div>
          <div className="text-3xl font-bold">{ta.time_spent_hours ?? 0}h</div>
          <div className="text-sm text-gray-600">Remaining {ta.time_remaining_hours ?? 0}h ({ta.deadline_status})</div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-white border rounded-lg p-4 shadow">
          <h2 className="font-semibold mb-2 flex items-center gap-2"><TrendingUp/> Trend</h2>
          <p className="text-gray-700">Trend: {pt.trend || "N/A"}</p>
          <p className="text-gray-700">Consistency: {pt.consistency_score ?? 0}%</p>
          <p className="text-gray-700">Improvement: {pt.improvement_rate ?? 0}%</p>
          {pt.recent_performance && (
            <div className="mt-2 text-sm text-gray-600">Recent performance: {pt.recent_performance.join(", ")}h</div>
          )}
        </div>
        <div className="bg-white border rounded-lg p-4 shadow">
          <h2 className="font-semibold mb-2 flex items-center gap-2"><Shield/> Performance</h2>
          <p className="text-gray-700">Productivity: {pi.productivity_score ?? 0}%</p>
          <p className="text-gray-700">Reliability: {pi.reliability_score ?? 0}%</p>
          <p className="text-gray-700">Quality: {pi.quality_score ?? 0}%</p>
          <p className="text-gray-700">Overall: {pi.overall_performance ?? 0}%</p>
        </div>
      </div>

      <div className="bg-white border rounded-lg p-4 shadow">
        <h2 className="font-semibold mb-2">Status</h2>
        <div className="text-gray-700 grid md:grid-cols-3 gap-2 text-sm">
          <div>Current: {sa.current_status}</div>
          <div>Health: {sa.status_health}</div>
          <div>Changes: {sa.status_changes}</div>
          <div>Stopped: {sa.is_stopped ? "Yes" : "No"}</div>
          <div>Repetitive: {sa.is_repetitive ? "Yes" : "No"}</div>
          <div>Stop frequency: {sa.stop_frequency}</div>
        </div>
      </div>

      <div className="bg-white border rounded-lg p-4 shadow">
        <h2 className="font-semibold mb-2">Summary</h2>
        <div className="text-gray-800 text-lg font-bold">Grade: {sum.grade}</div>
        <div className="text-gray-600">Overall score: {sum.overall_score}</div>
        {Array.isArray(sum.recommendations) && sum.recommendations.length > 0 && (
          <ul className="list-disc ml-6 mt-2 text-gray-700">
            {sum.recommendations.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
