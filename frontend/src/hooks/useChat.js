import { useState, useRef, useEffect, useCallback } from "react";
import { API } from "../constants";

/**
 * Manages chat messages, streaming SSE from the backend, and textarea auto-resize.
 *
 * @param {{ profile: import('../utils/normalizeExtracted').UserProfile }} opts
 */
export default function useChat({ profile }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  }, [input]);

  const pushMsg = useCallback(
    (msg) =>
      setMessages((prev) => [
        ...prev,
        { id: Date.now() + Math.random(), ...msg },
      ]),
    [],
  );

  const appendAssistantText = useCallback((text) => {
    setMessages((prev) => {
      const copy = [...prev];
      for (let i = copy.length - 1; i >= 0; i--) {
        if (copy[i].type === "assistant") {
          copy[i] = { ...copy[i], text: copy[i].text + text };
          return copy;
        }
      }
      return [...copy, { id: Date.now(), type: "assistant", text }];
    });
  }, []);

  const resolveToolStart = useCallback((tool, result) => {
    setMessages((prev) => {
      const copy = [...prev];
      for (let i = copy.length - 1; i >= 0; i--) {
        if (copy[i].type === "tool_start" && copy[i].tool === tool) {
          copy[i] = { ...copy[i], type: "tool_result", result };
          return copy;
        }
      }
      return [...copy, { id: Date.now(), type: "tool_result", tool, result }];
    });
  }, []);

  const sendMessage = useCallback(
    async (text) => {
      if (!text.trim() || loading) return;
      setInput("");
      setLoading(true);

      const history = messages
        .filter((m) => m.type === "user" || m.type === "assistant")
        .map((m) => ({
          role: m.type === "user" ? "user" : "assistant",
          content: m.text,
        }));

      pushMsg({ type: "user", text });

      try {
        const res = await fetch(`${API}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            messages: [...history, { role: "user", content: text }],
            profile,
          }),
        });

        if (!res.ok) throw new Error(`Server error: ${res.status}`);

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let assistantStarted = false;

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop();

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            try {
              const event = JSON.parse(line.slice(6));
              if (event.type === "tool_start") {
                pushMsg({
                  type: "tool_start",
                  tool: event.tool,
                  input: event.input,
                });
              } else if (event.type === "tool_result") {
                resolveToolStart(event.tool, event.result);
              } else if (event.type === "text" && event.content) {
                if (!assistantStarted) {
                  pushMsg({ type: "assistant", text: event.content });
                  assistantStarted = true;
                } else {
                  appendAssistantText(event.content);
                }
              }
            } catch {
              /* malformed SSE line — skip */
            }
          }
        }
      } catch (err) {
        pushMsg({
          type: "assistant",
          text: `Error: ${err.message}. Make sure the backend is running on port 8000.`,
        });
      } finally {
        setLoading(false);
      }
    },
    [
      loading,
      messages,
      profile,
      pushMsg,
      appendAssistantText,
      resolveToolStart,
    ],
  );

  const handleKey = useCallback(
    (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage(input);
      }
    },
    [input, sendMessage],
  );

  const clearMessages = useCallback(() => setMessages([]), []);

  return {
    messages,
    input,
    setInput,
    loading,
    bottomRef,
    textareaRef,
    sendMessage,
    handleKey,
    pushMsg,
    clearMessages,
  };
}
