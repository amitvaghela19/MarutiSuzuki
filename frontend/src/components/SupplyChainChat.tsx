import { useCallback, useEffect, useRef, useState } from "react";
import {
  fetchChatStatus,
  streamChat,
  type ChatMessage,
  type ChatStatus,
  type Snapshot,
} from "../api/client";

type Props = {
  snapshot: Snapshot | null;
};

const STARTERS = [
  "What are the top supply risks right now?",
  "Explain the MRF / Gulf tyre situation.",
  "Which scenario has the highest stockout risk?",
  "Summarize today's ops signals.",
];

const CHAT_SIZE_STORAGE_KEY = "msil-chat-panel-size";
const CHAT_SIZE_DEFAULT = { width: 420, height: 560 };
const CHAT_SIZE_MIN = { width: 300, height: 320 };

function loadChatPanelSize(): { width: number; height: number } {
  try {
    const raw = localStorage.getItem(CHAT_SIZE_STORAGE_KEY);
    if (!raw) return CHAT_SIZE_DEFAULT;
    const parsed = JSON.parse(raw) as { width?: number; height?: number };
    if (
      typeof parsed.width === "number" &&
      typeof parsed.height === "number" &&
      parsed.width >= CHAT_SIZE_MIN.width &&
      parsed.height >= CHAT_SIZE_MIN.height
    ) {
      return { width: parsed.width, height: parsed.height };
    }
  } catch {
    /* ignore */
  }
  return CHAT_SIZE_DEFAULT;
}

function clampChatSize(width: number, height: number) {
  const maxW = Math.min(800, window.innerWidth - 32);
  const maxH = Math.min(900, window.innerHeight - 100);
  return {
    width: Math.round(Math.min(maxW, Math.max(CHAT_SIZE_MIN.width, width))),
    height: Math.round(Math.min(maxH, Math.max(CHAT_SIZE_MIN.height, height))),
  };
}

export default function SupplyChainChat({ snapshot }: Props) {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<ChatStatus | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [panelSize, setPanelSize] = useState(loadChatPanelSize);
  const [resizing, setResizing] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  const refreshStatus = useCallback(() => {
    fetchChatStatus()
      .then(setStatus)
      .catch((e) =>
        setStatus({
          available: false,
          base_url: "",
          configured_model: "deepseek-r1:latest",
          model_ready: false,
          models: [],
          error: e instanceof Error ? e.message : "Cannot reach API",
        })
      );
  }, []);

  useEffect(() => {
    if (open) refreshStatus();
  }, [open, refreshStatus]);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const persistPanelSize = useCallback((size: { width: number; height: number }) => {
    try {
      localStorage.setItem(CHAT_SIZE_STORAGE_KEY, JSON.stringify(size));
    } catch {
      /* ignore */
    }
  }, []);

  const startResize = useCallback((e: React.PointerEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const startX = e.clientX;
    const startY = e.clientY;
    const startSize = panelSize;
    setResizing(true);

    const onMove = (ev: PointerEvent) => {
      setPanelSize(
        clampChatSize(
          startSize.width + (startX - ev.clientX),
          startSize.height + (startY - ev.clientY)
        )
      );
    };

    const onUp = (ev: PointerEvent) => {
      setResizing(false);
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
      const finalSize = clampChatSize(
        startSize.width + (startX - ev.clientX),
        startSize.height + (startY - ev.clientY)
      );
      setPanelSize(finalSize);
      persistPanelSize(finalSize);
    };

    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
  }, [panelSize, persistPanelSize]);

  const resetPanelSize = () => {
    setPanelSize(CHAT_SIZE_DEFAULT);
    persistPanelSize(CHAT_SIZE_DEFAULT);
  };

  const send = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;
    setError(null);
    const userMsg: ChatMessage = { role: "user", content: trimmed };
    const next = [...messages, userMsg];
    setMessages(next);
    setInput("");
    setLoading(true);

    const assistantIdx = next.length;
    setMessages([...next, { role: "assistant", content: "" }]);

    try {
      await streamChat(
        next,
        (content, done) => {
          setMessages((prev) => {
            const copy = [...prev];
            copy[assistantIdx] = { role: "assistant", content };
            return copy;
          });
          if (done) setLoading(false);
        },
        { includeSnapshot: true }
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "Chat failed");
      setMessages(next);
      setLoading(false);
    }
  };

  const ready = status?.available && status?.model_ready;

  return (
    <>
      <button
        type="button"
        className="chat-fab"
        aria-expanded={open}
        aria-label={open ? "Close supply chain assistant" : "Open supply chain assistant"}
        onClick={() => setOpen((v) => !v)}
      >
        {open ? "✕" : "💬"}
      </button>

      {open && (
        <div
          className={`chat-panel glass${resizing ? " chat-panel--resizing" : ""}`}
          role="dialog"
          aria-label="Supply chain assistant"
          style={{ width: panelSize.width, height: panelSize.height }}
        >
          <button
            type="button"
            className="chat-resize-handle"
            aria-label="Resize chat panel"
            title="Drag to resize"
            onPointerDown={startResize}
          />
          <header className="chat-panel-head">
            <div>
              <strong>Supply chain assistant</strong>
              <p className="muted small">
                Local · {status?.configured_model ?? "deepseek-r1:latest"} · free via Ollama
              </p>
            </div>
            <div className="chat-panel-actions">
              <button
                type="button"
                className="btn-ghost small"
                onClick={resetPanelSize}
                title="Reset panel size"
              >
                Reset size
              </button>
              <button type="button" className="btn-ghost small" onClick={refreshStatus}>
                Refresh
              </button>
            </div>
          </header>

          {!ready && (
            <div className="chat-status-banner warn">
              {status?.error ? (
                <p>
                  Ollama not reachable. Start the Ollama app or run{" "}
                  <code>ollama serve</code>, then ensure{" "}
                  <code>{status.configured_model}</code> is pulled.
                </p>
              ) : status?.hint ? (
                <p>{status.hint}</p>
              ) : (
                <p>Checking Ollama…</p>
              )}
            </div>
          )}

          {snapshot ? (
            <p className="chat-context-note muted small">
              Using analysis run <code>{snapshot.run_id.slice(0, 8)}</code>
            </p>
          ) : (
            <p className="chat-context-note muted small">
              No snapshot yet — run analysis for live risk context.
            </p>
          )}

          <div className="chat-messages" ref={listRef}>
            {messages.length === 0 && (
              <div className="chat-empty">
                <p>Ask about risks, parts, scenarios, or disruption history.</p>
                <div className="chat-starters">
                  {STARTERS.map((s) => (
                    <button
                      key={s}
                      type="button"
                      className="btn-ghost"
                      disabled={!ready || loading}
                      onClick={() => send(s)}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((m, i) => (
              <div
                key={`${i}-${m.role}`}
                className={`chat-bubble chat-bubble--${m.role}`}
              >
                {m.content || (loading && m.role === "assistant" ? "Thinking…" : "")}
              </div>
            ))}
          </div>

          {error && <p className="chat-error">{error}</p>}

          <form
            className="chat-compose"
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
          >
            <textarea
              rows={2}
              placeholder={
                ready
                  ? "Ask about MRF/Gulf tyres, allocations, stockout scenarios, suppliers…"
                  : "Start Ollama to chat…"
              }
              value={input}
              disabled={!ready || loading}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send(input);
                }
              }}
            />
            <button type="submit" className="btn-primary" disabled={!ready || loading}>
              {loading ? "…" : "Send"}
            </button>
          </form>
        </div>
      )}
    </>
  );
}
