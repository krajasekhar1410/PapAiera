"""
PapAiEra Copilot
=================
An Expert System / Copilot powered by the Handbook of Pulping and Papermaking.
Allows for conversational querying and DCS data troubleshooting.
"""

from .rag_engine import CopilotPapaiera
from .builder import KnowledgeBuilder

__all__ = ['CopilotPapaiera', 'KnowledgeBuilder']
