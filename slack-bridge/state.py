"""파일 기반 런타임 상태 — 승인 대기, 진행 중 주제 추적, 스레드 매핑.

인메모리 cancel 레지스트리는 B 플로우(중단+재시작)에서 실행 중 태스크를
외부에서 중단시키기 위해 쓴다. threading.Event 는 직렬화 불가라서
파일이 아닌 프로세스 메모리에만 존재 — 봇 재시작 시 자동으로 비워짐.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any

_STATE_DIR = Path(__file__).parent / "state"
_STATE_DIR.mkdir(exist_ok=True)

_PENDING = _STATE_DIR / "pending.json"
_TASKS = _STATE_DIR / "tasks.json"
_THREADS = _STATE_DIR / "threads.json"  # {f"{channel}:{thread_ts}": task_id}
_DM_SLUG_WAIT = _STATE_DIR / "dm-slug-wait.json"  # {user_id: {task, channel, thread_ts}}

_cancel_events: dict[str, threading.Event] = {}
_task_threads: dict[str, threading.Thread] = {}
_cancel_lock = threading.Lock()


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------- pending (승인 대기 / 슬러그 확인 등) ----------

def put_pending(approval_id: str, payload: dict[str, Any]) -> None:
    data = _load(_PENDING)
    data[approval_id] = {"created_at": time.time(), **payload}
    _save(_PENDING, data)


def pop_pending(approval_id: str) -> dict[str, Any] | None:
    data = _load(_PENDING)
    item = data.pop(approval_id, None)
    _save(_PENDING, data)
    return item


def get_pending(approval_id: str) -> dict[str, Any] | None:
    return _load(_PENDING).get(approval_id)


# ---------- tasks (워크스페이스 실행 기록) ----------

def put_task(task_id: str, payload: dict[str, Any]) -> None:
    data = _load(_TASKS)
    data[task_id] = {"created_at": time.time(), **payload}
    _save(_TASKS, data)
    _index_thread(task_id, payload.get("channel"), payload.get("thread_ts"))


def update_task(task_id: str, **updates: Any) -> None:
    data = _load(_TASKS)
    if task_id in data:
        data[task_id].update(updates)
        _save(_TASKS, data)


def get_task(task_id: str) -> dict[str, Any] | None:
    return _load(_TASKS).get(task_id)


# ---------- 스레드 역인덱스 ----------

def _thread_key(channel: str | None, thread_ts: str | None) -> str | None:
    if not channel or not thread_ts:
        return None
    return f"{channel}:{thread_ts}"


def _index_thread(task_id: str, channel: str | None, thread_ts: str | None) -> None:
    key = _thread_key(channel, thread_ts)
    if not key:
        return
    data = _load(_THREADS)
    data[key] = task_id
    _save(_THREADS, data)


def find_task_by_thread(channel: str, thread_ts: str) -> dict[str, Any] | None:
    """스레드에서 들어온 멘션이 기존 태스크에 속하는지 조회."""
    key = _thread_key(channel, thread_ts)
    if not key:
        return None
    task_id = _load(_THREADS).get(key)
    if not task_id:
        return None
    task = get_task(task_id)
    if task:
        task = {"task_id": task_id, **task}
    return task


# ---------- cancel 레지스트리 (인메모리) ----------

def register_cancel(task_id: str, event: threading.Event, thread: threading.Thread) -> None:
    with _cancel_lock:
        _cancel_events[task_id] = event
        _task_threads[task_id] = thread


def get_cancel_event(task_id: str) -> threading.Event | None:
    with _cancel_lock:
        return _cancel_events.get(task_id)


def get_task_thread(task_id: str) -> threading.Thread | None:
    with _cancel_lock:
        return _task_threads.get(task_id)


def unregister_task(task_id: str) -> None:
    with _cancel_lock:
        _cancel_events.pop(task_id, None)
        _task_threads.pop(task_id, None)


# ---------- 슬러그 수정 대화 ----------

def put_slug_wait(user_id: str, payload: dict[str, Any]) -> None:
    data = _load(_DM_SLUG_WAIT)
    data[user_id] = {"created_at": time.time(), **payload}
    _save(_DM_SLUG_WAIT, data)


def pop_slug_wait(user_id: str) -> dict[str, Any] | None:
    data = _load(_DM_SLUG_WAIT)
    item = data.pop(user_id, None)
    _save(_DM_SLUG_WAIT, data)
    return item


def get_slug_wait(user_id: str) -> dict[str, Any] | None:
    return _load(_DM_SLUG_WAIT).get(user_id)
