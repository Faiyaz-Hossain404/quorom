"use client";

import { useEffect, useRef } from "react";
import "maplibre-gl/dist/maplibre-gl.css";
import maplibregl from "maplibre-gl";
import { MapboxOverlay } from "@deck.gl/mapbox";
import { ScatterplotLayer, ArcLayer } from "@deck.gl/layers";
import type { FlatPort, Disruption, Shipment } from "../types";

const MAP_STYLE =
  "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json";

type ArcRow = {
  from: [number, number];
  to: [number, number];
  active: boolean;
};

function makeLayers(
  ports: FlatPort[],
  disruptions: Disruption[],
  shipments: Shipment[],
  selectedId: string | null,
  onSelect: (d: Disruption) => void
) {
  const idx = new Map(ports.map((p) => [p.id, p.coordinates]));

  const arcs: ArcRow[] = shipments
    .filter((s) => idx.has(s.origin) && idx.has(s.destination))
    .map((s) => ({
      from: idx.get(s.origin)!,
      to: idx.get(s.destination)!,
      active: s.status !== "arrived",
    }));

  const open = disruptions.filter((d) => d.status === "open");

  return [
    // Disruption influence radius
    new ScatterplotLayer<Disruption>({
      id: "d-rings",
      data: open,
      getPosition: (d) => d.location.coordinates as [number, number],
      getRadius: (d) => d.radius_km * 1000,
      getFillColor: (d) =>
        [239, 68, 68, d.severity * 8] as [number, number, number, number],
      stroked: true,
      getLineColor: (d) =>
        [239, 68, 68, 50 + d.severity * 16] as [number, number, number, number],
      getLineWidth: 1,
      lineWidthMinPixels: 1,
    }),
    // Shipment route arcs
    new ArcLayer<ArcRow>({
      id: "arcs",
      data: arcs,
      getSourcePosition: (d) => d.from,
      getTargetPosition: (d) => d.to,
      getSourceColor: (d) =>
        (d.active
          ? [251, 146, 60, 200]
          : [107, 114, 128, 100]) as [number, number, number, number],
      getTargetColor: (d) =>
        (d.active
          ? [251, 146, 60, 70]
          : [107, 114, 128, 30]) as [number, number, number, number],
      getWidth: 2,
      widthMinPixels: 1,
      greatCircle: true,
    }),
    // Port dots — sized by annual TEU
    new ScatterplotLayer<FlatPort>({
      id: "ports",
      data: ports,
      getPosition: (d) => d.coordinates as [number, number],
      getRadius: (d) => Math.sqrt(d.annual_teu) * 55,
      getFillColor: [76, 194, 255, 200],
      radiusMinPixels: 3,
      radiusMaxPixels: 13,
    }),
    // Disruption epicenters (clickable)
    new ScatterplotLayer<Disruption>({
      id: "d-dots",
      data: open,
      getPosition: (d) => d.location.coordinates as [number, number],
      getRadius: 22000,
      getFillColor: (d) =>
        (d.id === selectedId
          ? [255, 255, 255, 255]
          : d.severity >= 4
          ? [239, 68, 68, 255]
          : d.severity === 3
          ? [249, 115, 22, 255]
          : [234, 179, 8, 255]) as [number, number, number, number],
      radiusMinPixels: 7,
      radiusMaxPixels: 14,
      pickable: true,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      onClick: ({ object }: any) => {
        if (object) onSelect(object as Disruption);
      },
    }),
  ];
}

type Props = {
  ports: FlatPort[];
  disruptions: Disruption[];
  shipments: Shipment[];
  selectedId: string | null;
  onDisruptionSelect: (d: Disruption) => void;
};

export default function GlobeMap({
  ports,
  disruptions,
  shipments,
  selectedId,
  onDisruptionSelect,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const overlayRef = useRef<MapboxOverlay | null>(null);
  const onSelectRef = useRef(onDisruptionSelect);

  // Keep callback ref stable so layer rebuilds don't need it as dep
  useEffect(() => {
    onSelectRef.current = onDisruptionSelect;
  }, [onDisruptionSelect]);

  // Mount map once
  useEffect(() => {
    if (!containerRef.current) return;
    let isMounted = true;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: MAP_STYLE,
      center: [25, 20],
      zoom: 1.8,
      antialias: true,
    });

    const overlay = new MapboxOverlay({ layers: [] });

    map.on("load", () => {
      if (!isMounted) return;
      map.addControl(overlay);
      overlayRef.current = overlay;
    });

    return () => {
      isMounted = false;
      overlayRef.current = null;
      map.remove();
    };
  }, []);

  // Rebuild layers whenever data or selection changes
  useEffect(() => {
    const o = overlayRef.current;
    if (!o) return;
    o.setProps({
      layers: makeLayers(ports, disruptions, shipments, selectedId, (d) =>
        onSelectRef.current(d)
      ),
    });
  }, [ports, disruptions, shipments, selectedId]);

  return <div ref={containerRef} style={{ position: "absolute", inset: 0 }} />;
}
