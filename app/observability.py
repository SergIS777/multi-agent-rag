import json
import time
import functools
from datetime import datetime, timezone

LOG_FILE = "trace_log.jsonl"


def traced(name: str):
    """Декоратор-трейсер: каждая нода пишет JSON-строку в trace_log.jsonl."""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(state, *args, **kwargs):
            t0 = time.time()
            result = fn(state, *args, **kwargs)
            entry = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "trace_id": state.get("trace_id"),
                "node": name,
                "latency_ms": int((time.time() - t0) * 1000),
                "tokens": result.get("token_cost"),
                "keys": sorted(result.keys()),
            }
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            return result
        return wrapper
    return deco