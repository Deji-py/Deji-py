"""Neumorphic SVG toolkit shared by the profile card builders.

Every card is drawn on the exact GitHub page colour (white / #0D1117), so the
raised and pressed surfaces appear to come straight out of the page.
"""
import base64
import json
import math
import os
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ICONS = json.load(open(os.path.join(HERE, "icons.json")))

FONTS = []
for fam, weight, file in [("Unbounded", 300, "unbounded-300"), ("Unbounded", 400, "unbounded-400"),
                          ("Inter", 400, "inter-400"), ("Inter", 500, "inter-500")]:
    with open(os.path.join(HERE, "fonts", f"{file}.woff2"), "rb") as fh:
        FONTS.append((fam, weight, base64.b64encode(fh.read()).decode()))

THEMES = {
    # Flat areas use GitHub's own page colour, so the panels blend into the page.
    # face1 -> face2 is a subtle gradient on raised surfaces that stands in for the highlight
    # (nothing can be lighter than white, or show above #0D1117 without an edge).
    "light": dict(bg="#FFFFFF", hi="#FFFFFF", lo="#C3C8D0", well="#F5F6F8",
                  face1="#FFFFFF", face2="#F2F3F5",
                  ink="#1F2328", mute="#6E7781", faint="#AFB8C1",
                  tag="#EAECEF", tagink="#57606A", track="#E6E8EB"),
    "dark":  dict(bg="#0E1116", hi="#1F252E", lo="#06090D", well="#11151B",
                  face1="#151920", face2="#151920",
                  ink="#E6EDF3", mute="#8D96A0", faint="#3D444D",
                  tag="#21262D", tagink="#9198A1", track="#161B22"),
}

DISPLAY = "font-family:Unbounded,'Segoe UI',Helvetica,Arial,sans-serif"
BODY = "font-family:Inter,'Segoe UI',Helvetica,Arial,sans-serif"

# Logos whose letters are cut-outs: fill the holes so they read like the real logo.
UNDERLAY = {"javascript": "#000000", "typescript": "#FFFFFF"}


def _lum(hexc):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def brand(name, theme):
    """Brand colour, swapped for the ink colour when it would vanish (black logos on dark)."""
    hexc = "#" + ICONS[name]["hex"]
    if theme == "dark" and _lum(hexc) < 0.05:
        return THEMES["dark"]["ink"]
    if theme == "dark" and _lum(hexc) < 0.2:  # deep blues/purples: lift so they read on the dark surface
        h = hexc.lstrip("#")
        return "#" + "".join(f"{int(int(h[i:i+2], 16) * 0.6 + 255 * 0.4):02X}" for i in (0, 2, 4))
    return hexc


