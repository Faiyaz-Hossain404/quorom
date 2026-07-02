import type { Determination, EvalRun, SocietyEvent } from "../types";

const ENGINE = process.env.NEXT_PUBLIC_ENGINE_URL ?? "http://localhost:8000";

export async function getPorts() {
  const r = await fetch(`${ENGINE}/ports`);
  if (!r.ok) throw new Error(`GET /ports: ${r.status}`);
  return r.json();
}

export async function getDisruptions(status?: "open" | "resolved") {
  const q = status ? `?status=${status}` : "";
  const r = await fetch(`${ENGINE}/disruptions${q}`);
  if (!r.ok) throw new Error(`GET /disruptions: ${r.status}`);
  return r.json();
}

export async function getShipments(status?: "in_transit" | "delayed" | "arrived") {
  const q = status ? `?status=${status}` : "";
  const r = await fetch(`${ENGINE}/shipments${q}`);
  if (!r.ok) throw new Error(`GET /shipments: ${r.status}`);
  return r.json();
}

export function streamSociety(
  disruptionId: string,
  shipmentId: string,
  onEvent: (evt: SocietyEvent) => void,
  onDone: () => void,
): () => void {
  const url = `${ENGINE}/society/stream?disruption_id=${encodeURIComponent(disruptionId)}&shipment_id=${encodeURIComponent(shipmentId)}`;
  const es = new EventSource(url);
  es.onmessage = (e: MessageEvent) => {
    if (e.data === "[DONE]") {
      es.close();
      onDone();
      return;
    }
    try {
      onEvent(JSON.parse(e.data) as SocietyEvent);
    } catch {
      // ignore malformed events
    }
  };
  es.onerror = () => {
    es.close();
    onDone();
  };
  return () => es.close();
}

export async function runEval(): Promise<EvalRun> {
  const r = await fetch(`${ENGINE}/eval/run`, { method: "POST" });
  if (!r.ok) throw new Error(`POST /eval/run: ${r.status}`);
  return r.json();
}

export async function getEvalResults(): Promise<EvalRun[]> {
  const r = await fetch(`${ENGINE}/eval/results`);
  if (!r.ok) throw new Error(`GET /eval/results: ${r.status}`);
  return r.json();
}

export async function getEvalRun(runId: string): Promise<EvalRun> {
  const r = await fetch(`${ENGINE}/eval/results/${runId}`);
  if (!r.ok) throw new Error(`GET /eval/results/${runId}: ${r.status}`);
  return r.json();
}

export async function getDeterminations(params?: {
  disruption_id?: string;
  shipment_id?: string;
}): Promise<Determination[]> {
  const qs = new URLSearchParams();
  if (params?.disruption_id) qs.set("disruption_id", params.disruption_id);
  if (params?.shipment_id) qs.set("shipment_id", params.shipment_id);
  const r = await fetch(`${ENGINE}/society/determinations?${qs}`);
  if (!r.ok) throw new Error(`GET /society/determinations: ${r.status}`);
  return r.json();
}
