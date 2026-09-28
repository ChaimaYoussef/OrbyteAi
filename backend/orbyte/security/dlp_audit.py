"""Data Loss Prevention (DLP) & Query History Sensitivity Audit Module.

Analyzes user queries and chat messages for sensitive data keywords or patterns
(e.g., credit card numbers, passwords, confidential project names, SSNs)
and flags them for security auditing.
"""

import re
from typing import List
from typing import NamedTuple


class DLPRuleSeverity(str):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DLPAuditResult(NamedTuple):
    is_sensitive: bool
    matched_patterns: List[str]
    severity: str


# Common Regex Patterns for Sensitive Enterprise Data
DEFAULT_DLP_PATTERNS: dict[str, tuple[str, str]] = {
    "CREDIT_CARD": (
        r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b",
        DLPRuleSeverity.CRITICAL,
    ),
    "PASSWORD_KEYWORD": (
        r"(?i)\b(?:mot de passe|password|pwd|api_key|secret_key)\s*[:=]\s*\S+",
        DLPRuleSeverity.HIGH,
    ),
    "SSN_FR": (
        r"\b[12]\s?\d{2}\s?(?:0[1-9]|1[0-2])\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b",
        DLPRuleSeverity.HIGH,
    ),
    "CONFIDENTIAL_MARKER": (
        r"(?i)\b(?:confidentiel|strictement confidentiel|top secret|secret défense)\b",
        DLPRuleSeverity.MEDIUM,
    ),
}


def audit_query_for_sensitivity(
    query_text: str, custom_keywords: List[str] | None = None
) -> DLPAuditResult:
    """Analyze query text against DLP regex patterns and custom enterprise keywords.

    Args:
        query_text: The user's query or prompt string.
        custom_keywords: List of org-specific sensitive keywords (e.g. project codenames).

    Returns:
        DLPAuditResult indicating whether sensitive content was detected.
    """
    matched_patterns: List[str] = []
    max_severity = DLPRuleSeverity.LOW

    # Check default regex patterns
    for name, (pattern, severity) in DEFAULT_DLP_PATTERNS.items():
        if re.search(pattern, query_text):
            matched_patterns.append(name)
            if severity == DLPRuleSeverity.CRITICAL:
                max_severity = DLPRuleSeverity.CRITICAL
            elif (
                severity == DLPRuleSeverity.HIGH
                and max_severity != DLPRuleSeverity.CRITICAL
            ):
                max_severity = DLPRuleSeverity.HIGH
            elif (
                severity == DLPRuleSeverity.MEDIUM
                and max_severity == DLPRuleSeverity.LOW
            ):
                max_severity = DLPRuleSeverity.MEDIUM

    # Check custom keywords
    if custom_keywords:
        for kw in custom_keywords:
            if kw and kw.lower() in query_text.lower():
                matched_patterns.append(f"CUSTOM_KEYWORD:{kw}")
                if max_severity != DLPRuleSeverity.CRITICAL:
                    max_severity = DLPRuleSeverity.HIGH

    is_sensitive = len(matched_patterns) > 0
    return DLPAuditResult(
        is_sensitive=is_sensitive,
        matched_patterns=matched_patterns,
        severity=max_severity if is_sensitive else DLPRuleSeverity.LOW,
    )
