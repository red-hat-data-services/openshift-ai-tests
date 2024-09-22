import shutil
from typing import Optional

from simple_logger.logger import get_logger

LOGGER = get_logger(name=__name__)


def separator(symbol_: str, val: Optional[str] = None) -> str:
    terminal_width = shutil.get_terminal_size(fallback=(120, 40))[0]
    if not val:
        return f"{symbol_ * terminal_width}"

    sepa = int((terminal_width - len(val) - 2) // 2)
    return f"{symbol_ * sepa} {val} {symbol_ * sepa}"
