import os
import subprocess
import shutil
import time
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import soundfile as sf

from app.models.generation import GenerationConfig
from app.services.dialogue_parser import DialogueParser


class AudioGenerator:
    """Application service wrapping Chatterbox Turbo + FFmpeg."""

    def __init__(
        self,
        parser: DialogueParser,
        log: Callable[[str], None],
        status: Callable[[str], None],
        progress: Callable[[int, int], None],
        model_ready: Callable[[str], None],
    ):
        self.parser = parser
        self.log = log
        self.status = status
        self.progress = progress
        self.model_ready = model_ready
        self.model = None

    def generate(self, config: GenerationConfig) -> str:
        import torch
        import perth
        from chatterbox.tts_turbo import ChatterboxTurboTTS

        watermarker = getattr(perth, "PerthImplicitWatermarker", None)
        if not callable(watermarker):
            raise RuntimeError(
                "PerthImplicitWatermarker is unavailable.\n\n"
                "This project requires setuptools==80.10.2.\n"
                "Do not upgrade setuptools above 80.x for this environment."
            )

        if not torch.cuda.is_available():
            raise RuntimeError(
                "CUDA is unavailable. Open System → Check GPU."
            )

        text = Path(config.input_file).read_text(encoding="utf-8")
        items, warnings = self.parser.parse(text)

        for warning in warnings:
            self.log(warning)

        if not items:
            raise RuntimeError(
                "No valid lines found.\n"
                "Example: Hello there. [speaker1] [2]"
            )

        speakers = dict(config.speakers)
        if not speakers:
            raise RuntimeError(
                "No valid speakers are configured."
            )

        # If a line has no speaker tag, always use Speaker 1 / the first
        # configured speaker. This also works when multiple speakers exist.
        default_speaker = next(iter(speakers))
        items = [
            type(item)(
                text=item.text,
                speaker=item.speaker or default_speaker,
                pause=item.pause,
                line=item.line,
            )
            for item in items
        ]

        for item in items:
            if not item.speaker:
                raise RuntimeError(
                    f"Line {item.line} has no speaker tag."
                )
            if item.speaker not in speakers:
                raise RuntimeError(
                    f"Line {item.line} uses [{item.speaker}], "
                    "but that speaker has no valid reference audio."
                )

        self.log("=" * 70)
        self.log("LinguaForge")
        self.log("=" * 70)
        self.log(f"GPU: {torch.cuda.get_device_name(0)}")
        self.log(f"Sentences: {len(items)}")
        self.log(f"Speakers: {', '.join(speakers)}")
        self.log(f"MP3 bitrate: {config.bitrate}")

        if self.model is None:
            self.status("Loading model…")
            self.model_ready("Loading Chatterbox Turbo...")
            self.log("Loading Chatterbox Turbo...")
            self.model = ChatterboxTurboTTS.from_pretrained(device="cuda")
            self.log(f"Model ready — {self.model.sr} Hz")

        self.model_ready("Chatterbox Ready")
        self.status("Generating…")

        sr = self.model.sr
        all_audio = []

        for index, item in enumerate(items, start=1):
            reference = speakers[item.speaker]
            self.log(
                f"[{index}/{len(items)}] [{item.speaker}] "
                f"{item.text} (pause {item.pause:.2f}s)"
            )

            with torch.inference_mode():
                wav = self.model.generate(
                    item.text,
                    audio_prompt_path=reference,
                )

            audio = (
                wav.squeeze()
                .detach()
                .cpu()
                .numpy()
                .astype(np.float32)
            )
            all_audio.append(audio)
            all_audio.append(
                np.zeros(int(sr * item.pause), dtype=np.float32)
            )

            self.progress(index, len(items))
            self.status(f"Generating {index}/{len(items)}…")

        final_audio = np.concatenate(all_audio)

        output = Path(config.output_file).resolve()
        output.parent.mkdir(parents=True, exist_ok=True)

        temp_original = output.parent / "_chatterbox_original.wav"
        temp_slow = output.parent / "_chatterbox_slow.wav"

        try:
            sf.write(str(temp_original), final_audio, sr, subtype="PCM_16")

            ffmpeg = shutil.which("ffmpeg")
            if ffmpeg is None:
                bundled = Path(__file__).resolve().parents[2] / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
                if bundled.exists():
                    ffmpeg = str(bundled)
            if ffmpeg is None:
                raise RuntimeError("FFmpeg was not found in PATH or tools/ffmpeg/bin/ffmpeg.exe")

            self.status("Applying speed...")
            subprocess.run(
                [
                    ffmpeg, "-y", "-i", str(temp_original),
                    "-filter:a", f"atempo={config.speed:.4f}",
                    "-ar", str(sr), "-ac", "1", str(temp_slow),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )

            self.status("Encoding MP3...")
            # Explicitly constrain the LAME encoder to the selected CBR bitrate.
            # Without the min/max constraints, some FFmpeg/LAME builds can choose
            # a different effective bitrate than the UI selection.
            subprocess.run(
                [
                    ffmpeg, "-y", "-i", str(temp_slow),
                    "-codec:a", "libmp3lame",
                    "-filter:a", f"volume={config.volume:.4f}",
                    "-b:a", config.bitrate,
                    "-minrate", config.bitrate,
                    "-maxrate", config.bitrate,
                    "-bufsize", config.bitrate,
                    # 24 kHz MP3 is limited to 160 kbps by the MPEG-2 bitrate
                    # table. Resample the final MP3 to 44.1 kHz so 192/256/320k
                    # selections are actually available.
                    "-ar", "44100",
                    "-ac", "1",
                    str(output),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )

            duration = len(final_audio) / sr / config.speed
            self.log("")
            self.log("=" * 70)
            self.log("✓ GENERATION COMPLETE")
            self.log("=" * 70)
            self.log(f"Output: {output}")
            self.log(f"Duration: {duration / 60:.2f} min")
            return str(output)

        finally:
            for temp in (temp_original, temp_slow):
                try:
                    temp.unlink(missing_ok=True)
                except OSError:
                    pass
