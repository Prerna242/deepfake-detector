import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";

import axiosInstance from "../api/axiosInstance";

export default function RegisterPage() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();
  const navigate = useNavigate();

  const [serverError, setServerError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const onSubmit = async (data) => {
    setLoading(true);
    setServerError("");

    try {
      await axiosInstance.post("/api/auth/register", {
        username: data.username,
        email: data.email,
        password: data.password,
      });
      setSuccess(true);
      setTimeout(() => navigate("/login"), 1600);
    } catch (error) {
      setServerError(error.response?.data?.detail || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <main className="flex min-h-screen items-center justify-center px-4 py-10">
        <section className="card-panel w-full max-w-md p-8 text-center">
          <h1 className="text-2xl font-bold text-emerald-700">Account Created</h1>
          <p className="mt-2 text-slate-600">Redirecting you to login...</p>
        </section>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-10">
      <section className="card-panel w-full max-w-md p-8">
        <h1 className="text-3xl font-bold text-slate-900">Create Account</h1>
        <p className="mt-1 text-slate-600">Start scanning images with DeepDetect.</p>

        <form className="mt-7 space-y-5" onSubmit={handleSubmit(onSubmit)}>
          <div>
            <label className="mb-1 block text-sm text-slate-700" htmlFor="username">
              Username
            </label>
            <input
              id="username"
              className="w-full rounded-xl border border-amber-200 bg-white px-4 py-2.5 outline-none transition focus:border-teal-500"
              {...register("username", {
                required: "Username is required",
                minLength: { value: 3, message: "Minimum 3 characters" },
              })}
            />
            {errors.username && (
              <p className="mt-1 text-xs text-rose-600">{errors.username.message}</p>
            )}
          </div>

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
              {...register("password", {
                required: "Password is required",
                minLength: { value: 6, message: "Minimum 6 characters" },
              })}
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
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-600">
          Already have an account?{" "}
          <Link className="font-semibold text-orange-700 hover:underline" to="/login">
            Sign in
          </Link>
        </p>
      </section>
    </main>
  );
}
