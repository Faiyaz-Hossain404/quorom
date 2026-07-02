"use client";

import { useEffect, useState } from "react";
import { streamSociety } from "../lib/api";
import type { Disruption, Shipment, SocietyEvent } from "../types";
import EvalPanel from "./EvalPanel";

const SEV_COLOR: Record<number, string> = {
  5: "#ef4444",
  4: "#f97316",
  3: "#eab308",
  2: "#84cc16",
  1: "#84cc16",
};

const TYPE_LABEL: Record<string, string> = {
  port_closure: "PORT CLOSURE",
  vessel_delay: "VESSEL DELAY",
  storm: "STORM",
  strike: "STRIKE",
  tariff: "TARIFF",
};

function sevColor(n: number) {
  return SEV_COLOR[n] ?? SEV_COLOR[1];
}

type Props = {
  disruptions: Disruption[];
  shipments: Shipment[];
  selected: Disruption | null;
  onSelect: (d: Disruption | null) => void;
};

export default function SidePanel({
  disruptions,
  shipments,
  selected,
  onSelect,
}: Props) {
  const [showEval, setShowEval] = useState(false);

  if (showEval) {
    return <EvalPanel onBack={() => setShowEval(false)} />;
  }

  if (selected) {
    return (
      <DetailView
        disruption={selected}
        shipments={shipments}
        onBack={() => onSelect(null)}
      />
    );
  }

  const open = disruptions.filter((d) => d.status === "open");
  const active = shipments.filter((s) => s.status !== "arrived");

  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-kicker">Track 3 · Agent Society</div>
        <h1 className="panel-title">Quorum</h1>
        <p className="panel-sub">Supply-chain exception management</p>
      </div>

      <section className="panel-section">
        <div className="section-head">
          <span>Disruptions</span>
          <span className="badge-count">{open.length} active</span>
        </div>
        {open.map((d) => (
          <button key={d.id} className="list-row" onClick={() => onSelect(d)}>
            <span className="sev-dot" style={{ background: sevColor(d.severity) }} />
            <span className="row-label">{d.title}</span>
            <span className="sev-num" style={{ color: sevColor(d.severity) }}>
              {d.severity}
            </span>
          </button>
        ))}
        {open.length === 0 && <p className="empty">No active disruptions</p>}
      </section>

      <section className="panel-section">
        <div className="section-head">
          <span>Active Shipments</span>
          <span className="badge-count">{active.length}</span>
        </div>
        {active.map((s) => (
          <div key={s.id} className="ship-row">
            <div className="ship-name">{s.vessel_name}</div>
            <div className="ship-route">
              {s.origin} <span className="arrow">→</span> {s.destination}
            </div>
          </div>
        ))}
        {active.length === 0 && <p className="empty">No active shipments</p>}
      </section>

      <div className="panel-footer">
        <span>Click a disruption marker to run the agent society</span>
        <button className="eval-link-btn" onClick={() => setShowEval(true)}>
          Eval
        </button>
      </div>
    </div>
  );
}

function DetailView({
  disruption: d,
  shipments,
  onBack,
}: {
  disruption: Disruption;
  shipments: Shipment[];
  onBack: () => void;
}) {
  const impacted = shipments.filter(
    (s) =>
      d.affected_ports.includes(s.origin) ||
      d.affected_ports.includes(s.destination),
  );

  const [targetShipmentId, setTargetShipmentId] = useState<string | null>(null);
  const [events, setEvents] = useState<SocietyEvent[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    if (!targetShipmentId) return;
    setEvents([]);
    setIsStreaming(true);
    const close = streamSociety(
      d.id,
      targetShipmentId,
      (evt) => setEvents((prev) => [...prev, evt]),
      () => setIsStreaming(false),
    );
    return close;
  }, [targetShipmentId, d.id]);

  return (
    <div className="panel">
      <button className="back-btn" onClick={onBack}>
        ← Back
      </button>

      <div className="detail-head">
        <div className="detail-type" style={{ color: sevColor(d.severity) }}>
          {TYPE_LABEL[d.type] ?? d.type}
        </div>
        <h2 className="detail-title">{d.title}</h2>
        <div className="detail-meta">
          <span
            className="sev-chip"
            style={{
              borderColor: sevColor(d.severity),
              color: sevColor(d.severity),
            }}
          >
            Severity {d.severity}
          </span>
          <span className={`status-chip ${d.status}`}>
            {d.status.toUpperCase()}
          </span>
        </div>
      </div>

      <p className="detail-desc">{d.description}</p>

      <div className="detail-stat">
        <span className="stat-label">Radius</span>
        <span className="stat-val">{d.radius_km.toLocaleString()} km</span>
      </div>

      <div className="detail-stat">
        <span className="stat-label">Affected Ports</span>
        <span className="stat-val">{d.affected_ports.join(", ")}</span>
      </div>

      <div className="society-section">
        <div className="society-head">Agent Society Determination</div>

        {impacted.length === 0 && (
          <p className="empty" style={{ fontSize: "0.73rem" }}>
            No directly impacted shipments on this route.
          </p>
        )}

        {impacted.map((s) => (
          <ShipmentAnalysis
            key={s.id}
            shipment={s}
            isActive={targetShipmentId === s.id}
            isStreaming={isStreaming && targetShipmentId === s.id}
            events={targetShipmentId === s.id ? events : []}
            onAnalyze={() => setTargetShipmentId(s.id)}
          />
        ))}
      </div>
    </div>
  );
}

