"""
Priority Queue Server — Slack Webhook 수신 + 터미널 입력을 단일 큐로 통합하고
claude -p 로 Team Lead 를 트리거합니다.

우선순위 태그 (메시지 맨 앞):
  !urgent   → 0  즉시 실행
  !task     → 1  일반 (기본값)
  !schedule → 2  여유 있을 때
"""

import heapq
import json
import os
import subprocess
import threading
import time
from pathlib import Path
import yaml
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# slack-bot/.env 에서 토큰 로드 (이미 설정된 SLACK_BOT_TOKEN 재사용)
load_dotenv(Path(__file__).parent / "slack-bot" / ".env")

# ── 설정 로드 ──────────────────────────────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.dirname(__file__), ".claude", "configs", "queue-config.yaml")

def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

PRIORITY_MAP: dict[str, int] = config.get("priority", {"urgent": 0, "task": 1, "schedule": 2, "default": 1})
DEFAULT_PRIORITY: int = PRIORITY_MAP.get("default", 1)
PORT: int = config["slack"]["webhook_receive_port"]
MODEL: str = config["opencode"]["default_model"]

# ── Slack 역보고 설정 ──────────────────────────────────────────────────────
SLACK_BOT_TOKEN: str = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_REPORT_CHANNEL: str = os.environ.get("SLACK_REPORT_CHANNEL", "#agent-log")

_LEVEL_EMOJI = {
    "info":     "🟡",
    "progress": "🔄",
    "success":  "✅",
    "error":    "⚠️",
    "rollback": "🔴",
}


def slack_report(message: str, level: str = "info") -> bool:
    """
    Slack 채널에 진행상황 메시지 전송.
    level: info | success | error | progress | rollback
    SLACK_BOT_TOKEN 미설정 시 콘솔 출력으로 폴백.
    """
    emoji = _LEVEL_EMOJI.get(level, "🟡")
    full_msg = f"{emoji} {message}"
    if not SLACK_BOT_TOKEN:
        print(f"[slack_report] {full_msg}")
        return False
    try:
        resp = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={
                "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
                "Content-Type": "application/json; charset=utf-8",
            },
            json={"channel": SLACK_REPORT_CHANNEL, "text": full_msg},
            timeout=5,
        )
        data = resp.json()
        if not data.get("ok"):
            print(f"[slack_report] Slack API 오류: {data.get('error')}")
            return False
        return True
    except Exception as e:
        print(f"[slack_report] 전송 실패: {e}")
        return False


# ── Priority Queue (thread-safe) ───────────────────────────────────────────
_queue: list = []          # heapq: (priority, seq, task_text)
_queue_lock = threading.Lock()
_seq_counter = 0           # 동일 priority 내 FIFO 보장


def _parse_priority(text: str) -> tuple[int, str]:
    """메시지 앞 !태그 파싱. 태그 제거 후 (priority, cleaned_text) 반환."""
    for tag, prio in [("!urgent", PRIORITY_MAP["urgent"]),
                      ("!task",   PRIORITY_MAP["task"]),
                      ("!schedule", PRIORITY_MAP["schedule"])]:
        if text.strip().startswith(tag):
            return prio, text.strip()[len(tag):].strip()
    return DEFAULT_PRIORITY, text.strip()


def enqueue(task_text: str, priority: int | None = None) -> dict:
    global _seq_counter
    if priority is None:
        priority, task_text = _parse_priority(task_text)
    with _queue_lock:
        _seq_counter += 1
        heapq.heappush(_queue, (priority, _seq_counter, task_text))

    # 작업 수신 보고
    summary = task_text[:80] + ("..." if len(task_text) > 80 else "")
    if "[AUTO:" in task_text:
        slug = task_text.split("]")[0].replace("[AUTO:", "").strip()
    else:
        slug = f"seq-{_seq_counter}"
    slack_report(f"[작업 시작] {slug} — {summary}", "info")

    return {"queued": True, "priority": priority, "seq": _seq_counter, "task": task_text}


def queue_status() -> dict:
    with _queue_lock:
        items = [{"priority": p, "seq": s, "task": t} for p, s, t in _queue]
    return {"queue_length": len(items), "items": items}


# ── Task Runner (백그라운드 루프) ──────────────────────────────────────────
_running = False


def _runner_loop():
    while _running:
        item = None
        with _queue_lock:
            if _queue:
                item = heapq.heappop(_queue)
        if item:
            priority, seq, task_text = item
            print(f"[runner] seq={seq} priority={priority} → {task_text[:80]}")
            _run_opencode(task_text, seq)
        else:
            time.sleep(1)


def _run_opencode(task_text: str, seq: int):
    start = time.time()
    cmd = ["claude", "-p", task_text, "--model", MODEL]
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        elapsed = int(time.time() - start)
        if result.returncode != 0:
            print(f"[runner] claude exited with code {result.returncode}")
            slack_report(f"[작업 오류] seq={seq} — exit code {result.returncode}", "error")
        else:
            if "[AUTO:" in task_text:
                slug = task_text.split("]")[0].replace("[AUTO:", "").strip()
            else:
                slug = f"seq-{seq}"
            slack_report(
                f"[작업 완료] {slug} | 소요: {elapsed}s | 산출물: output/{slug}/final/final-artifact.md",
                "success",
            )
    except FileNotFoundError:
        slack_report("[오류] 'claude' 명령을 찾을 수 없습니다. PATH를 확인하세요.", "error")
        print("[runner] ERROR: 'claude' 명령을 찾을 수 없습니다.")
    except Exception as e:
        slack_report(f"[오류] {e}", "error")
        print(f"[runner] ERROR: {e}")


def start_runner():
    global _running
    _running = True
    t = threading.Thread(target=_runner_loop, daemon=True)
    t.start()
    return t


# ── Flask 앱 ───────────────────────────────────────────────────────────────
app = Flask(__name__)


@app.route("/slack/events", methods=["POST"])
def slack_events():
    """Slack Events API / Incoming Webhook 수신."""
    data = request.get_json(silent=True) or {}

    # Slack URL verification challenge
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data["challenge"]})

    # Slack Events API: message 이벤트
    event = data.get("event", {})
    text = event.get("text", "")
    if not text:
        # Slack Bot token 검증용 ping — 무시
        return jsonify({"ok": True})

    result = enqueue(text)
    return jsonify(result), 202


@app.route("/task", methods=["POST"])
def add_task():
    """터미널 또는 외부에서 직접 태스크 주입.

    Body (JSON): {"task": "...", "priority": 0|1|2}  (priority 생략 가능)
    """
    data = request.get_json(silent=True) or {}
    task_text = data.get("task", "").strip()
    if not task_text:
        return jsonify({"error": "task field is required"}), 400
    explicit_priority = data.get("priority")
    result = enqueue(task_text, priority=explicit_priority)
    return jsonify(result), 202


@app.route("/report", methods=["POST"])
def report():
    """
    opencode(Team Lead) 또는 deploy-heal 스킬이 배포 단계별 보고를 push하는 엔드포인트.

    Body (JSON): {"message": "...", "level": "info|success|error|progress|rollback"}
    """
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    level   = data.get("level", "info")
    if not message:
        return jsonify({"error": "message required"}), 400
    ok = slack_report(message, level)
    return jsonify({"ok": ok}), 200


@app.route("/status", methods=["GET"])
def status():
    """큐 상태 확인."""
    return jsonify(queue_status())


# ── 진입점 ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    start_runner()
    print(f"[queue_server] 포트 {PORT} 에서 시작. /status, /task, /slack/events, /report")
    app.run(host="0.0.0.0", port=PORT, debug=False)
