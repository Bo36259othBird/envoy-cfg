"""Schema validation for environment variable configs.

Allows defining expected keys, types, and required fields for a given
environment, and validating an env dict against that schema.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SchemaField:
    """Definition of a single expected environment variable."""

    key: str
    required: bool = True
    default: Optional[str] = None
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "required": self.required,
            "default": self.default,
            "description": self.description,
        }

    @classmethod
    def from_dict, Any]) -> "SchemaField":
        return cls(
            key=data["key"],
            required=data.get("required", True),
            default=data.get("default"),
            description=data.get("description", ""),
        )


@dataclass
class EnvSchema:
    """Schema describing expected environment variables for a target."""

    name: str
    fields: List[SchemaField] = field(default_factory=list)

    def add_field(self, schema_field: SchemaField) -> None:
        self.fields.append(schema_field)

    def validate(self, env: Dict[str, str]) -> List[str]:
        """Validate env dict against schema. Returns list of error messages."""
        errors: List[str] = []
        for f in self.fields:
            if f.key not in env:
                if f.required and f.default is None:
                    errors.append(f"Missing required key: '{f.key}'")
        unknown = set(env.keys()) - {f.key for f in self.fields}
        for key in sorted(unknown):
            errors.append(f"Unexpected key not in schema: '{key}'")
        return errors

    def apply_defaults(self, env: Dict[str, str]) -> Dict[str, str]:
        """Return a copy of env with schema defaults filled in for missing keys."""
        result = dict(env)
        for f in self.fields:
            if f.key not in result and f.default is not None:
                result[f.key] = f.default
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "fields": [f.to_dict() for f in self.fields]}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnvSchema":
        schema = cls(name=data["name"])
        schema.fields = [SchemaField.from_dict(fd) for fd in data.get("fields", [])]
        return schema
