import logging
from pathlib import Path

LOG_FILE = Path("debug.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class Colours:

    SHOW = "\033[?25h"
    HIDE = "\033[?25l"
    END = "\033[0m"

    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37

    DESCRIPTION = YELLOW
    DECO = GREEN
    TITLE = YELLOW
    PIPE = GREEN
    UNDERSCORE = YELLOW
    EQUALS = GREEN
    DASH = GREEN
    HASH = GREEN
    SLASH = YELLOW
    UP = GREEN
    TITLE_WHITE = WHITE

    colour_counter = 0

    @classmethod
    def c(cls, text, fg="green", bg=None, *, bold=False, italics=False, underline=False, invert=False, no_reset=False):

        codes = []

        if bold:
            codes.append("1")      # ANSI code for bold
        if italics:
            codes.append("3")      # ANSI code for italics
        if underline:
            codes.append("4")      # ANSI code for underline
        if invert:
            codes.append("7")

        try:
            fg=fg.upper()
            fg_code = getattr(cls, fg)
        except AttributeError:
            logging.warning(f"Unknown colour '{fg}', using baseline")
            fg_code = cls.RED

        codes.append(str(fg_code))

        if bg:
            bg=bg.upper()
            bg_code = getattr(cls, bg, cls.BLACK) + 10
            codes.append(str(bg_code))

        start = f"\033[{';'.join(codes)}m"
        end = "" if no_reset else cls.END
        return f"{start}{text}{end}"

