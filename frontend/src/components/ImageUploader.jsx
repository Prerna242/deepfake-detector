import { useRef } from "react";

export default function ImageUploader({ onFileSelect }) {
  const fileInputRef = useRef(null);

  const handleChange = (event) => {
    const file = event.target.files?.[0];

    if (file) {
      onFileSelect(file);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="rounded-3xl border-2 border-dashed border-purple-300 bg-white p-14 text-center shadow-lg transition-all duration-300 hover:shadow-xl">

      <div className="mb-6 text-7xl">
        <span className="inline-block rounded-full bg-purple-100 p-5">
          📤
        </span>
      </div>

      <h2 className="text-3xl font-bold text-slate-800">
        Upload Image
      </h2>

      <p className="mt-2 text-slate-500">
        Upload an image for AI-powered deepfake analysis
      </p>

      <p className="mt-1 text-xs text-slate-400">
        JPG • PNG • WEBP • Max 5MB
      </p>

      <button
        className="mt-6 rounded-xl bg-gradient-to-r from-purple-600 to-pink-500 px-8 py-4 font-semibold text-white shadow-lg transition hover:scale-105"
        onClick={handleClick}
        type="button"
      >
        📂 Select Image
      </button>

      <p className="mt-4 text-sm text-slate-400">
        Your files are processed securely and never stored permanently.
      </p>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleChange}
        className="hidden"
      />

      <div className="mt-12 grid gap-6 md:grid-cols-3">

        <div className="rounded-2xl bg-purple-50 p-6 shadow-md transition hover:-translate-y-1 hover:shadow-lg">
          <div className="text-4xl">🧠</div>

          <h3 className="mt-3 font-bold text-purple-600">
            AI Powered
          </h3>

          <p className="text-sm text-slate-500">
            Deep learning based detection.
          </p>
        </div>

        <div className="rounded-2xl bg-green-50 p-6 shadow-md transition hover:-translate-y-1 hover:shadow-lg">
          <div className="text-4xl">⚡</div>

          <h3 className="mt-3 font-bold text-green-600">
            Fast & Reliable
          </h3>

          <p className="text-sm text-slate-500">
            Get results within seconds.
          </p>
        </div>

        <div className="rounded-2xl bg-pink-50 p-6 shadow-md transition hover:-translate-y-1 hover:shadow-lg">
          <div className="text-4xl">🔒</div>

          <h3 className="mt-3 font-bold text-pink-600">
            Privacy Focused
          </h3>

          <p className="text-sm text-slate-500">
            Uploaded images remain secure.
          </p>
        </div>

      </div>

    </div>
  );
}
