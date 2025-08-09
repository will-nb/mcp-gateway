import logging
from typing import Dict

import app.services.mongo_client as mongo_client_module

logger = logging.getLogger(__name__)


async def get_mongo_health() -> Dict[str, str]:
    try:
        cli = mongo_client_module.get_mongo_client()
        # use server_info() to match tests that monkeypatch server_info behavior
        cli.server_info()
        return {"status": "healthy", "message": "MongoDB连接正常"}
    except Exception as e:
        logger.error(f"MongoDB健康检查失败: {e}")
        return {"status": "unhealthy", "message": str(e)}
