from __future__ import annotations

from typing import Any, Protocol
import numpy as np


class PosePort(Protocol):
    model_version: str

    def estimate_pose(self, frame: np.ndarray) -> dict[str, Any]:
        ...


class BehaviourPort(Protocol):
    model_version: str

    def predict_events(
        self,
        frames: list[np.ndarray],
        poses: list[dict[str, Any]],
        fps: float,
    ) -> list[dict[str, Any]]:
        ...