class SVG:
    def __init__(self, w, h, theme):
        self.w, self.h, self.theme, self.t, self.parts = w, h, theme, THEMES[theme], []
        self.corners = None   # "top" / "bottom" / "all": round the slab's outer corners
        self._groups = 0

    def shift(self, dx, dy):
        """Offset everything drawn after this call."""
        self.add(f'<g transform="translate({dx} {dy})">')
        self._groups += 1

    def add(self, s):
        self.parts.append(s)

    # ---- surfaces ----
    def raised(self, x, y, w, h, r, size="lg"):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#face)" filter="url(#up-{size})"/>')

    def inset(self, x, y, w, h, r, size="lg"):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{self.t["well"]}" filter="url(#in-{size})"/>')

    def circle_raised(self, cx, cy, r, size="sm"):
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#face)" filter="url(#up-{size})"/>')

    def circle_inset(self, cx, cy, r, size="lg"):
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{self.t["well"]}" filter="url(#in-{size})"/>')

    # ---- content ----
    def text(self, x, y, s, size, color="ink", font="body", weight=400, anchor="start", ls=0):
        fam = DISPLAY if font == "display" else BODY
        c = self.t.get(color, color)
        self.add(f'<text x="{x}" y="{y}" style="{fam};font-size:{size}px;font-weight:{weight};letter-spacing:{ls}px" '
                 f'fill="{c}" text-anchor="{anchor}">{escape(str(s))}</text>')

    def logo(self, name, cx, cy, size):
        """Brand logo in its own colour."""
        if name == "zustand":  # no official mark in simple-icons: bear-brown wordmark letter
            col = "#8A6A4A" if self.theme == "light" else "#C9A27A"
            self.text(cx, cy + size * 0.36, "Z", size * 0.95, col, font="display", weight=400, anchor="middle")
            return
        s = size / 24
        x0, y0 = cx - size / 2, cy - size / 2
        if name in UNDERLAY:
            self.add(f'<rect x="{x0 + 1.5*s:.2f}" y="{y0 + 1.5*s:.2f}" width="{21*s:.2f}" height="{21*s:.2f}" fill="{UNDERLAY[name]}"/>')
        self.add(f'<path transform="translate({x0:.2f} {y0:.2f}) scale({s:.4f})" d="{ICONS[name]["path"]}" fill="{brand(name, self.theme)}"/>')

    def logo_button(self, name, cx, cy, r=25, size=22, label=None):
        self.circle_raised(cx, cy, r)
        self.logo(name, cx, cy, size)
        if label:
            self.text(cx, cy + r + 25, label, 10.5, "mute", anchor="middle", weight=500)

    def outline_badge(self, cx, cy, r, label):
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{self.t["faint"]}" stroke-width="1.2"/>')
        self.text(cx, cy + 4.5, label, 12, "mute", anchor="middle", weight=500)

    def tag(self, x, y, label, h=26):
        w = len(label) * 7.6 + 22
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{self.t["tag"]}"/>')
        self.text(x + w / 2, y + h / 2 + 4.5, label, 12, "tagink", anchor="middle", weight=500, ls=0.6)
        return w

    def section_label(self, x, y, num, label):
        self.text(x, y, f"{num}  —  {label.upper()}", 12, "mute", weight=500, ls=2)

    def line_icon(self, kind, cx, cy, color="ink"):
        c = self.t.get(color, color)
        st = f'fill="none" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
        if kind == "code":
            self.add(f'<path d="M{cx-4} {cy-7} L{cx-11} {cy} L{cx-4} {cy+7} M{cx+4} {cy-7} L{cx+11} {cy} L{cx+4} {cy+7}" {st}/>')
        elif kind == "mail":
            self.add(f'<rect x="{cx-10}" y="{cy-7}" width="20" height="14" rx="3" {st}/><path d="M{cx-9} {cy-5} L{cx} {cy+1} L{cx+9} {cy-5}" {st}/>')
        elif kind == "arrow":
            self.add(f'<path d="M{cx-6} {cy+6} L{cx+6} {cy-6} M{cx-3} {cy-6} L{cx+6} {cy-6} L{cx+6} {cy+3}" {st}/>')
        elif kind == "right":
            self.add(f'<path d="M{cx-8} {cy} L{cx+8} {cy} M{cx+2} {cy-6} L{cx+8} {cy} L{cx+2} {cy+6}" {st}/>')
        elif kind == "linkedin":
            col = "#0A66C2" if self.theme == "light" else "#4C9BEA"
            self.add(f'<rect x="{cx-10}" y="{cy-10}" width="20" height="20" rx="4" fill="{col}"/>'
                     f'<path d="M{cx-5} {cy-1} L{cx-5} {cy+5} M{cx} {cy+5} L{cx} {cy-1} M{cx} {cy+1.5} C{cx} {cy-2} {cx+5} {cy-2.5} {cx+5} {cy+1} L{cx+5} {cy+5}" '
                     f'fill="none" stroke="#FFFFFF" stroke-width="1.9" stroke-linecap="round"/><circle cx="{cx-5}" cy="{cy-4.6}" r="1.2" fill="#FFFFFF"/>')
        elif kind == "gmail":
            self.add(f'<rect x="{cx-10}" y="{cy-7.5}" width="20" height="15" rx="2.5" fill="none" stroke="{self.t["faint"]}" stroke-width="1.4"/>'
                     f'<path d="M{cx-9} {cy-5.5} L{cx} {cy+1} L{cx+9} {cy-5.5}" fill="none" stroke="#EA4335" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')

    # ---- output ----
    def render(self, title):
        t, W, H = self.t, self.w, self.h
        faces = "".join(f"@font-face{{font-family:'{n}';font-weight:{w};src:url(data:font/woff2;base64,{b}) format('woff2')}}"
                        for n, w, b in FONTS)
        def up(name, blur, off, lo_op):
            return (f'<filter id="up-{name}" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
                    f'<feGaussianBlur in="SourceAlpha" stdDeviation="{blur}" result="b"/>'
                    f'<feOffset in="b" dx="{off}" dy="{off}" result="d"/><feFlood flood-color="{t["lo"]}" flood-opacity="{lo_op}"/><feComposite in2="d" operator="in" result="ds"/>'
                    f'<feOffset in="b" dx="-{off}" dy="-{off}" result="l"/><feFlood flood-color="{t["hi"]}"/><feComposite in2="l" operator="in" result="ls"/>'
                    f'<feMerge><feMergeNode in="ds"/><feMergeNode in="ls"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
        in_op = 0.5 if self.theme == "dark" else 0.5
        def inn(name, off, blur):
            return (f'<filter id="in-{name}" color-interpolation-filters="sRGB" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
                    f'<feFlood flood-color="{t["lo"]}" flood-opacity="{in_op}" result="c1"/><feComposite in="c1" in2="SourceAlpha" operator="out" result="f1"/>'
                    f'<feOffset in="f1" dx="{off}" dy="{off}" result="o1"/><feGaussianBlur in="o1" stdDeviation="{blur}" result="b1"/>'
                    f'<feComposite in="b1" in2="SourceAlpha" operator="in" result="s1"/>'
                    f'<feFlood flood-color="{t["hi"]}" result="c2"/><feComposite in="c2" in2="SourceAlpha" operator="out" result="f2"/>'
                    f'<feOffset in="f2" dx="-{off}" dy="-{off}" result="o2"/><feGaussianBlur in="o2" stdDeviation="{blur}" result="b2"/>'
                    f'<feComposite in="b2" in2="SourceAlpha" operator="in" result="s2"/>'
                    f'<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="s1"/><feMergeNode in="s2"/></feMerge></filter>')
        lo_op = 0.9 if self.theme == "dark" else 0.75
        defs = (f"<defs><style>{faces}</style>"
                f'<linearGradient id="face" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["face1"]}"/>'
                f'<stop offset="1" stop-color="{t["face2"]}"/></linearGradient>'
 + up("lg", 7, 6, lo_op) + up("sm", 3.5, 3, lo_op)
                + inn("lg", 3, 4) + inn("sm", 2, 2.5) + "</defs>")
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">'
                f'<title>{escape(title)}</title>{defs}{self._slab()}'
                + "".join(self.parts) + "</g>" * self._groups + "</svg>")

    def _slab(self):
        W, H, r, c = self.w, self.h, 32, self.t["bg"]
        if self.corners == "top":
            return f'<path d="M0 {H} V{r} Q0 0 {r} 0 H{W-r} Q{W} 0 {W} {r} V{H} Z" fill="{c}"/>'
        if self.corners == "bottom":
            return f'<path d="M0 0 H{W} V{H-r} Q{W} {H} {W-r} {H} H{r} Q0 {H} 0 {H-r} Z" fill="{c}"/>'
        if self.corners == "bottom-left":
            return f'<path d="M0 0 H{W} V{H} H{r} Q0 {H} 0 {H-r} Z" fill="{c}"/>'
        if self.corners == "bottom-right":
            return f'<path d="M0 0 H{W} V{H-r} Q{W} {H} {W-r} {H} H0 Z" fill="{c}"/>'
        if self.corners == "all":
            return f'<rect width="{W}" height="{H}" rx="{r}" fill="{c}"/>'
        return f'<rect width="{W}" height="{H}" fill="{c}"/>'


CARD_GAP = 20  # space between raised cards inside one panel


def compose(theme, sections, w=840):
    """Stack several cards (each drawn with its card at y=36 of its own height h)
    onto one rounded mid-tone panel."""
    heights = [h - 72 for _, h in sections]
    PAD = 24
    H = PAD + sum(heights) + CARD_GAP * (len(sections) - 1) + PAD
    out = SVG(w, H, theme)
    out.corners = "all"
    y = PAD
    for (sec, _), ch in zip(sections, heights):
        out.add(f'<g transform="translate(0 {y - 36})">' + "".join(sec.parts) + "</g>" * sec._groups + "</g>")
        y += ch + CARD_GAP
    return out


def write_panel(name, section_builders, title):
    """section_builders: list of fn(theme) -> SVG section (card drawn at y=36, height s.h)."""
    write(name, lambda th: compose(th, [(b(th), b(th).h) for b in section_builders]), title)


def write(name, build, title):
    """build(svg_theme_name) -> SVG; writes light + dark variants."""
    for theme in THEMES:
        d = os.path.join(ROOT, "assets", theme)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, f"{name}.svg"), "w") as fh:
            fh.write(build(theme).render(title))
