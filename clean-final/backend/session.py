"""
Session management for the Pocket AI e-commerce agent.
This module handles user sessions and chat history.
"""

import uuid
from typing import Dict, List, Tuple, Any, Optional


# In-memory session storage
sessions = {}


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return str(uuid.uuid4())


def get_session(session_id: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """
    Get or create a session.
    
    Args:
        session_id: Optional session ID. If None or invalid, a new session is created.
        
    Returns:
        A tuple of (session_id, session_data)
    """
    if not session_id or session_id not in sessions:
        # Create new session
        session_id = generate_session_id()
        sessions[session_id] = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are Pocket AI, a helpful shopping assistant for an e-commerce website. "
                               "You help users find products, answer questions about shopping, and provide "
                               "recommendations. Be concise, friendly, and helpful. If asked about products, "
                               "focus on those that would be found in our store catalog."
                }
            ]
        }
    
    return session_id, sessions[session_id]


def add_message_to_session(session_id: str, role: str, content: str) -> None:
    """
    Add a message to a session's chat history.
    
    Args:
        session_id: The session ID
        role: Message role (user, assistant, system)
        content: Message content
    """
    if session_id in sessions:
        sessions[session_id]["messages"].append({
            "role": role,
            "content": content
        })


def get_session_messages(session_id: str) -> List[Dict[str, str]]:
    """
    Get all messages from a session.
    
    Args:
        session_id: The session ID
        
    Returns:
        A list of message objects with role and content
    """
    if session_id in sessions:
        return sessions[session_id]["messages"]
    return [] 