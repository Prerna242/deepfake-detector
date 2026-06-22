
export default function ResultCard({ result }) {
  const isFake = result.label === "FAKE";

  const badgeClasses = isFake
    ? "bg-red-100 text-red-700 border-red-200"
    : "bg-green-100 text-green-700 border-green-200";

  const barClasses = isFake
    ? "bg-gradient-to-r from-red-500 to-rose-500"
    : "bg-gradient-to-r from-green-500 to-emerald-500";

  return (
    <section className="overflow-hidden rounded-3xl border border-slate-100 bg-white p-8 shadow-2xl">

      <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">

        <div>
          <div className="flex items-center gap-4">

            <div className="text-5xl">
              {isFake ? "🚨" : "✅"}
            </div>

            <div>
              <h2 className="text-3xl font-bold text-slate-900">
                {isFake
                  ? "Potential Deepfake Detected"
                  : "Authentic Image"}
              </h2>

              <p className="mt-1 text-slate-500">
                {result.filename}
              </p>
            </div>

          </div>
        </div>

        <span
          className={`rounded-full border px-5 py-2 text-sm font-bold ${badgeClasses}`}
        >
          {result.label}
        </span>

      </div>

      <div className="mt-8">

        <div className="mb-2 flex items-center justify-between">

          <span className="font-medium text-slate-600">
            Confidence Score
          </span>

          <span className="text-lg font-bold text-slate-900">
            {result.confidence}%
          </span>

        </div>

        <div className="h-4 w-full overflow-hidden rounded-full bg-slate-200">

          <div
            className={`h-full rounded-full transition-all duration-1000 ${barClasses}`}
            style={{
              width: `${result.confidence}%`,
            }}
          />

        </div>

      </div>

      <div className="mt-8 grid gap-4 md:grid-cols-3">

        <div className="rounded-2xl bg-purple-50 p-5">
          <div className="text-2xl">🧠</div>

          <p className="mt-2 text-xs uppercase text-slate-500">
            Detection Engine
          </p>

          <h3 className="mt-2 font-bold text-slate-800">
            Deep Learning
          </h3>
        </div>

        <div className="rounded-2xl bg-blue-50 p-5">
          <div className="text-2xl">⚙️</div>

          <p className="mt-2 text-xs uppercase text-slate-500">
            Framework
          </p>

          <h3 className="mt-2 font-bold text-slate-800">
            TensorFlow
          </h3>
        </div>

        <div className="rounded-2xl bg-green-50 p-5">
          <div className="text-2xl">
            {isFake ? "🚨" : "✅"}
          </div>

          <p className="mt-2 text-xs uppercase text-slate-500">
            Status
          </p>

          <h3
            className={`mt-2 font-bold ${
              isFake
                ? "text-red-600"
                : "text-green-600"
            }`}
          >
            {isFake ? "Fake" : "Real"}
          </h3>
        </div>

      </div>

      <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-4">

        <p className="text-sm text-slate-600">
          Scan completed on{" "}
          <span className="font-semibold">
            {new Date(
              result.scanned_at
            ).toLocaleString()}
          </span>
        </p>

      </div>

    </section>
  );
}

