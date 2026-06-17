import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Navbar() {
  const { username, logout } = useAuth();

  const [darkMode, setDarkMode] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const savedTheme = localStorage.getItem("theme");

    if (savedTheme === "dark") {
      document.documentElement.classList.add("dark");
      setDarkMode(true);
    }
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const toggleTheme = () => {
    const root = document.documentElement;

    if (darkMode) {
      root.classList.remove("dark");
      localStorage.setItem("theme", "light");
    } else {
      root.classList.add("dark");
      localStorage.setItem("theme", "dark");
    }

    setDarkMode(!darkMode);
  };

  const isActive = (path) => {
    return location.pathname === path
      ? "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300"
      : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800";
  };

  return (
    <nav className="sticky top-0 z-50 border-b border-slate-200 bg-white/80 backdrop-blur-lg dark:border-slate-800 dark:bg-slate-900/90">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 md:px-6">

        {/* Logo */}
        <Link
          to="/dashboard"
          className="flex items-center gap-3"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-purple-600 to-pink-500 font-bold text-white">
            AI
          </div>

          <div>
            <h1 className="text-lg font-bold text-slate-900 dark:text-white">
              DeepDetect
            </h1>

            <p className="text-xs text-slate-500 dark:text-slate-400">
              Deepfake Detection
            </p>
          </div>
        </Link>

        {/* Navigation */}
        <div className="flex items-center gap-2">
          <Link
            to="/dashboard"
            className={`rounded-xl px-4 py-2 text-sm font-medium transition ${isActive(
              "/dashboard"
            )}`}
          >
            Detect
          </Link>

          <Link
            to="/history"
            className={`rounded-xl px-4 py-2 text-sm font-medium transition ${isActive(
              "/history"
            )}`}
          >
            History
          </Link>
        </div>

        {/* User Section */}
        <div className="flex items-center gap-3">

          <div className="hidden items-center gap-2 md:flex">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 font-semibold text-white">
              {username?.charAt(0)?.toUpperCase() || "U"}
            </div>

            <div>
              <p className="text-sm font-medium text-slate-800 dark:text-white">
                {username}
              </p>

              <p className="text-xs text-slate-500 dark:text-slate-400">
                User
              </p>
            </div>
          </div>

          {/* Dark Mode Toggle */}
          <button
            onClick={toggleTheme}
            type="button"
            className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
          >
            {darkMode ? "☀️" : "🌙"}
          </button>

          {/* Logout */}
          <button
            onClick={handleLogout}
            type="button"
            className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700 dark:bg-purple-600 dark:hover:bg-purple-700"
          >
            Logout
          </button>

        </div>

      </div>
    </nav>
  );
}