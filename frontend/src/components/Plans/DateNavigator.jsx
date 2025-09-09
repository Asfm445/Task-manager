import { addDays, format, subDays } from "date-fns";
import { CalendarDays, ChevronLeft, ChevronRight } from "lucide-react";

export default function DateNavigator({ selectedDate, setSelectedDate }) {
  const goToYesterday = () => setSelectedDate((prev) => subDays(prev, 1));
  const goToTomorrow = () => setSelectedDate((prev) => addDays(prev, 1));
  const goToToday = () => setSelectedDate(new Date());

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mb-8 px-2">
      {/* Yesterday Button - Hidden on mobile, visible on larger screens */}
      <button
        onClick={goToYesterday}
        className="hidden sm:flex items-center gap-2 text-gray-600 hover:text-blue-700 font-medium px-4 py-2 rounded-lg transition-colors hover:bg-blue-100 shadow"
        title="Go to yesterday"
      >
        <ChevronLeft className="w-5 h-5" />
        <span>Yesterday</span>
      </button>

      {/* Mobile Navigation */}
      <div className="flex sm:hidden items-center justify-between w-full">
        <button
          onClick={goToYesterday}
          className="flex items-center justify-center w-10 h-10 text-gray-600 hover:text-blue-700 rounded-full transition-colors hover:bg-blue-100"
          title="Go to yesterday"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
        
        <div className="flex flex-col items-center">
          <button
            onClick={goToToday}
            className="text-xs text-blue-500 hover:text-blue-700 font-medium mb-1 px-2 py-1 rounded transition-colors"
          >
            Today
          </button>
          <div className="flex items-center gap-2 bg-white/90 px-4 py-2 rounded-xl shadow-lg border border-blue-100">
            <CalendarDays className="w-5 h-5 text-blue-500" />
            <h2 className="text-lg font-bold text-blue-700 tracking-tight">
              {format(selectedDate, "MMM dd, yyyy")}
            </h2>
          </div>
        </div>
        
        <button
          onClick={goToTomorrow}
          className="flex items-center justify-center w-10 h-10 text-gray-600 hover:text-blue-700 rounded-full transition-colors hover:bg-blue-100"
          title="Go to tomorrow"
        >
          <ChevronRight className="w-6 h-6" />
        </button>
      </div>

      {/* Desktop Navigation */}
      <div className="hidden sm:flex items-center gap-2 bg-white/90 px-4 py-3 rounded-xl shadow-lg border border-blue-100">
        <CalendarDays className="w-5 h-5 sm:w-6 sm:h-6 text-blue-500" />
        <h2 className="text-xl sm:text-2xl font-bold text-blue-700 tracking-tight">
          {format(selectedDate, "MMMM dd, yyyy")}
        </h2>
      </div>

      {/* Tomorrow Button - Hidden on mobile, visible on larger screens */}
      <button
        onClick={goToTomorrow}
        className="hidden sm:flex items-center gap-2 text-gray-600 hover:text-blue-700 font-medium px-4 py-2 rounded-lg transition-colors hover:bg-blue-100 shadow"
        title="Go to tomorrow"
      >
        <span>Tomorrow</span>
        <ChevronRight className="w-5 h-5" />
      </button>

      {/* Today Button - Desktop only */}
      <button
        onClick={goToToday}
        className="hidden sm:block bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 rounded-lg transition-colors shadow"
      >
        Today
      </button>
    </div>
  );
}