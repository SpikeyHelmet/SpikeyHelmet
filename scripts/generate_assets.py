"""Generate the light/dark SVG panels for the SpikeyHelmet GitHub profile README."""
import html
import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
os.makedirs(OUT, exist_ok=True)

W = 840
DISPLAY = ("'Inter Tight', Inter, 'Segoe UI Variable Display', 'Segoe UI', system-ui, "
           "-apple-system, 'Helvetica Neue', Arial, sans-serif")
MONO = ("'Geist Mono', ui-monospace, 'SF Mono', 'Cascadia Mono', 'Segoe UI Mono', "
        "Menlo, Consolas, monospace")

INK, PAPER = "#0b0b14", "#f4f4fa"
PRIMARY, PACTIVE = "#2563eb", "#1e40af"
LED, MINT, AMBER, LILAC, RED = "#6e9bff", "#3ce6a8", "#ffb020", "#b79cff", "#ff5a5a"
LED_OFF_INK, DIM, DIM2 = "#1b1e2e", "#2a2d40", "#3a3d52"

THEMES = {
    "dark": dict(card="#151515", well="#1c1c1e", border="#313131", strong="#484848",
                 fg="#f5f5f5", muted="#c9cbda", faint="#8f91a3", ptext="#7aa2ff",
                 cap="#1f1f22", capfg="#f4f4fa", lip="#5e5f6b", ledoff="#25283a"),
    "light": dict(card="#ffffff", well="#f6f6f8", border="#e0e0e0", strong="#c4c4c4",
                  fg="#0b0b14", muted="#2b2f47", faint="#6b6e80", ptext="#1d4ed8",
                  cap="#ffffff", capfg="#0b0b14", lip="#636363", ledoff="#d6d6e2"),
}

BASE_CSS = """
.ch{opacity:0;animation:ch 4.5s linear infinite}
@keyframes ch{0%{opacity:0}4%{opacity:1}30%{opacity:0}100%{opacity:0}}
.hu{animation:hu 6s linear infinite}
@keyframes hu{0%,100%{fill:#6e9bff}33%{fill:#3ce6a8}66%{fill:#b79cff}}
.pu{animation:pu 2.4s ease-in-out infinite}
@keyframes pu{50%{opacity:.35}}
.bl{animation:bl 1.6s steps(1) infinite}
@keyframes bl{50%{opacity:.18}}
.pk{opacity:0;animation:pk 1.8s linear infinite}
@keyframes pk{0%{transform:translateX(0);opacity:0}15%{opacity:1}85%{opacity:1}100%{transform:translateX(64px);opacity:0}}
"""


def esc(s):
    return html.escape(s, quote=True)


def mw(s, size, ls=0.0):
    """Rough monospace width estimate."""
    return len(s) * (0.6 * size + ls)


def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def grad3(t):
    return lerp(LED, MINT, t * 2) if t < 0.5 else lerp(MINT, LILAC, (t - 0.5) * 2)


