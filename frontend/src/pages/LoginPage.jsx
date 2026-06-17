import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";

import axiosInstance from "../api/axiosInstance";
import { useAuth } from "../hooks/useAuth";

export default function LoginPage() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();
  const { login } = useAuth();
  const navigate = useNavigate();

  const [serverError, setServerError] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (data) => {
    setLoading(true);
    setServerError("");

    try {
      const response = await axiosInstance.post("/api/auth/login", {
        email: data.email,
        password: data.password,
      });
      login(response.data.access_token, response.data.username);
      navigate("/dashboard");
    } catch (error) {
      setServerError(error.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <section className="card-panel w-full max-w-md p-8">
        <h1 className="text-3xl font-bold text-slate-900">Sign In</h1>
        <p className="mt-1 text-slate-600">Access your deepfake detection workspace.</p>

        <form className="mt-7 space-y-5" onSubmit={handleSubmit(onSubmit)}>
          <div>
            <label className="mb-1 block text-sm text-slate-700" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              className="w-full rounded-xl border border-amber-200 bg-white px-4 py-2.5 outline-none transition focus:border-teal-500"
              {...register("email", { required: "Email is required" })}
            />
            {errors.email && <p className="mt-1 text-xs text-rose-600">{errors.email.message}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm text-slate-700" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="w-full rounded-xl border border-amber-200 bg-white px-4 py-2.5 outline-none transition focus:border-teal-500"
              {...register("password", { required: "Password is required" })}
            />
            {errors.password && (
              <p className="mt-1 text-xs text-rose-600">{errors.password.message}</p>
            )}
          </div>

          {serverError && (
            <p className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-2 text-sm text-rose-700">
              {serverError}
            </p>
          )}

          <button
            className="w-full rounded-xl bg-teal-700 py-3 font-semibold text-white transition hover:bg-teal-600 disabled:opacity-60"
            disabled={loading}
            type="submit"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-600">
          No account yet?{" "}
          <Link className="font-semibold text-orange-700 hover:underline" to="/register">
            Register
          </Link>
        </p>
      </section>
    </main>
  );
}
