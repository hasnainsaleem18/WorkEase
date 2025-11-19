"""
MIND-Model Framework

Mesh Integration Networked Development Model - A non-linear SDLC framework.
"""

from mind_model.core import MINDModel, Node, NodeState, Transition
from mind_model.nodes import (
    ArchitectureReviewNode,
    CapacityPlanningNode,
    CodingNode,
    ComplianceNode,
    DeploymentNode,
    DesignNode,
    DocumentationNode,
    FeedbackAnalyticsNode,
    IncidentResponseNode,
    KnowledgeManagementNode,
    MaintenanceNode,
    OperationsNode,
    PerformanceNode,
    RequirementsNode,
    SecurityNode,
    TestingNode,
    UXNode,
)
from mind_model.tiers import EnterpriseTier, LightTier, StandardTier, Tier

__version__ = "2.0.0"

__all__ = [
    # Core
    "MINDModel",
    "Node",
    "NodeState",
    "Transition",
    # Tiers
    "Tier",
    "LightTier",
    "StandardTier",
    "EnterpriseTier",
    # Nodes
    "RequirementsNode",
    "DesignNode",
    "CodingNode",
    "TestingNode",
    "DeploymentNode",
    "MaintenanceNode",
    "SecurityNode",
    "DocumentationNode",
    "OperationsNode",
    "UXNode",
    "FeedbackAnalyticsNode",
    "PerformanceNode",
    "ComplianceNode",
    "ArchitectureReviewNode",
    "IncidentResponseNode",
    "CapacityPlanningNode",
    "KnowledgeManagementNode",
]
