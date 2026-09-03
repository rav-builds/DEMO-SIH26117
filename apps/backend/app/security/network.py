"""
Egress network controls for air-gapped sovereign operation.

Validates that all outbound HTTP requests from the backend are directed only
to allowed local endpoints (model serving ports, vector DB). Logs violations
to the audit trail.
"""

import logging
from typing import FrozenSet, Optional, Set
from urllib.parse import urlparse

from app.config import settings

logger = logging.getLogger(__name__)


# Allowed local hosts (loopback addresses)
_ALLOWED_HOSTS: FrozenSet[str] = frozenset({
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "::1",
})

# Allowed ports — model serving and vector DB
_ALLOWED_PORTS: FrozenSet[int] = frozenset({
    11434,  # Ollama
    1234,   # LM Studio / MLX
    8080,   # mlx-lm CLI server
    8000,   # vLLM
    6333,   # Qdrant HTTP
    6334,   # Qdrant gRPC
})


class EgressGuard:
    """
    Validates outbound network requests against a whitelist of allowed
    local endpoints. Designed for air-gapped sovereign deployments.
    """

    def __init__(
        self,
        allowed_hosts: Optional[Set[str]] = None,
        allowed_ports: Optional[Set[int]] = None,
    ):
        self.allowed_hosts = frozenset(allowed_hosts) if allowed_hosts else _ALLOWED_HOSTS
        self.allowed_ports = frozenset(allowed_ports) if allowed_ports else _ALLOWED_PORTS
        self._violation_count = 0

    def validate_url(self, url: str) -> bool:
        """
        Check if a URL is allowed by the egress policy.

        Returns True if the URL targets an allowed local endpoint,
        False if it would constitute an egress violation.
        """
        try:
            parsed = urlparse(url)
        except Exception:
            logger.warning("Egress guard: malformed URL rejected: %s", url)
            self._violation_count += 1
            return False

        host = parsed.hostname or ""
        port = parsed.port

        # Check host whitelist
        if host not in self.allowed_hosts:
            logger.warning(
                "Egress violation: host '%s' is not in allowed list. URL: %s",
                host, url,
            )
            self._violation_count += 1
            return False

        # Check port whitelist (if port is specified)
        if port is not None and port not in self.allowed_ports:
            logger.warning(
                "Egress violation: port %d is not in allowed list. URL: %s",
                port, url,
            )
            self._violation_count += 1
            return False

        return True

    def get_status(self) -> dict:
        """Return the current egress guard status."""
        return {
            "air_gapped": True,
            "allowed_hosts": sorted(self.allowed_hosts),
            "allowed_ports": sorted(self.allowed_ports),
            "violation_count": self._violation_count,
            "policy": "deny-all-except-whitelist",
        }

    @property
    def violation_count(self) -> int:
        return self._violation_count


# Singleton egress guard
egress_guard = EgressGuard()
