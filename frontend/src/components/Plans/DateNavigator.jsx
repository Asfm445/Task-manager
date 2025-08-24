import { addDays, format, subDays } from "date-fns";
import { CalendarDays, ChevronLeft, ChevronRight } from "lucide-react";

export default function DateNavigator({ selectedDate, setSelectedDate }) {
  const goToYesterday = () => setSelectedDate((prev) => subDays(prev, 1));
  const goToTomorrow = () => setSelectedDate((prev) => addDays(prev, 1));

  return (
    <div className="flex items-center justify-between mb-8 px-2">
      <button
        onClick={goToYesterday}
        className="flex items-center gap-2 text-gray-600 hover:text-blue-700 font-medium px-4 py-2 rounded-lg transition-colors hover:bg-blue-100 shadow"
        title="Go to yesterday"
      >
        <ChevronLeft className="w-5 h-5" />
        <span>Yesterday</span>
      </button>
      <div className="flex items-center gap-2 bg-white/90 px-6 py-3 rounded-xl shadow-lg border border-blue-100">
        <CalendarDays className="w-6 h-6 text-blue-500" />
        <h2 className="text-2xl font-bold text-blue-700 tracking-tight">
          {format(selectedDate, "MMMM dd, yyyy")}
        </h2>
      </div>
      <button
        onClick={goToTomorrow}
        className="flex items-center gap-2 text-gray-600 hover:text-blue-700 font-medium px-4 py-2 rounded-lg transition-colors hover:bg-blue-100 shadow"
        title="Go to tomorrow"
      >
        <span>Tomorrow</span>
        <ChevronRight className="w-5 h-5" />
      </button>
    </div>
  );
}
