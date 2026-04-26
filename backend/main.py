
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from backend.mcp import tools, call_tool, get_available_tools
from typing import Dict, Any
import logging
import json
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()
app = FastAPI(
    title="Healthcare MCP API",
    description="Model Context Protocol API for Healthcare Management",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
def api_info():
    return {
        "message": "Healthcare MCP API",
        "endpoints": {
            "tools": "/mcp/tools",
            "call": "/mcp/call",
            "docs": "/docs"
        }
    }

@app.get("/mcp/tools")
def list_tools():
    """Get all available MCP tools with their schemas"""
    return {"tools": get_available_tools()}

@app.post("/mcp/call")
def mcp_call(payload: Dict[str, Any] = Body(...)):
    """
    Execute an MCP tool with provided arguments
    
    Request body:
    {
        "name": "tool_name",
        "args": { ... }
    }
    """
    name = payload.get("name")
    args = payload.get("args", {})
    
    if not name:
        logger.error("❌ Missing 'name' field in request")
        return {"error": "Missing 'name' field in request"}
    
    # Log the incoming request
    logger.info("=" * 80)
    logger.info(f"🔧 TOOL CALL: {name}")
    logger.info(f"📥 INPUT ARGS:")
    for key, value in args.items():
        logger.info(f"   • {key}: {value}")
    logger.info("-" * 80)
    
    # Execute the tool
    result = call_tool(name, args)
    
    # Log the response
    if "error" in result:
        logger.error(f"❌ ERROR: {result.get('error')}")
        if "suggestion" in result:
            logger.info(f"💡 SUGGESTION: {result.get('suggestion')}")
    else:
        logger.info(f"✅ SUCCESS")
        logger.info(f"📤 OUTPUT:")
        
        # Pretty print the result
        if name == "book_appointment" and "confirmation_number" in result:
            logger.info(f"   🎫 Confirmation: {result['confirmation_number']}")
            logger.info(f"   👤 Patient: {result.get('details', {}).get('Patient ID', 'N/A')}")
            logger.info(f"   📅 Time: {result.get('details', {}).get('Appointment Time', 'N/A')}")
        elif name == "generate_diet" and "plan" in result:
            logger.info(f"   🥗 Diet: {result.get('preference', 'N/A')}")
            logger.info(f"   📊 Calories: {result.get('daily_calories', 'N/A')}")
            if result.get('plan'):
                logger.info(f"   📋 Meals: {len(result['plan']) if isinstance(result['plan'], dict) else 'Generated'}")
        elif name == "general_query" and "answer" in result:
            answer_preview = result['answer'][:100] + "..." if len(result['answer']) > 100 else result['answer']
            logger.info(f"   💬 Answer: {answer_preview}")
    
    logger.info("=" * 80)
    logger.info("")
    
    return result

# ── Serve Frontend ──────────────────────────────────────────────────────
# Mount frontend static files (must be after API routes)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

@app.get("/")
def serve_frontend():
    """Serve the frontend index.html"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# Mount static assets from frontend/ at /assets (for future CSS/JS files)
if os.path.isdir(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="frontend-assets")
