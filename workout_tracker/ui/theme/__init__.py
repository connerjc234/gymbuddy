"""GymBuddy — Warm Premium Editorial Theme.

Re-exports all theme constants and utilities.
"""

from .colors import (
    ACCENT_GOLD,
    ACCENT_GOLD_BG,
    ACCENT_GREEN,
    ACCENT_GREEN_BG,
    ACCENT_TERRACOTTA,
    ACCENT_TERRACOTTA_HOVER,
    ACCENT_TERRACOTTA_SUBTLE,
    BG_ALT,
    BG_CARD,
    BG_WARM,
    BORDER_HOVER,
    BORDER_LIGHT,
    FONT_ACCENT,
    FONT_BODY,
    FONT_DISPLAY,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from .fonts import register_fonts
from .styles import (
    CARD_STYLE,
    STAT_CARD,
    STYLESHEET,
    body_compact,
    body_small,
    get_stylesheet,
    h1,
    h2,
)

__all__ = [
    "FONT_DISPLAY",
    "FONT_BODY",
    "FONT_ACCENT",
    "BG_WARM",
    "BG_CARD",
    "BG_ALT",
    "TEXT_PRIMARY",
    "TEXT_SECONDARY",
    "TEXT_MUTED",
    "ACCENT_TERRACOTTA",
    "ACCENT_TERRACOTTA_HOVER",
    "ACCENT_TERRACOTTA_SUBTLE",
    "BORDER_LIGHT",
    "BORDER_HOVER",
    "ACCENT_GREEN",
    "ACCENT_GREEN_BG",
    "ACCENT_GOLD",
    "ACCENT_GOLD_BG",
    "register_fonts",
    "get_stylesheet",
    "STYLESHEET",
    "CARD_STYLE",
    "STAT_CARD",
    "h1",
    "h2",
    "body_small",
    "body_compact",
]
