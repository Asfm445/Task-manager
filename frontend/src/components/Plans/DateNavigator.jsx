import { format, addDays, subDays } from "date-fns";

export default function DateNavigator({ selectedDate, setSelectedDate }) {
  const goToYesterday = () => setSelectedDate((prev) => subDays(prev, 1));
  const goToTomorrow = () => setSelectedDate((prev) => addDays(prev, 1));

  return (
    <div className="flex items-center justify-between mb-8">
      <button
        onClick={goToYesterday}
        className="flex items-center gap-1 text-gray-600 hover:text-blue-700 font-medium px-3 py-2 rounded transition-colors hover:bg-blue-100"
      >
        <span className="text-lg">⬅</span> Yesterday
      </button>
      <h2 className="text-2xl font-bold text-blue-700 tracking-tight shadow-sm px-4 py-2 rounded bg-white/80">
        {format(selectedDate, "MMMM dd, yyyy")}
      </h2>
      <button
        onClick={goToTomorrow}
        className="flex items-center gap-1 text-gray-600 hover:text-blue-700 font-medium px-3 py-2 rounded transition-colors hover:bg-blue-100"
      >
        Tomorrow <span className="text-lg">➡</span>
      </button>
    </div>
  );
}
