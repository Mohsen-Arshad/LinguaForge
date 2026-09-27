from __future__ import annotations

import hashlib
import importlib
import json
import importlib.metadata
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable


class SystemService:
    """Runtime diagnostics and optional dependency repair for LinguaForge."""

    PROJECT_PYTHON = (3, 11)

    # These are the versions that match the user's working environment and
    # the Chatterbox Turbo build used by this project.
    PACKAGES = (
        ("torch", "torch", "2.6.0+cu124"),
        ("torchvision", "torchvision", "0.21.0+cu124"),
        ("torchaudio", "torchaudio", "2.6.0+cu124"),
        ("chatterbox-tts", "chatterbox.tts_turbo", "0.1.7"),
        ("resemble-perth", "perth", "1.0.1"),
        ("setuptools", "pkg_resources", "80.10.2"),
        ("soundfile", "soundfile", "0.14.0"),
        ("numpy", "numpy", None),
        ("PySide6", "PySide6", "6.11.2"),
        ("PySide6-Fluent-Widgets", "qfluentwidgets", "1.11.3"),
    )

    INSTALL_SPECS = (
        "torch==2.6.0+cu124",
        "torchvision==0.21.0+cu124",
        "torchaudio==2.6.0+cu124",
        "chatterbox-tts==0.1.7",
        "resemble-perth==1.0.1",
        "setuptools==80.10.2",
        "soundfile==0.14.0",
        "numpy",
        "PySide6==6.11.2",
        "PySide6-Fluent-Widgets==1.11.3",
    )

    CACHE_VERSION = 1
    CACHE_FILE_NAME = ".runtime_cache.json"

    def __init__(self, project_dir: str | Path | None = None):
        self.project_dir = Path(project_dir or Path(__file__).resolve().parents[2])
        self.wheels_dir = self.project_dir / "wheels"
        self.requirements_file = self.project_dir / "requirements.txt"
        self.cache_file = self.project_dir / self.CACHE_FILE_NAME

    @property
    def local_wheels_available(self) -> bool:
        return self.wheels_dir.is_dir() and any(self.wheels_dir.glob("*.whl"))

    def ffmpeg_path(self) -> str | None:
        bundled = self.project_dir / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
        return str(bundled) if bundled.exists() else shutil.which("ffmpeg")

    def check_gpu(self) -> tuple[bool, str, str]:
        try:
            import torch
        except Exception as exc:
            return False, "TORCH NOT AVAILABLE", f"Could not import PyTorch.\n\n{exc}"

        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            props = torch.cuda.get_device_properties(0)
            vram = props.total_memory / (1024 ** 3)
            cuda_version = getattr(torch.version, "cuda", None) or "unknown"
            return (True, f"CUDA READY  •  {name}  •  {vram:.1f} GB VRAM",
                    f"CUDA: available\nGPU: {name}\nVRAM: {vram:.1f} GB\n"
                    f"Torch: {torch.__version__}\nTorch CUDA: {cuda_version}")

        cuda_version = getattr(torch.version, "cuda", None) or "none"
        return (False, "CUDA NOT AVAILABLE",
                f"CUDA: unavailable\nTorch: {torch.__version__}\nTorch CUDA build: {cuda_version}\n"
                "The installed Torch build/driver may not expose CUDA.")

    def model_status(self) -> tuple[bool, str]:
        try:
            module = importlib.import_module("chatterbox.tts_turbo")
            getattr(module, "ChatterboxTurboTTS")
            version = importlib.metadata.version("chatterbox-tts")
            try:
                import perth
                watermarker = getattr(perth, "PerthImplicitWatermarker", None)
                if watermarker is None or not callable(watermarker):
                    return False, "Chatterbox installed, but Perth watermarker is unavailable (setuptools must be 80.10.2)."
            except Exception as exc:
                return False, f"Perth dependency unavailable: {exc}"
            return True, f"Chatterbox Turbo installed • v{version}"
        except Exception as exc:
            return False, f"Chatterbox unavailable: {exc}"

    def dependencies(self) -> tuple[list[tuple[str, str, str, bool]], bool]:
        rows = []
        all_ok = True
        for dist, module_name, expected in self.PACKAGES:
            try:
                installed = importlib.metadata.version(dist)
            except importlib.metadata.PackageNotFoundError:
                installed = "-"
                rows.append((dist, installed, "✕ MISSING", False))
                all_ok = False
                continue
            except Exception as exc:
                rows.append((dist, "?", f"✕ METADATA ERROR: {exc}", False))
                all_ok = False
                continue

            # Torch's local build suffix is important here.
            version_ok = expected is None or installed == expected
            if not version_ok:
                rows.append((dist, installed, f"⚠ VERSION MISMATCH (need {expected})", False))
                all_ok = False
                continue

            try:
                importlib.import_module(module_name)
                rows.append((dist, installed, "✓ READY", True))
            except Exception as exc:
                rows.append((dist, installed, f"✕ IMPORT BROKEN: {exc}", False))
                all_ok = False

        # The most important historical failure: Perth can exist but expose
        # PerthImplicitWatermarker=None when setuptools is too new.
        try:
            import perth
            if not callable(getattr(perth, "PerthImplicitWatermarker", None)):
                rows.append(("perth watermarker", "-", "✕ BROKEN: setuptools must be 80.10.2", False))
                all_ok = False
        except Exception as exc:
            rows.append(("perth watermarker", "-", f"✕ BROKEN: {exc}", False))
            all_ok = False

        try:
            if self.ffmpeg_path():
                rows.append(("ffmpeg", "PATH", "✓ READY", True))
            else:
                rows.append(("ffmpeg", "-", "✕ NOT FOUND", False))
                all_ok = False
        except Exception:
            pass

        return rows, all_ok

    def _requirements_fingerprint(self) -> str:
        try:
            data = self.requirements_file.read_bytes()
        except OSError:
            data = b""
        return hashlib.sha256(data).hexdigest()

    def _cache_context(self) -> dict:
        return {
            "cache_version": self.CACHE_VERSION,
            "python_exe": str(Path(sys.executable).resolve()),
            "python_version": sys.version.split()[0],
            "requirements_fingerprint": self._requirements_fingerprint(),
        }

    def save_diagnostics(self, diagnostics: dict) -> None:
        payload = {
            "context": self._cache_context(),
            "diagnostics": diagnostics,
        }
        try:
            self.cache_file.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass

    def load_cached_diagnostics(self) -> dict | None:
        try:
            payload = json.loads(
                self.cache_file.read_text(encoding="utf-8")
            )
            if not isinstance(payload, dict):
                return None
            if payload.get("context") != self._cache_context():
                return None
            diagnostics = payload.get("diagnostics")
            if not isinstance(diagnostics, dict):
                return None
            required = {
                "deps", "deps_ok", "gpu_ok", "gpu_short", "gpu_details",
                "model_ok", "model_details", "local_wheels", "ffmpeg",
                "python", "python_exe",
            }
            if not required.issubset(diagnostics):
                return None
            return diagnostics
        except (OSError, ValueError, TypeError):
            return None

    def diagnostics(self, *, persist: bool = True) -> dict:
        deps, deps_ok = self.dependencies()
        gpu_ok, gpu_short, gpu_details = self.check_gpu()
        model_ok, model_details = self.model_status()
        result = {
            "deps": deps, "deps_ok": deps_ok, "gpu_ok": gpu_ok,
            "gpu_short": gpu_short, "gpu_details": gpu_details,
            "model_ok": model_ok, "model_details": model_details,
            "local_wheels": self.local_wheels_available,
            "ffmpeg": self.ffmpeg_path(), "python": sys.version.split()[0],
            "python_exe": sys.executable,
        }
        if persist:
            self.save_diagnostics(result)
        return result

    def _run_pip(self, args: list[str], log: Callable[[str], None] | None = None):
        command = [sys.executable, "-m", "pip", "--disable-pip-version-check"] + args
        if log:
            log("$ " + " ".join(command))
        process = subprocess.Popen(command, cwd=str(self.project_dir), stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                   errors="replace", bufsize=1)
        assert process.stdout is not None
        for line in process.stdout:
            line = line.rstrip()
            if log and line:
                log(line)
        code = process.wait()
        if code != 0:
            raise RuntimeError(f"pip exited with code {code}")

    def _offline_install(self, specs, log=None):
        if not self.local_wheels_available:
            raise RuntimeError("Local wheels directory is not available.")
        self._run_pip(["install", "--no-index", "--only-binary=:all:", "--find-links",
                       str(self.wheels_dir), *specs], log)

    def _online_install(self, specs, log=None):
        # Torch CUDA wheels are served from the official PyTorch CUDA 12.4
        # index. The rest of the runtime comes from PyPI.
        torch_specs = [s for s in specs if s.startswith(("torch==", "torchvision==", "torchaudio=="))]
        other_specs = [s for s in specs if s not in torch_specs]
        if torch_specs:
            self._run_pip([
                "install", "--index-url",
                "https://download.pytorch.org/whl/cu124",
                *torch_specs,
            ], log)
        if other_specs:
            self._run_pip(["install", *other_specs], log)

    def install_missing(self, log=None) -> dict:
        if sys.version_info[:2] != self.PROJECT_PYTHON:
            raise RuntimeError(f"This project requires Python 3.11. Current: {sys.version.split()[0]}")

        rows, _ = self.dependencies()
        states = {row[0]: row for row in rows}
        specs = []
        for dist, spec in zip((
            "torch", "torchvision", "torchaudio", "chatterbox-tts",
            "resemble-perth", "setuptools", "soundfile", "numpy",
            "PySide6", "PySide6-Fluent-Widgets"), self.INSTALL_SPECS):
            row = states.get(dist)
            if row is None or not row[3]:
                specs.append(spec)
        if any("perth watermarker" == row[0] and not row[3] for row in rows) and "setuptools==80.10.2" not in specs:
            specs.append("setuptools==80.10.2")

        if not specs:
            if log: log("All Python dependencies are already ready.")
            return {"installed": [], "mode": "none"}

        if log: log("Packages requiring repair: " + ", ".join(specs))
        if self.local_wheels_available:
            try:
                if log: log(f"Using local wheels: {self.wheels_dir}")
                self._offline_install(specs, log)
                return {"installed": specs, "mode": "offline"}
            except Exception as exc:
                if log: log(f"Offline repair failed: {exc}")
                if log: log("Falling back to PyPI…")
        self._online_install(specs, log)
        return {"installed": specs, "mode": "online"}

    def repair_all(self, log=None) -> dict:
        if sys.version_info[:2] != self.PROJECT_PYTHON:
            raise RuntimeError(f"This project requires Python 3.11. Current: {sys.version.split()[0]}")
        specs = list(self.INSTALL_SPECS)
        if self.local_wheels_available:
            try:
                if log: log(f"Repairing complete runtime from local wheels: {self.wheels_dir}")
                self._offline_install(specs, log)
                return {"installed": specs, "mode": "offline"}
            except Exception as exc:
                if log: log(f"Offline full repair failed: {exc}")
                if log: log("Falling back to PyPI…")
        self._online_install(specs, log)
        return {"installed": specs, "mode": "online"}
