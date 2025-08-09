import logging
from typing import Dict

import app.services.redis_client as redis_client_module

logger = logging.getLogger(__name__)


async def get_redis_health() -> Dict[str, str]:
    try:
        svc = redis_client_module.get_redis_service()
        ok = svc.ping()
        if ok:
            return {"status": "healthy", "message": "Redis连接正常"}
        return {"status": "unhealthy", "message": "Redis ping 失败"}
    except Exception as e:
        logger.error(f"Redis健康检查失败: {e}")
        return {"status": "unhealthy", "message": str(e)}
