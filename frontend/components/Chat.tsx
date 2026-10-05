"use client";

import { useEffect, useRef, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL;

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
};

export default function Chat() {
  const [docs, setDocs] = useState<string[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  // Load the list of uploaded documents when the page opens
  async function loadDocs() {
    const res = await fetch(`${API}/documents`);
    const data = await res.json();
    setDocs(data.documents);
  }
  useEffect(() => {
    loadDocs();
  }, []);

  // Auto-scroll to the newest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Upload one or more PDFs, one at a time
  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files ?? []);
    if (!files.length) return;

    setUploading(true);
    for (const file of files) {
      setStatus(`Processing ${file.name}...`);
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API}/upload`, { method: "POST", body: form });
      if (!res.ok) {
        const err = await res.json();
        setStatus(`❌ ${file.name}: ${err.detail}`);
        setUploading(false);
        return;
      }
    }
    setStatus("✅ Upload complete");
    setUploading(false);
    e.target.value = ""; // allow re-selecting the same file
    loadDocs();
  }

  async function removeDoc(name: string) {
    await fetch(`${API}/documents/${encodeURIComponent(name)}`, {
      method: "DELETE",
    });
    loadDocs();
  }

  // Send a question; the user's message appears instantly
  async function sendMessage() {
    const question = input.trim();
    if (!question || loading) return;

    setMessages((m) => [...m, { role: "user", content: question }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: data.answer, sources: data.sources },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `⚠️ ${(err as Error).message}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto flex h-screen max-w-3xl flex-col gap-4 p-4">
      <h1 className="text-xl font-bold">📚 Multi-Doc PDF Chatbot</h1>

      {/* Upload + document list */}
      <section className="rounded-lg border p-3">
        <label className="inline-block cursor-pointer rounded bg-black px-3 py-2 text-sm text-white hover:bg-gray-800">
          {uploading ? "Uploading..." : "Upload PDFs"}
          <input
            type="file"
            accept="application/pdf"
            multiple
            hidden
            disabled={uploading}
            onChange={handleUpload}
          />
        </label>
        {status && <span className="ml-3 text-sm text-gray-600">{status}</span>}

        <ul className="mt-3 flex flex-wrap gap-2">
          {docs.map((d) => (
            <li
              key={d}
              className="flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 text-xs"
            >
              {d}
              <button
                onClick={() => removeDoc(d)}
                className="text-gray-400 hover:text-red-500"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>
      </section>

      {/* Chat messages */}
      <section className="flex-1 space-y-3 overflow-y-auto rounded-lg border p-3">
        {messages.length === 0 && (
          <p className="text-sm text-gray-400">
            Upload a PDF, then ask a question about it.
          </p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={m.role === "user" ? "text-right" : "text-left"}
          >
            <div
              className={`inline-block max-w-[85%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm ${
                m.role === "user" ? "bg-black text-white" : "bg-gray-100"
              }`}
            >
              {m.content}
            </div>
            {m.sources && m.sources.length > 0 && (
              <p className="mt-1 text-xs text-gray-500">
                Sources: {m.sources.join(", ")}
              </p>
            )}
          </div>
        ))}
        {loading && <p className="text-sm text-gray-400">Thinking...</p>}
        <div ref={bottomRef} />
      </section>

      {/* Input box */}
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask about your documents..."
          className="flex-1 rounded border px-3 py-2 text-sm outline-none focus:border-black"
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          className="rounded bg-black px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          Send
        </button>
      </div>
    </div>
  );
}
