from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schema.analysis import AnalysisSessionResponse, CharacterValidationRequest
from app.service.character_analysis_service import create_analysis_session_record, get_analysis_session_detail

router = APIRouter(prefix="/api/v1/analysis-sessions", tags=["analysis"])


@router.post("", response_model=AnalysisSessionResponse)
def create_analysis_session(payload: CharacterValidationRequest, db: Session = Depends(get_db)):
    try:
        return create_analysis_session_record(db=db, character=payload.character)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{session_id}", response_model=AnalysisSessionResponse)
def get_analysis_session(session_id: int, db: Session = Depends(get_db)):
    session = get_analysis_session_detail(db=db, session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail="分析会话不存在")

    return session
