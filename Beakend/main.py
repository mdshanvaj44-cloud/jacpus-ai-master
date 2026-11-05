import os, sqlite3, json, uuid, time
from pathlib import Path
from typing import Optional
import httpx
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = os.getenv("DB_PATH", "/tmp/jacpus.db")
APP_SECRET = os.getenv("APP_SECRET", "CHANGE-ME-BEFORE-PRODUCTION")

app = FastAPI(title="JACPU-S Cloud Backend", version="1.0.0",
              description="Lightweight backend starter for JACPU-S AI Studio")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"]
)

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS projects(
            id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT DEFAULT '',
            created_at INTEGER NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS files(
            project_id TEXT NOT NULL, path TEXT NOT NULL, content TEXT NOT NULL,
            updated_at INTEGER NOT NULL, PRIMARY KEY(project_id,path))""")
init_db()

def auth(x_jacpus_token: Optional[str]):
    # Public health endpoint; protect mutating and private API operations.
    if not APP_SECRET or APP_SECRET == "CHANGE-ME-BEFORE-PRODUCTION":
        return
    if x_jacpus_token != APP_SECRET:
        raise HTTPException(401, "Invalid or missing JACPU-S token")

class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=2000)

class FileIn(BaseModel):
    content: str = Field(max_length=2_000_000)

class ChatIn(BaseModel):
    messages: list[dict] = Field(min_length=1)
    system: str = "You are JACPU-S AI, a helpful app and game development assistant. Work in small files and explain limitations honestly."
    max_tokens: int = Field(default=2000, ge=1, le=8000)

class SessionIn(BaseModel):
    build_id: str = "demo"
    gpu_profile: str = "not-configured"

@app.get("/")
def root():
    return {"service":"JACPU-S Cloud Backend","docs":"/docs","health":"/health"}

@app.get("/health")
def health():
    return {"ok":True,"service":"jacpus-backend","gpu_streaming":False,
            "gpu_status":"not_configured","ai_configured":bool(os.getenv("AI_API_KEY"))}

@app.get("/api/projects")
def list_projects(x_jacpus_token: Optional[str] = Header(default=None)):
    auth(x_jacpus_token)
    with db() as con:
        rows = con.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]

@app.post("/api/projects")
def create_project(data: ProjectIn, x_jacpus_token: Optional[str] = Header(default=None)):
    auth(x_jacpus_token)
    pid = str(uuid.uuid4())
    with db() as con:
        con.execute("INSERT INTO projects VALUES(?,?,?,?)",
                    (pid, data.name, data.description, int(time.time())))
    return {"id":pid,"name":data.name,"description":data.description}

@app.get("/api/projects/{project_id}/files")
def get_files(project_id: str, x_jacpus_token: Optional[str] = Header(default=None)):
    auth(x_jacpus_token)
    with db() as con:
        exists = con.execute("SELECT id FROM projects WHERE id=?", (project_id,)).fetchone()
        if not exists: raise HTTPException(404, "Project not found")
        rows = con.execute("SELECT path,content,updated_at FROM files WHERE project_id=?", (project_id,)).fetchall()
    return [dict(r) for r in rows]

@app.put("/api/projects/{project_id}/files/{file_path:path}")
def put_file(project_id: str, file_path: str, data: FileIn,
             x_jacpus_token: Optional[str] = Header(default=None)):
    auth(x_jacpus_token)
    if file_path.startswith("/") or ".." in Path(file_path).parts:
        raise HTTPException(400, "Invalid file path")
    with db() as con:
        exists = con.execute("SELECT id FROM projects WHERE id=?", (project_id,)).fetchone()
        if not exists: raise HTTPException(404, "Project not found")
        con.execute("""INSERT INTO files VALUES(?,?,?,?)
          ON CONFLICT(project_id,path) DO UPDATE SET content=excluded.content, updated_at=excluded.updated_at""",
          (project_id, file_path, data.content, int(time.time())))
    return {"ok":True,"path":file_path}

@app.post("/api/ai/chat")
async def ai_chat(data: ChatIn, x_jacpus_token: Optional[str] = Header(default=None)):
    auth(x_jacpus_token)
    base = os.getenv("AI_BASE_URL", "").rstrip("/")
    key = os.getenv("AI_API_KEY", "")
    model = os.getenv("AI_MODEL", "")
    if not (base and key and model):
        raise HTTPException(503, "AI provider not configured. Set AI_BASE_URL, AI_MODEL and AI_API_KEY in Render.")
    payload = {"model":model, "messages":[{"role":"system","content":data.system}, *data.messages],
               "max_tokens":data.max_tokens}
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            res = await client.post(base + "/chat/completions", json=payload,
                                    headers={"Authorization":f"Bearer {key}"})
        res.raise_for_status()
        return res.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(e.response.status_code, "AI provider returned an error")
    except Exception:
        raise HTTPException(502, "Could not reach AI provider")

@app.post("/api/sessions")
def create_session(data: SessionIn, x_jacpus_token: Optional[str] = Header(default=None)):
    auth(x_jacpus_token)
    # Honest placeholder: no GPU host or WebRTC streamer is provisioned yet.
    return {"ok":False,"session_id":None,"stream_url":None,
            "status":"gpu_not_configured",
            "message":"Connect a GPU host and WebRTC/browser streaming service to enable cloud gaming."}

@app.post("/api/sessions/{session_id}/stop")
def stop_session(session_id: str, x_jacpus_token: Optional[str] = Header(default=None)):
    auth(x_jacpus_token)
    return {"ok":True,"session_id":session_id,"status":"stopped"}
