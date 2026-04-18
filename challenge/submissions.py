from __future__ import annotations

import importlib.util
import sys
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

from .utils import read_json


class SubmissionError(RuntimeError):
    pass


@contextmanager
def _temporary_sys_path(path: Path):
    sys.path.insert(0, str(path))
    try:
        yield
    finally:
        if str(path) in sys.path:
            sys.path.remove(str(path))


def _load_module(module_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        f"challenge_submission_{module_path.parent.name}",
        module_path,
    )
    if spec is None or spec.loader is None:
        raise SubmissionError(f"Unable to load module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Submission:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.config = read_json(path / "config.json")
        self.metadata = self.config.get("metadata", {})
        impl_path = path / "submission_impl.py"
        self.module = None
        if impl_path.exists():
            with _temporary_sys_path(path):
                self.module = _load_module(impl_path)
        self._callable = self._resolve_callable()

    def _resolve_callable(self) -> Callable[..., dict[str, Any]]:
        if self.module is None:
            from .default_submission import run_task

            return run_task
        if hasattr(self.module, "build_submission"):
            built = self.module.build_submission(self.config)
            if callable(built):
                return built
        if hasattr(self.module, "run_task"):
            return getattr(self.module, "run_task")
        raise SubmissionError(
            f"Submission module at {self.path / 'submission_impl.py'} must expose run_task(...) or build_submission(...)."
        )

    def run_task(self, task: dict[str, Any], tools: Any) -> dict[str, Any]:
        output = self._callable(task=task, tools=tools, config=self.config)
        if not isinstance(output, dict):
            raise SubmissionError("Submission must return a dict.")
        return output


def load_submission(path_like: str | Path) -> Submission:
    path = Path(path_like).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Missing submission path: {path}")
    if not (path / "config.json").exists():
        raise FileNotFoundError(f"Submission is missing config.json: {path}")
    return Submission(path)
