import asyncio
import sys
from pathlib import Path
from uuid import UUID

BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.database import AsyncSessionLocal
from app.services.knowledge import KnowledgeService  # type: ignore[reportMissingImports]


BRAND_ID = UUID("ed271a6f-0c27-4b17-b580-e9d71eed15f5")


async def main() -> None:
    async with AsyncSessionLocal() as session:
        knowledge_service = KnowledgeService(session)

        count = await knowledge_service.index_brand_knowledge(
            brand_id=BRAND_ID
        )

        print(f"Indexed {count} knowledge documents for brand {BRAND_ID}")


if __name__ == "__main__":
    asyncio.run(main())