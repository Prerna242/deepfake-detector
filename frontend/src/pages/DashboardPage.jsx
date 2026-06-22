import { useState } from "react";

import axiosInstance from "../api/axiosInstance";
import ImageUploader from "../components/ImageUploader";
import LoadingSpinner from "../components/LoadingSpinner";
import Navbar from "../components/Navbar";
import ResultCard from "../components/ResultCard";
import { useAuth } from "../hooks/useAuth";

export default function DashboardPage() {
  const { username } = useAuth();

  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileSelect = (file) => {
    if (!file) return;

    const allowedTypes = [
      "image/jpeg",
      "image/png",
      "image/webp",
    ];

    if (!allowedTypes.includes(file.type)) {
      setError("Please select a JPG, PNG, or WEBP image.");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError("File is too large. Maximum 5MB allowed.");
      return;
    }

    setError("");
    setResult(null);
    setSelectedFile(file);

    const reader = new FileReader();
    reader.onloadend = () => setPreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await axiosInstance.post(
        "/api/detect",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResult(response.data);
    } catch (requestError) {
      setError(
        requestError.response?.data?.detail ||
          "Detection failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError("");
  };

  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <Navbar />

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-10 md:px-6">

        {/* Hero Section */}
        <header className="mb-8 overflow-hidden rounded-3xl bg-gradient-to-r from-purple-700 via-violet-600 to-pink-500 p-10 text-white shadow-xl">

          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">

            <div>
              <h1 className="text-5xl font-bold">
                DeepDetect AI
              </h1>

              <p className="mt-4 text-xl text-purple-100">
                Deepfake Image Detection System
              </p>

              <p className="mt-2 text-purple-100">
                Detect manipulated images using TensorFlow
                and Deep Learning technology.
              </p>

              <div className="mt-6 flex flex-wrap gap-3">

                <span className="rounded-full bg-white/20 px-4 py-2 text-sm">
                  🧠 TensorFlow 
                </span>

                <span className="rounded-full bg-white/20 px-4 py-2 text-sm">
                  ⚡ Real-Time Analysis
                </span>

                <span className="rounded-full bg-white/20 px-4 py-2 text-sm">
                  🔒 Secure Upload
                </span>

                <span className="rounded-full bg-white/20 px-4 py-2 text-sm">
                  🎯 AI Powered
                </span>

              </div>
            </div>

            <div className="hidden md:block">
              <div className="h-24 w-24 rounded-2xl bg-white/10 backdrop-blur-sm"></div>
            </div>

          </div>

        </header>

        {/* Stats Cards */}
        <div className="mb-8 grid gap-6 md:grid-cols-4">

          <div className="rounded-2xl bg-white p-6 shadow-md">
            <p className="text-slate-500">
             Detection Engine
            </p>

            <h3 className="mt-2 text-3xl font-bold">
             Deep Learning

            </h3>
          </div>

          <div className="rounded-2xl bg-white p-6 shadow-md">
            <p className="text-slate-500">
              Accuracy
            </p>

            <h3 className="mt-2 text-3xl font-bold text-green-600">
              AI Powered
            </h3>
          </div>

          <div className="rounded-2xl bg-white p-6 shadow-md">
            <p className="text-slate-500">
              Processing
            </p>

            <h3 className="mt-2 text-3xl font-bold text-orange-500">
              {"< 2 sec"}
            </h3>
          </div>

          <div className="rounded-2xl bg-white p-6 shadow-md">
            <p className="text-slate-500">
              Security
            </p>

            <h3 className="mt-2 text-3xl font-bold text-purple-600">
              100%
            </h3>
          </div>

        </div>

        {!preview && (
          <ImageUploader
            onFileSelect={handleFileSelect}
          />
        )}

        {preview && (
          <section className="space-y-5">

            <div className="overflow-hidden rounded-3xl bg-white shadow-xl">
              <img
                src={preview}
                alt="Selected"
                className="max-h-[28rem] w-full bg-slate-100 object-contain"
              />
            </div>

            {!result && (
              <div className="flex flex-col gap-3 sm:flex-row">

                <button
                  className="rounded-xl bg-gradient-to-r from-purple-600 to-pink-500 px-6 py-3 font-semibold text-white shadow-lg transition hover:scale-105"
                  disabled={loading}
                  onClick={handleAnalyze}
                  type="button"
                >
                  {loading
                    ? "Analyzing..."
                    : "Analyze Image"}
                </button>

                <button
                  className="rounded-xl border border-slate-300 bg-white px-6 py-3 font-medium text-slate-700 transition hover:bg-slate-50"
                  onClick={handleReset}
                  type="button"
                >
                  Cancel
                </button>

              </div>
            )}

            {loading && (
              <div className="rounded-2xl bg-white p-4 shadow-lg">

                <div className="flex items-center gap-3 text-slate-600">
                  <LoadingSpinner />

                  <span>
                    Running AI analysis...
                  </span>
                </div>

              </div>
            )}

            {result && (
              <>
                <ResultCard result={result} />

                <button
                  className="rounded-xl border border-slate-300 bg-white px-6 py-3 font-medium text-slate-700 transition hover:bg-slate-50"
                  onClick={handleReset}
                  type="button"
                >
                  Analyze Another Image
                </button>
              </>
            )}

          </section>
        )}

        {error && (
          <p className="mt-4 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </p>
        )}

      </main>

      <footer className="mt-10 border-t bg-white py-6">

        <div className="mx-auto max-w-6xl text-center">

          <p className="font-semibold text-slate-700">
            © 2026 DeepDetect AI
          </p>

          <p className="text-sm text-slate-500">
            TensorFlow CNN Deepfake Detection
          </p>

        </div>

      </footer>

    </div>
  );
}
