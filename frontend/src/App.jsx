import { useState, useRef, useEffect } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const AGENTS = {
  "Travel Coordinator":   { icon: "✦", color: "#e8c87a" },
  "Destination Expert":   { icon: "🗺", color: "#7ab8e8" },
  "Travel Meteorologist": { icon: "☁", color: "#86d8c0" },
  "Language Expert":      { icon: "語", color: "#e87ab5" },
  System:                 { icon: "⚙", color: "#aaaaaa" },
};

const EVENT_LABELS = {
  agent_start:    "INITIATED",
  agent_thinking: "THINKING",
  tool_call:      "TOOL CALL",
  agent_done:     "COMPLETE",
  final_result:   "RESULT",
  error:          "ERROR",
};

function AgentBadge({ name }) {
  const cfg = AGENTS[name] || { icon: "◆", color: "#aaa" };
  return (
    <span style={{ color: cfg.color, fontFamily: "monospace", fontSize: 12, fontWeight: 700, letterSpacing: 1 }}>
      {cfg.icon} {name.toUpperCase()}
    </span>
  );
}

function EventRow({ ev, idx }) {
  const cfg = AGENTS[ev.agent] || { icon: "◆", color: "#aaa" };
  const label = EVENT_LABELS[ev.event] || ev.event.toUpperCase();
  const isResult = ev.event === "final_result";
  const isError = ev.event === "error";

  return (
    <div style={{
      display: "flex", gap: 12, padding: "10px 16px",
      borderBottom: "1px solid rgba(255,255,255,0.04)",
      background: isResult ? "rgba(232,200,122,0.06)" : isError ? "rgba(255,80,80,0.06)" : "transparent",
      animation: `fadeSlide 0.35s ease ${idx * 0.04}s both`,
    }}>
      <div style={{ paddingTop: 3, flexShrink: 0 }}>
        <div style={{ width: 8, height: 8, borderRadius: "50%", background: cfg.color, boxShadow: `0 0 8px ${cfg.color}88` }} />
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 4, flexWrap: "wrap" }}>
          <AgentBadge name={ev.agent} />
          <span style={{
            fontSize: 10, letterSpacing: 2, fontWeight: 700,
            color: isResult ? "#e8c87a" : isError ? "#ff6b6b" : "rgba(255,255,255,0.3)",
            fontFamily: "monospace",
          }}>
            {label}
          </span>
          {ev.data?.tool && (
            <span style={{ fontSize: 10, color: "rgba(255,255,255,0.25)", fontFamily: "monospace" }}>
              → {ev.data.tool}
            </span>
          )}
        </div>
        {isResult ? (
          <ResultCard text={ev.message} />
        ) : (
          <p style={{ margin: 0, fontSize: 13, color: "rgba(255,255,255,0.65)", lineHeight: 1.6 }}>
            {ev.message}
          </p>
        )}
        {ev.data?.highlights && (
          <div style={{ marginTop: 6, display: "flex", flexWrap: "wrap", gap: 6 }}>
            {ev.data.highlights.map(h => (
              <span key={h} style={{ fontSize: 11, padding: "2px 8px", borderRadius: 4, background: "rgba(122,184,232,0.15)", color: "#7ab8e8" }}>{h}</span>
            ))}
          </div>
        )}
        {ev.data?.phrases && (
          <div style={{ marginTop: 6, display: "flex", flexWrap: "wrap", gap: 6 }}>
            {ev.data.phrases.map(p => (
              <span key={p} style={{ fontSize: 11, padding: "2px 8px", borderRadius: 4, background: "rgba(232,122,181,0.15)", color: "#e87ab5" }}>{p}</span>
            ))}
          </div>
        )}
        {ev.data?.summary && (
          <p style={{ margin: "6px 0 0", fontSize: 12, color: "#86d8c0", fontStyle: "italic" }}>{ev.data.summary}</p>
        )}
      </div>
    </div>
  );
}

