import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

BACKEND_DIR = Path(__file__).resolve().parents[1]

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.database import AsyncSessionLocal


async def main() -> None:
    async with AsyncSessionLocal() as session:
        brand_id = await session.scalar(
            text("select id from brands where slug = 'demo-store' limit 1")
        )

        if brand_id is None:
            brand_id = await session.scalar(
                text(
                    "insert into brands (name, slug) "
                    "values ('Demo Store', 'demo-store') returning id"
                )
            )

        customer_id = await session.scalar(
            text(
                "insert into customers (name, email) "
                "values ('Aisha Khan', 'aisha@example.com') returning id"
            )
        )

        conversation_id = await session.scalar(
            text(
                "insert into conversations (brand_id, customer_id, status) "
                "values (:brand_id, :customer_id, 'open') returning id"
            ),
            {
                "brand_id": brand_id,
                "customer_id": customer_id,
            },
        )

        await session.execute(
            text(
                "insert into messages (conversation_id, sender_type, content) "
                "values (:conversation_id, 'customer', :content)"
            ),
            {
                "conversation_id": conversation_id,
                "content": "My order arrived damaged. What can you do?",
            },
        )

        await session.execute(
            text(
                "insert into orders "
                "(conversation_id, order_number, product_name, status, delivery_date) "
                "values "
                "(:conversation_id, :order_number, :product_name, 'delivered', :delivery_date)"
            ),
            {
                "conversation_id": conversation_id,
                "order_number": f"DS-DEMO-{str(conversation_id)[:8]}",
                "product_name": "Insulated Water Bottle",
                "delivery_date": datetime(2026, 8, 30, tzinfo=timezone.utc),
            },
        )

        await session.commit()

        print(conversation_id)


if __name__ == "__main__":
    asyncio.run(main())
