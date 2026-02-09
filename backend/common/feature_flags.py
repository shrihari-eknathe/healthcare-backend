import os
import logging
from functools import wraps
from flask import jsonify

logger = logging.getLogger(__name__)


class FeatureFlags:
    """Simple feature flag management using environment variables."""
    
    _flags = {
        "reimbursement_module": os.environ.get("FEATURE_REIMBURSEMENTS", "true").lower() == "true",
        "auto_approve_small_claims": os.environ.get("FEATURE_AUTO_APPROVE", "false").lower() == "true",
    }

    @classmethod
    def is_enabled(cls, flag_name: str, default: bool = False) -> bool:
        """Check if a feature flag is enabled."""
        return cls._flags.get(flag_name, default)

    @classmethod
    def set_flag(cls, flag_name: str, enabled: bool) -> None:
        """Set a feature flag (for testing)."""
        cls._flags[flag_name] = enabled

    @classmethod
    def get_all_flags(cls) -> dict:
        """Get all feature flags."""
        return cls._flags.copy()


def is_feature_enabled(flag_name: str, default: bool = False) -> bool:
    """Check if a feature is enabled."""
    return FeatureFlags.is_enabled(flag_name, default)


def require_feature(flag_name: str, error_message: str = "This feature is not available"):
    """Decorator to protect routes with feature flags."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_feature_enabled(flag_name):
                logger.warning(f"Feature '{flag_name}' is disabled, blocking access")
                return jsonify({"error": error_message}), 404
            return f(*args, **kwargs)
        return decorated_function
    return decorator