def doc(w, h, label, body, css="", glow_w=None):
    gw = glow_w or 3 * w
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<style><![CDATA[
.d{{font-family:{DISPLAY}}}
.m{{font-family:{MONO}}}
{BASE_CSS}
{css}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}.ch{{opacity:0}}.pk{{opacity:0}}}}
]]></style>
<defs><filter id="glow" filterUnits="userSpaceOnUse" x="{-w}" y="{-h}" width="{gw}" height="{3 * h}"><feGaussianBlur stdDeviation="2.4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
{body}
</svg>
"""


def card(w, h, t, r=24):
    return f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{r}" fill="{t["card"]}" stroke="{t["border"]}"/>'


def text(x, y, s, cls, size, fill, weight=400, anchor="start", ls=None, extra=""):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    l = f' letter-spacing="{ls}"' if ls is not None else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}"{a}{l}{extra}>{esc(s)}</text>')


def sticker(x, y, label, color, rot=0, size=11):
    ls = 0.6
    w = mw(label, size, ls) + 20
    h = size + 13
    cx, cy = x + w / 2, y + h / 2
    s = (f'<g transform="rotate({rot} {cx:.1f} {cy:.1f})">'
         f'<rect x="{x + 2:.1f}" y="{y + 3:.1f}" width="{w:.1f}" height="{h}" rx="6" fill="{INK}" opacity=".25"/>'
         f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="6" fill="{color}"/>'
         + text(cx, y + h / 2 + size * 0.36, label, "m", size, INK, 700, "middle", ls)
         + "</g>")
    return s, w


def track(x0, x1, y, t, period=4.5, step=14, r=2.6):
    n = int((x1 - x0) // step) + 1
    base = "".join(f'<circle cx="{x0 + i * step:.1f}" cy="{y}" r="{r}" fill="{t["ledoff"]}"/>' for i in range(n))
    lit = "".join(
        f'<circle class="ch" cx="{x0 + i * step:.1f}" cy="{y}" r="{r}" fill="{grad3(i / (n - 1))}" '
        f'style="animation-delay:{(i / n) * period - period:.2f}s"/>' for i in range(n))
    return base + f'<g filter="url(#glow)">{lit}</g>'


def heading(label, title, t, y=48):
    return (text(40, y, label, "m", 12, t["faint"], 500, ls=1.2)
            + text(39, y + 34, title, "d", 28, t["fg"], 700, ls=-0.6))


# ---------------------------------------------------------------- panels

def ticker():
    w, h, size, ls = W, 44, 12, 1.0
    items = ["Member Technical Staff @ Zoho", "4+ years in enterprise IAM", "100+ enterprise clients",
             "50k+ end users", "CI/CD 62% faster", "Java · Rust · Spring Boot", "Chennai, India / Remote"]
    slots, x = [], 0.0
    for s in items:
        s = s.upper()
        slots.append((x, s))
        x += mw(s, size, ls) + 52
    period = x
    copies = math.ceil((w + period) / period) + 1
    texts, dots = [], []
    for k in range(copies):
        for sx, s in slots:
            X = 24 + sx + k * period
            texts.append(text(X, 26.5, s, "m", size, PAPER, 500, ls=ls))
            dots.append(f'<circle cx="{X + mw(s, size, ls) + 24:.1f}" cy="22" r="3" fill="{MINT}"/>')
    css = (f".tk{{animation:tk {period / 40:.1f}s linear infinite}}"
           f"@keyframes tk{{to{{transform:translateX(-{period:.1f}px)}}}}")
    body = (f'<clipPath id="c"><rect width="{w}" height="{h}" rx="12"/></clipPath>'
            f'<rect width="{w}" height="{h}" rx="12" fill="{PRIMARY}"/>'
            f'<g clip-path="url(#c)"><g class="tk">{"".join(texts)}<g filter="url(#glow)">{"".join(dots)}</g></g></g>')
    label = " · ".join(items)
    return doc(w, h, label, body, css, glow_w=int(copies * period + 2 * w))


GLYPHS = {
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
}


def hero(t):
    w, h = W, 360
    b = [card(w, h, t), track(32, 808, 24, t)]
    b.append(text(40, 70, "SPIKEYHELMET", "m", 12, t["faint"], 500, ls=1.2))
    lines = [("Behind the login.", t["fg"]), ("Inside the directory.", t["fg"]), ("Under every deploy.", t["ptext"])]
    for i, (s, c) in enumerate(lines):
        b.append(text(37, 126 + i * 50, s, "d", 42, c, 700, ls=-1.2))
    b.append(text(40, 268, "Software Engineer at Zoho, building enterprise IAM", "d", 16, t["muted"]))
    b.append(text(40, 292, "for ManageEngine Identity360. 100+ clients, 50k+ users.", "d", 16, t["muted"]))
    b.append(f'<circle class="pu" cx="45" cy="327" r="4" fill="{MINT}" filter="url(#glow)"/>')
    b.append(text(58, 331, "26 · CHENNAI, INDIA / REMOTE", "m", 11.5, t["faint"], 500, ls=1.2))

    # LED matrix with "RR"
    wx, wy, ww, wh, cell = 566, 52, 244, 176, 17
    cols, rows = 13, 9
    gx = wx + (ww - cols * cell) / 2
    gy = wy + (wh - rows * cell) / 2
    lit = set()
    for off, letter in ((1, "S"), (7, "H")):
        for r, row in enumerate(GLYPHS[letter]):
            for c, ch in enumerate(row):
                if ch == "#":
                    lit.add((off + c, 1 + r))
    b.append(f'<rect x="{wx}.5" y="{wy}.5" width="{ww}" height="{wh}" rx="16" fill="{INK}" stroke="{t["border"]}"/>')
    off_dots, on_dots = [], []
    for r in range(rows):
        for c in range(cols):
            cx, cy = gx + cell / 2 + c * cell, gy + cell / 2 + r * cell
            if (c, r) in lit:
                on_dots.append(f'<circle class="hu" cx="{cx:.1f}" cy="{cy:.1f}" r="5.4" '
                               f'style="animation-delay:{c * 0.35 - 6:.2f}s"/>')
            else:
                off_dots.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="5.4" fill="{LED_OFF_INK}"/>')
    b.append("".join(off_dots))
    b.append(f'<g filter="url(#glow)" fill="{LED}">{"".join(on_dots)}</g>')

    b.append(sticker(624, 262, "IAM · SSO · MFA", MINT, -4)[0])
    label = ("SpikeyHelmet (Rayon Rozario). Behind the login. Inside the directory. Under every deploy. "
             "Software Engineer at Zoho, building enterprise IAM for ManageEngine Identity360.")
    return doc(w, h, label, "".join(b))


def lore(t):
    w = W
    b = [heading("THE LORE", "Started at 7. Never logged off.", t)]
    para = ["Got my first computer at 7, the internet at 11, and I've been chronically online since.",
            "Java and JavaScript are my OGs. Self-taught on MERN, now deep in enterprise IAM at Zoho,",
            "making sure the right people get in and everyone else gets left on read.",
            "Off the clock: gaming, guitar, game servers, and convincing ceiling fans to speak MQTT."]
    for i, line in enumerate(para):
        b.append(text(40, 120 + i * 23, line, "d", 15, t["muted"]))

    # 2027 goals as a terminal-style patch file
    wx, wy, ww = 40, 214, w - 80
    notes = [("+", MINT, "open source arc: more merged PRs than open browser tabs. delusional? we ball."),
             ("+", MINT, "AI adoption: get the team actually shipping with AI, not just saying it in standup."),
             ("~", AMBER, "rust era: me and the borrow checker are in a situationship."),
             ("+", MINT, "touch grass: scheduled. cron job still pending code review.")]
    wh = 108 + len(notes) * 24
    b.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="16" fill="{INK}" stroke="{t["border"]}"/>')
    for k, col in enumerate((RED, AMBER, MINT)):
        b.append(f'<circle cx="{wx + 22 + k * 16}" cy="{wy + 22}" r="5" fill="{col}"/>')
    b.append(text(wx + ww - 20, wy + 26, "~/2027 $ cat goals.patch", "m", 11.5, "#8f91a3", 500, "end", ls=0.6))
    b.append(f'<line x1="{wx}" y1="{wy + 42}" x2="{wx + ww}" y2="{wy + 42}" stroke="{DIM}"/>')
    b.append(text(wx + 20, wy + 80, "2027: let him cook.", "d", 24, PAPER, 700, ls=-0.5))
    for k, (sign, col, line) in enumerate(notes):
        y = wy + 112 + k * 24
        b.append(text(wx + 20, y, sign, "m", 13, col, 700))
        b.append(text(wx + 40, y, line, "m", 12.5, "#c9cbda", 400))
    b.append(sticker(wx + ww - 120, wy + 56, "NO CAP", AMBER, 6)[0])

    qy = wy + wh + 46
    b.append(text(40, qy, "“I got 99 problems but a 401 ain't one.”", "d", 22, t["fg"], 700, ls=-0.4))
    b.append(text(40, qy + 26, "— EVERY IAM ENGINEER, PROBABLY", "m", 11.5, t["faint"], 500, ls=1.2))
    h = qy + 50
    body = card(w, h, t) + "".join(b)
    label = ("The lore: first computer at 7, internet at 11, chronically online since. Java and JavaScript are my OGs; "
             "self-taught on MERN, now in enterprise IAM at Zoho. Off the clock: gaming, guitar, game servers and IoT. "
             "2027 goals: more open source, real AI adoption on the team, the Rust era, and touching grass. "
             "\"I got 99 problems but a 401 ain't one.\"")
    return doc(w, h, label, body)


def numbers(t):
    w, h = W, 236
    b = [card(w, h, t), heading("AT ZOHO SINCE DEC 2021", "5 numbers from the day job", t)]
    items = [("4+", ["years building", "enterprise IAM"], LED),
             ("100+", ["enterprise", "clients"], MINT),
             ("50k+", ["end users on", "Identity360"], AMBER),
             ("62%", ["faster CI/CD", "(20 → 8 min)"], LILAC),
             ("20+", ["zero-downtime", "DB migrations"], RED)]
    cw = (w - 80) / 5
    for i, (n, cap, col) in enumerate(items):
        x = 40 + i * cw
        if i:
            b.append(f'<line x1="{x - 14:.1f}" y1="110" x2="{x - 14:.1f}" y2="210" stroke="{t["border"]}"/>')
        b.append(f'<circle cx="{x + 5:.1f}" cy="118" r="4.5" fill="{col}" filter="url(#glow)"/>')
        b.append(text(x - 2, 168, n, "d", 46, t["fg"], 700, ls=-1.5))
        b.append(text(x, 192, cap[0], "d", 13.5, t["muted"]))
        b.append(text(x, 210, cap[1], "d", 13.5, t["muted"]))
    label = ("5 numbers from the day job: 4+ years building enterprise IAM, 100+ enterprise clients, "
             "50k+ end users, 62% faster CI/CD, 20+ zero-downtime DB migrations.")
    return doc(w, h, label, "".join(b))


def shipped(t):
    w = W
    items = [("Directory sync", ["Azure AD cloud sync, plus an on-prem Active",
                                 "Directory agent that talks over WebSockets."]),
             ("Identity360 features", ["MFA Agents, GRC with JIT Access, Reports and",
                                       "Dashboards for ManageEngine's IAM product."]),
             ("Faster builds", ["Internal tool that cut CI/CD from 20 to 8 min:",
                                "multi-repo builds, parallel tests, cached deps."]),
             ("Zero-downtime migrations", ["Led 20+ schema and data migrations on",
                                           "production MySQL with no service disruption."])]
    cw, ch, top = (w - 80 - 16) / 2, 108, 106
    b = [heading("MEMBER TECHNICAL STAFF · ZOHO", "What I've shipped", t)]
    for i, (title, lines) in enumerate(items):
        x = 40 + (i % 2) * (cw + 16)
        y = top + (i // 2) * (ch + 16)
        b.append(f'<rect x="{x:.1f}" y="{y}.5" width="{cw:.1f}" height="{ch}" rx="16" fill="{t["well"]}" stroke="{t["border"]}"/>')
        b.append(f'<circle cx="{x + 34:.1f}" cy="{y + 34}" r="14" fill="{PRIMARY}"/>')
        b.append(text(x + 34, y + 38.5, str(i + 1), "m", 13, PAPER, 700, "middle"))
        b.append(text(x + 60, y + 40, title, "d", 17, t["fg"], 700, ls=-0.3))
        b.append(text(x + 20, y + 72, lines[0], "d", 13.5, t["muted"]))
        b.append(text(x + 20, y + 92, lines[1], "d", 13.5, t["muted"]))
    fy = top + 2 * ch + 16 + 34
    b.append(text(40, fy, "ALSO: MYSQL QUERY TUNING · AI-BUILT QENGINE TESTS (CLAUDE CODE) · MENTORING",
                  "m", 11, t["faint"], 500, ls=0.8))
    h = fy + 26
    body = card(w, h, t) + "".join(b)
    label = ("What I've shipped at Zoho: directory sync for Azure AD and on-prem Active Directory over WebSockets; "
             "Identity360 MFA Agents, GRC with JIT Access, Reports and Dashboards; an internal tool that cut CI/CD "
             "from 20 to 8 minutes; 20+ zero-downtime MySQL migrations.")
    return doc(w, h, label, body)


BULB = ["..###..", ".#####.", "#######", "#######", "#######", ".#####.", "..###..", "..bbb..", "..bbb.."]


def projects(t):
    w = W
    cw, ch, top = (w - 80 - 16) / 2, 300, 106
    b = [heading("OFF THE CLOCK", "Built after hours", t)]
    cards = [
        ("Multiplayer game server platform",
         [("TOP 3 IN INDIA", AMBER, -4), ("200K+ PLAYERS", MINT, 3)],
         ["Self-hosted and community-run. 50+ concurrent",
          "players at peak, years of continuous uptime.",
          "5+ custom Java plugins, 75+ game mechanics,",
          "4 game modes and a 20+ person volunteer staff."]),
        ("Hyper Atlas · Twoto",
         [("ESP32", LILAC, -3), ("MQTT", LED, 4), ("FLUTTER", MINT, -2)],
         ["Smart-home IoT that retrofits ordinary fans",
          "and lights with remote control and automation.",
          "PlatformIO firmware, a Flutter app and a",
          "Node.js backend over low-latency MQTT."]),
    ]
    for i, (title, stickers, lines) in enumerate(cards):
        x = 40 + i * (cw + 16)
        y = top
        b.append(f'<rect x="{x:.1f}" y="{y}.5" width="{cw:.1f}" height="{ch}" rx="18" fill="{t["well"]}" stroke="{t["border"]}"/>')
        wx, wy, ww, wh = x + 12, y + 12, cw - 24, 124
        b.append(f'<rect x="{wx:.1f}" y="{wy}" width="{ww:.1f}" height="{wh}" rx="12" fill="{INK}"/>')
        if i == 0:
            ux = wx + (ww - 150) / 2
            for u in range(3):
                uy = wy + 18 + u * 32
                b.append(f'<rect x="{ux:.1f}" y="{uy}" width="150" height="24" rx="4" fill="{LED_OFF_INK}" stroke="{DIM}"/>')
                for k, (col, dur, dl) in enumerate([(MINT, 1.6, -0.3 * u), (MINT, 2.3, -0.7 * u - 0.4), (AMBER, 1.1, -0.5 * u)]):
                    b.append(f'<circle class="bl" cx="{ux + 14 + k * 12:.1f}" cy="{uy + 12}" r="3.3" fill="{col}" '
                             f'filter="url(#glow)" style="animation-duration:{dur}s;animation-delay:{dl:.1f}s"/>')
                for v in range(6):
                    vx = ux + 74 + v * 12
                    b.append(f'<line x1="{vx:.1f}" y1="{uy + 7}" x2="{vx:.1f}" y2="{uy + 17}" stroke="{DIM2}" stroke-width="2" stroke-linecap="round"/>')
        else:
            px, py = wx + 84, wy + 32
            b.append(f'<rect x="{px:.1f}" y="{py}" width="34" height="60" rx="7" fill="{LED_OFF_INK}" stroke="{DIM2}" stroke-width="1.5"/>')
            b.append(f'<rect x="{px + 7:.1f}" y="{py + 25}" width="20" height="11" rx="5.5" fill="{MINT}"/>')
            b.append(f'<circle cx="{px + 21.5:.1f}" cy="{py + 30.5}" r="3.6" fill="{INK}"/>')
            for k in range(3):
                b.append(f'<circle class="pk" cx="{px + 44:.1f}" cy="{py + 30}" r="2.6" fill="{MINT}" '
                         f'style="animation-delay:{-0.6 * k:.1f}s"/>')
            cell = 10
            bx, by = px + 124, wy + (wh - 9 * cell) / 2
            lit, base = [], []
            for r, row in enumerate(BULB):
                for c, chh in enumerate(row):
                    cx, cy = bx + c * cell + cell / 2, by + r * cell + cell / 2
                    if chh == "#":
                        lit.append(f'<rect x="{cx - 4:.1f}" y="{cy - 4:.1f}" width="8" height="8" rx="2"/>')
                    elif chh == "b":
                        base.append(f'<rect x="{cx - 4:.1f}" y="{cy - 4:.1f}" width="8" height="8" rx="2" fill="{DIM2}"/>')
            b.append("".join(base))
            b.append(f'<g class="pu" fill="{AMBER}" filter="url(#glow)">{"".join(lit)}</g>')
        sx = x + 24
        for label, col, rot in stickers:
            s, sw = sticker(sx, wy + wh - 12, label, col, rot)
            b.append(s)
            sx += sw + 8
        b.append(text(x + 24, y + 186, title, "d", 18, t["fg"], 700, ls=-0.3))
        for k, line in enumerate(lines):
            b.append(text(x + 24, y + 214 + k * 20, line, "d", 13.5, t["muted"]))
    h = top + ch + 24
    body = card(w, h, t) + "".join(b)
    label = ("Built after hours: a self-hosted multiplayer game server platform (Top 3 in India, 200k+ players, "
             "5+ custom Java plugins); and Hyper Atlas / Twoto, a smart-home IoT framework with ESP32 firmware, "
             "a Flutter app and a Node.js backend over MQTT.")
    return doc(w, h, label, body)


def chip(x, y, name, kind, t):
    size = 12
    w = mw(name, size) + 20
    h = 30
    if kind:
        cap, lip, fg, stroke = PRIMARY, PACTIVE, PAPER, "none"
    else:
        cap, lip, fg, stroke = t["cap"], t["lip"], t["capfg"], t["strong"]
    s = (f'<rect x="{x:.1f}" y="{y + 3.5}" width="{w:.1f}" height="{h}" rx="8" fill="{lip}"/>'
         f'<rect x="{x:.1f}" y="{y + .5}" width="{w:.1f}" height="{h}" rx="8" fill="{cap}" stroke="{stroke}"/>'
         + text(x + w / 2, y + 19.5, name, "m", size, fg, 500, "middle"))
    if kind == 2:
        s += sticker(x + w - 22, y - 11, "NEW", MINT, 9, size=9)[0]
    return s, w


def stack(t):
    w = W
    rows = [("LANGUAGES", [("Java", 1), ("Rust", 2), ("TypeScript", 0), ("JavaScript", 0), ("C++", 0),
                           ("SQL", 0), ("HTML", 0), ("CSS", 0)]),
            ("FRAMEWORKS", [("Spring Boot", 1), ("Spring", 0), ("Node.js", 0), ("Next.js", 0), ("React", 0),
                            ("Ember.js", 0), ("Tomcat", 0)]),
            ("IDENTITY", [("SAML", 0), ("OAuth 2.0 / OIDC", 0), ("SCIM", 0), ("LDAP", 0),
                          ("Active Directory", 1), ("MFA", 0), ("RBAC", 0), ("SSO", 0), ("JIT Access", 0)]),
            ("DATA", [("MySQL", 1), ("PostgreSQL", 0), ("Redis", 0), ("MongoDB", 0)]),
            ("CLOUD & OPS", [("AWS", 0), ("Azure", 0), ("GCP", 0), ("Docker", 0), ("CI/CD", 0), ("Linux", 0),
                             ("Git", 0), ("GitHub", 0)]),
            ("AI TOOLS", [("Claude Code", 0), ("GitHub Copilot", 0), ("ChatGPT", 0)])]
    b = [heading("STACK", "What it runs on", t)]
    y, cx0, maxx = 112, 176, 800
    for label, chips in rows:
        b.append(text(40, y + 20, label, "m", 11.5, t["faint"], 500, ls=1.2))
        x = cx0
        for name, kind in chips:
            cw = mw(name, 12) + 20
            if x + cw > maxx:
                x = cx0
                y += 44
            s, cw = chip(x, y, name, kind, t)
            b.append(s)
            x += cw + 8
        y += 52
    h = y + 8
    body = card(w, h, t) + "".join(b)
    label = "Stack: " + "; ".join(f"{lbl.title()}: " + ", ".join(n for n, _ in chips) for lbl, chips in rows)
    return doc(w, h, label, body)


def footer(t):
    w, h = W, 156
    b = [card(w, h, t), track(32, 808, 24, t)]
    b.append(text(39, 78, "SpikeyHelmet", "d", 26, t["fg"], 700, ls=-0.6))
    b.append(text(40, 106, "Enterprise IAM by day. Game servers and smart-home IoT after hours.", "d", 15, t["muted"]))
    b.append(text(40, 136, "MADE IN CHENNAI, INDIA", "m", 11, t["faint"], 500, ls=1.2))
    b.append(text(800, 136, "THANKS FOR STOPPING BY", "m", 11, t["faint"], 500, "end", ls=1.2))
    return doc(w, h, "SpikeyHelmet. Enterprise IAM by day. Game servers and smart-home IoT after hours. Made in Chennai, India.", "".join(b))


def keycap(label, kind, t):
    size, ls = 14, 0.3
    tw = mw(label, size, ls)
    w, h = 20 + tw + 10 + 11 + 20, 44
    if kind:
        cap, lip, fg, stroke = PRIMARY, PACTIVE, PAPER, "none"
    else:
        cap, lip, fg, stroke = t["cap"], t["lip"], t["capfg"], t["strong"]
    ax, ay = 21 + tw + 10, 1 + h / 2 - 5.5
    body = (f'<rect x="1" y="5.5" width="{w:.1f}" height="{h}" rx="10" fill="{lip}"/>'
            f'<rect x="1" y="1.5" width="{w:.1f}" height="{h}" rx="10" fill="{cap}" stroke="{stroke}"/>'
            + text(21, 1 + h / 2 + 5, label, "m", size, fg, 600, ls=ls)
            + f'<path d="M{ax:.1f} {ay + 11:.1f}L{ax + 11:.1f} {ay:.1f}M{ax + 3.5:.1f} {ay:.1f}H{ax + 11:.1f}V{ay + 7.5:.1f}" '
              f'stroke="{fg}" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    return doc(int(w + 3), h + 8, label, body)


def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


write("ticker.svg", ticker())
for mode, t in THEMES.items():
    write(f"hero-{mode}.svg", hero(t))
    write(f"lore-{mode}.svg", lore(t))
    write(f"numbers-{mode}.svg", numbers(t))
    write(f"shipped-{mode}.svg", shipped(t))
    write(f"projects-{mode}.svg", projects(t))
    write(f"stack-{mode}.svg", stack(t))
    write(f"footer-{mode}.svg", footer(t))
    write(f"key-linkedin-{mode}.svg", keycap("LinkedIn", 1, t))
    write(f"key-instagram-{mode}.svg", keycap("Instagram", 0, t))
print("ok", sorted(os.listdir(OUT)))
