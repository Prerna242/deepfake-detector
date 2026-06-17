export default function ScanHistoryTable({ scans }) {
  return (
    <div className="overflow-hidden rounded-3xl bg-white shadow-xl">
      <div className="border-b border-slate-200 px-6 py-4">
        <h2 className="text-xl font-bold text-slate-900">
          Detection Records
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Complete history of all deepfake detection scans.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-slate-50 text-slate-700">
              <th className="px-6 py-4 font-semibold">
                File Name
              </th>

              <th className="px-6 py-4 font-semibold">
                Result
              </th>

              <th className="px-6 py-4 font-semibold">
                Confidence
              </th>

              <th className="px-6 py-4 font-semibold">
                Scan Date
              </th>
            </tr>
          </thead>

          <tbody>
            {scans.map((scan) => {
              const isFake =
                scan.label === "FAKE";

              return (
                <tr
                  key={scan.scan_id}
                  className="border-b border-slate-100 transition hover:bg-slate-50"
                >
                  <td className="max-w-xs truncate px-6 py-4 font-medium text-slate-800">
                    {scan.filename}
                  </td>

                  <td className="px-6 py-4">
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-bold ${
                        isFake
                          ? "bg-red-100 text-red-700"
                          : "bg-green-100 text-green-700"
                      }`}
                    >
                      {isFake
                        ? "FAKE"
                        : "REAL"}
                    </span>
                  </td>

                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">

                      <div className="h-2 w-28 overflow-hidden rounded-full bg-slate-200">
                        <div
                          className={`h-full rounded-full ${
                            isFake
                              ? "bg-gradient-to-r from-red-500 to-rose-500"
                              : "bg-gradient-to-r from-green-500 to-emerald-500"
                          }`}
                          style={{
                            width: `${scan.confidence}%`,
                          }}
                        />
                      </div>

                      <span className="font-semibold text-slate-700">
                        {scan.confidence}%
                      </span>

                    </div>
                  </td>

                  <td className="px-6 py-4 text-slate-500">
                    {new Date(
                      scan.scanned_at
                    ).toLocaleString()}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}