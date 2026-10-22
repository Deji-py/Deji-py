"""Builds the neumorphic GitHub stats card from live data.

Run by .github/workflows/stats.yml (daily + on push). Locally:
    GH_TOKEN=<token> GH_USER=Deji-py python scripts/build_stats.py
    python scripts/build_stats.py --sample      # preview with fake numbers
    python scripts/build_stats.py --placeholder # card shown before the first run
"""
import datetime as dt
import json
import os
import sys
import urllib.request

from neu import SVG, write, compose

W, P = 840, 36
USER = os.environ.get("GH_USER", "Deji-py")

QUERY = """
query($login:String!, $after:String) {
  user(login:$login) {
    followers { totalCount }
    pullRequests { totalCount }
    repositories(first:100, after:$after, ownerAffiliations:OWNER, isFork:false) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes { stargazerCount
        languages(first:10, orderBy:{field:SIZE, direction:DESC}) { edges { size node { name color } } } }
    }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar { totalContributions weeks { contributionDays { contributionCount date contributionLevel } } }
    }
  }
}"""


def gql(token, variables):
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": QUERY, "variables": variables}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": "neu-stats"})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.load(r)
    if "errors" in body:
        raise SystemExit(f"GraphQL error: {body['errors']}")
    return body["data"]["user"]


def fetch(token):
    after, stars, langs, first = None, 0, {}, None
    while True:
        u = gql(token, {"login": USER, "after": after})
        first = first or u
        repos = u["repositories"]
        for n in repos["nodes"]:
            stars += n["stargazerCount"]
            for e in n["languages"]["edges"]:
                name = e["node"]["name"]
                size, col = langs.get(name, (0, e["node"]["color"]))
                langs[name] = (size + e["size"], col or "#8D96A0")
        if not repos["pageInfo"]["hasNextPage"]:
            break
        after = repos["pageInfo"]["endCursor"]
    cal = first["contributionsCollection"]["contributionCalendar"]
    lv = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    days = [(d["date"], d["contributionCount"], lv.get(d["contributionLevel"], 0))
            for w in cal["weeks"] for d in w["contributionDays"]]
    return dict(contrib=cal["totalContributions"],
                commits=first["contributionsCollection"]["totalCommitContributions"],
                prs=first["pullRequests"]["totalCount"], stars=stars,
                repos=first["repositories"]["totalCount"], followers=first["followers"]["totalCount"],
                days=days, langs=langs)


def streaks(days):
    counts = [d[1] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today not started yet — don't break the streak
        i -= 1
    while i >= 0 and counts[i]:
        cur, i = cur + 1, i - 1
    return cur, longest


def fmt(n):
    return f"{n/1000:.1f}k" if n >= 10000 else f"{n:,}"


# GitHub's own contribution greens (levels 0-4)
HEAT = {"light": ["#EBEDF0", "#9BE9A8", "#40C463", "#30A14E", "#216E39"],
        "dark":  ["#161B22", "#0E4429", "#006D32", "#26A641", "#39D353"]}


def levels(days):
    """Use GitHub's level when present, otherwise quartiles of the busiest day."""
    if days and len(days[0]) > 2:
        return [d[2] for d in days]
    mx = max((d[1] for d in days), default=0) or 1
    return [0 if c == 0 else min(4, 1 + int(4 * (c - 1) / mx)) for _, c in days]


def heatmap(s, theme, days, gx, gy, gw):
    """GitHub-style contribution grid: one column per week, Sunday on top."""
    pitch, cell = 12, 9.5
    first = dt.date.fromisoformat(days[0][0])
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)  # back to Sunday
    ncols = (dt.date.fromisoformat(days[-1][0]) - start).days // 7 + 1
    x0 = gx + (gw - 30 - ncols * pitch) / 2 + 30
    y0 = gy + 58
    cols = HEAT[theme]
    rects = []
    for (d, c, *_), lv in zip(days, levels(days)):
        dd = dt.date.fromisoformat(d)
        col, row = (dd - start).days // 7, (dd.weekday() + 1) % 7
        rects.append(f'<rect x="{x0 + col*pitch:.1f}" y="{y0 + row*pitch}" width="{cell}" height="{cell}" rx="2" fill="{cols[lv]}"><title>{c} on {d}</title></rect>')
    s.add("".join(rects))
    for row, lab in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        s.text(x0 - 8, y0 + row * pitch + 8.5, lab, 9.5, "mute", anchor="end")
    last_m = None
    for col in range(ncols):
        d = start + dt.timedelta(days=col * 7)
        if d.month != last_m and col < ncols - 2:
            if last_m is not None or d.day <= 7:
                s.text(x0 + col * pitch, y0 - 8, d.strftime("%b"), 9.5, "mute")
            last_m = d.month
    ly = y0 + 7 * pitch + 14
    right = x0 + ncols * pitch - (pitch - cell)
    s.text(right, ly + 8.5, "More", 9.5, "mute", anchor="end")
    bx0 = right - 30 - 5 * pitch
    for i in range(5):
        s.add(f'<rect x="{bx0 + i*pitch:.1f}" y="{ly}" width="{cell}" height="{cell}" rx="2" fill="{cols[i]}"/>')
    s.text(bx0 - 6, ly + 8.5, "Less", 9.5, "mute", anchor="end")