function ShipmentAnalysis({
  shipment: s,
  isActive,
  isStreaming,
  events,
  onAnalyze,
}: {
  shipment: Shipment;
  isActive: boolean;
  isStreaming: boolean;
  events: SocietyEvent[];
  onAnalyze: () => void;
}) {
  const complete = events.find((e) => e.phase === "complete");
  const skepticRunning = events.find(
    (e) => e.phase === "skeptic" && e.status === "running",
  );
  const skepticDone = events.find(
    (e) => e.phase === "skeptic" && e.status === "done",
  );
  const analystRunning = events.find(
    (e) => e.phase === "analyst" && e.status === "running",
  );
  const analystDone = events.find(
    (e) => e.phase === "analyst" && e.status === "done",
  );
  const escalating = events.find((e) => e.phase === "escalating");
  const judgeRunning = [...events]
    .reverse()
    .find((e) => e.phase === "judge" && e.status === "running");

  return (
    <div className="society-ship-item">
      <div className="society-ship-header">
        <div>
          <div className="society-ship-name">{s.vessel_name}</div>
          <div className="ship-route" style={{ fontSize: "0.68rem" }}>
            {s.origin} <span className="arrow">→</span> {s.destination}
          </div>
        </div>
        <button
          className="analyze-btn"
          onClick={onAnalyze}
          disabled={isStreaming}
        >
          {isStreaming ? "Running…" : complete ? "Re-analyze" : "Analyze"}
        </button>
      </div>

      {isActive && events.length > 0 && (
        <div className="society-events">
          {skepticRunning && !skepticDone && (
            <div className="sev-running">
              <span className="pulse-dot" />
              Skeptic arguing immaterial…
            </div>
          )}
          {skepticDone && (
            <div className="sev-agent-block skeptic">
              <div className="sev-agent-label">SKEPTIC</div>
              <div className="sev-agent-text">{skepticDone.text}</div>
            </div>
          )}

          {analystRunning && !analystDone && (
            <div className="sev-running">
              <span className="pulse-dot" style={{ background: "#fb923c" }} />
              Analyst arguing material…
            </div>
          )}
          {analystDone && (
            <div className="sev-agent-block analyst">
              <div className="sev-agent-label">ANALYST</div>
              <div className="sev-agent-text">{analystDone.text}</div>
            </div>
          )}

          {escalating && (
            <div className="sev-escalate">
              ⚠ Low confidence ({Math.round((escalating.confidence ?? 0) * 100)}
              %) — escalating to qwen-max
            </div>
          )}

          {judgeRunning && !complete && (
            <div className="sev-running">
              <span className="pulse-dot" style={{ background: "#c084fc" }} />
              Judge deliberating ({judgeRunning.tier})…
            </div>
          )}

          {complete && (
            <div
              className={`society-verdict ${complete.is_material ? "material" : "immaterial"}`}
            >
              <div
                className={`verdict-label ${complete.is_material ? "material" : "immaterial"}`}
              >
                {complete.is_material ? "MATERIAL RISK" : "IMMATERIAL"}
              </div>
              <div className="verdict-confidence-row">
                <div className="verdict-conf-bar">
                  <div
                    className={`verdict-conf-fill ${complete.is_material ? "material" : "immaterial"}`}
                    style={{
                      width: `${Math.round((complete.confidence ?? 0) * 100)}%`,
                    }}
                  />
                </div>
                <span className="verdict-conf-pct">
                  {Math.round((complete.confidence ?? 0) * 100)}%
                </span>
              </div>
              <div className="verdict-reasoning">{complete.judge_reasoning}</div>
              <div className="verdict-tier">via qwen-{complete.tier_used}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
