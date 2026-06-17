import { useEffect, useState } from "react";

import axiosInstance from "../api/axiosInstance";
import LoadingSpinner from "../components/LoadingSpinner";
import Navbar from "../components/Navbar";
import ScanHistoryTable from "../components/ScanHistoryTable";

export default function HistoryPage() {
  const [scans, setScans] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await axiosInstance.get("/api/history");

        setScans(response.data.scans);
        setTotal(response.data.total);
      } catch (requestError) {
        setError(
          requestError.response?.data?.detail ||
            "Failed to load history."
        );
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  const fakeCount = scans.filter(
    (scan) => scan.label === "FAKE"
  ).length;

  const realCount = scans.filter(
    (scan) => scan.label === "REAL"
  ).length;

  const avgConfidence =
    scans.length > 0
      ? (
          scans.reduce(
            (sum, scan) => sum + scan.confidence,
            0
          ) / scans.length
        ).toFixed(1)
      : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      <Navbar />

      <main className="mx-auto w-full max-w-6xl px-4 py-10 md:px-6">

        {/* Hero Section */}
        <header className="mb-8 rounded-3xl bg-gradient-to-r from-indigo-700 via-purple-700 to-pink-600 p-8 text-white shadow-xl">
          <h1 className="text-4xl font-bold">
            Detection Analytics
          </h1>

          <p className="mt-3 text-indigo-100">
            Monitor all deepfake detection activities,
            predictions and confidence scores.
          </p>
        </header>

        {/* Statistics Cards */}
        <div className="mb-8 grid gap-4 md:grid-cols-4">

          <div className="rounded-2xl bg-white p-5 shadow-lg">
            <p className="text-sm text-slate-500">
              Total Scans
            </p>

            <h3 className="mt-2 text-3xl font-bold text-slate-900">
              {total}
            </h3>
          </div>

          <div className="rounded-2xl bg-white p-5 shadow-lg">
            <p className="text-sm text-slate-500">
              Fake Images
            </p>

            <h3 className="mt-2 text-3xl font-bold text-red-600">
              {fakeCount}
            </h3>
          </div>

          <div className="rounded-2xl bg-white p-5 shadow-lg">
            <p className="text-sm text-slate-500">
              Real Images
            </p>

            <h3 className="mt-2 text-3xl font-bold text-green-600">
              {realCount}
            </h3>
          </div>

          <div className="rounded-2xl bg-white p-5 shadow-lg">
            <p className="text-sm text-slate-500">
              Avg Confidence
            </p>

            <h3 className="mt-2 text-3xl font-bold text-purple-600">
              {avgConfidence}%
            </h3>
          </div>

        </div>

        {/* Loading */}
        {loading && (
          <div className="flex justify-center py-16">
            <LoadingSpinner />
          </div>
        )}

        {/* Error */}
        {error && (
          <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </p>
        )}

        {/* Empty State */}
        {!loading && !error && scans.length === 0 && (
          <section className="rounded-3xl bg-white p-10 text-center shadow-lg">
            <h2 className="text-2xl font-semibold text-slate-800">
              No Scan History Found
            </h2>

            <p className="mt-2 text-slate-500">
              Run your first deepfake detection from the
              dashboard.
            </p>
          </section>
        )}

        {/* History Table */}
        {!loading && !error && scans.length > 0 && (
          <ScanHistoryTable scans={scans} />
        )}

      </main>
    </div>
  );
}