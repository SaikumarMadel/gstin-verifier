"""
Thread-safe in-memory session store with TTL auto-expiration.
Prevents memory leaks from abandoned captcha requests.
"""

import time
import uuid
import threading
import requests
from typing import Optional, Dict, Any
from .config import Config


class SessionItem:
    def __init__(self, session: requests.Session, ttl_seconds: int):
        self.session = session
        self.created_at = time.time()
        self.expires_at = self.created_at + ttl_seconds

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at


class SessionStore:
    def __init__(self, ttl_seconds: int = 300, cleanup_interval: int = 60):
        self._ttl = ttl_seconds
        self._cleanup_interval = cleanup_interval
        self._sessions: Dict[str, SessionItem] = {}
        self._lock = threading.RLock()
        self._stop_event = threading.Event()

        # Start background cleanup daemon
        self._cleanup_thread = threading.Thread(
            target=self._background_cleanup,
            name="SessionCleanupThread",
            daemon=True
        )
        self._cleanup_thread.start()

    def create_session(self, session: requests.Session) -> str:
        """Stores a requests.Session and returns a unique UUID session ID."""
        session_id = str(uuid.uuid4())
        item = SessionItem(session, self._ttl)
        with self._lock:
            self._sessions[session_id] = item
        return session_id

    def get_session(self, session_id: str) -> Optional[requests.Session]:
        """Retrieves an active session. Returns None if expired or not found."""
        if not session_id:
            return None
        with self._lock:
            item = self._sessions.get(session_id)
            if not item:
                return None
            if item.is_expired:
                del self._sessions[session_id]
                return None
            return item.session

    def delete_session(self, session_id: str) -> bool:
        """Removes a session after completion to release resources immediately."""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def active_count(self) -> int:
        """Returns the count of active, non-expired sessions."""
        now = time.time()
        with self._lock:
            return sum(1 for s in self._sessions.values() if s.expires_at > now)

    def _background_cleanup(self):
        """Periodically purges expired sessions."""
        while not self._stop_event.is_set():
            time.sleep(self._cleanup_interval)
            now = time.time()
            with self._lock:
                expired_keys = [k for k, v in self._sessions.items() if v.expires_at <= now]
                for k in expired_keys:
                    del self._sessions[k]

    def shutdown(self):
        """Stops the cleanup background thread."""
        self._stop_event.set()


# Global singleton instance
session_store = SessionStore(
    ttl_seconds=Config.SESSION_TTL_SECONDS,
    cleanup_interval=Config.SESSION_CLEANUP_INTERVAL_SECONDS
)
