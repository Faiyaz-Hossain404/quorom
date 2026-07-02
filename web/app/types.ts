export type GeoCoord = [number, number]; // [lng, lat]

export type FlatPort = {
  id: string;
  name: string;
  country: string;
  annual_teu: number;
  coordinates: GeoCoord;
};

export type DisruptionType =
  | "port_closure"
  | "vessel_delay"
  | "storm"
  | "strike"
  | "tariff";

export type Disruption = {
  id: string;
  type: DisruptionType;
  title: string;
  description: string;
  location: { type: "Point"; coordinates: GeoCoord };
  affected_ports: string[];
  severity: number;
  radius_km: number;
  status: "open" | "resolved";
  created_at: string;
};

export type Shipment = {
  id: string;
  vessel_name: string;
  imo_number: string;
  origin: string;
  destination: string;
  cargo_type: string;
  cargo_description: string;
  current_position: { type: "Point"; coordinates: GeoCoord };
  predicted_eta: string;
  actual_arrival: string | null;
  sla_deadline: string;
  status: "in_transit" | "delayed" | "arrived";
  created_at: string;
};

export type SocietyPhase =
  | "skeptic"
  | "analyst"
  | "judge"
  | "escalating"
  | "complete"
  | "error";

export type SocietyEvent = {
  phase: SocietyPhase;
  status?: "running" | "done";
  text?: string;
  tier?: "flash" | "max";
  is_material?: boolean;
  confidence?: number;
  reasoning?: string;
  reason?: string;
  threshold?: number;
  determination_id?: string;
  skeptic_argument?: string;
  analyst_argument?: string;
  judge_reasoning?: string;
  message?: string;
};

export type EvalCase = {
  shipment_id: string;
  disruption_id: string;
  vessel_name: string;
  disruption_title: string;
  ground_truth_material: boolean;
  baseline_is_material: boolean | null;
  baseline_confidence: number | null;
  baseline_correct: boolean | null;
  society_is_material: boolean | null;
  society_confidence: number | null;
  society_tier_used: "flash" | "max" | null;
  society_correct: boolean | null;
  determination_id: string | null;
  error: string | null;
};

export type EvalSummary = {
  total_cases: number;
  society_correct: number;
  baseline_correct: number;
  society_accuracy: number;
  baseline_accuracy: number;
  society_beats_baseline: boolean;
};

export type EvalRun = {
  run_id: string;
  created_at: string;
  summary: EvalSummary;
  cases?: EvalCase[];
};

export type Determination = {
  id: string;
  disruption_id: string;
  shipment_id: string;
  is_material: boolean;
  confidence: number;
  tier_used: "flash" | "max";
  skeptic_argument: string;
  analyst_argument: string;
  judge_reasoning: string;
  created_at: string;
};
