"""
FORGE Framework - Core Module

This module contains the orchestrator, event bus, AI components,
automation systems, and enterprise features for the AUTOCOM platform.
"""

# Core Components
from core.digest_generator import Digest, DigestGenerator
from core.draft_manager import DraftManager, EmailDraft
from core.event_bus import EventBus
from core.learning_engine import LearningEngine
from core.llm import LocalLLM
from core.multi_agent_coordinator import MultiAgentCoordinator, MultiStepCommand
from core.notification_hub import Notification, NotificationHub, Priority
from core.orchestrator import Intent, Orchestrator
from core.sentiment_analyzer import SentimentAnalysis, SentimentAnalyzer
from core.task_extractor import Task, TaskExtractor

# Enterprise Features
from core.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitBreakerManager,
    CircuitState,
    circuit_breaker,
    get_circuit_breaker_manager,
)
from core.dependency_injection import (
    DependencyContainer,
    Scope,
    ScopeContext,
    configure_container,
    get_container,
    inject,
)
from core.health_check import (
    AgentHealthCheck,
    DatabaseHealthCheck,
    EventBusHealthCheck,
    HealthCheck,
    HealthCheckManager,
    HealthCheckResult,
    HealthStatus,
    LLMHealthCheck,
)
from core.middleware import (
    AuthenticationMiddleware,
    CachingMiddleware,
    ErrorHandlingMiddleware,
    LoggingMiddleware,
    MetricsMiddleware,
    Middleware,
    MiddlewareStack,
    RateLimitMiddleware,
    create_development_stack,
    create_production_stack,
)

__all__ = [
    # Core Components
    "Orchestrator",
    "Intent",
    "EventBus",
    "LocalLLM",
    # Automation Components
    "NotificationHub",
    "Notification",
    "Priority",
    "TaskExtractor",
    "Task",
    "DraftManager",
    "EmailDraft",
    "LearningEngine",
    "SentimentAnalyzer",
    "SentimentAnalysis",
    "DigestGenerator",
    "Digest",
    "MultiAgentCoordinator",
    "MultiStepCommand",
    # Enterprise Features - Middleware
    "Middleware",
    "MiddlewareStack",
    "LoggingMiddleware",
    "AuthenticationMiddleware",
    "RateLimitMiddleware",
    "CachingMiddleware",
    "ErrorHandlingMiddleware",
    "MetricsMiddleware",
    "create_production_stack",
    "create_development_stack",
    # Enterprise Features - Dependency Injection
    "DependencyContainer",
    "Scope",
    "ScopeContext",
    "inject",
    "get_container",
    "configure_container",
    # Enterprise Features - Health Checks
    "HealthCheck",
    "HealthCheckManager",
    "HealthCheckResult",
    "HealthStatus",
    "DatabaseHealthCheck",
    "LLMHealthCheck",
    "AgentHealthCheck",
    "EventBusHealthCheck",
    # Enterprise Features - Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerManager",
    "CircuitBreakerError",
    "CircuitState",
    "circuit_breaker",
    "get_circuit_breaker_manager",
]
