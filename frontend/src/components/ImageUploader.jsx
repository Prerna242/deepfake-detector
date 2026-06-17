

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
   <div className="rounded-3xl border-2 border-dashed border-purple-500 bg-white p-10 text-center shadow-xl dark:border-purple-700 dark:bg-slate-800">

      <div className="mb-4 text-6xl">📤</div>

      <h2 className="text-3xl font-bold text-slate-800 dark:text-white">
  Drag & Drop Image
</h2>

      
      <p className="mt-2 text-slate-500 dark:text-slate-400">
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

      <div className="mt-10 grid gap-6 md:grid-cols-3">

        <div className="rounded-2xl bg-slate-50 p-6 shadow-lg transition-all duration-300 hover:-translate-y-1 hover:shadow-xl dark:bg-slate-700">
          <div className="text-4xl">🧠</div>
          <h3 className="mt-3 font-bold text-purple-600">
            AI Powered
          </h3>
          <p className="text-sm text-slate-500">
            Deep learning based detection.
          </p>
        </div>

        <div className="rounded-2xl text-slate-500 p-6 shadow-lg">
          <div className="text-4xl">⚡</div>
          <h3 className="mt-3 font-bold text-green-600">
            Fast & Reliable
          </h3>
          <p className="text-sm text-slate-500">
            Get results within seconds.
          </p>
        </div>

        <div className="rounded-2xl text-slate-500 p-6 shadow-lg">
          <div className="text-4xl">🔒</div>
          <h3 className="mt-3 font-bold text-pink-600">
            Privacy Focused
          </h3>
          <p className="text-sm text-slate-500">
            Uploaded images remain secure.
          </p>
        </div>

      </div>
       <footer className="bg-transparent text-slate-400 py-6 text-center">
  <h3>DeepDetect AI</h3>
  <p>CNN Based Deepfake Image Detection System</p>
</footer>
    </div>
  );
}

