# redis_publisher.py

import redis
import json
import logging

logger = logging.getLogger(__name__)

REDIS_STREAM  = "alerts_stream"
STREAM_MAXLEN = 10_000


class RedisPublisher:

    NOISE_CLASSIFICATIONS = {
        "Not Suspicious Traffic",
        "Unknown Traffic",
    }

    KEEP_SEVERITIES = {"critical", "high", "medium"}

    NOISE_SIGNATURE_IDS = {
        "119:4",
        "119:7",
        "119:2",
        "119:15",
    }

    SUPPORTED_RECORD_TYPES = {400, 500, 502, 503}

    def __init__(self) -> None:
        self._client = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True,
            socket_timeout=5,
            retry_on_timeout=True,
        )

    def publish(self, payload: str) -> None:
        try:
            data = json.loads(payload)
        except (json.JSONDecodeError, TypeError):
            logger.warning("redis_publisher: invalid json payload")
            return

        computed = data.get("@computed", {})

        record_type = data.get("recordType")
        if record_type not in self.SUPPORTED_RECORD_TYPES:
            return

        classification = str(
            computed.get("classificationDescription") or ""
        ).strip()
        if classification in self.NOISE_CLASSIFICATIONS:
            return

        severity = (computed.get("priority") or "info").lower().strip()
        if severity not in self.KEEP_SEVERITIES:
            return

        generator_id = str(data.get("generatorId", ""))
        rule_id      = str(data.get("ruleId", ""))
        signature_id = f"{generator_id}:{rule_id}"
        if signature_id in self.NOISE_SIGNATURE_IDS:
            return

        blocked_raw = str(computed.get("blocked") or "No")
        blocked     = "Yes" if blocked_raw.lower() in ("yes", "true", "1") else "No"

        event = {
            "timestamp":      str(computed.get("eventDateTime") or data.get("eventSecond", "")),
            "type":           str(computed.get("recordTypeDescription") or "Unknown"),
            "src_ip":         str(data.get("sourceIpAddress", "")),
            "dst_ip":         str(data.get("destinationIpAddress", "")),
            "severity":       severity,
            "title":          str(computed.get("message") or "Unknown"),
            "classification": classification,
            "protocol":       str(computed.get("transportProtocol") or "N/A"),
            "blocked":        blocked,
        }

        self._xadd(event)

    def _xadd(self, event: dict) -> None:
        try:
            self._client.xadd(
                REDIS_STREAM,
                event,
                maxlen=STREAM_MAXLEN,
                approximate=True,
            )
            logger.info(
                "redis_publisher: published [%s] severity=%s src=%s",
                event["title"],
                event["severity"],
                event["src_ip"],
            )
        except redis.RedisError as e:
            logger.error("redis_publisher: xadd failed: %s", str(e))


publisher = RedisPublisher()