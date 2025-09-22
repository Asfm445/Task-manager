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

  const linkBase =
    "relative text-sm md:text-base font-semibold px-4 py-2 rounded-lg transition-all";
  const linkActive =
    "text-blue-900 bg-blue-100 shadow-sm after:content-[''] after:absolute after:left-4 after:right-4 after:-bottom-1 after:h-0.5 after:rounded-full after:bg-blue-500";
  const linkIdle =
    "text-blue-600 hover:text-blue-800 hover:bg-blue-50";

  return (
    <header className="backdrop-blur bg-white/80 border-b border-blue-100 sticky top-0 z-50">
      <div className="mx-auto max-w-7xl px-4 md:px-6">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <span className="bg-gradient-to-br from-blue-600 to-blue-500 text-white rounded-xl px-3 py-1 font-extrabold text-lg shadow-sm select-none">
              TP
            </span>
            <div className="flex flex-col leading-tight">
              <h1 className="text-xl md:text-2xl font-extrabold tracking-tight text-blue-800">
                TimePlanner
              </h1>
              <span className="hidden md:block text-xs text-blue-500/80 font-medium">
                Plan. Track. Improve.
              </span>
            </div>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 rounded-lg text-blue-700 hover:bg-blue-100"
            onClick={() => setNavOpen((v) => !v)}
            aria-label="Open navigation"
          >
            <Menu size={24} />
          </button>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1">
            <NavLink
              to="/tasks"
              className={({ isActive }) =>
                `${linkBase} ${isActive ? linkActive : linkIdle}`
              }
            >
              Tasks
            </NavLink>
            <NavLink
              to="/plans"
              className={({ isActive }) =>
                `${linkBase} ${isActive ? linkActive : linkIdle}`
              }
            >
              Plans
            </NavLink>
            <NavLink
              to="/date-analytics"
              className={({ isActive }) =>
                `${linkBase} ${isActive ? linkActive : linkIdle}`
              }
            >
              Date Analytics
            </NavLink>
            <NavLink
              to="/task-analytics"
              className={({ isActive }) =>
                `${linkBase} ${isActive ? linkActive : linkIdle}`
              }
            >
              Task Analytics
            </NavLink>

            <div className="mx-2 h-6 w-px bg-blue-100" />

            <button
              onClick={handleLogout}
              className="flex items-center gap-2 bg-red-50 hover:bg-red-100 text-red-600 hover:text-red-800 px-4 py-2 rounded-lg font-semibold transition-colors shadow-sm"
              title="Logout"
            >
              <LogOut size={18} /> Logout
            </button>
          </nav>
        </div>
      </div>

      {/* Mobile drawer */}
      {navOpen && (
        <div className="md:hidden border-t border-blue-100 bg-white/95 backdrop-blur">
          <nav className="max-w-7xl mx-auto px-4 py-3 flex flex-col gap-2">
            <NavLink
              to="/tasks"
              className={({ isActive }) =>
                `${linkBase} ${isActive ? "bg-blue-100 text-blue-900" : "text-blue-700 hover:bg-blue-50"}`
              }
              onClick={() => setNavOpen(false)}
            >
              Tasks
            </NavLink>
            <NavLink
              to="/plans"
              className={({ isActive }) =>
                `${linkBase} ${isActive ? "bg-blue-100 text-blue-900" : "text-blue-700 hover:bg-blue-50"}`
              }
              onClick={() => setNavOpen(false)}
            >
              Plans
            </NavLink>
            <NavLink
              to="/date-analytics"
              className={({ isActive }) =>
                `${linkBase} ${isActive ? "bg-blue-100 text-blue-900" : "text-blue-700 hover:bg-blue-50"}`
              }
              onClick={() => setNavOpen(false)}
            >
              Date Analytics
            </NavLink>
            <NavLink
              to="/task-analytics"
              className={({ isActive }) =>
                `${linkBase} ${isActive ? "bg-blue-100 text-blue-900" : "text-blue-700 hover:bg-blue-50"}`
              }
              onClick={() => setNavOpen(false)}
            >
              Task Analytics
            </NavLink>

            <button
              onClick={() => {
                setNavOpen(false);
                handleLogout();
              }}
              className="mt-1 flex items-center gap-2 bg-red-50 hover:bg-red-100 text-red-600 hover:text-red-800 px-4 py-2 rounded-lg font-semibold transition-colors shadow-sm"
              title="Logout"
            >
              <LogOut size={18} /> Logout
            </button>
          </nav>
        </div>
      )}
    </header>
  );
}
