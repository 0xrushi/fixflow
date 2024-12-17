from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn
from typing import Optional, List, Dict
from pydantic import BaseModel

app = FastAPI(title="VS Code Tab Control API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# VS Code extension server URL
VSCODE_SERVER = "http://localhost:3001"

class CommandResponse(BaseModel):
    status: str
    command: str
    message: Optional[str] = None

class RecentFile(BaseModel):
    path: str
    label: str

class RecentFilesResponse(BaseModel):
    status: str
    command: str
    files: List[RecentFile]

async def forward_to_vscode(command: str, params: Dict = None) -> dict:
    """Forward command to VS Code extension server."""
    async with httpx.AsyncClient() as client:
        try:
            url = f"{VSCODE_SERVER}/{command}"
            response = await client.get(url, params=params)
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail="VS Code extension not running. Please start the extension in VS Code first (press F5 in the extension project)"
            )

@app.get("/nextTab", response_model=CommandResponse)
async def next_tab():
    """Switch to next tab in VS Code."""
    return await forward_to_vscode("nextTab")

@app.get("/previousTab", response_model=CommandResponse)
async def previous_tab():
    """Switch to previous tab in VS Code."""
    return await forward_to_vscode("previousTab")

@app.get("/closeTab", response_model=CommandResponse)
async def close_tab():
    """Close current tab in VS Code."""
    return await forward_to_vscode("closeTab")

@app.get("/closeAllTabs", response_model=CommandResponse)
async def close_all_tabs():
    """Close all tabs in VS Code."""
    return await forward_to_vscode("closeAllTabs")

@app.get("/closeTabsToRight", response_model=CommandResponse)
async def close_tabs_to_right():
    """Close all tabs to the right of current tab in VS Code."""
    return await forward_to_vscode("closeTabsToRight")

@app.get("/goToLine", response_model=CommandResponse)
async def go_to_line(line: int):
    """Go to specific line in current file."""
    if line < 1:
        raise HTTPException(status_code=400, detail="Line number must be positive")
    return await forward_to_vscode("goToLine", {"line": line})

@app.get("/recentFiles", response_model=RecentFilesResponse)
async def get_recent_files():
    """Get list of recently opened files."""
    return await forward_to_vscode("recentFiles")

@app.get("/status")
async def check_status():
    """Check if VS Code extension is running."""
    try:
        async with httpx.AsyncClient() as client:
            await client.get(VSCODE_SERVER)
            return {"status": "connected", "message": "VS Code extension is running"}
    except httpx.RequestError:
        return {
            "status": "disconnected",
            "message": "VS Code extension is not running"
        }

if __name__ == "__main__":
    print("Starting VS Code Control API...")
    print("\nAvailable endpoints:")
    print("- GET /nextTab")
    print("- GET /previousTab")
    print("- GET /closeTab")
    print("- GET /closeAllTabs")
    print("- GET /closeTabsToRight")
    print("- GET /goToLine?line=<number>")
    print("- GET /recentFiles")
    print("- GET /status")
    
    uvicorn.run(app, host="0.0.0.0", port=3000)