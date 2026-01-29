"""
Phone Agent - An AI-powered phone automation framework.

This package provides tools for automating Android and iOS phone interactions
using AI models for visual understanding and decision making.
"""

from phone_agent.agent import AgentConfig, PhoneAgent, StepResult
from phone_agent.agent_ios import IOSPhoneAgent
from phone_agent.evaluation import ScoreResult, ScoringConfig, TaskScorer
from phone_agent.utils import AgentLogger, LogConfig

__version__ = "0.1.0"
__all__ = [
    "PhoneAgent",
    "IOSPhoneAgent",
    "AgentConfig",
    "StepResult",
    "AgentLogger",
    "LogConfig",
    "TaskScorer",
    "ScoringConfig",
    "ScoreResult",
]
