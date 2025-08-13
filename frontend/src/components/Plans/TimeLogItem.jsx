export default function TimeLogItem({ log, onMarkSuccess, formatTime, getDuration }) {
  return (
    <li className="flex flex-col md:flex-row md:justify-between md:items-center bg-blue-50 rounded-lg px-5 py-3 border border-blue-100 shadow-sm hover:bg-blue-100 transition">
      <div className="flex items-center gap-4">
        <span className="font-mono text-lg text-blue-800">
          {formatTime(log.start_time)} <span className="mx-1 text-gray-400">–</span>{" "}
          {formatTime(log.end_time)}
        </span>
        <span className="text-sm text-blue-600 font-semibold bg-blue-100 px-3 py-1 rounded-full">
          {getDuration(log.start_time, log.end_time)}
        </span>
      </div>
      <div className="flex items-center gap-4 mt-2 md:mt-0">
        <span className="text-sm text-gray-700 font-medium">
          Task: <span className="text-blue-700">{log.task?.description || log.task || log.task_id}</span>
        </span>
        {!log.success && (
          <button
            onClick={() => onMarkSuccess(log.id)}
            className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded-lg text-sm font-semibold"
          >
            Mark Success
          </button>
        )}
      </div>
    </li>
  );
}
