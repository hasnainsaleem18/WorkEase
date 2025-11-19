"""
Draft Manager - AI-Powered Email Draft Generation

Generates contextually appropriate email drafts with tone matching
and learns from user edits and approvals.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class EmailDraft:
    """Generated email draft."""

    id: str
    original_message_id: str
    recipient: str
    subject: str
    body: str
    tone: str  # "formal", "casual", "friendly", "professional"
    confidence: float
    generated_at: datetime
    approved: bool = False
    edited: bool = False
    sent: bool = False


class DraftManager:
    """
    Manages AI-generated email draft suggestions.

    Analyzes incoming emails and generates appropriate responses
    with tone matching and context awareness.
    """

    # Important sender indicators
    IMPORTANT_DOMAINS = ["@company.com", "@client.com", "@boss.com"]
    IMPORTANT_KEYWORDS = ["ceo", "director", "manager", "lead", "vp", "president"]

    def __init__(self, llm: Any, learning_engine: Any) -> None:
        """
        Initialize the draft manager.

        Args:
            llm: Local LLM for draft generation
            learning_engine: Learning engine for personalization
        """
        self.llm = llm
        self.learning_engine = learning_engine
        self.drafts: list[EmailDraft] = []

    async def generate_draft(
        self,
        original_message: dict[str, Any],
        context: Optional[list[dict[str, Any]]] = None,
    ) -> EmailDraft:
        """
        Generate a draft reply for an email.

        Args:
            original_message: Original email data
            context: Previous conversation context

        Returns:
            Generated EmailDraft
        """
        try:
            # Determine sender importance
            sender = original_message.get("from", "")
            is_important = self._is_important_sender(sender)

            # Get user's preferred tone for this sender
            preferred_tone = await self.learning_engine.get_preferred_tone(sender)

            # Determine appropriate tone
            tone = preferred_tone or ("professional" if is_important else "friendly")

            # Build prompt for LLM
            prompt = self._build_draft_prompt(original_message, tone, context)

            # Generate draft
            draft_text = await self.llm.generate(prompt, system="You are a helpful email assistant.")

            # Create draft object
            draft = EmailDraft(
                id=f"draft_{datetime.now().timestamp()}",
                original_message_id=original_message.get("id", ""),
                recipient=sender,
                subject=f"Re: {original_message.get('subject', '')}",
                body=draft_text,
                tone=tone,
                confidence=0.8 if is_important else 0.9,
                generated_at=datetime.now(),
            )

            self.drafts.append(draft)
            logger.info(f"Draft generated for {sender} with {tone} tone")
            return draft

        except Exception as e:
            logger.error(f"Error generating draft: {e}", exc_info=True)
            raise

    def _is_important_sender(self, sender: str) -> bool:
        """
        Determine if sender is important.

        Args:
            sender: Sender email address

        Returns:
            True if sender is important
        """
        sender_lower = sender.lower()

        # Check domain
        if any(domain in sender_lower for domain in self.IMPORTANT_DOMAINS):
            return True

        # Check keywords
        if any(keyword in sender_lower for keyword in self.IMPORTANT_KEYWORDS):
            return True

        return False

    def _build_draft_prompt(
        self,
        original_message: dict[str, Any],
        tone: str,
        context: Optional[list[dict[str, Any]]],
    ) -> str:
        """
        Build LLM prompt for draft generation.

        Args:
            original_message: Original email
            tone: Desired tone
            context: Conversation context

        Returns:
            Formatted prompt
        """
        sender = original_message.get("from", "Unknown")
        subject = original_message.get("subject", "")
        body = original_message.get("body", "")

        context_str = ""
        if context:
            context_str = "\n\nPrevious conversation:\n" + "\n".join(
                [f"- {msg.get('snippet', '')}" for msg in context[-3:]]
            )

        prompt = f"""Generate a {tone} email reply to the following message.

From: {sender}
Subject: {subject}

Message:
{body}
{context_str}

Write a concise, {tone} reply that addresses the main points. Keep it under 150 words.
Reply:"""

        return prompt

    async def approve_draft(self, draft_id: str, edited_body: Optional[str] = None) -> bool:
        """
        Approve a draft for sending.

        Args:
            draft_id: Draft identifier
            edited_body: Optional edited version of the draft

        Returns:
            True if draft found and approved
        """
        for draft in self.drafts:
            if draft.id == draft_id:
                draft.approved = True

                if edited_body and edited_body != draft.body:
                    draft.edited = True
                    # Learn from the edit
                    await self.learning_engine.learn_from_edit(
                        original=draft.body, edited=edited_body, tone=draft.tone
                    )
                    draft.body = edited_body

                logger.info(f"Draft approved: {draft_id} (edited: {draft.edited})")
                return True

        return False

    async def reject_draft(self, draft_id: str, reason: Optional[str] = None) -> bool:
        """
        Reject a draft.

        Args:
            draft_id: Draft identifier
            reason: Optional rejection reason

        Returns:
            True if draft found
        """
        for draft in self.drafts:
            if draft.id == draft_id:
                # Learn from rejection
                await self.learning_engine.learn_from_rejection(draft.tone, reason)
                self.drafts.remove(draft)
                logger.info(f"Draft rejected: {draft_id}")
                return True

        return False

    def get_pending_drafts(self, limit: int = 10) -> list[EmailDraft]:
        """
        Get pending (unapproved) drafts.

        Args:
            limit: Maximum number of drafts

        Returns:
            List of pending drafts
        """
        pending = [d for d in self.drafts if not d.approved and not d.sent]
        return pending[-limit:]

    def mark_draft_sent(self, draft_id: str) -> bool:
        """
        Mark a draft as sent.

        Args:
            draft_id: Draft identifier

        Returns:
            True if draft found
        """
        for draft in self.drafts:
            if draft.id == draft_id:
                draft.sent = True
                logger.info(f"Draft marked as sent: {draft_id}")
                return True
        return False

    def get_draft_stats(self) -> dict[str, Any]:
        """
        Get draft generation statistics.

        Returns:
            Dictionary with stats
        """
        total = len(self.drafts)
        approved = sum(1 for d in self.drafts if d.approved)
        edited = sum(1 for d in self.drafts if d.edited)
        sent = sum(1 for d in self.drafts if d.sent)

        return {
            "total_generated": total,
            "approved": approved,
            "edited": edited,
            "sent": sent,
            "approval_rate": approved / total if total > 0 else 0,
            "edit_rate": edited / approved if approved > 0 else 0,
        }
