"""Enhanced Join Link Security Module.

Provides advanced security rules for Orbyte join links:
- Expiration timestamp checks
- Max usage count limits
- Domain restrictions (e.g. only allowing @company.com emails)
"""

from datetime import datetime
from datetime import timezone
import re
from typing import NamedTuple


class JoinLinkValidationResult(NamedTuple):
    is_valid: bool
    reason: str | None


def validate_join_link_security(
    expires_at: datetime | None = None,
    use_count: int = 0,
    max_uses: int | None = None,
    allowed_email_domain: str | None = None,
    user_email: str | None = None,
) -> JoinLinkValidationResult:
    """Validate a join link against all security constraints."""
    now = datetime.now(timezone.utc)

    # 1. Expiration Check
    if expires_at is not None:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at <= now:
            return JoinLinkValidationResult(
                is_valid=False, reason="This join link has expired."
            )

    # 2. Usage Limit Check
    if max_uses is not None and max_uses > 0:
        if use_count >= max_uses:
            return JoinLinkValidationResult(
                is_valid=False,
                reason="This join link has reached its maximum allowed uses.",
            )

    # 3. Domain Restriction Check
    if allowed_email_domain and user_email:
        domain = allowed_email_domain.strip().lstrip("@").lower()
        user_domain = user_email.split("@")[-1].lower() if "@" in user_email else ""
        if user_domain != domain:
            return JoinLinkValidationResult(
                is_valid=False,
                reason=f"Only email addresses ending in @{domain} are allowed to use this join link.",
            )

    return JoinLinkValidationResult(is_valid=True, reason=None)
