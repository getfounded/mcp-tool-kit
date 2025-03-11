# In your server.py or a new file agent_api.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional

from agent_generator import create_agent

# Create FastAPI app
api_app = FastAPI()


class AgentCreate(BaseModel):
    name: str
    description: str
    code: str
    api_key: str  # Simple API key auth


@api_app.post("/agents")
async def create_new_agent(agent: AgentCreate, background_tasks: BackgroundTasks):
    """API endpoint to create a new agent"""
    # Verify API key
    if agent.api_key != os.environ.get("AGENT_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        # Create the agent file
        file_path = create_agent(agent.name, agent.description, agent.code)

        return {
            "status": "success",
            "message": f"Agent {agent.name} created successfully",
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating agent: {str(e)}")

# In your main server code, add:
# from fastapi import FastAPI
# app = FastAPI()
# app.mount("/api", api_app)
