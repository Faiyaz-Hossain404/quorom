"use client";

import { useEffect, useState } from "react";
import { getEvalResults, getEvalRun, runEval } from "../lib/api";
import type { EvalCase, EvalRun } from "../types";

function pct(n: number) {
  return `${Math.round(n * 100)}%`;
}

function EvalCaseRow({ c }: { c: EvalCase }) {
  const sOk = c.society_correct;
  const bOk = c.baseline_correct;
  return (
    <div className="eval-case-row">
      <div className="eval-case-vessel">{c.vessel_name}</div>
      <div className="eval-case-dis">{c.disruption_title}</div>
      <div className="eval-case-gt">
        GT:{" "}
        <span className={c.ground_truth_material ? "eval-material" : "eval-immaterial"}>
          {c.ground_truth_material ? "MAT" : "IMM"}
        </span>
      </div>
      <div className="eval-case-pips">
        <span
          className={`eval-pip ${sOk === true ? "correct" : sOk === false ? "wrong" : "unknown"}`}
          title={`Society: ${c.society_is_material ? "MATERIAL" : "IMMATERIAL"} (${pct(c.society_confidence ?? 0)})`}
        >
          S
        </span>
        <span
          className={`eval-pip ${bOk === true ? "correct" : bOk === false ? "wrong" : "unknown"}`}
          title={`Baseline: ${c.baseline_is_material ? "MATERIAL" : "IMMATERIAL"} (${pct(c.baseline_confidence ?? 0)})`}
        >
          B
        </span>
      </div>
    </div>
  );
}

export default function EvalPanel({ onBack }: { onBack: () => void }) {
  const [runs, setRuns] = useState<EvalRun[]>([]);
  const [active, setActive] = useState<EvalRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    getEvalResults()
      .then((rs) => {
        setRuns(rs);
        if (rs.length > 0) handleSelectRun(rs[0]);
      })
      .catch(() => setErr("Failed to load eval history"))
      .finally(() => setLoading(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleSelectRun(run: EvalRun) {
    if (run.cases) {
      setActive(run);
      return;
    }
    try {
      const full = await getEvalRun(run.run_id);
      setActive(full);
    } catch {
      // silently ignore; show summary-only view
      setActive(run);
    }
  }

  async function handleRunEval() {
    setRunning(true);
    setErr(null);
    try {
      const result = await runEval();
      setRuns((prev) => [result, ...prev]);
      setActive(result);
    } catch {
      setErr("Eval run failed — check engine logs");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="panel">
      <button className="back-btn" onClick={onBack}>
        ← Back
      </button>

      <div className="eval-head">
        <div className="eval-head-row">
          <div>
            <div className="eval-kicker">Day 4 · Accuracy</div>
            <div className="eval-title">Eval Harness</div>
          </div>
          <button className="run-eval-btn" onClick={handleRunEval} disabled={running}>
            {running ? "Running…" : "Run Eval"}
          </button>
        </div>
        <p className="eval-desc">
          Society vs single-agent baseline on historical shipments with known SLA outcomes.
        </p>
      </div>

      {err && <div className="eval-error">{err}</div>}

      {(loading || running) && (
        <div className="eval-loading">
          <span className="pulse-dot" />
          {running ? "Running eval — ~30–60s…" : "Loading…"}
        </div>
      )}

      {active && (
        <div className="eval-result-block">
          <div className="eval-score-row">
            <div className="eval-score-card society">
              <div className="eval-score-val">{pct(active.summary.society_accuracy)}</div>
              <div className="eval-score-label">Society</div>
              <div className="eval-score-sub">
                {active.summary.society_correct}/{active.summary.total_cases}
              </div>
            </div>
            <div className="eval-vs">vs</div>
            <div className="eval-score-card baseline">
              <div className="eval-score-val">{pct(active.summary.baseline_accuracy)}</div>
              <div className="eval-score-label">Baseline</div>
              <div className="eval-score-sub">
                {active.summary.baseline_correct}/{active.summary.total_cases}
              </div>
            </div>
          </div>
          <div
            className={`eval-verdict-tag ${active.summary.society_beats_baseline ? "wins" : "tied"}`}
          >
            {active.summary.society_beats_baseline
              ? "Society ≥ baseline"
              : "Tied"}
          </div>

          {active.cases && active.cases.length > 0 && (
            <div className="eval-cases">
              <div className="eval-cases-head">Cases</div>
              {active.cases.map((c, i) => (
                <EvalCaseRow key={i} c={c} />
              ))}
            </div>
          )}
        </div>
      )}

      {!loading && !running && !active && runs.length === 0 && (
        <p className="eval-empty">No runs yet. Click "Run Eval" to start.</p>
      )}

      {runs.length > 1 && (
        <div className="eval-history">
          <div className="eval-hist-label">History</div>
          {runs.slice(0, 6).map((r) => (
            <button
              key={r.run_id}
              className={`eval-hist-row ${active?.run_id === r.run_id ? "active" : ""}`}
              onClick={() => handleSelectRun(r)}
            >
              <span className="eval-hist-time">
                {new Date(r.created_at).toLocaleString(undefined, {
                  month: "short",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
              <span className="eval-hist-score">
                S {pct(r.summary.society_accuracy)} · B {pct(r.summary.baseline_accuracy)}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
