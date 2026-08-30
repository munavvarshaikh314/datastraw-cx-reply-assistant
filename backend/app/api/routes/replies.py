from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.repositories.conversation import ConversationRepository
from app.db.repositories.reply_generation import ReplyGenerationRepository
from app.schemas.reply import (
    ReplyGenerationResponse,
    ReplyGenerateRequest,
    ReplyUpdateRequest,
)
from app.services.reply_service import ReplyService


router = APIRouter(
    prefix="/conversations",
    tags=["Replies"],
)


@router.post(
    "/{conversation_id}/reply",
    response_model=ReplyGenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_reply(
    conversation_id: UUID,
    request: ReplyGenerateRequest,
    session: AsyncSession = Depends(get_db),
) -> ReplyGenerationResponse:

    conversation_repository = ConversationRepository(session)

    conversation = await conversation_repository.get_with_context(
        conversation_id
    )

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    try:
        reply_service = ReplyService(session)

        generation = await reply_service.generate_reply(
            conversation=conversation,
            agent_id=request.agent_id,
            customer_message=request.customer_message,
        )

        await session.commit()

        return generation

    except ValueError as exc:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        await session.rollback()

        print(
            "REPLY GENERATION ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.patch(
    "/replies/{reply_id}",
    response_model=ReplyGenerationResponse,
)
async def update_reply(
    reply_id: UUID,
    request: ReplyUpdateRequest,
    session: AsyncSession = Depends(get_db),
) -> ReplyGenerationResponse:

    repository = ReplyGenerationRepository(session)

    generation = await repository.get_by_id(reply_id)

    if generation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply generation not found",
        )

    try:
        service = ReplyService(session)

        generation = await service.update_reply(
            generation=generation,
            edited_response=request.edited_response,
        )

        await session.commit()

        return generation

    except ValueError as exc:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        await session.rollback()

        print(
            "REPLY UPDATE ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


@router.post(
    "/replies/{reply_id}/approve",
    response_model=ReplyGenerationResponse,
)
async def approve_reply(
    reply_id: UUID,
    session: AsyncSession = Depends(get_db),
) -> ReplyGenerationResponse:

    repository = ReplyGenerationRepository(session)

    generation = await repository.get_by_id(reply_id)

    if generation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reply generation not found",
        )

    try:
        service = ReplyService(session)

        generation = await service.approve_reply(
            generation=generation,
        )

        await session.commit()

        return generation

    except ValueError as exc:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        await session.rollback()

        print(
            "REPLY APPROVAL ERROR:",
            repr(exc),
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc