# LinguaForge Architecture

LinguaForge is a local desktop application with a Qt presentation layer and a service-oriented application core.

## Layering

```text
Presentation
  app/ui/
      MainWindow
      GenerateView
      SpeakersView
      SystemView
      reusable widgets

Application / Domain Services
  app/services/
      AudioGenerator
      DialogueParser
      PauseService
      SpeakerRepository
      SystemService

Domain Models
  app/models/
      Speaker
      DialogueItem
      GenerationConfig
      GenerationProgress
      AppEvent

Composition Root
  app/main.py
      creates QApplication and MainWindow
```

The UI knows how to render controls and collect user input. Services own business operations. Models carry domain state. This keeps TTS, parsing, persistence, and diagnostics independent from Qt.

## SOLID

- **Single Responsibility:** parsing, pause calculation, speaker persistence, TTS/FFmpeg generation, and runtime diagnostics have separate services.
- **Open/Closed:** UI pages and services communicate through small public methods, so new presentation or runtime strategies can be added without changing unrelated code.
- **Liskov Substitution:** views and widgets use Qt's established widget contracts; services do not depend on UI subclasses.
- **Interface Segregation:** services expose focused APIs instead of one universal application service.
- **Dependency Inversion:** `AudioGenerator` receives its parser and callbacks through its constructor rather than creating UI dependencies internally.

## Patterns

### Service Layer
Business/application operations are isolated in `app/services`.

### Repository
`SpeakerRepository` is the persistence boundary. Replacing JSON with SQLite later does not require changing the UI.

### Observer / Event Queue
Background work publishes `AppEvent` instances into a queue. The Qt event loop consumes those events on the main thread, preventing worker threads from touching widgets directly.

### Strategy-ready generation boundary
`AudioGenerator` owns the Chatterbox/FFmpeg integration behind one application-facing `generate()` operation. A future TTS engine can be introduced behind a dedicated strategy/adapter without leaking engine details into views.

## Fast startup and runtime caching

The first launch performs a complete diagnostic:

1. Python/package versions and imports
2. Perth watermarker
3. CUDA/GPU availability
4. Chatterbox import/status
5. FFmpeg availability

A validated snapshot is saved to:

```text
.runtime_cache.json
```

Subsequent launches read this snapshot instead of importing/checking every dependency again.

The cache is automatically invalidated when:
- the Python executable changes;
- the Python version changes;
- `requirements.txt` changes;
- the cache schema version changes.

The **System → Refresh** action always performs a fresh diagnostic and rewrites the cache. Installation/repair should also be followed by a refresh.

## Concurrency

Long-running operations run on worker threads. UI updates are marshalled through `AppEvent` and processed by a `QTimer` on the main thread.

## Testability

Pure parsing and pause logic can be tested without starting the GUI or loading Chatterbox:

```text
pytest -q
```

The next production upgrade would be extracting explicit ports/protocols for TTS, filesystem access, and process execution so those infrastructure concerns can be mocked independently.
