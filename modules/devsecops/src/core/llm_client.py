"""
DevSecOps Module - LLM Client
Local-first AI inference via Ollama (codellama:13b-instruct).
No cloud APIs permitted (Zero-Trust Architecture).
"""

from typing import Optional, Dict, Any
from .config import settings
from .logger import get_logger

logger = get_logger(__name__)

# Try importing langchain-ollama; provide fallback if not installed
try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("langchain-ollama not installed. LLM features will use fallback mode.")


class LLMClient:
    """
    Manages communication with the local Ollama LLM.
<<<<<<< HEAD
    Model: qwen2.5-coder:7b (specialized for code analysis).
=======
    Model: codellama:13b-instruct (specialized for code analysis).
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
    """

    def __init__(
        self,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.1,
    ):
        self.model = model or settings.PRIMARY_AGENT_MODEL
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.temperature = temperature
        self._client = None

        if OLLAMA_AVAILABLE:
            try:
                self._client = ChatOllama(
                    model=self.model,
                    base_url=self.base_url,
                    temperature=self.temperature,
                )
                logger.info(f"LLM Client initialized: {self.model} @ {self.base_url}")
            except Exception as e:
                logger.error(f"Failed to initialize Ollama client: {e}")
                self._client = None
        else:
            logger.warning("Running in fallback mode (no LLM).")

    @property
    def is_available(self) -> bool:
        """Check if the LLM client is ready."""
        return self._client is not None

    def invoke(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a prompt to the LLM and get a response.

        Args:
            prompt: The user/task prompt.
            system_prompt: Optional system-level instructions.

        Returns:
            str: The LLM response text.
        """
        if not self.is_available:
            logger.warning("LLM not available. Returning fallback response.")
            return self._fallback_response(prompt)

        try:
            messages = []
            if system_prompt:
                messages.append(("system", system_prompt))
            messages.append(("human", prompt))

            response = self._client.invoke(messages)
            result = response.content if hasattr(response, "content") else str(response)

            logger.info(f"LLM invoked successfully (prompt length: {len(prompt)})")
            return result

        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            return self._fallback_response(prompt)

    def invoke_for_code_analysis(self, code_snippet: str, vulnerability: str) -> str:
        """
        Specialized invocation for code analysis and vulnerability assessment.

        Args:
            code_snippet: The source code to analyze.
            vulnerability: Description of the vulnerability found.

        Returns:
            str: AI analysis of the vulnerability and suggested fix.
        """
        system_prompt = (
            "You are an expert DevSecOps AI agent specialized in code security analysis. "
            "Your role is to analyze code vulnerabilities, assess their severity, and provide "
            "detailed remediation guidance. Always provide actionable, specific fixes."
        )
        prompt = (
            f"## Vulnerability Report\n"
            f"**Type:** {vulnerability}\n\n"
            f"## Affected Code\n```\n{code_snippet}\n```\n\n"
            f"## Required Analysis\n"
            f"1. Explain the vulnerability and its potential impact.\n"
            f"2. Provide the corrected code.\n"
            f"3. Rate severity (Critical/High/Medium/Low).\n"
            f"4. List any related CWE/CVE references."
        )
        return self.invoke(prompt, system_prompt=system_prompt)

    def invoke_for_patch_generation(self, code_snippet: str, vulnerability: str) -> str:
        """
        Generate an automated code patch for a vulnerability.

        Args:
            code_snippet: The vulnerable source code.
            vulnerability: Description of the vulnerability.

        Returns:
            str: The patched code with explanation.
        """
        system_prompt = (
            "You are an automated code patching agent. Generate ONLY the corrected code "
            "with minimal changes to fix the security vulnerability. Include a brief comment "
            "explaining the fix. Output format: the fixed code block followed by a one-line summary."
        )
        prompt = (
            f"Fix this security vulnerability:\n"
            f"Vulnerability: {vulnerability}\n\n"
            f"Original Code:\n```\n{code_snippet}\n```\n\n"
            f"Provide the patched code:"
        )
        return self.invoke(prompt, system_prompt=system_prompt)

    def _fallback_response(self, prompt: str) -> str:
        """Provide a deterministic fallback when LLM is unavailable."""
        return (
            "[FALLBACK] LLM is not available. "
            "This is a placeholder response. "
            "Please ensure Ollama is running with the "
            f"'{self.model}' model loaded at {self.base_url}."
        )


# ── Module-level convenience instance ─────────────────────────
llm_client = LLMClient()
