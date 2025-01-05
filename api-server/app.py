from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn
from typing import Optional, List, Dict, Union
from pydantic import BaseModel
from win import get_vscode_windows, switch_to_window
from dotenv import load_dotenv
load_dotenv()

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
VSCODE_SERVER = "http://localhost:3068"


class CommandResponse(BaseModel):
    status: str
    command: str
    message: Optional[str] = None


class RecentFile(BaseModel):
    path: Optional[str]
    label: str


class TabInfo(BaseModel):
    groupIndex: int
    isActive: bool
    label: str
    path: Optional[str]


class RecentFilesResponse(BaseModel):
    status: str
    command: str
    files: List[RecentFile]


class TabListResponse(BaseModel):
    status: str
    command: str
    tabs: List[TabInfo]
    

class WindowInfo(BaseModel):
    name: str

class WindowListResponse(BaseModel):
    status: str
    windows: List[str]


async def forward_to_vscode(command: str, params: Dict = None) -> dict:
    """Forward command to VS Code extension server."""
    async with httpx.AsyncClient() as client:
        try:
            url = f"{VSCODE_SERVER}/{command}"
            response = await client.get(url, params=params)
            data = response.json()

            # If the response indicates an error, ensure it includes the command
            if data.get("status") == "error":
                data["command"] = command

            return data
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail="VS Code extension not running. Please start the extension in VS Code first (press F5 in the extension project)",
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


@app.get("/openFile", response_model=CommandResponse)
async def open_file(path: str):
    """Open a file in VS Code using its path."""
    if not path:
        raise HTTPException(status_code=400, detail="File path must be provided")
    return await forward_to_vscode("openFile", {"path": path})


@app.get("/listOpenTabs", response_model=TabListResponse)
async def list_open_tabs():
    """Get a list of all open tabs in VS Code."""
    return await forward_to_vscode("listOpenTabs")


@app.get("/goToTabName", response_model=CommandResponse)
async def go_to_tab_name(name: str):
    """Switch to a specific tab by its name."""
    if not name:
        raise HTTPException(status_code=400, detail="Tab name must be provided")
    return await forward_to_vscode("goToTabName", {"name": name})


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
        return {"status": "disconnected", "message": "VS Code extension is not running"}


@app.get("/listWindows", response_model=WindowListResponse)
async def list_windows():
    """Get a list of all open VSCode windows."""
    windows = get_vscode_windows()
    return {"status": "success", "windows": windows}

@app.get("/switchWindow", response_model=CommandResponse)
async def switch_window(title: str):
    """Switch to a specific VSCode window by its title."""
    if not title:
        raise HTTPException(status_code=400, detail="Window title must be provided")
    
    success = switch_to_window(title)
    if success:
        return {"status": "success", "command": "switchWindow", "message": f"Switched to window: {title}"}
    else:
        raise HTTPException(status_code=404, detail=f"Window '{title}' not found or failed to switch")


if __name__ == "__main__":
    print("Starting VS Code Control API...")
    print("\nAvailable endpoints:")
    print("- GET /listWindows")
    print("- GET /switchWindow?name=<window_title>")
    print("- GET /nextTab")
    print("- GET /previousTab")
    print("- GET /closeTab")
    print("- GET /closeAllTabs")
    print("- GET /closeTabsToRight")
    print("- GET /openFile?path=<path>")
    print("- GET /listOpenTabs")
    print("- GET /goToTabName?name=<name>")
    print("- GET /goToLine?line=<number>")
    print("- GET /recentFiles")
    print("- GET /status")

    uvicorn.run(app, host="0.0.0.0", port=3000)
