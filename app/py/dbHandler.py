import asyncpg
import os
from datetime import datetime

# Database connection credentials from environment or defaults
DB_HOST = os.getenv("DB_HOST", "postgresDb") # Servicename in docker-compose
DB_USER = os.getenv("DB_USER", "trackerUser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "trackerPassword")
DB_NAME = os.getenv("DB_NAME", "trackerMasterData")

async def getConnection():
    return await asyncpg.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

async def saveRecentLocation(deviceId: str, latitude: float, longitude: float, trackerTimestamp: datetime, signalType: str, rawHex: str):
    conn = await getConnection()
    try:
        trackerRecord = await conn.fetchrow(
            'SELECT "id" FROM trackers WHERE "deviceId" = $1', deviceId
        )
        
        if not trackerRecord:
            print(f"[DB Warning] Tracker with deviceId {deviceId} not found in Master Data. Skipping insert.")
            return False

        trackerId = trackerRecord["id"]

        query = """
            INSERT INTO recentLocations ("trackerId", "latitude", "longitude", "trackerTimestamp", "signalType", "rawHex")
            VALUES ($1, $2, $3, $4, $5, $6)
        """
        await conn.execute(query, trackerId, latitude, longitude, trackerTimestamp, signalType, rawHex)
        print(f"[DB Success] Saved location for device {deviceId}")
        return True

    except Exception as e:
        print(f"[DB Error] Failed to save location: {e}")
        return False
    finally:
        await conn.close()