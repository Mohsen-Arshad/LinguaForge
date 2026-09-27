import threading
from typing import Callable


def run_background(
    target: Callable,
    on_success: Callable | None = None,
    on_error: Callable | None = None,
    daemon: bool = True,
):
    def worker():
        try:
            result = target()
            if on_success:
                on_success(result)
        except Exception as exc:
            if on_error:
                on_error(exc)

    thread = threading.Thread(target=worker, daemon=daemon)
    thread.start()
    return thread
