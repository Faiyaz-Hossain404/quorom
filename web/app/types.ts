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
