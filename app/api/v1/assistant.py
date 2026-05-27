from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.db.schema import User
from app.models.assistant import AssistantQuery, AssistantResponse
from app.services.assistant_service import AssistantService, AssistantUnavailableError

router = APIRouter()


def get_assistant_service(db: Session = Depends(get_db)) -> AssistantService:
    return AssistantService(session=db)


@router.post("/assistant/query", response_model=AssistantResponse)
def query_assistant(
    query: AssistantQuery,
    current_user: User = Depends(get_current_user),
    service: AssistantService = Depends(get_assistant_service),
):
    try:
        return service.answer_query(user=current_user, message=query.message)
    except AssistantUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
