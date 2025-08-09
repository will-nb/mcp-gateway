import logging
from typing import Dict

from app.services.qdrant import get_qdrant_service

logger = logging.getLogger(__name__)


async def get_qdrant_health() -> Dict[str, str]:
    try:
        svc = get_qdrant_service()
        svc.get_client().get_collections()
        return {"status": "healthy", "message": "Qdrant连接正常"}
    except Exception as e:
        logger.error(f"Qdrant健康检查失败: {e}")
        return {"status": "unhealthy", "message": str(e)}
