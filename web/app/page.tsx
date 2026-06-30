"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import SidePanel from "./components/SidePanel";
import { getPorts, getDisruptions, getShipments } from "./lib/api";
import type { Disruption, FlatPort, Shipment } from "./types";

const GlobeMap = dynamic(() => import("./components/GlobeMap"), { ssr: false });

export default function Home() {
  const [ports, setPorts] = useState<FlatPort[]>([]);
  const [disruptions, setDisruptions] = useState<Disruption[]>([]);
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [selected, setSelected] = useState<Disruption | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getPorts(), getDisruptions(), getShipments()])
      .then(([portCollection, disruptionList, shipmentList]) => {
        // Flatten GeoJSON FeatureCollection → FlatPort[]
        const flat: FlatPort[] = portCollection.features.map(
          (f: {
            geometry: { coordinates: [number, number] };
            properties: {
              id: string;
              name: string;
              country: string;
              annual_teu: number;
            };
          }) => ({
            id: f.properties.id,
            name: f.properties.name,
            country: f.properties.country,
            annual_teu: f.properties.annual_teu,
            coordinates: f.geometry.coordinates,
          })
        );
        setPorts(flat);
        setDisruptions(disruptionList);
        setShipments(shipmentList);
      })
      .catch((e: unknown) => {
        setError(e instanceof Error ? e.message : "Failed to load data");
      });
  }, []);

  return (
    <div className="app-layout">
      {error && <div className="error-banner">{error} — is the engine running?</div>}
      <GlobeMap
        ports={ports}
        disruptions={disruptions}
        shipments={shipments}
        selectedId={selected?.id ?? null}
        onDisruptionSelect={setSelected}
      />
      <SidePanel
        disruptions={disruptions}
        shipments={shipments}
        selected={selected}
        onSelect={setSelected}
      />
    </div>
  );
}
