import time
import json
import os
from typing import Dict, Any, Optional

USER_STATE_DB = "C:/OsintNeoAi/data/user_investigation_states.json"
MAX_ACTIVE_INVESTIGATIONS = 3
DAILY_INPUT_ALLOWANCE = 50000  # Generous daily token / character allowance

class InvestigationStateManager:
    def __init__(self, db_path: str = USER_STATE_DB):
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load(self) -> Dict[str, Any]:
        with open(self.db_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, data: Dict[str, Any]):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_or_create_user(self, user_id: str) -> Dict[str, Any]:
        data = self._load()
        today = time.strftime("%Y-%m-%d")

        if user_id not in data:
            data[user_id] = {
                "active_investigations": [],
                "daily_usage": {
                    "date": today,
                    "tokens_used": 0
                },
                "total_submissions": 0
            }
            self._save(data)
            return data[user_id]

        if data[user_id]["daily_usage"]["date"] != today:
            data[user_id]["daily_usage"] = {
                "date": today,
                "tokens_used": 0
            }
            self._save(data)

        return data[user_id]

    def can_start_investigation(self, user_id: str) -> tuple[bool, str]:
        user = self.get_or_create_user(user_id)
        active_count = len(user.get("active_investigations", []))
        if active_count >= MAX_ACTIVE_INVESTIGATIONS:
            return False, f"Limit reached: You have {active_count}/{MAX_ACTIVE_INVESTIGATIONS} active investigations."
        return True, "OK"

    def can_submit_input(self, user_id: str, input_length: int) -> tuple[bool, str]:
        user = self.get_or_create_user(user_id)
        current_used = user["daily_usage"]["tokens_used"]
        if current_used + input_length > DAILY_INPUT_ALLOWANCE:
            return False, f"Daily input allowance exceeded ({current_used}/{DAILY_INPUT_ALLOWANCE})."
        return True, "OK"

    def record_submission(self, user_id: str, investigation_id: str, input_length: int):
        data = self._load()
        user = self.get_or_create_user(user_id)
        user["daily_usage"]["tokens_used"] += input_length
        user["total_submissions"] += 1
        
        if investigation_id not in user["active_investigations"]:
            user["active_investigations"].append(investigation_id)
            
        data[user_id] = user
        self._save(data)
