"""
Healthcare MCP (Model Context Protocol) Server
Provides tools for diet planning, appointment booking, and health queries.
"""

from typing import Dict, Any, List, Optional
from backend.tools import diet, booking, general


# MCP Tool Registry with detailed schemas
tools = {
    "generate_diet": {
        "name": "generate_diet",
        "description": "Generate personalized AI-powered diet plans based on user preferences and health goals",
        "inputSchema": {
            "type": "object",
            "properties": {
                "preferences": {
                    "type": "string",
                    "description": "Dietary preferences (e.g., 'vegetarian', 'low-carb', 'diabetic-friendly')"
                },
                "calories": {
                    "type": "integer",
                    "description": "Target daily calorie intake"
                },
                "allergies": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of food allergies or restrictions"
                }
            },
            "required": ["preferences"]
        }
    },
    "book_appointment": {
        "name": "book_appointment",
        "description": "Book medical appointments with healthcare providers. Appointments are scheduled in 15-minute intervals.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "Unique identifier for the patient"
                },
                "date": {
                    "type": "string",
                    "description": "Appointment date (YYYY-MM-DD format)"
                },
                "time": {
                    "type": "string",
                    "description": "Appointment time in 15-minute intervals (HH:MM format, e.g., '09:00', '09:15', '09:30')"
                },
                "specialty": {
                    "type": "string",
                    "description": "Medical specialty (e.g., 'cardiology', 'general practice')"
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for visit"
                }
            },
            "required": ["user_id", "date", "time"]
        }
    },
    "general_query": {
        "name": "general_query",
        "description": "Answer general health and wellness questions with evidence-based information",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Health-related question to answer"
                },
                "context": {
                    "type": "string",
                    "description": "Additional context or patient information (optional)"
                }
            },
            "required": ["question"]
        }
    }
}


def get_available_tools() -> List[Dict[str, Any]]:
    """
    Return list of all available MCP tools with their schemas.
    
    Returns:
        List of tool definitions compatible with MCP protocol
    """
    return list(tools.values())


def call_tool(name: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Execute a tool by name with provided arguments.
    
    Args:
        name: Name of the tool to execute
        args: Dictionary of arguments for the tool
        
    Returns:
        Tool execution result or error message
        
    Raises:
        ValueError: If tool name is unknown or required arguments are missing
    """
    if args is None:
        args = {}
    
    # Validate tool exists
    if name not in tools:
        return {
            "error": f"Unknown tool: {name}",
            "available_tools": list(tools.keys())
        }
    
    try:
        # Route to appropriate tool handler
        if name == "generate_diet":
            preferences = args.get("preferences")
            if not preferences:
                return {"error": "Missing required parameter: preferences"}
            
            return diet.generate(
                preferences=preferences,
                calories=args.get("calories"),
                allergies=args.get("allergies", [])
            )
            
        elif name == "book_appointment":
            user_id = args.get("user_id")
            date = args.get("date")
            time = args.get("time")
            
            if not user_id or not date or not time:
                return {"error": "Missing required parameters: user_id, date, and time"}
            
            return booking.book(
                user_id=user_id,
                date=date,
                time=time,
                specialty=args.get("specialty"),
                reason=args.get("reason")
            )
            
        elif name == "general_query":
            question = args.get("question")
            if not question:
                return {"error": "Missing required parameter: question"}
            
            return general.answer(
                question=question,
                context=args.get("context")
            )
            
    except Exception as e:
        return {
            "error": f"Tool execution failed: {str(e)}",
            "tool": name
        }
    
    return {"error": "Tool handler not implemented"}


def validate_tool_args(tool_name: str, args: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate arguments against tool schema.
    
    Args:
        tool_name: Name of the tool
        args: Arguments to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if tool_name not in tools:
        return False, f"Unknown tool: {tool_name}"
    
    tool_schema = tools[tool_name]["inputSchema"]
    required_fields = tool_schema.get("required", [])
    
    for field in required_fields:
        if field not in args or args[field] is None:
            return False, f"Missing required field: {field}"
    
    return True, None
