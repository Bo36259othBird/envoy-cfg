"""Deployment target management for envoy-cfg."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


VALID_ENVIRONMENTS = {"development", "staging", "production"}


@dataclass
class DeploymentTarget:
    """Represents a single deployment target."""

    name: str
    environment: str
    url: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.environment not in VALID_ENVIRONMENTS:
            raise ValueError(
                f"Invalid environment '{self.environment}'. "
                f"Must be one of: {', '.join(sorted(VALID_ENVIRONMENTS))}"
            )
        if not self.name or not self.name.strip():
            raise ValueError("Target name must not be empty.")

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "environment": self.environment,
            "url": self.url,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DeploymentTarget":
        return cls(
            name=data["name"],
            environment=data["environment"],
            url=data.get("url"),
            tags=data.get("tags", []),
        )


class TargetRegistry:
    """Manages a collection of deployment targets."""

    def __init__(self):
        self._targets: Dict[str, DeploymentTarget] = {}

    def register(self, target: DeploymentTarget) -> None:
        """Register a new deployment target."""
        if target.name in self._targets:
            raise ValueError(f"Target '{target.name}' is already registered.")
        self._targets[target.name] = target

    def get(self, name: str) -> Optional[DeploymentTarget]:
        """Retrieve a target by name."""
        return self._targets.get(name)

    def remove(self, name: str) -> bool:
        """Remove a target by name. Returns True if removed, False if not found."""
        if name in self._targets:
            del self._targets[name]
            return True
        return False

    def list_targets(self, environment: Optional[str] = None) -> List[DeploymentTarget]:
        """List all targets, optionally filtered by environment."""
        targets = list(self._targets.values())
        if environment:
            targets = [t for t in targets if t.environment == environment]
        return targets

    def __len__(self) -> int:
        return len(self._targets)
