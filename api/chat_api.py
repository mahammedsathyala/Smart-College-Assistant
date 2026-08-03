"""
Smart College Assistant — Chat API Blueprint
The AI chatbot endpoint using multi-agent routing and conversation memory.
"""

from __future__ import annotations
import json
from datetime import datetime

from flask import Blueprint, request, jsonify, session

from agents.coordinator_agent import get_coordinator
from database.models import ChatHistory, get_session as db_session
from utils.validators import sanitize_chat_input, validate_required_fields
from utils.logger import setup_logger, get_ai_logger

logger = setup_logger(__name__)
ai_logger = get_ai_logger()

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")

# ── In-memory conversation history (keyed by session_id) ─────
_conversations: dict[str, list[dict]] = {}


def _get_history(session_id: str) -> list[dict]:
    return _conversations.get(session_id, [])


def _add_to_history(session_id: str, role: str, content: str) -> None:
    if session_id not in _conversations:
        _conversations[session_id] = []
    _conversations[session_id].append({"role": role, "content": content})
    # Keep last 20 turns
    _conversations[session_id] = _conversations[session_id][-20:]


def _save_to_db(
    user_id: int | None,
    session_id: str,
    role: str,
    content: str,
    agent_used: str = "",
    confidence: float = 0.0,
    sources: list | None = None,
) -> None:
    """Persist chat turn to database."""
    try:
        db = db_session()
        entry = ChatHistory(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content,
            agent_used=agent_used,
            confidence=confidence,
            sources=json.dumps(sources or []),
            timestamp=datetime.utcnow(),
        )
        db.add(entry)
        db.commit()
        db.close()
    except Exception as e:
        logger.error("Failed to save chat to DB: %s", e)


@chat_bp.route("/message", methods=["POST"])
def send_message():
    """
    POST /api/chat/message
    Body: {"message": str, "session_id": str (optional)}
    Returns: AI-generated response with agent info.
    """
    data = request.get_json(silent=True) or {}
    valid, msg = validate_required_fields(data, ["message"])
    if not valid:
        return jsonify({"success": False, "error": msg}), 400

    raw_message = sanitize_chat_input(data.get("message", ""))
    if not raw_message:
        return jsonify({"success": False, "error": "Message cannot be empty."}), 400

    session_id = data.get("session_id") or session.get("session_id", "anonymous")
    user_id = session.get("user_id")

    # Retrieve conversation history
    history = _get_history(session_id)
    _add_to_history(session_id, "user", raw_message)
    _save_to_db(user_id, session_id, "user", raw_message)

    ai_logger.info("Chat message | session=%s | message='%s'", session_id, raw_message[:80])

    try:
        coordinator = get_coordinator()
        result = coordinator.handle(
            query=raw_message,
            history=history,
            context={"user_id": user_id},
        )

        answer = result.get("answer", "I'm sorry, I couldn't process your request.")
        agent = result.get("agent", "unknown")
        confidence = result.get("confidence", 0.0)
        sources = result.get("sources", [])
        routed_to = result.get("routed_to", agent)

        _add_to_history(session_id, "assistant", answer)
        _save_to_db(
            user_id, session_id, "assistant", answer,
            agent_used=agent, confidence=confidence, sources=sources,
        )

        ai_logger.info(
            "Chat response | agent=%s | confidence=%.2f | session=%s",
            routed_to, confidence, session_id,
        )

        return jsonify({
            "success": True,
            "response": answer,
            "agent": routed_to,
            "confidence": confidence,
            "sources": sources,
        })

    except Exception as e:
        logger.error("Chat error: %s", e)
        return jsonify({
            "success": True,
            "response": (
                "I apologize for the technical difficulty. 😔 "
                "Please try again or contact the helpdesk at helpdesk@smartcollege.edu"
            ),
            "agent": "fallback",
            "confidence": 0.0,
            "sources": [],
        })


@chat_bp.route("/history", methods=["GET"])
def get_chat_history():
    """GET /api/chat/history — Return session chat history."""
    session_id = request.args.get("session_id") or session.get("session_id", "anonymous")
    history = _get_history(session_id)
    return jsonify({"success": True, "history": history})


@chat_bp.route("/clear", methods=["POST"])
def clear_history():
    """POST /api/chat/clear — Clear conversation memory."""
    session_id = request.json.get("session_id") if request.json else None
    if session_id and session_id in _conversations:
        del _conversations[session_id]
    return jsonify({"success": True, "message": "Chat history cleared."})


@chat_bp.route("/suggestions", methods=["GET"])
def get_suggestions():
    """GET /api/chat/suggestions — Return quick reply suggestions."""
    suggestions = [
        "What documents are needed for admission?",
        "How is CGPA calculated?",
        "When are the placement drives?",
        "What is the attendance requirement?",
        "How do I get my hall ticket?",
        "What scholarships are available?",
        "Tell me about hostel facilities",
        "What are the library rules?",
    ]
    return jsonify({"success": True, "suggestions": suggestions})
