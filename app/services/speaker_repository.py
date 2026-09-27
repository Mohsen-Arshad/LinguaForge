import json
from pathlib import Path

from app.models.speaker import Speaker


class SpeakerRepository:
    """Persistence boundary for speaker configuration."""

    def __init__(self, path: str | Path | None = None):
        project_dir = Path(__file__).resolve().parents[2]
        self.path = Path(path) if path else project_dir / "speakers.json"

    def load(self) -> list[Speaker]:
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                return []
            return [Speaker.from_dict(item) for item in data if isinstance(item, dict)]
        except (OSError, ValueError, KeyError, TypeError):
            return []

    def save(self, speakers: list[Speaker]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps([speaker.to_dict() for speaker in speakers], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
