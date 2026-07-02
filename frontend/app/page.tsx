"use client";

import { useState } from "react";

type GenerateResponse = {
  platform: string;
  tone: string;
  post: string;
};

export default function Home() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleGenerate() {
    setError(null);
    setResult(null);

    if (!text.trim()) {
      setError("Please enter a topic or announcement first.");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        const detail = data?.detail;
        const message = typeof detail === "string" ? detail : detail?.error;
        throw new Error(message || "The backend could not generate a post.");
      }

      setResult(data as GenerateResponse);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong while generating the post.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <section className="mx-auto flex w-full max-w-3xl flex-col gap-8">
        <header className="space-y-3">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-teal-300">Digital FTE Agent</p>
          <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">Generate a platform-ready social post</h1>
          <p className="max-w-2xl text-base leading-7 text-slate-300">
            Enter a topic or announcement. The backend analyzes the best platform and tone, then drafts a post through the existing agent API.
          </p>
        </header>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 shadow-2xl shadow-slate-950/40">
          <label htmlFor="topic" className="mb-3 block text-sm font-medium text-slate-200">
            Topic or announcement
          </label>
          <textarea
            id="topic"
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder="Example: We launched an AI assistant that turns meeting notes into social posts for small teams."
            className="min-h-40 w-full resize-y rounded-xl border border-slate-700 bg-slate-950/80 p-4 text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-teal-400 focus:ring-2 focus:ring-teal-400/20"
          />
          <button
            type="button"
            onClick={handleGenerate}
            disabled={isLoading}
            className="mt-4 flex w-full items-center justify-center rounded-xl bg-teal-400 px-5 py-3 font-semibold text-slate-950 transition hover:bg-teal-300 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
          >
            {isLoading ? (
              <span className="flex items-center gap-3">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-950/30 border-t-slate-950" />
                Generating...
              </span>
            ) : (
              "Generate Post"
            )}
          </button>
        </div>

        {error ? (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">{error}</div>
        ) : null}

        {result ? (
          <section className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900/70 p-5 shadow-2xl shadow-slate-950/30">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
                <p className="text-sm text-slate-400">Platform</p>
                <p className="mt-1 text-2xl font-semibold text-teal-300">{result.platform}</p>
              </div>
              <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4">
                <p className="text-sm text-slate-400">Tone</p>
                <p className="mt-1 text-2xl font-semibold text-blue-300">{result.tone}</p>
              </div>
            </div>

            <article className="rounded-xl border border-slate-800 bg-slate-950/70 p-5">
              <h2 className="mb-3 text-lg font-semibold text-white">Generated Post</h2>
              <p className="whitespace-pre-wrap leading-7 text-slate-200">{result.post}</p>
            </article>
          </section>
        ) : null}
      </section>
    </main>
  );
}
