"""Browser-based implementation of the Mathador game.

This module launches the HTML/JavaScript version of the game located in
``mathador_web/index.html`` using the default web browser. The original Pygame
implementation has been replaced so that the game can run directly in browsers
without requiring any native dependencies.
"""

from __future__ import annotations

import os
import threading
import webbrowser
import tkinter as tk

WEB_DIR = os.path.join(os.path.dirname(__file__), "mathador_web")

def _open_game() -> None:
    """Open the HTML game in the user's default browser."""
    index_path = os.path.abspath(os.path.join(WEB_DIR, "index.html"))
    url = "file://" + index_path.replace("\\", "/")
    webbrowser.open(url, new=2)

def main(parent: tk.Tk | None = None) -> None:
    """Entry point used by the main switchboard.

    When run standalone, the function simply opens the browser tab. If a
    ``parent`` tkinter window is supplied, a temporary hidden ``Toplevel``
    widget is created so that the caller can block until the browser is
    launched, mirroring the behaviour of the other games in this repository.
    """
    if parent is None:
        _open_game()
    else:
        dummy = tk.Toplevel(parent)
        dummy.withdraw()
        dummy.grab_set()

        def launch_and_close() -> None:
            _open_game()
            dummy.destroy()

        threading.Thread(target=launch_and_close, daemon=True).start()
        parent.wait_window(dummy)

if __name__ == "__main__":
    main()
