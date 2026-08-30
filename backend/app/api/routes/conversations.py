from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel



from app.db.database import get_db
from app.db.repositories.conversation import ConversationRepository
from app.schemas.conversation import (
    ConversationListItem,
    ConversationResponse,
)

class ConversationStatusUpdate(BaseModel):
    status: str


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],

)


@router.get(
    "",
    response_model=list[ConversationListItem],
)
async def list_conversations(
    limit: int = 50,
    offset: int = 0,
    status: str | None = None,
    session: AsyncSession = Depends(get_db),

) -> list[ConversationListItem]:

    repository = ConversationRepository(session)

    conversations = await repository.list_conversations(
    limit=limit,
    offset=offset,
    status=status,
)

    return conversations


@router.patch(
    "/{conversation_id}/status",
    response_model=ConversationResponse,
)
async def update_conversation_status(
    conversation_id: UUID,
    request: ConversationStatusUpdate,
    session: AsyncSession = Depends(get_db),
) -> ConversationResponse:

    allowed_statuses = {
        "open",
        "pending",
        "closed",
    }

    if request.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid status. "
                "Allowed values: open, pending, closed."
            ),
        )

    repository = ConversationRepository(session)

    conversation = await repository.get_by_id(
        conversation_id
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    conversation.status = request.status

    await session.commit()
    await session.refresh(conversation)

    return conversation

@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
async def get_conversation(
    conversation_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> ConversationResponse:

    repository = ConversationRepository(session)

    conversation = await repository.get_with_context(
        conversation_id
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return conversation