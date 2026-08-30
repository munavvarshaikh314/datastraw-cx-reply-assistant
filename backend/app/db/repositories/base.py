from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base


ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Base repository providing common async database operations."""

    def __init__(
        self,
        session: AsyncSession,
        model: type[ModelT],
    ) -> None:
        self.session = session
        self.model = model

    async def create(
        self,
        entity: ModelT,
    ) -> ModelT:
        """Add an entity to the current transaction."""

        self.session.add(entity)

        await self.session.flush()

        return entity

    async def get_by_id(
        self,
        entity_id: UUID,
    ) -> ModelT | None:
        result = await self.session.execute(
            select(self.model).where(
                self.model.id == entity_id
            )
        )

        return result.scalar_one_or_none()

    async def list_all(self) -> list[ModelT]:
        result = await self.session.execute(
            select(self.model)
        )

        return list(result.scalars().all())

    async def delete(
        self,
        entity_id: UUID,
    ) -> bool:
        result = await self.session.execute(
            delete(self.model).where(
                self.model.id == entity_id
            )
        )

        return result.rowcount > 0