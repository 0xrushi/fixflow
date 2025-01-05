from fastapi import FastAPI, HTTPException
from typing import Dict
from pydantic import BaseModel
from filesearch import llm_file_search
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

class VSCodeCommandRequest(BaseModel):
    command: str

# Initialize the agent with the OpenAI API key
agent = None
if "OPENAI_API_KEY" in os.environ:
    from typing import Dict, List, Optional, Type, Any
    from langchain_core.tools import BaseTool
    from langchain_openai import ChatOpenAI
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate
    from pydantic import BaseModel, Field
    import httpx
    import os
    
    class VSCodeControlTool(BaseTool):
        name: str
        description: str
        endpoint: str
        params: Optional[List[str]] = []
        base_url: str = "http://localhost:3000"

        def _run(self, **kwargs: Any) -> str:
            """Execute the VS Code control command synchronously."""
            import asyncio
            return asyncio.run(self._arun(**kwargs))

        async def _arun(self, **kwargs: Any) -> str:
            """Execute the VS Code control command asynchronously."""
            async with httpx.AsyncClient() as client:
                try:
                    if self.name == "open_file" and "path" in kwargs:
                        workspace_dir = os.getenv("WORKSPACE_DIR", "/Users/bread/Documents/vscodeproj/api-server")
                        
                        # Use llm_file_search to find the closest matching file
                        search_result = llm_file_search(
                            directory=workspace_dir,
                            search_term=kwargs["path"],
                            api_key=os.getenv("OPENAI_API_KEY")
                        )
                        
                        if "error" in search_result:
                            return {"status": "error", "message": f"File search error: {search_result['error']}"}
                        
                        if search_result.get("full_path"):
                            kwargs["path"] = search_result["full_path"]
                        else:
                            return {"status": "error", "message": "No matching file found"}
                    params = {k: kwargs[k] for k in self.params if k in kwargs}
                    response = await client.get(f"{self.base_url}/{self.endpoint}", params=params)
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPError as e:
                    return {"status": "error", "message": f"HTTP error occurred: {str(e)}"}
                except Exception as e:
                    return {"status": "error", "message": f"An error occurred: {str(e)}"}

    class VSCodeControlAgent:
        def __init__(self, openai_api_key: str):
            """Initialize the VS Code Control Agent."""
            self.llm = ChatOpenAI(
                api_key=openai_api_key,
                model="gpt-4o"
            )
            
            # Define all VS Code control tools
            self.tools = [
                VSCodeControlTool(
                    name="next_tab",
                    description="Switch to the next tab in VS Code",
                    endpoint="nextTab"
                ),
                VSCodeControlTool(
                    name="previous_tab",
                    description="Switch to the previous tab in VS Code",
                    endpoint="previousTab"
                ),
                VSCodeControlTool(
                    name="close_tab",
                    description="Close the current tab in VS Code",
                    endpoint="closeTab"
                ),
                VSCodeControlTool(
                    name="close_all_tabs",
                    description="Close all tabs in VS Code",
                    endpoint="closeAllTabs"
                ),
                VSCodeControlTool(
                    name="close_tabs_to_right",
                    description="Close all tabs to the right of the current tab",
                    endpoint="closeTabsToRight"
                ),
                VSCodeControlTool(
                    name="open_file",
                    description="Open a specific file. Required parameter: 'path' - the name or path of the file to open. The tool will automatically search for similar filenames if exact match not found.",
                    endpoint="openFile",
                    params=["path"]
                ),
                VSCodeControlTool(
                    name="list_open_tabs",
                    description="Get a list of all currently open tabs in VS Code",
                    endpoint="listOpenTabs"
                ),
                VSCodeControlTool(
                    name="go_to_tab",
                    description="Switch to a specific tab by providing its name",
                    endpoint="goToTabName",
                    params=["name"]
                ),
                VSCodeControlTool(
                    name="go_to_line",
                    description="Go to a specific line number in the current file",
                    endpoint="goToLine",
                    params=["line"]
                ),
                VSCodeControlTool(
                    name="get_recent_files",
                    description="Get a list of recently opened files in VS Code",
                    endpoint="recentFiles"
                ),
                VSCodeControlTool(
                    name="check_status",
                    description="Check if the VS Code extension is running",
                    endpoint="status"
                ),
                VSCodeControlTool(
                    name="list_windows",
                    description="Get a list of all open VS Code window titles",
                    endpoint="listWindows"
                ),
                VSCodeControlTool(
                    name="switch_window",
                    description="Switch to a specific VS Code window by its title",
                    endpoint="switchWindow",
                    params=["title"]
                ),
            ]

            self.prompt = ChatPromptTemplate.from_messages([
                (
                    "system",
                    """You are a VS Code control assistant that helps users manage their editor tabs, windows, and navigation.
                    You have access to several tools to control VS Code through natural language commands.
                    
                    Important guidelines:
                    1. Always check the status first before executing other commands to ensure the extension is running.
                    
                    2. When opening files:
                       - You MUST use the 'path' parameter with the open_file tool
                       - Example: If user says "open the config file", use open_file(path="config")
                       - The path can be a partial filename, relative path, or description
                       - The tool includes automatic file search functionality that will:
                         * Search for files matching the provided name or description
                         * Find similar filenames if exact match isn't found
                         * Search through the entire workspace recursively
                       - If initial open fails, don't give up - the search will try to find similar files
                       - Example handling:
                         * "open the main JavaScript file" -> open_file(path="main.js")
                         * "open the user config" -> open_file(path="user config")
                         * "open the API routes" -> open_file(path="api routes")
                    
                    3. When switching tabs:
                       - Use the 'name' parameter with go_to_tab
                       - Example: go_to_tab(name="index.js")
                    
                    4. When going to a specific line:
                       - Use the 'line' parameter with go_to_line
                       - Example: go_to_line(line="42")
                       
                    5. When managing windows:
                       - Use list_windows to get available windows first
                       - Use the 'title' parameter with switch_window
                       - Example: switch_window(title="project-name - VS Code")
                       - Window titles should match exactly what's returned by list_windows
                    
                    6. For better results:
                       - First list_open_tabs or get_recent_files if the user's request is ambiguous
                       - If file not found, try alternative search terms based on the user's description
                       - Consider file extensions when searching (.js, .py, .json, etc.)
                       - When switching windows, list available windows first if the target is unclear
                    
                    Always provide the required parameters for tools that need them. Never skip parameters that are marked as required in the tool descriptions. If a file isn't found immediately, the built-in search will help find the closest match."""
                ),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])

            self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True
            )

        async def execute(self, command: str) -> dict:
            """
            Execute a natural language command to control VS Code.
            
            Args:
                command (str): Natural language command for VS Code control
                
            Returns:
                dict: Response from the agent executor
            """
            return await self.agent_executor.ainvoke({"input": command})

    agent = VSCodeControlAgent(openai_api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/execute")
async def execute_command(request: VSCodeCommandRequest) -> Dict:
    if not agent:
        raise HTTPException(status_code=500, detail="VS Code agent not initialized")
    try:
        result = await agent.execute(request.command)
        return {"status": "success", "output": result["output"]}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def read_root():
    return {"message": "VS Code Control Server is running!"}