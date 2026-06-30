"use client";

import type { Disruption, Shipment } from "../types";

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
  if (selected) {
    return <DetailView disruption={selected} shipments={shipments} onBack={() => onSelect(null)} />;
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
        Click a disruption marker to see details and society determination
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
      d.affected_ports.includes(s.origin) || d.affected_ports.includes(s.destination)
  );

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
          <span className="sev-chip" style={{ borderColor: sevColor(d.severity), color: sevColor(d.severity) }}>
            Severity {d.severity}
          </span>
          <span className={`status-chip ${d.status}`}>{d.status.toUpperCase()}</span>
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

      {impacted.length > 0 && (
        <section className="panel-section" style={{ marginTop: "1rem" }}>
          <div className="section-head">
            <span>Impacted Shipments</span>
            <span className="badge-count">{impacted.length}</span>
          </div>
          {impacted.map((s) => (
            <div key={s.id} className="ship-row">
              <div className="ship-name">{s.vessel_name}</div>
              <div className="ship-route">
                {s.origin} <span className="arrow">→</span> {s.destination}
              </div>
            </div>
          ))}
        </section>
      )}

      <div className="society-placeholder">
        <div className="sp-label">Agent Society Determination</div>
        <div className="sp-body">
          Skeptic · Analyst · Judge debate appears here after Day 3.
        </div>
      </div>
    </div>
  );
}
