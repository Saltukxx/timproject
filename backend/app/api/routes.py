import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..config import settings
from ..services.ai_client import AISummaryError, generate_ai_summary
from ..services.excel_processor import ExcelProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze")
async def analyze_workbook(file: UploadFile = File(...)) -> Any:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".xlsx", ".xlsm"}:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp.flush()
            temp_path = Path(tmp.name)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail="Failed to persist upload") from exc

    try:
        processor = ExcelProcessor(temp_path)
        result = processor.analyse()

        ai_summary = None
        if settings.enable_ai_summary:
            try:
                ai_summary = await generate_ai_summary(result.to_dict())
            except AISummaryError as exc:
                logger.warning("AI summary unavailable: %s", exc)
                ai_summary = {
                    "headline": "Automated interpretation unavailable",
                    "bullets": [
                        "The AI assistant could not process this report at the moment.",
                    ],
                    "cautions": [str(exc)],
                }
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Unexpected AI summary error")
                ai_summary = {
                    "headline": "Automated interpretation unavailable",
                    "bullets": [
                        "An unexpected error occurred while contacting the AI service.",
                    ],
                    "cautions": ["Check backend logs for ai_summary stack trace."],
                }

        result.ai_summary = ai_summary
        return result.to_dict()
    finally:
        try:
            temp_path.unlink(missing_ok=True)
        except OSError:
            pass
