import { LogOut, Menu } from "lucide-react";
import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";

export default function Header() {
  const navigate = useNavigate();
  const [navOpen, setNavOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/login");
  };

  return (
    <header className="bg-white shadow-md px-4 py-3 md:px-12 md:py-6 sticky top-0 z-50">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-3">
          <span className="bg-blue-600 text-white rounded-full px-3 py-1 font-bold text-lg select-none shadow">
            TP
          </span>
          <h1 className="text-xl md:text-3xl font-extrabold text-blue-700 tracking-tight select-none">
            TimePlanner
          </h1>
        </div>
        {/* Mobile menu button */}
        <button
          className="md:hidden p-2 rounded-lg text-blue-700 hover:bg-blue-100"
          onClick={() => setNavOpen((v) => !v)}
          aria-label="Open navigation"
        >
          <Menu size={28} />
        </button>
        {/* Desktop nav */}
        <nav className="hidden md:flex gap-6 md:gap-10 items-center">
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
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 bg-red-50 hover:bg-red-100 text-red-600 hover:text-red-800 px-4 py-2 rounded-lg font-semibold transition-colors shadow"
            title="Logout"
          >
            <LogOut size={18} /> Logout
          </button>
        </nav>
      </div>
      {/* Mobile nav */}
      {navOpen && (
        <nav className="flex flex-col gap-2 mt-3 md:hidden">
          <NavLink
            to="/tasks"
            className={({ isActive }) =>
              `text-base font-semibold px-4 py-2 rounded-lg transition-colors 
               ${
                 isActive
                   ? "bg-blue-100 text-blue-900"
                   : "text-blue-600 hover:text-blue-800 hover:bg-blue-50"
               }`
            }
            onClick={() => setNavOpen(false)}
          >
            Tasks
          </NavLink>
          <NavLink
            to="/plans"
            className={({ isActive }) =>
              `text-base font-semibold px-4 py-2 rounded-lg transition-colors 
               ${
                 isActive
                   ? "bg-blue-100 text-blue-900"
                   : "text-blue-600 hover:text-blue-800 hover:bg-blue-50"
               }`
            }
            onClick={() => setNavOpen(false)}
          >
            Plans
          </NavLink>
          <button
            onClick={() => {
              setNavOpen(false);
              handleLogout();
            }}
            className="flex items-center gap-2 bg-red-50 hover:bg-red-100 text-red-600 hover:text-red-800 px-4 py-2 rounded-lg font-semibold transition-colors shadow"
            title="Logout"
          >
            <LogOut size={18} /> Logout
          </button>
        </nav>
      )}
    </header>
  );
}
