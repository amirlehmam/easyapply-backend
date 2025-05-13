from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from backend.bot_runner import BotRunner
import asyncio
import logging

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths (adjust as needed)
BOT_SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'main.py'))
LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs', 'activity.log.jsonl'))
bot_runner = BotRunner(BOT_SCRIPT_PATH, LOG_PATH)

@app.get("/")
def root():
    return {"message": "EasyApply Bot API is running."}

@app.get("/logs")
def get_logs():
    log_path = os.path.join("logs", "activity.log.jsonl")
    if not os.path.exists(log_path):
        return JSONResponse(content={"logs": []})
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    logs = [line.strip() for line in lines if line.strip()]
    return JSONResponse(content={"logs": logs})

@app.post("/start-bot")
def start_bot():
    print("/start-bot endpoint called")
    logging.info("/start-bot endpoint called")
    if bot_runner.is_running():
        print("Bot is already running")
        return {"status": "already_running"}
    try:
        started = bot_runner.start()
        print(f"BotRunner.start() returned: {started}")
        logging.info(f"BotRunner.start() returned: {started}")
        if not started:
            return {"status": "failed", "error": "BotRunner.start() returned False"}
        return {"status": "started"}
    except Exception as e:
        print(f"Exception in /start-bot: {e}")
        logging.error(f"Exception in /start-bot: {e}")
        return {"status": "failed", "error": str(e)}

@app.post("/stop-bot")
def stop_bot():
    stopped = bot_runner.stop()
    return {"status": "stopped" if stopped else "not_running"}

@app.get("/status")
def status():
    return {"running": bot_runner.is_running()}

@app.websocket("/logs/stream")
async def websocket_log_stream(websocket: WebSocket):
    await websocket.accept()
    log_path = LOG_PATH
    last_size = 0
    try:
        while True:
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    f.seek(last_size)
                    new_lines = f.readlines()
                    if new_lines:
                        for line in new_lines:
                            await websocket.send_text(line.strip())
                    last_size = f.tell()
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass

@app.get("/config")
def get_config():
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.yaml'))
    if not os.path.exists(config_path):
        return JSONResponse(content={"content": ""})
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()
    return JSONResponse(content={"content": content})

@app.post("/config")
def save_config(request: Request):
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.yaml'))
    data = request.json() if hasattr(request, 'json') else None
    if not data:
        data = request._json
    content = data.get("content", "")
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)
    return {"status": "saved"}

# More endpoints (start/stop bot, websocket for logs) will be added next. 