import { NavLink } from "react-router-dom";

export default function Header() {
  return (
    <header className="bg-white shadow-md flex justify-between items-center px-6 py-4 md:px-12 md:py-6 sticky top-0 z-50">
      <h1 className="text-2xl md:text-3xl font-extrabold text-blue-700 tracking-tight select-none">
        TimePlanner
      </h1>
      <nav className="flex gap-6 md:gap-10">
        <NavLink
          to="/tasks"
          className={({ isActive }) =>
            `text-lg font-semibold px-4 py-2 rounded-lg transition-colors 
             ${
               isActive
                 ? "bg-blue-100 text-blue-900"
                 : "text-blue-600 hover:text-blue-800 hover:bg-blue-50"
             }`
          }
        >
          Tasks
        </NavLink>
        <NavLink
          to="/plans"
          className={({ isActive }) =>
            `text-lg font-semibold px-4 py-2 rounded-lg transition-colors 
             ${
               isActive
                 ? "bg-blue-100 text-blue-900"
                 : "text-blue-600 hover:text-blue-800 hover:bg-blue-50"
             }`
          }
        >
          Plans
        </NavLink>
      </nav>
    </header>
  );
}
