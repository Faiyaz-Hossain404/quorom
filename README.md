# Quorum

**A multi-agent society for supply-chain exception management.**
Track 3 · Agent Society · Global AI Hackathon with Qwen Cloud.

Given an external disruption signal — a port closure, vessel delay, storm,
strike, or tariff change — Quorum decides whether it is **material** to a given
shipment (will it breach an SLA or cause a stockout?), then routes, recovers,
and **proves the call against ground truth** (predicted ETA vs. actual port-call
arrival).

A single LLM guesses. A *society* deliberates: a **Skeptic** argues the
disruption is noise, an **Analyst** argues it is material, and a **Judge**
renders a determination with a full audit trail — escalating from a fast model
to a deep one only when the call is genuinely contestable.

---

## Why a society (and not one prompt)

Materiality is **contestable** — the same signal is "ignore it" for one lane and
"reroute now" for another. That is exactly the kind of judgment that benefits
from structured disagreement plus a deterministic ground-truth check. Quorum
pairs probabilistic debate with deterministic verification.

## Architecture

```
feeds → ingestion → exposure mapping → confidence cascade → society → judge
(GDELT,   (FastAPI)    (Mongo 2dsphere)   (qwen-flash →      (Skeptic /   (determination
 GDACS,                                    qwen-max)          Analyst)     + obligations
 NOAA)                                                                     + audit)
                                                                              │
                              outcome check (ETA vs AIS arrival) ◄────────────┘
                                                                              │
                                          live globe map + scoreboard (Next.js + deck.gl)
```

## Tech stack

| Layer | Tech |
|---|---|
| LLM | Qwen via Alibaba Cloud Model Studio (OpenAI-compatible), `qwen-flash` → `qwen-max` cascade |
| Engine | FastAPI + async Python, SSE live stream |
| Database | MongoDB Atlas (GeoJSON + 2dsphere geospatial queries) |
| Frontend | Next.js 15 + react-map-gl + MapLibre GL (globe) + deck.gl |
| Deploy | Alibaba Cloud ECS + Docker Compose + nginx |

## Repository layout

```
quorum/
├── engine/                # FastAPI agent + ingestion + eval engine
│   ├── app/               # main.py, config.py, qwen.py
│   └── scripts/           # verify_qwen.py — Day-1 cascade smoke test
├── web/                   # Next.js 15 dashboard (static export)
├── nginx/                 # reverse proxy (SSE-ready)
└── docker-compose.yml
```

## Quick start (local)

```bash
cp .env.example .env          # add your Model Studio key
pip install -r engine/requirements.txt
python engine/scripts/verify_qwen.py        # confirm the Qwen cascade

uvicorn app.main:app --reload --app-dir engine   # engine on :8000
cd web && npm install && npm run dev              # web on :3000
```

Full stack via Docker: `docker compose up --build` (build the web first:
`cd web && npm ci && npm run build`). The stack deploys to Alibaba Cloud ECS
via Docker Compose + nginx.

## License

MIT — see [LICENSE](LICENSE).
