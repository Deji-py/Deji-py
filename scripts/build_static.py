"""Builds the static profile cards (everything except the live stats card).

Run:  python scripts/build_static.py
Edit the CONTENT section to change copy, projects or tech stacks.
"""
import math
from neu import SVG, write

W = 840
P = 36   # side padding of the slab


def frame(theme, h, r=40, top=0, bottom=0):
    """One raised card, drawn at y=36 of a section (compose() stacks sections into a panel).
    top/bottom trim the card's inner padding; content is laid out untrimmed and shifted."""
    H = h - top - bottom
    s = SVG(W, H, theme)
    s.raised(P, P, W - 2 * P, H - 2 * P, r)
    s.shift(0, -top)
    return s

# ============================ CONTENT ============================
HEADER = dict(name="DEJI.PY", role="Software engineer · product builder",
              kicker="Currently exploring", focus="AI PRODUCTS", status="OPEN",
              badges=["typescript", "react"])

ABOUT_LINES = ["I turn messy problems into clear, usable products —",
               "caring about the details users feel and the",
               "architecture developers maintain."]
ABOUT_ROWS = [("BUILD", "Web apps · mobile · dashboards · APIs"),
              ("VALUE", "Thoughtful UX · clean architecture · speed"),
              ("NOW", "AI-powered products · building in public")]

# stack = logos shown in the card (simple-icons slugs from icons.json, or "zustand")
PROJECTS = [
    ("01", "BusyBuddy", "busybuddy", ["A mobile app built with Expo and", "React Native, backed by Supabase."],
     ["expo", "react", "supabase", "reactquery"]),
    ("02", "Fastro", "fastro", ["A streamlined Supabase dashboard", "that makes data admin less tedious."],
     ["supabase", "postgresql"]),
    ("03", "Collabr", "collabr", ["A web app exploring a collaborative", "product experience."],
     ["react", "vite"]),
    ("04", "Keyp", "keyp", ["A frontend project from my portfolio —", "open it for the implementation."],
     ["typescript", "react"]),
]

TOOLBOX = [
    ("Frontend", [("typescript", "TypeScript"), ("javascript", "JavaScript"), ("react", "React"), ("nextdotjs", "Next.js"),
                  ("tailwindcss", "Tailwind"), ("html5", "HTML"), ("css", "CSS"), ("vite", "Vite")]),
    ("Backend", [("nodedotjs", "Node.js"), ("python", "Python"), ("django", "Django"), ("postgresql", "Postgres"),
                 ("supabase", "Supabase"), ("redis", "Redis")]),
    ("Mobile", [("react", "React Native"), ("expo", "Expo"), ("reactquery", "TanStack"), ("zustand", "Zustand")]),
    ("Workflow", [("git", "Git"), ("github", "GitHub"), ("docker", "Docker"), ("vercel", "Vercel"), ("figma", "Figma")]),
]

PRINCIPLES = [("Start with why", "Clarify the real user problem before writing code."),
              ("Main flow first", "Make the core experience clear before adding complexity."),
              ("Clear boundaries", "Keep UI, logic, data access and integrations separate."),
              ("Every state matters", "Loading, empty, error and success are part of the product."),
              ("Document decisions", "So the next person knows what changed — and why.")]

EMAIL = "ayodejialakija037@gmail.com"
# ================================================================


def header(theme):
    s = frame(theme, 400, top=14, bottom=10)
    s.text(78, 126, HEADER["name"], 58, font="display", weight=300, ls=1)
    s.text(78, 166, HEADER["role"], 19, "mute")
    for i, b in enumerate(reversed(HEADER["badges"])):
        cx = W - 92 - i * 52
        s.circle_raised(cx, 104, 20)
        s.logo(b, cx, 104, 18)
    s.inset(60, 210, W - 120, 124, 62)
    s.text(106, 256, HEADER["kicker"], 14, "mute")
    s.text(106, 298, HEADER["focus"], 28, font="display", weight=300, ls=0.5)
    s.tag(352, 277, HEADER["status"])
    s.circle_raised(W - 214, 272, 34)
    s.line_icon("code", W - 214, 272)
    s.circle_raised(W - 128, 272, 34)
    s.line_icon("mail", W - 128, 272)
    return s


def about(theme):
    s = frame(theme, 480, top=14, bottom=4)
    t = s.t
    s.section_label(76, 86, "01", "About")
    cx, cy, R = 200, 262, 116
    s.circle_inset(cx, cy, R)
    tick = f'stroke="{t["faint"]}" stroke-width="1.6" stroke-linecap="round"'
    s.add(f'<line x1="{cx}" y1="{cy-R+10}" x2="{cx}" y2="{cy-R+26}" {tick}/><line x1="{cx}" y1="{cy+R-26}" x2="{cx}" y2="{cy+R-10}" {tick}/>'
          f'<line x1="{cx-R+10}" y1="{cy}" x2="{cx-R+26}" y2="{cy}" {tick}/><line x1="{cx+R-26}" y1="{cy}" x2="{cx+R-10}" y2="{cy}" {tick}/>')
    s.text(cx - R + 34, cy + 4, "09", 10, "mute")
    s.text(cx + R - 34, cy + 4, "03", 10, "mute", anchor="end")
    for deg, ln, wd, col in [(213, 60, 3, t["ink"]), (0, 90, 2.2, t["ink"]), (48, 96, 1, t["mute"])]:
        a = math.radians(deg)
        s.add(f'<line x1="{cx}" y1="{cy}" x2="{cx + math.sin(a)*ln:.1f}" y2="{cy - math.cos(a)*ln:.1f}" stroke="{col}" stroke-width="{wd}" stroke-linecap="round"/>')
    s.add(f'<circle cx="{cx}" cy="{cy}" r="4" fill="{t["ink"]}"/>')
    x0 = 362
    s.text(x0, 134, "Hi, I'm Deji.", 26, font="display", weight=300)
    for i, ln in enumerate(ABOUT_LINES):
        s.text(x0, 168 + i * 23, ln, 15, "mute")
    for i, (k, v) in enumerate(ABOUT_ROWS):
        y = 258 + i * 58
        s.inset(x0 - 8, y, W - 76 - x0 + 8, 44, 22, "sm")
        s.text(x0 + 14, y + 27, k, 11, "mute", weight=500, ls=1.6)
        s.text(x0 + 86, y + 27, v, 14.5)
    return s


