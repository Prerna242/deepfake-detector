from app.db.mongo import get_database


async def get_user_history(user_id: str, limit: int = 20) -> dict:
    db = get_database()

    cursor = (
        db["scans"]
        .find({"user_id": user_id}, {"_id": 0})
        .sort("scanned_at", -1)
        .limit(limit)
    )

    scans = await cursor.to_list(length=limit)
    total = await db["scans"].count_documents({"user_id": user_id})

    return {"scans": scans, "total": total}
