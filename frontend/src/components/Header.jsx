import { Link } from "react-router-dom";

export default function Header() {
  return (
    <header className="bg-white shadow-md flex justify-between items-center px-6 py-4 md:px-12 md:py-6">
      <h1 className="text-2xl md:text-3xl font-extrabold text-blue-700 tracking-tight">
        TimePlanner
      </h1>
      <nav className="flex gap-4 md:gap-8">
        <Link
          to="/tasks"
          className="text-blue-600 hover:text-blue-800 hover:bg-blue-50 transition-colors px-3 py-2 rounded-lg text-lg font-semibold"
        >
          Tasks
        </Link>
        <Link
          to="/plans"
          className="text-blue-600 hover:text-blue-800 hover:bg-blue-50 transition-colors px-3 py-2 rounded-lg text-lg font-semibold"
        >
          Plans
        </Link>
      </nav>
    </header>
  );
}
