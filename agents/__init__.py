"""
Agents Package for AutoReturn

This package contains all communication service agents.
Each agent is responsible for interfacing with a specific platform
(Gmail, Slack, etc.) and converting platform-specific messages to
the universal Message format used by the orchestrator.
"""

from .base_agent import Agent, BaseAgent, Message
from .gmail_agent import GmailAgent
from .slack_agent import SlackAgent, SlackMessage

__all__ = [
    "Agent",
    "BaseAgent",
    "Message",
    "GmailAgent",
    "SlackAgent",
    "SlackMessage",
]
