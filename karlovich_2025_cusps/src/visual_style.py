"""Shared thesis presentation palette, copied from config/colors.tex."""

COLORS = {
    "geometry": "#2469B4",   # GeometryBlue
    "transport": "#208E66",  # TransportGreen
    "proved": "#268852",     # ProvedGreen
    "wiener": "#E17E23",     # WienerOrange
    "mellin": "#B13F91",     # MellinMagenta
    "warning": "#B0373E",    # OpenRed
    "symbol": "#684CAE",     # FredholmViolet
    "main": "#1C375A",       # ThesisBlue
    "ink": "#141C26",        # ThesisInk
    "muted": "#586069",      # ThesisMuted
    "rule": "#CDD3DA",       # ThesisRule
    "soft": "#F6F8FA",       # ThesisSoft
}

TYPE_COLORS = {
    "CC": COLORS["geometry"],
    "CR": COLORS["symbol"],
    "RC": COLORS["transport"],
    "RR": COLORS["mellin"],
}
