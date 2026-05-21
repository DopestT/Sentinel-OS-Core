"""
Simple persistent JSONL logger for Sentinel OS.

This gives the 30-day watcher memory across process output and creates clean data
for later analysis, reports, and strategy tuning.
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, List


class DataLogger:
    def __init__(self, log_dir: str = "data"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def write_event(self, stream: str, payload: Dict[str, Any]) -> str:
        """Append one JSON event to a stream file."""
        event = {
            "logged_at": datetime.utcnow().isoformat(),
            "stream": stream,
            "payload": payload,
        }

        path = os.path.join(self.log_dir, f"{stream}.jsonl")
        with open(path, "a", encoding="utf-8") as file:
            file.write(json.dumps(event, default=str) + "\n")

        return path

    def read_recent(self, stream: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Read the most recent JSONL events from a stream file."""
        path = os.path.join(self.log_dir, f"{stream}.jsonl")
        if not os.path.exists(path):
            return []

        with open(path, "r", encoding="utf-8") as file:
            lines = file.readlines()[-limit:]

        events = []
        for line in lines:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

        return events

    def build_daily_summary(self, stream: str = "crypto_signals", limit: int = 1440) -> Dict[str, Any]:
        """Build a lightweight summary from recent signal records."""
        events = self.read_recent(stream, limit=limit)
        if not events:
            return {
                "events": 0,
                "paper_trades": 0,
                "best_strategy_counts": {},
                "latest_decision": None,
            }

        best_strategy_counts: Dict[str, int] = {}
        paper_trades = 0

        for event in events:
            payload = event.get("payload", {})
            best = payload.get("best_strategy_now")
            if best:
                best_strategy_counts[best] = best_strategy_counts.get(best, 0) + 1

            decision = payload.get("decision", {}).get("decision")
            if decision == "paper_trade":
                paper_trades += 1

        return {
            "events": len(events),
            "paper_trades": paper_trades,
            "best_strategy_counts": best_strategy_counts,
            "latest_decision": events[-1].get("payload", {}).get("decision"),
        }
