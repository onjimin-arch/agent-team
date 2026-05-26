import os
import re
import threading

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from runner import run_agent_task

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])


def _dispatch(task: str, channel: str, thread_ts: str, say, client):
    if not task:
        say(
            "작업 내용을 입력해 주세요.\n예: `2026년 전기차 시장 분석해줘`",
            thread_ts=thread_ts,
        )
        return

    say(f"⏳ 에이전트 팀이 작업을 시작합니다.\n\n> {task}", thread_ts=thread_ts)

    def run_and_post():
        result_text = run_agent_task(task)
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=result_text,
        )

    threading.Thread(target=run_and_post, daemon=True).start()


@app.event("app_mention")
def handle_mention(event, say, client):
    raw_text = event.get("text", "")
    task = re.sub(r"<@[^>]+>\s*", "", raw_text).strip()
    _dispatch(task, event["channel"], event.get("ts"), say, client)


@app.event("message")
def handle_dm(event, say, client):
    # DM 채널(im)만 처리, 봇 자신의 메시지 및 서브타입(편집·삭제 등) 제외
    if event.get("channel_type") != "im":
        return
    if event.get("subtype") or event.get("bot_id"):
        return

    task = event.get("text", "").strip()
    _dispatch(task, event["channel"], event.get("ts"), say, client)


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    print("⚡ Slack 에이전트 봇 시작 (Socket Mode)")
    handler.start()
