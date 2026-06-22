import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function Navbar() {
  const { username, logout } = useAuth();

  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isActive = (path) => {
    return location.pathname === path
      ? "bg-purple-100 text-purple-700"
      : "text-slate-600 hover:bg-slate-100";
  };

  return (
    <nav className="sticky top-0 z-50 border-b border-slate-200 bg-white shadow-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 md:px-6">

        {/* Logo */}
        <Link
          to="/dashboard"
          className="flex items-center gap-3"
        >
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-r from-purple-600 to-pink-500 font-bold text-white shadow-md">
            AI
          </div>

          <div>
            <h1 className="text-lg font-bold text-slate-900">
              DeepDetect AI
            </h1>

            <p className="text-xs text-slate-500">
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

        {/* User */}
        <div className="flex items-center gap-4">

          <div className="hidden items-center gap-2 md:flex">

            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 font-semibold text-white">
              {username?.charAt(0)?.toUpperCase() || "U"}
            </div>

            <div>
              <p className="text-sm font-medium text-slate-800">
                {username}
              </p>

              <p className="text-xs text-slate-500">
                User
              </p>
            </div>

          </div>

          <button
            onClick={handleLogout}
            type="button"
            className="rounded-xl bg-gradient-to-r from-purple-600 to-pink-500 px-4 py-2 text-sm font-medium text-white shadow-md transition hover:scale-105"
          >
            Logout
          </button>

        </div>

      </div>
    </nav>
  );
}
