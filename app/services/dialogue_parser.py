import re

from app.models.generation import DialogueItem


class DialogueParser:
    PAUSE_RE = re.compile(r"\s*\[(\d+(?:\.\d+)?)\]\s*$")
    SPEAKER_TAG_RE = re.compile(r"\[(speaker\d+)\]", re.IGNORECASE)
    SPEAKER_PREFIX_RE = re.compile(
        r"^(speaker\d+)\s*:\s*(.+)$", re.IGNORECASE
    )

    def parse(self, text: str) -> tuple[list[DialogueItem], list[str]]:
        items = []
        warnings = []

        for line_no, raw in enumerate(text.splitlines(), start=1):
            line = raw.strip()
            if not line:
                continue

            pause_match = self.PAUSE_RE.search(line)
            if pause_match:
                pause = float(pause_match.group(1))
                content = line[:pause_match.start()].strip()
            else:
                # A missing pause is valid: use zero seconds and keep the line.
                pause = 0.0
                content = line

            speaker = None
            speaker_match = self.SPEAKER_TAG_RE.search(content)

            if speaker_match:
                speaker = speaker_match.group(1).lower()
                content = (
                    content[:speaker_match.start()]
                    + content[speaker_match.end():]
                ).strip()

            prefix = self.SPEAKER_PREFIX_RE.match(content)
            if prefix:
                if speaker is None:
                    speaker = prefix.group(1).lower()
                content = prefix.group(2).strip()

            if not content:
                warnings.append(f"Line {line_no}: empty text — skipped")
                continue

            items.append(
                DialogueItem(
                    text=content,
                    speaker=speaker,
                    pause=pause,
                    line=line_no,
                )
            )

        return items, warnings
