"use client";

import { useEffect, useState } from "react";

const ENGINE = process.env.NEXT_PUBLIC_ENGINE_URL || "http://localhost:8000";

export default function Home() {
  const [health, setHealth] = useState("checking…");

  useEffect(() => {
    fetch(`${ENGINE}/health`)
      .then((r) => r.json())
      .then((d) => setHealth(JSON.stringify(d)))
      .catch((e) => setHealth(`unreachable: ${e}`));
  }, []);

  return (
    <main className="wrap">
      <span className="kicker">Track 3 · Agent Society</span>
      <h1>Quorum</h1>
      <p className="lede">
        A multi-agent society that decides whether an external disruption is{" "}
        <em>material</em> to your shipments — then routes, recovers, and proves
        it against ground truth.
      </p>
      <div className="card">
        <span className="card-label">engine /health</span>
        <code>{health}</code>
      </div>
      <p className="foot">
        Day 1 scaffold · engine + web wired. Live map &amp; the society land next.
      </p>
    </main>
  );
}
