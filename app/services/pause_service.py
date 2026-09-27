import re
from pathlib import Path


class PauseService:
    @staticmethod
    def calculate_pause(text: str) -> int:
        clean = re.sub(r"\s+", " ", text).strip()
        if not clean:
            return 2

        words = re.findall(r"\S+", clean)
        weighted_length = len(clean) + (4 * len(words))
        pause = round(1.5 + (weighted_length / 25.0))
        return max(2, min(6, pause))

    def add_missing_pauses(self, input_file: str) -> tuple[int, int, str]:
        path = Path(input_file)
        original = path.read_text(encoding="utf-8")

        added = 0
        skipped = 0
        output_lines = []

        for raw in original.splitlines():
            stripped = raw.strip()

            if not stripped:
                output_lines.append(raw)
                continue

            if re.search(r"\s*\[(\d+(?:\.\d+)?)\]\s*$", stripped):
                output_lines.append(raw)
                skipped += 1
                continue

            content = re.sub(
                r"\[speaker\d+\]", "", stripped, flags=re.IGNORECASE
            )
            content = re.sub(
                r"^speaker\d+\s*:\s*", "", content, flags=re.IGNORECASE
            ).strip()

            if not content:
                output_lines.append(raw)
                continue

            pause = self.calculate_pause(content)
            output_lines.append(f"{stripped} [{pause}]")
            added += 1

        if added == 0:
            return 0, skipped, ""

        backup = str(path) + ".bak"
        Path(backup).write_text(original, encoding="utf-8")
        path.write_text(
            "\n".join(output_lines) + ("\n" if original.endswith("\n") else ""),
            encoding="utf-8",
        )
        return added, skipped, backup