function ResultCard({ text }) {
  const lines = text.split("\n");
  return (
    <div style={{
      marginTop: 6, padding: "16px 18px", borderRadius: 8,
      background: "rgba(232,200,122,0.05)",
      border: "1px solid rgba(232,200,122,0.2)",
    }}>
      {lines.map((line, i) => {
        if (!line.trim()) return <br key={i} />;
        if (line.startsWith("**") && line.endsWith("**")) {
          return <h4 key={i} style={{ margin: "14px 0 6px", color: "#e8c87a", fontSize: 13, letterSpacing: 1, fontWeight: 700 }}>{line.replace(/\*\*/g, "")}</h4>;
        }
        if (line.startsWith("• ")) {
          return <p key={i} style={{ margin: "3px 0", fontSize: 13, color: "rgba(255,255,255,0.8)", paddingLeft: 12 }}>• {line.slice(2)}</p>;
        }
        return <p key={i} style={{ margin: "4px 0", fontSize: 13, color: "rgba(255,255,255,0.75)", lineHeight: 1.65 }}>{line}</p>;
      })}
    </div>
  );
}

function AgentStatusBar({ events }) {
  const agentStatus = {};
  events.forEach(ev => {
    const key = ev.agent;
    if (!agentStatus[key]) agentStatus[key] = { last: ev.event, active: false };
    agentStatus[key].last = ev.event;
    agentStatus[key].active = ev.event === "agent_start" || ev.event === "agent_thinking" || ev.event === "tool_call";
    if (ev.event === "agent_done" || ev.event === "final_result") agentStatus[key].active = false;
  });
  return (
    <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 20 }}>
      {Object.entries(AGENTS).filter(([k]) => k !== "System").map(([name, cfg]) => {
        const s = agentStatus[name];
        const active = s?.active;
        const done = s?.last === "agent_done" || s?.last === "final_result";
        return (
          <div key={name} style={{
            display: "flex", alignItems: "center", gap: 7, padding: "6px 12px", borderRadius: 20,
            background: active ? `${cfg.color}18` : done ? "rgba(255,255,255,0.04)" : "rgba(255,255,255,0.02)",
            border: `1px solid ${active ? cfg.color + "55" : done ? cfg.color + "22" : "rgba(255,255,255,0.06)"}`,
            transition: "all 0.3s",
          }}>
            {active && (
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: cfg.color, display: "inline-block", animation: "pulse 1s infinite" }} />
            )}
            {done && <span style={{ fontSize: 10, color: cfg.color }}>✓</span>}
            <span style={{ fontSize: 11, color: active ? cfg.color : "rgba(255,255,255,0.4)", fontFamily: "monospace", letterSpacing: 0.5, fontWeight: 600 }}>
              {name}
            </span>
          </div>
        );
      })}
    </div>
  );
}

