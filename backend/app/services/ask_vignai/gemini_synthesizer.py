"""
Gemini Synthesizer and Deterministic Fallback Engine for Ask VIGNAI.
Grounds responses strictly on authorized tool execution results with zero hallucination.
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List
from app.config import settings

logger = logging.getLogger(__name__)

VIGNAI_SYSTEM_PROMPT = """You are VIGNAI, the intelligent AI campus operating system assistant for Vignan University.

Your job is to provide clear, helpful, and natural conversational answers to students, faculty, and institutional administrators.

STRICT OPERATIONAL RULES:
1. Ground your answers strictly on the provided verified TOOL EVIDENCE.
2. NEVER invent, modify, or hallucinate numbers, percentages, attendance logs, exam dates, marks, job openings, or pattern statistics.
3. If a tool result is provided, explain it naturally and accurately.
4. If a piece of data is missing or not connected, state clearly that it is not available.
5. NEVER infer guilt or take sides on student/faculty complaints.
6. NEVER disclose protected student identities, passwords, or personal records of other students.
7. For General Knowledge questions (e.g. "What is recursion in C?", "What is photosynthesis?"), explain clearly with structured code blocks and examples.
8. Output clean conversational markdown (using bolding, clean bullet points, and code blocks). NEVER output raw internal schema tags or diagnostic template headings.
"""


class SynthesisResult:
    def __init__(
        self,
        answer: str,
        provider: str,
        model: str,
        provider_status: str,
        latency_ms: Optional[float] = None,
    ):
        self.answer = answer
        self.provider = provider
        self.model = model
        self.provider_status = provider_status
        self.latency_ms = latency_ms


class GeminiSynthesizer:
    """Invokes Google Gemini 3.6 Flash with tool-grounded context using the modern Interactions API."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL or "gemini-3.6-flash"

    def synthesize(
        self,
        query: str,
        user_role: str,
        intent: str,
        tool_name: Optional[str],
        tool_evidence: Optional[Dict[str, Any]],
        fallback_answer: str,
    ) -> SynthesisResult:
        if not self.api_key or not self.api_key.strip():
            logger.info("GEMINI_API_KEY is missing. Using deterministic heuristic synthesis.")
            return SynthesisResult(
                answer=fallback_answer,
                provider="local_heuristic",
                model="vignex-nlp-rules-v2",
                provider_status="fallback",
                latency_ms=0.0,
            )

        t0 = time.time()
        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)

            prompt_parts = [
                f"User Role: {user_role.upper()}\n",
                f"User Query: {query}\n",
                f"Classified Intent: {intent}\n",
            ]

            if tool_name and tool_evidence:
                prompt_parts.append(f"Tool Used: {tool_name}\n")
                prompt_parts.append(f"Verified Tool Output Data:\n```json\n{json.dumps(tool_evidence, indent=2, default=str)}\n```\n")
            else:
                prompt_parts.append("No campus database tool required (General Knowledge / Conversational).\n")

            prompt_parts.append(
                "\nSynthesize a clear, natural, friendly, and grounded conversational response. Never expose internal JSON schemas, tool names, or raw system tokens."
            )

            prompt_input = "".join(prompt_parts)
            answer_text = None

            # Primary: Modern Interactions API
            try:
                interaction = client.interactions.create(
                    model=self.model_name,
                    input=prompt_input,
                    system_instruction=VIGNAI_SYSTEM_PROMPT,
                )
                if interaction and interaction.output_text:
                    answer_text = interaction.output_text.strip()
            except Exception as inter_err:
                logger.info(f"Interactions API fallback to Chat: {inter_err}")

            # Secondary fallback: Modern Chat API without AFC warnings
            if not answer_text:
                chat = client.chats.create(model=self.model_name)
                resp = chat.send_message(f"{VIGNAI_SYSTEM_PROMPT}\n\n{prompt_input}")
                if resp and resp.text:
                    answer_text = resp.text.strip()

            latency = round((time.time() - t0) * 1000, 2)
            if answer_text:
                return SynthesisResult(
                    answer=answer_text,
                    provider="gemini",
                    model=self.model_name,
                    provider_status="live",
                    latency_ms=latency,
                )
            else:
                raise ValueError("Empty response from Gemini API")

        except Exception as exc:
            latency = round((time.time() - t0) * 1000, 2)
            logger.warning(
                f"Gemini API synthesis failed ({exc}). Gracefully activating local heuristic fallback.",
                exc_info=True,
            )
            return SynthesisResult(
                answer=fallback_answer,
                provider="local_heuristic",
                model="vignex-nlp-rules-v2",
                provider_status="fallback",
                latency_ms=latency,
            )


gemini_synthesizer = GeminiSynthesizer()
