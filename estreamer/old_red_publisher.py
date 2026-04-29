import redis
import json
import logging

REDIS_STREAM = "alerts_stream"
logger = logging.getLogger(__name__)

class RedisPublisher:
    def __init__(self):
        self.client = redis.Redis(
            host='localhost', 
            port=6379, 
            decode_responses=True,
            socket_timeout=5 
        )

    def publish(self, payload: str):
        try:
            data = json.loads(payload)
        except Exception as e:
            # logger.error(f"JSON Decode Error: {e}")
            return

        computed = data.get("@computed", {})
        
        if "recordType" not in data:
            return

        event = {
            "timestamp": str(computed.get("eventDateTime") or data.get("eventSecond", "")),
            "type": str(computed.get("recordTypeDescription") or "Unknown"),
            "src_ip": str(data.get("sourceIpAddress", "")),
            "dst_ip": str(data.get("destinationIpAddress", "")),
            "severity": (computed.get("priority") or "low").lower(),
            "title": str(computed.get("message") or "No Message"),
            "protocol": str(computed.get("transportProtocol") or "N/A"),
            "blocked": str(computed.get("blocked") or "false"),
            "src_lat": "0.0", 
            "src_lon": "0.0",
        }

        try:
            # Synchronous XADD
            self.client.xadd(
                REDIS_STREAM,
                event,
                maxlen=10000,
                approximate=True
            )
        except Exception as e:
            logger.error(f"Redis XADD Error: {e}")

publisher = RedisPublisher()