export default function TravelPlannerApp() {
  const [query, setQuery] = useState("");
  const [destinations, setDestinations] = useState("");
  const [days, setDays] = useState(14);
  const [travelerType, setTravelerType] = useState("first-time");
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const logRef = useRef(null);

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [events]);

  const handleSubmit = async () => {
    if (!query.trim()) return;
    setEvents([]);
    setLoading(true);
    setDone(false);
    setError("");

    try {
      const res = await fetch(`${API_BASE}/plan/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          destinations: destinations.split(",").map(d => d.trim()).filter(Boolean),
          duration_days: Number(days),
          traveler_type: travelerType,
        }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";

      while (true) {
        const { done: streamDone, value } = await reader.read();
        if (streamDone) break;
        buf += decoder.decode(value, { stream: true });
        const parts = buf.split("\n\n");
        buf = parts.pop();
        for (const part of parts) {
          const line = part.trim();
          if (line.startsWith("data: ")) {
            try {
              const ev = JSON.parse(line.slice(6));
              setEvents(prev => [...prev, ev]);
              if (ev.event === "final_result" || ev.event === "error") setDone(true);
            } catch {}
          }
        }
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0b0e17",
      fontFamily: "'Georgia', serif",
      color: "#f0ece0",
    }}>
      <style>{`
        @keyframes fadeSlide { from { opacity:0; transform:translateY(8px) } to { opacity:1; transform:none } }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
        @keyframes spin { to { transform: rotate(360deg) } }
        * { box-sizing: border-box; }
        textarea:focus, input:focus, select:focus { outline: none; }
        ::-webkit-scrollbar { width: 4px } ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius:2px }
      `}</style>

      <header style={{
        padding: "28px 40px 0",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        background: "rgba(255,255,255,0.015)",
      }}>
        <div style={{ maxWidth: 900, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 14, marginBottom: 6 }}>
            <span style={{ fontSize: 11, letterSpacing: 4, color: "#e8c87a", fontFamily: "monospace", fontWeight: 700 }}>✦ MULTI-AGENT</span>
          </div>
          <h1 style={{ margin: "0 0 4px", fontSize: 36, fontWeight: 400, letterSpacing: -0.5, color: "#f0ece0" }}>
            Travel Planner
          </h1>
          <p style={{ margin: "0 0 20px", fontSize: 14, color: "rgba(255,255,255,0.35)", fontFamily: "monospace" }}>
            Powered by 4 specialized AI agents · Destination · Weather · Language · Coordinator
          </p>
        </div>
      </header>

      <main style={{ maxWidth: 900, margin: "0 auto", padding: "32px 40px" }}>

        <div style={{
          background: "rgba(255,255,255,0.03)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: 12,
          padding: 24,
          marginBottom: 28,
        }}>
          <label style={{ display: "block", fontSize: 11, letterSpacing: 2, color: "rgba(255,255,255,0.4)", fontFamily: "monospace", marginBottom: 8 }}>
            YOUR TRAVEL REQUEST
          </label>
          <textarea
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Describe your ideal trip — destinations, interests, travel style, duration…"
            rows={4}
            style={{
              width: "100%", padding: "12px 14px",
              background: "rgba(255,255,255,0.04)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: 8, color: "#f0ece0", fontSize: 14, lineHeight: 1.6,
              resize: "vertical", fontFamily: "Georgia, serif",
            }}
          />

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14, marginTop: 14 }}>
            <div>
              <label style={{ display: "block", fontSize: 11, letterSpacing: 1.5, color: "rgba(255,255,255,0.35)", fontFamily: "monospace", marginBottom: 6 }}>DESTINATIONS</label>
              <input
                value={destinations}
                onChange={e => setDestinations(e.target.value)}
                placeholder="Tokyo, Osaka, Kyoto"
                style={{
                  width: "100%", padding: "9px 12px",
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 6, color: "#f0ece0", fontSize: 13,
                  fontFamily: "monospace",
                }}
              />
            </div>
            <div>
              <label style={{ display: "block", fontSize: 11, letterSpacing: 1.5, color: "rgba(255,255,255,0.35)", fontFamily: "monospace", marginBottom: 6 }}>DURATION (DAYS)</label>
              <input
                type="number" value={days} min={1} max={90}
                onChange={e => setDays(e.target.value)}
                style={{
                  width: "100%", padding: "9px 12px",
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 6, color: "#f0ece0", fontSize: 13,
                  fontFamily: "monospace",
                }}
              />
            </div>
            <div>
              <label style={{ display: "block", fontSize: 11, letterSpacing: 1.5, color: "rgba(255,255,255,0.35)", fontFamily: "monospace", marginBottom: 6 }}>TRAVELER TYPE</label>
              <select
                value={travelerType}
                onChange={e => setTravelerType(e.target.value)}
                style={{
                  width: "100%", padding: "9px 12px",
                  background: "#141720",
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 6, color: "#f0ece0", fontSize: 13,
                  fontFamily: "monospace",
                }}
              >
                <option value="first-time">First-time visitor</option>
                <option value="repeat">Repeat visitor</option>
                <option value="backpacker">Backpacker</option>
                <option value="luxury">Luxury traveler</option>
                <option value="family">Family</option>
                <option value="solo">Solo traveler</option>
              </select>
            </div>
          </div>

          <div style={{ marginTop: 18, display: "flex", gap: 12, alignItems: "center" }}>
            <button
              onClick={handleSubmit}
              disabled={loading || !query.trim()}
              style={{
                padding: "11px 28px",
                background: loading ? "rgba(232,200,122,0.15)" : "#e8c87a",
                color: loading ? "#e8c87a" : "#0b0e17",
                border: loading ? "1px solid rgba(232,200,122,0.3)" : "none",
                borderRadius: 6, fontSize: 13, fontWeight: 700,
                letterSpacing: 1.5, fontFamily: "monospace",
                cursor: loading ? "not-allowed" : "pointer",
                transition: "all 0.2s",
              }}
            >
              {loading ? (
                <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ width: 12, height: 12, borderRadius: "50%", border: "2px solid #e8c87a", borderTopColor: "transparent", display: "inline-block", animation: "spin 0.8s linear infinite" }} />
                  PLANNING…
                </span>
              ) : "PLAN MY TRIP ✦"}
            </button>
            {events.length > 0 && (
              <button
                onClick={() => { setEvents([]); setDone(false); setError(""); }}
                style={{ padding: "11px 18px", background: "transparent", color: "rgba(255,255,255,0.3)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6, fontSize: 12, fontFamily: "monospace", cursor: "pointer" }}
              >
                CLEAR
              </button>
            )}
          </div>
        </div>

        {error && (
          <div style={{ padding: "12px 16px", borderRadius: 8, background: "rgba(255,80,80,0.08)", border: "1px solid rgba(255,80,80,0.2)", color: "#ff6b6b", fontFamily: "monospace", fontSize: 13, marginBottom: 20 }}>
            ⚠ {error}
          </div>
        )}

        {events.length > 0 && <AgentStatusBar events={events} />}

        {events.length > 0 && (
          <div style={{
            border: "1px solid rgba(255,255,255,0.07)",
            borderRadius: 12,
            overflow: "hidden",
          }}>
            <div style={{
              padding: "10px 16px",
              background: "rgba(255,255,255,0.03)",
              borderBottom: "1px solid rgba(255,255,255,0.06)",
              display: "flex", alignItems: "center", justifyContent: "space-between",
            }}>
              <span style={{ fontSize: 11, letterSpacing: 2, color: "rgba(255,255,255,0.3)", fontFamily: "monospace" }}>
                AGENT ACTIVITY LOG
              </span>
              <span style={{ fontSize: 11, color: "rgba(255,255,255,0.2)", fontFamily: "monospace" }}>
                {events.length} events
              </span>
            </div>
            <div ref={logRef} style={{ maxHeight: 700, overflowY: "auto" }}>
              {events.map((ev, i) => <EventRow key={i} ev={ev} idx={i} />)}
              {loading && !done && (
                <div style={{ padding: "12px 16px", display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#e8c87a", display: "inline-block", animation: "pulse 1s infinite" }} />
                  <span style={{ fontSize: 12, color: "rgba(255,255,255,0.3)", fontFamily: "monospace" }}>Agents working…</span>
                </div>
              )}
            </div>
          </div>
        )}

        {events.length === 0 && !loading && (
          <div style={{ textAlign: "center", padding: "60px 20px", color: "rgba(255,255,255,0.15)" }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>✦</div>
            <p style={{ fontFamily: "monospace", fontSize: 13, letterSpacing: 1 }}>Enter your travel request above to begin</p>
            <p style={{ fontFamily: "monospace", fontSize: 11, marginTop: 8, color: "rgba(255,255,255,0.1)" }}>
              4 specialist agents will collaborate in real-time
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
