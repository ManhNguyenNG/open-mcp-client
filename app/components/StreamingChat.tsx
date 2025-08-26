"use client";

import React, { useRef, useState } from "react";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

// Spinner component
function Spinner() {
  return (
    <div className="flex items-center justify-center">
      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      <span className="ml-2 text-sm text-gray-600">Génération en cours...</span>
    </div>
  );
}

export default function StreamingChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  async function streamAnswer(userText: string, onDelta: (t: string) => void) {
    const controller = new AbortController();
    abortRef.current = controller;

    const res = await fetch("/api/copilotkit/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userText }),
      signal: controller.signal,
    });

    if (!res.body) return;

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const raw = line.slice(6).trim();
        if (!raw || raw === "[DONE]") continue;
        try {
          const evt = JSON.parse(raw);
          const delta =
            evt?.data?.delta ?? evt?.data?.content ?? evt?.delta ?? evt?.content ?? "";
          if (delta) onDelta(String(delta));
        } catch {
          // ignore parse errors on keep-alive comments, etc.
        }
      }
    }
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input,
    };

    const assistantId = `assistant-${Date.now()}`;
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setInput("");
    setLoading(true);

    try {
      await streamAnswer(userMessage.content, (delta) => {
        setMessages((prev) =>
          prev.map((m) => (m.id === assistantId ? { ...m, content: m.content + delta } : m))
        );
      });
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: m.content || "Désolé, une erreur est survenue pendant le streaming." }
            : m
        )
      );
    } finally {
      setLoading(false);
      abortRef.current = null;
    }
  }

  function onStop() {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((m) => (
          <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm ${
                m.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}
        
        {/* Spinner visible pendant le loading */}
        {loading && (
          <div className="flex justify-start">
            <div className="max-w-[80%] bg-gray-100 text-gray-900 rounded-lg px-3 py-2">
              <Spinner />
            </div>
          </div>
        )}
      </div>

      <form onSubmit={onSubmit} className="border-t p-3 flex gap-2 items-center">
        <input
          className="flex-1 border rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Type a message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button
          type="submit"
          className="bg-blue-600 text-white text-sm rounded-md px-3 py-2 disabled:opacity-50 flex items-center gap-2"
          disabled={loading || !input.trim()}
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Envoi...
            </>
          ) : (
            "Send"
          )}
        </button>
        <button
          type="button"
          onClick={onStop}
          className="bg-gray-200 text-gray-800 text-sm rounded-md px-3 py-2 disabled:opacity-50"
          disabled={!loading}
        >
          Stop
        </button>
      </form>
    </div>
  );
}
