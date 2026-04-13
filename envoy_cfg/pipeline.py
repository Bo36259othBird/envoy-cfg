"""Pipeline module: chain multiple env transformations in sequence."""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

EnvMap = Dict[str, str]
Transform = Callable[[EnvMap], EnvMap]


@dataclass
class PipelineStep:
    name: str
    transform: Transform
    enabled: bool = True

    def apply(self, env: EnvMap) -> EnvMap:
        if not self.enabled:
            return env
        return self.transform(env)

    def __repr__(self) -> str:
        status = "on" if self.enabled else "off"
        return f"PipelineStep({self.name!r}, {status})"


@dataclass
class PipelineResult:
    steps_applied: List[str] = field(default_factory=list)
    steps_skipped: List[str] = field(default_factory=list)
    final_env: EnvMap = field(default_factory=dict)
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None

    def __repr__(self) -> str:
        return (
            f"PipelineResult(applied={self.steps_applied}, "
            f"skipped={self.steps_skipped}, success={self.success})"
        )


class EnvPipeline:
    """Executes an ordered list of env transformation steps."""

    def __init__(self) -> None:
        self._steps: List[PipelineStep] = []

    def add_step(self, name: str, transform: Transform, enabled: bool = True) -> "EnvPipeline":
        self._steps.append(PipelineStep(name=name, transform=transform, enabled=enabled))
        return self

    def disable_step(self, name: str) -> None:
        for step in self._steps:
            if step.name == name:
                step.enabled = False
                return
        raise KeyError(f"No step named {name!r}")

    def enable_step(self, name: str) -> None:
        for step in self._steps:
            if step.name == name:
                step.enabled = True
                return
        raise KeyError(f"No step named {name!r}")

    def run(self, env: EnvMap) -> PipelineResult:
        result = PipelineResult(final_env=dict(env))
        current = dict(env)
        for step in self._steps:
            if not step.enabled:
                result.steps_skipped.append(step.name)
                continue
            try:
                current = step.apply(current)
                result.steps_applied.append(step.name)
            except Exception as exc:  # noqa: BLE001
                result.error = f"Step {step.name!r} failed: {exc}"
                result.final_env = current
                return result
        result.final_env = current
        return result

    def step_names(self) -> List[str]:
        return [s.name for s in self._steps]
