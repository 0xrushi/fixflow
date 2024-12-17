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
            model="gpt-3.5-turbo-0125"
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
                description="Open a specific file in VS Code by providing its path",
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
            )
        ]

        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                """You are a VS Code control assistant that helps users manage their editor tabs and navigation.
                Use the available tools to help users control VS Code through natural language commands.
                Always check the status first before executing other commands to ensure the extension is running."""
            ),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        # Create the agent and executor
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

# Example usage
async def main():
    # Initialize the agent
    agent = VSCodeControlAgent(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    # Example commands
    commands = [
        "Check if VS Code extension is running",
        "Show me all open tabs",
        "close app.py tab"
        # "Close all tabs except the current one",
    ]
    
    for command in commands:
        print(f"\nExecuting: {command}")
        try:
            result = await agent.execute(command)
            print(f"Result: {result['output']}")
        except Exception as e:
            print(f"Error executing command: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())