def work(theme):
    s = frame(theme, 136, r=32)
    s.text(76, 74, "02  —  SELECTED WORK", 12, "mute", weight=500, ls=2)
    s.text(W - 118, 74, "View all repositories", 13, weight=500, anchor="end")
    s.circle_raised(W - 86, 68, 16, "sm")
    s.line_icon("arrow", W - 86, 68)
    return s


def projects(theme):
    cw, ch, gap = (W - 2 * P - 20) // 2, 228, 20
    H = 36 + ch * 2 + gap + 36
    s = SVG(W, H, theme)
    for i, (num, name, slug, desc, stack) in enumerate(PROJECTS):
        x = P + (i % 2) * (cw + gap)
        y = P + (i // 2) * (ch + gap)
        s.raised(x, y, cw, ch, 34)
        s.text(x + 30, y + 58, name, 26, font="display", weight=300)
        s.outline_badge(x + cw - 46, y + 47, 16, num)
        for j, ln in enumerate(desc):
            s.text(x + 30, y + 92 + j * 22, ln, 14, "mute")
        s.inset(x + 18, y + 146, cw - 36, 64, 32, "sm")
        for j, ic in enumerate(stack):
            cx = x + 52 + j * 44
            s.circle_raised(cx, y + 178, 17, "sm")
            s.logo(ic, cx, y + 178, 17)
        s.circle_raised(x + cw - 54, y + 178, 22)
        s.line_icon("arrow", x + cw - 54, y + 178)
    return s


def toolbox(theme):
    RH = 100
    H = 136 + RH * len(TOOLBOX) + 30
    s = frame(theme, H, top=14)
    s.section_label(76, 86, "03", "Toolbox")
    s.text(W - 76, 86, "Tools chosen for the problem, not the trend", 13, "mute", anchor="end")
    for gi, (label, items) in enumerate(TOOLBOX):
        y = 116 + gi * RH
        s.inset(64, y + 14, 128, 40, 20, "sm")
        s.text(128, y + 39, label.upper(), 11, "mute", anchor="middle", weight=500, ls=1.6)
        for ii, (ic, nm) in enumerate(items):
            s.logo_button(ic, 240 + ii * 74, y + 34, 25, 23, nm)
    return s


def principles(theme):
    H = 132 + 62 * len(PRINCIPLES) + 30
    s = frame(theme, H, top=14)
    s.section_label(76, 86, "05", "How I build")
    for i, (k, v) in enumerate(PRINCIPLES):
        y = 112 + i * 62
        s.inset(62, y, W - 124, 50, 25, "sm")
        s.circle_raised(94, y + 25, 16, "sm")
        s.text(94, y + 29.5, f"0{i+1}", 11, anchor="middle", weight=500)
        s.text(128, y + 30, k, 15, weight=500)
        s.text(316, y + 30, v, 14, "mute")
    return s


def contact(theme):
    s = frame(theme, 316, top=14, bottom=2)
    s.section_label(76, 86, "06", "Contact")
    s.text(76, 134, "Let's build something.", 26, font="display", weight=300)
    s.inset(60, 168, W - 120, 88, 44)
    s.inset(80, 184, W - 240, 56, 28, "sm")
    s.line_icon("gmail", 120, 212)
    s.text(144, 217, EMAIL, 16, "mute")
    s.circle_raised(W - 118, 212, 30)
    s.line_icon("right", W - 118, 212)
    return s


def button(label, kind):
    def build(theme):
        s = SVG(268, 124, theme)
        s.corners = "all"
        s.raised(28, 28, 212, 68, 34)
        s.circle_inset(70, 62, 21, "sm")
        if kind == "github":
            s.logo("github", 70, 62, 19)
        else:
            s.line_icon("linkedin", 70, 62)
        s.text(106, 67, label, 15, weight=500)
        s.line_icon("arrow", 210, 62, "mute")
        return s
    return build


if __name__ == "__main__":
    from neu import write_panel
    write_panel("hero", [header, about], "DEJI.PY — Software engineer and product builder")
    write_panel("work", [work, projects], "Selected work: BusyBuddy, Fastro, Collabr, Keyp")
    write_panel("toolbox", [toolbox], "Toolbox")
    write_panel("principles", [principles], "How I build")
    write_panel("contact", [contact], "Email Deji")
    write("btn-github", button("GitHub", "github"), "GitHub")
    write("btn-linkedin", button("LinkedIn", "linkedin"), "LinkedIn")
    print("panels built")
