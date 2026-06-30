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
