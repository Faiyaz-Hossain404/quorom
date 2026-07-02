"""Evaluation harness endpoints."""
import logging

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from ..db.client import get_db
from ..eval.harness import run_eval

router = APIRouter(prefix="/eval", tags=["eval"])
logger = logging.getLogger(__name__)


@router.post("/run")
async def trigger_eval() -> dict:
    """Run the ground-truth evaluation harness and return accuracy results."""
    try:
        return await run_eval()
    except Exception as exc:
        logger.exception("Eval run failed")
        return JSONResponse(status_code=500, content={"error": str(exc)})


@router.get("/results")
async def list_eval_results() -> list[dict]:
    """List past evaluation run summaries, newest first."""
    db = get_db()
    cursor = db.eval_runs.find({}, {"summary": 1, "created_at": 1}).sort("created_at", -1).limit(20)
    runs = []
    async for doc in cursor:
        runs.append({
            "run_id": str(doc["_id"]),
            "created_at": doc["created_at"].isoformat(),
            "summary": doc.get("summary", {}),
        })
    return runs


@router.get("/results/{run_id}")
async def get_eval_result(run_id: str) -> dict:
    """Get full details of a single eval run including all cases."""
    try:
        oid = ObjectId(run_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid run_id")

    db = get_db()
    doc = await db.eval_runs.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Eval run not found")

    doc["run_id"] = str(doc.pop("_id"))
    if hasattr(doc.get("created_at"), "isoformat"):
        doc["created_at"] = doc["created_at"].isoformat()
    return doc
