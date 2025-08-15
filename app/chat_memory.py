from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Optional, List


class ChatMemory:
    """
    Lightweight session persistence for ResumeScan.
    Stores sessions, current_session, analysis_result, questions, conversation_history, extra_criteria
    in data/sessions.json (atomic writes; tolerant loader).
    """

    def __init__(self, base_dir: Optional[Path] = None, filename: str = "sessions.json") -> None:
        if base_dir is None:
            base_dir = Path(__file__).resolve().parents[1]  # project root
        self.data_dir = Path(base_dir) / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.data_dir / filename

        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.current_session: Optional[str] = None

        self.load()

    # ----------------- Internal I/O -----------------

    def _atomic_write_json(self, payload: dict) -> None:
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
        tmp.replace(self.path)

    def save(self) -> None:
        payload = {"sessions": self.sessions, "current_session": self.current_session}
        self._atomic_write_json(payload)

    def load(self) -> None:
        if not self.path.exists():
            self.save()
            return
        try:
            with self.path.open("r", encoding="utf-8") as f:
                payload = json.load(f)
            self.sessions = payload.get("sessions", {}) or {}
            self.current_session = payload.get("current_session")
            if self.current_session and self.current_session not in self.sessions:
                self.current_session = None
        except Exception:
            self.sessions = {}
            self.current_session = None

    # ----------------- Session CRUD -----------------

    def create_session(self, name: Optional[str] = None) -> str:
        sid = f"session_{len(self.sessions) + 1}"
        if name is None:
            name = f"Session {len(self.sessions) + 1}"
        self.sessions[sid] = {
            "name": name,
            "analysis_result": None,
            "conversation_history": [],
            "questions": [],
            "extra_criteria": "",  # NEW
        }
        self.current_session = sid
        self.save()
        return sid

    def switch_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            self.current_session = session_id
            self.save()

    def rename_session(self, session_id: str, new_name: str) -> None:
        if session_id in self.sessions and new_name.strip():
            self.sessions[session_id]["name"] = new_name.strip()
            self.save()

    def delete_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.current_session == session_id:
                self.current_session = None
            self.save()

    # ----------------- Data updates -----------------

    def update_analysis(
        self,
        session_id: str,
        analysis_result: Dict[str, Any],
        questions: Optional[List[Dict[str, Any]]] = None,
        reset_history: bool = True,
    ) -> None:
        if session_id not in self.sessions:
            return
        self.sessions[session_id]["analysis_result"] = analysis_result
        if questions is not None:
            self.sessions[session_id]["questions"] = questions
        if reset_history:
            self.sessions[session_id]["conversation_history"] = []
        self.save()

    def set_questions(self, session_id: str, questions: List[Dict[str, Any]]) -> None:
        if session_id not in self.sessions:
            return
        self.sessions[session_id]["questions"] = questions
        self.save()

    def replace_conversation(self, session_id: str, history: List[Dict[str, str]]) -> None:
        if session_id not in self.sessions:
            return
        self.sessions[session_id]["conversation_history"] = history
        self.save()

    def append_chat_message(self, session_id: str, role: str, content: str) -> None:
        if session_id not in self.sessions:
            return
        self.sessions[session_id]["conversation_history"].append({"role": role, "content": content})
        self.save()

    # Extra criteria (NEW)
    def set_extra_criteria(self, session_id: str, text: str) -> None:
        if session_id not in self.sessions:
            return
        self.sessions[session_id]["extra_criteria"] = text or ""
        self.save()

    def get_extra_criteria(self, session_id: str) -> str:
        if session_id not in self.sessions:
            return ""
        return self.sessions[session_id].get("extra_criteria", "") or ""

    # ----------------- Accessors -----------------

    def get_current(self) -> Optional[Dict[str, Any]]:
        if self.current_session and self.current_session in self.sessions:
            return self.sessions[self.current_session]
        return None

    def ensure_one_session(self) -> None:
        if not self.sessions:
            self.create_session()
        if not self.current_session:
            self.current_session = next(iter(self.sessions))
            self.save()