def card(data, placeholder=False):
    def build(theme):
        H = 640
        s = SVG(W, H, theme)
        s.raised(P, P, W - 2 * P, H - 2 * P, 40)
        s.section_label(76, 76, "04", "Build log")
        stamp = "Waiting for first update" if placeholder else "Updated " + dt.date.today().strftime("%d %b %Y")
        s.text(W - 76, 76, stamp, 13, "mute", anchor="end")

        # ---- six metric tiles ----
        if placeholder:
            vals = ["—"] * 6
        else:
            cur, longest = streaks(data["days"])
            vals = [fmt(data["contrib"]), f"{cur}d", f"{longest}d", fmt(data["commits"]), fmt(data["prs"]), fmt(data["stars"])]
        labels = ["CONTRIBUTIONS", "CURRENT STREAK", "LONGEST STREAK", "COMMITS · 12 MO", "PULL REQUESTS", "STARS EARNED"]
        gap, th = 20, 72
        tw = (W - 128 - 2 * gap) / 3
        for i, (v, lb) in enumerate(zip(vals, labels)):
            x = 64 + (i % 3) * (tw + gap)
            y = 96 + (i // 3) * (th + 16)
            s.inset(x, y, tw, th, 22, "sm")
            s.text(x + 22, y + 38, v, 24, font="display", weight=300)
            s.text(x + 22, y + 59, lb, 10, "mute", weight=500, ls=1.4)

        # ---- contribution graph ----
        gx, gy, gw, gh = 64, 280, W - 128, 178
        s.inset(gx, gy, gw, gh, 26)
        title = "CONTRIBUTIONS · LAST 12 MONTHS"
        s.text(gx + 24, gy + 28, title, 10, "mute", weight=500, ls=1.4)
        if placeholder:
            end = dt.date.today()
            days = [((end - dt.timedelta(days=364 - i)).isoformat(), 0) for i in range(365)]
        else:
            days = data["days"]
        heatmap(s, theme, days, gx, gy, gw)

        # ---- languages ----
        ly = 486
        s.text(68, ly + 4, "TOP LANGUAGES", 10, "mute", weight=500, ls=1.4)
        bx, by, bw, bh = 64, ly + 16, W - 128, 22
        s.inset(bx, by, bw, bh, 11, "sm")
        if not placeholder and data["langs"]:
            top = sorted(data["langs"].items(), key=lambda kv: -kv[1][0])[:6]
            total = sum(v[0] for _, v in top) or 1
            s.add(f'<clipPath id="bar"><rect x="{bx+5}" y="{by+5}" width="{bw-10}" height="{bh-10}" rx="6"/></clipPath>')
            x, segs = bx + 5, []
            for name, (size, col) in top:
                w = (bw - 10) * size / total
                segs.append(f'<rect x="{x:.1f}" y="{by+5}" width="{w+0.6:.1f}" height="{bh-10}" fill="{col}"/>')
                x += w
            s.add(f'<g clip-path="url(#bar)">{"".join(segs)}</g>')
            for i, (name, (size, col)) in enumerate(top):
                cx = 72 + (i % 3) * 240
                cy = by + 48 + (i // 3) * 26
                s.add(f'<circle cx="{cx}" cy="{cy - 4}" r="5" fill="{col}"/>')
                s.text(cx + 14, cy, name, 13.5, weight=500)
                s.text(cx + 200, cy, f"{100*size/total:.1f}%", 12.5, "mute", anchor="end")
        else:
            s.text(W / 2, by + 52, "Language breakdown appears after the first workflow run.", 12.5, "mute", anchor="middle")
        return compose(theme, [(s, H)])
    return build


def sample():
    import random
    random.seed(4)
    start = dt.date.today() - dt.timedelta(days=364)
    days = []
    for i in range(365):
        d = start + dt.timedelta(i)
        busy = 0.35 + 0.4 * (i > 200) - 0.25 * (d.weekday() >= 5)
        days.append((d.isoformat(), 0 if random.random() > busy else int(random.expovariate(0.25)) + 1))
    return dict(contrib=sum(d[1] for d in days), commits=1180, prs=96, stars=41, repos=38, followers=60, days=days,
                langs={"TypeScript": (520, "#3178c6"), "JavaScript": (260, "#f1e05a"), "Python": (140, "#3572A5"),
                       "CSS": (60, "#663399"), "HTML": (30, "#e34c26"), "Shell": (8, "#89e051")})


if __name__ == "__main__":
    if "--placeholder" in sys.argv:
        write("stats", card(None, placeholder=True), "GitHub stats")
    elif "--sample" in sys.argv:
        write("stats", card(sample()), "GitHub stats (sample)")
    else:
        tok = os.environ.get("GH_TOKEN") or sys.exit("GH_TOKEN not set")
        write("stats", card(fetch(tok)), f"GitHub stats for {USER}")
    print("stats card built")
