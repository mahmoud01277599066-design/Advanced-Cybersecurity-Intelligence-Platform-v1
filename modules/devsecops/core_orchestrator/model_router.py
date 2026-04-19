"""
DevSecOps Module - Model Router
Routes AI requests to the correct model (codellama:13b-instruct Ollama).
Provides specialized prompt templates for different DevSecOps tasks.
"""

from typing import Optional, Dict, Any
from ..src.core.llm_client import LLMClient, llm_client
from ..src.core.logger import get_logger

logger = get_logger(__name__)


# ── Prompt Templates ──────────────────────────────────────────

PROMPT_TEMPLATES: Dict[str, str] = {
    "code_analysis": (
        "You are a security code analyst. Analyze the following vulnerability and code.\n"
        "Provide: severity assessment, root cause, impact, and recommended fix.\n\n"
        "Vulnerability: {vulnerability}\n"
        "File: {file_path}\n"
        "Code:\n```\n{code_snippet}\n```\n\n"
        "Context from knowledge base:\n{rag_context}\n"
    ),

    "patch_generation": (
        "You are an automated code patching agent. Generate ONLY the corrected code.\n"
        "Fix the security vulnerability with minimal changes.\n"
        "Include a brief comment explaining each fix.\n\n"
        "Vulnerability: {vulnerability}\n"
        "Original Code:\n```\n{code_snippet}\n```\n\n"
        "Remediation guidance:\n{rag_context}\n\n"
        "Output the patched code:"
    ),

    "risk_assessment": (
        "You are a security risk assessment expert.\n"
        "Evaluate the following findings and provide a risk score (0-10) with justification.\n\n"
        "Findings:\n{findings_summary}\n\n"
        "Context:\n{rag_context}\n\n"
        "Provide: risk_score (float), justification (string), recommended_action (string)."
    ),

    "report_generation": (
        "You are a security report writer.\n"
        "Summarize the following security analysis results into a clear, executive-ready report.\n\n"
        "Module: DevSecOps\n"
        "Findings:\n{findings_summary}\n"
        "Actions Taken:\n{actions_summary}\n"
        "Remediation Status:\n{remediation_status}\n"
    ),

    "network_remediation": (
        "You are a network security expert.\n"
        "Analyze the following network/IP security breach and provide actionable remediation steps.\n\n"
        "Alert Details:\n{alert_description}\n\n"
        "Affected Target: {affected_target}\n\n"
        "Network Details:\n{network_details}\n\n"
        "Provide the following:\n"
        "1. Immediate containment actions to stop the breach\n"
        "2. Specific firewall/IDS rules to implement\n"
        "3. Long-term prevention recommendations\n"
        "4. Monitoring and alerting suggestions\n"
        "5. Any relevant CVE/CWE references if applicable"
    ),
<<<<<<< HEAD
=======

    "dependency_audit": (
        "You are a Software Composition Analysis (SCA) expert.\n"
        "Review the following dependency manifest file (e.g., requirements.txt or package.json).\n"
        "Identify strictly known outdated libraries and any associated CVEs.\n\n"
        "Manifest File: {file_path}\n"
        "Contents:\n```\n{file_content}\n```\n\n"
        "For each vulnerable package found, output a section exactly like this:\n"
        "PACKAGE: <name>\n"
        "VERSION: <version>\n"
        "SEVERITY: <1.0 to 10.0>\n"
        "CVE: <CVE-xxxx-xxxx>\n"
        "DESCRIPTION: <Brief explanation of vulnerability>"
    ),
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
}


class ModelRouter:
    """
    Routes AI requests to the appropriate model with task-specific prompts.
    Currently all tasks route to qwen2.5-coder:7b via Ollama.
    """

    def __init__(self, client: Optional[LLMClient] = None):
        self._client = client or llm_client
        logger.info(
            f"ModelRouter initialized → model: {self._client.model}, "
            f"available: {self._client.is_available}"
        )

    def route(
        self,
        task_type: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Route a task to the LLM with an appropriate prompt template.

        Args:
            task_type: One of 'code_analysis', 'patch_generation',
<<<<<<< HEAD
                       'risk_assessment', 'report_generation'.
=======
                       'risk_assessment', 'report_generation',
                       'network_remediation', 'dependency_audit'.
>>>>>>> fe593c7172cd4a511612aa8f3ba161b83e2d879f
            context: Dict of template variables to fill.

        Returns:
            str: The LLM response.
        """
        template = PROMPT_TEMPLATES.get(task_type)
        if not template:
            logger.error(f"Unknown task type: {task_type}")
            return f"[ERROR] Unknown task type: {task_type}"

        try:
            prompt = template.format(**context)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            return f"[ERROR] Missing context variable: {e}"

        logger.info(f"Routing task '{task_type}' to model '{self._client.model}'")

        system_prompt = (
            "You are an AI agent within the ACIP DevSecOps module. "
            "You specialize in code security analysis, vulnerability assessment, "
            "and automated remediation. Always be precise and actionable."
        )

        return self._client.invoke(prompt, system_prompt=system_prompt)


# ── Module-level convenience instance ─────────────────────────
model_router = ModelRouter()
