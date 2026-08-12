#!/usr/bin/env python3
"""Generate Upbound-branded slide SVGs (960x540) for the reveal deck.

Design system:
  - Translucent deep-purple panel over the WebGL cube background
  - Light purple (#B9A6FF) titles vs pale lavender (#EDE9FF) body = dark/light contrast
  - Upbound 'up' dot motif, consistent footer
"""
import os, io, base64
from PIL import Image

HERE   = os.path.dirname(os.path.abspath(__file__))
OUT    = HERE                                    # SVGs are written next to this script
AVATAR = os.path.join(HERE, "..", "images", "upbound_avatar.png")

# palette
DEEP   = "#140B33"   # panel dark purple
BORDER = "#8B6CFF"   # light purple border/accents
TITLE  = "#B9A6FF"   # light purple titles
BODY   = "#EDE9FF"   # pale lavender body text
DIM    = "#7C6FAE"   # muted footer
BRAND  = "#6B5BCD"   # upbound brand purple (from avatar)
WHITE  = "#FFFFFF"

FONT = 'font-family="Helvetica, Arial, sans-serif"'

# --- real Upbound logo, embedded as base64 so it survives <img>-loaded SVGs ---
def _logo_uri(size):
    im = Image.open(AVATAR).convert("RGBA").resize((size, size), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

LOGO_CORNER = _logo_uri(80)
LOGO_HERO   = _logo_uri(240)

def logo(x, y, w, uri=LOGO_CORNER):
    return f'  <image href="{uri}" x="{x}" y="{y}" width="{w}" height="{w}"/>\n'

def head():
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" '
            'viewBox="0 0 960 540">\n')

def panel(op=0.88):
    return (f'  <rect x="20" y="20" width="920" height="500" rx="24" '
            f'fill="{DEEP}" fill-opacity="{op}" stroke="{BORDER}" '
            f'stroke-opacity="0.35" stroke-width="2"/>\n')

def updot(x, y, s=1.0):
    """Brand mark: the real Upbound logo (replaces the old hand-drawn 'up' dot)."""
    return logo(x - 8, y - 46, 54 * s)

def footer(idx, total):
    return (f'  <text x="60" y="492" {FONT} font-size="15" fill="{DIM}">'
            f'Upbound &#8226; upbound.io</text>\n'
            f'  <text x="900" y="492" text-anchor="end" {FONT} font-size="15" '
            f'fill="{DIM}">{idx} / {total}</text>\n')

def title_bar(title, kicker=None):
    s = ""
    if kicker:
        s += (f'  <text x="60" y="86" {FONT} font-size="19" font-weight="700" '
              f'letter-spacing="3" fill="{BORDER}">{kicker.upper()}</text>\n')
    s += (f'  <text x="60" y="138" {FONT} font-size="42" font-weight="700" '
          f'fill="{TITLE}">{title}</text>\n'
          f'  <rect x="60" y="158" width="120" height="5" rx="2.5" fill="{BRAND}"/>\n')
    return s

def bullets(items, y0=215, dy=62, size=25):
    s = ""
    y = y0
    for head_txt, sub in items:
        s += f'  <circle cx="72" cy="{y-8}" r="6" fill="{BORDER}"/>\n'
        s += (f'  <text x="94" y="{y}" {FONT} font-size="{size}" '
              f'font-weight="700" fill="{BODY}">{head_txt}</text>\n')
        if sub:
            s += (f'  <text x="94" y="{y+27}" {FONT} font-size="19" '
                  f'fill="{DIM}">{sub}</text>\n')
        y += dy
    return s

def std_slide(kicker, title, items, idx, total):
    return (head() + panel() + title_bar(title, kicker)
            + bullets(items) + updot(880, 84) + footer(idx, total) + "</svg>\n")

slides = {}

# ---------------- Section 1: why control planes ----------------
slides["1/1"] = (head() + panel(0.82)
    # real logo replaces the old hand-lettered wordmark
    + logo(370, 92, 220, LOGO_HERO)
    + f'  <rect x="330" y="340" width="300" height="5" rx="2.5" fill="{BRAND}"/>\n'
    + f'  <text x="480" y="392" text-anchor="middle" {FONT} font-size="34" font-weight="700" fill="{BODY}">The Universal Cloud Platform</text>\n'
    + f'  <text x="480" y="430" text-anchor="middle" {FONT} font-size="21" fill="{DIM}">Control planes for platform engineering</text>\n'
    + f'  <text x="480" y="474" text-anchor="middle" {FONT} font-size="19" fill="{DIM}">John Boero &#8226; 2026</text>\n'
    + "</svg>\n")

slides["1/2"] = std_slide("The problem", "Cloud operations don&#8217;t scale by hand", [
    ("Ticket-driven infrastructure slows every team", "Days or weeks to provision what apps need today"),
    ("Tool and script sprawl across clouds", "Terraform here, consoles there &#8212; no single source of truth"),
    ("Configuration drift goes unchecked", "What&#8217;s running no longer matches what was declared"),
    ("Platform teams become the bottleneck", "Experts stuck fielding requests instead of building"),
], 2, 10)

slides["1/3"] = std_slide("The shift", "Platform engineering needs a control plane", [
    ("Self-service for developers, guardrails for the org", "Golden paths instead of tickets"),
    ("Infrastructure as APIs, not scripts", "Declare the what &#8212; the control plane handles the how"),
    ("Continuous reconciliation", "Desired state is enforced 24/7, drift heals itself"),
    ("One control point across every cloud", "AWS, Azure, GCP, on-prem &#8212; one consistent model"),
], 3, 10)

# ---------------- Section 2: products ----------------
slides["2/1"] = std_slide("Open source", "Crossplane &#8212; the foundation", [
    ("CNCF project, created by Upbound", "Open source, vendor neutral, huge community"),
    ("Extends Kubernetes into a universal control plane", "The same API machinery, pointed at everything"),
    ("Declarative management of any cloud resource", "Databases, networks, clusters, queues &#8212; and beyond"),
    ("GitOps-native from day one", "Works with Argo CD, Flux, and your existing pipelines"),
], 4, 10)

slides["2/2"] = std_slide("Compositions", "Compose your own cloud APIs", [
    ("Turn infrastructure patterns into products", "A &#8220;PostgresInstance&#8221; API instead of 40 resources"),
    ("Expose simple, safe self-service to developers", "One kubectl apply &#8212; batteries and policy included"),
    ("Governance baked into the platform", "Regions, sizes, tags and cost controls enforced by design"),
    ("Versioned and shareable", "Your platform evolves like software, because it is software"),
], 5, 10)

slides["2/3"] = std_slide("The product", "Enterprise Crossplane, managed", [
    ("Managed control planes with Spaces", "Fully managed in Upbound&#8217;s cloud or self-hosted in yours"),
    ("Official hardened providers", "Complete, supported coverage for AWS, Azure and GCP"),
    ("Upbound Marketplace", "Discover and share providers and configurations"),
    ("Console, RBAC, SSO and enterprise support", "Operate your platform with confidence and SLAs"),
], 6, 10)

# diagram slide: Devs -> Your API -> Control plane -> Clouds
def box(x, y, w, h, label, sub=None, fill=DEEP, stroke=BORDER, tcol=BODY, scol=DIM):
    s = (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" '
         f'fill-opacity="0.95" stroke="{stroke}" stroke-width="2"/>\n')
    cy = y + h/2 + (0 if sub else 8)
    s += (f'  <text x="{x+w/2}" y="{cy}" text-anchor="middle" {FONT} '
          f'font-size="22" font-weight="700" fill="{tcol}">{label}</text>\n')
    if sub:
        s += (f'  <text x="{x+w/2}" y="{cy+26}" text-anchor="middle" {FONT} '
              f'font-size="16" fill="{scol}">{sub}</text>\n')
    return s

def arrow(x1, y1, x2, y2):
    import math
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return (f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{BORDER}" '
            f'stroke-width="3"/>\n'
            f'  <path d="M 0 0 l -13 -6 l 0 12 z" fill="{BORDER}" '
            f'transform="translate({x2} {y2}) rotate({ang:.1f})"/>\n')

d = head() + panel() + title_bar("GitOps in, cloud out", "How it fits")
d += box(60, 240, 170, 90, "Developers", "git push / kubectl")
d += arrow(230, 285, 292, 285)
d += box(295, 240, 180, 90, "Your APIs", "Compositions")
d += arrow(475, 285, 537, 285)
# control plane box in brand purple
d += box(540, 218, 200, 134, "Control plane", "Upbound / Crossplane",
         fill=BRAND, stroke=WHITE, tcol=WHITE, scol="#EDE9FF")
d += arrow(740, 250, 800, 250)
d += arrow(740, 306, 800, 306)
d += arrow(740, 362, 800, 362)
d += box(803, 226, 100, 48, "AWS")
d += box(803, 282, 100, 48, "Azure")
d += box(803, 338, 100, 48, "GCP")
d += f'  <text x="480" y="430" text-anchor="middle" {FONT} font-size="20" fill="{DIM}">Declared once in Git &#8226; reconciled continuously &#8226; consistent everywhere</text>\n'
d += updot(880, 84) + footer(7, 10) + "</svg>\n"
slides["2/4"] = d

# ---------------- Section 3: value ----------------
slides["3/1"] = std_slide("The value", "Why teams choose Upbound", [
    ("Provision in minutes, not weeks", "Self-service APIs remove the ticket queue"),
    ("Freedom and governance at the same time", "Developers move fast inside guardrails you define"),
    ("Drift eliminated by design", "Continuous reconciliation keeps reality equal to intent"),
    ("One platform for every cloud", "Consolidate tools, skills and policy into one control plane"),
], 8, 10)

slides["3/2"] = std_slide("In practice", "What teams build with it", [
    ("Internal developer platforms", "Golden-path infrastructure behind a clean API"),
    ("Multi-cloud provisioning", "One workflow spanning AWS, Azure, GCP and on-prem"),
    ("Anything-as-a-service", "Databases, clusters, queues offered as products"),
    ("SaaS infrastructure automation", "Per-tenant infrastructure, stamped out reliably"),
], 9, 10)

slides["3/3"] = (head() + panel(0.82)
    + logo(410, 70, 140, LOGO_HERO)
    + f'  <text x="480" y="266" text-anchor="middle" {FONT} font-size="34" font-weight="700" fill="{BODY}">Own your cloud platform.</text>\n'
    + f'  <text x="480" y="330" text-anchor="middle" {FONT} font-size="23" fill="{BODY}">upbound.io &#8226; marketplace.upbound.io</text>\n'
    + f'  <text x="480" y="366" text-anchor="middle" {FONT} font-size="23" fill="{BODY}">github.com/crossplane/crossplane</text>\n'
    + f'  <rect x="390" y="398" width="180" height="5" rx="2.5" fill="{BRAND}"/>\n'
    + f'  <text x="480" y="444" text-anchor="middle" {FONT} font-size="21" fill="{DIM}">Thank you &#8212; John Boero</text>\n'
    + "</svg>\n")

# ================= Section 4: reusable TEMPLATES =================
# Placeholder slides for people to duplicate. Bracketed [ text ] is meant to be
# overwritten; dashed boxes are blank image drop-zones.

def tfoot(name):
    return (f'  <text x="60" y="492" {FONT} font-size="15" fill="{DIM}">'
            f'TEMPLATE &#8212; {name}</text>\n'
            f'  <text x="900" y="492" text-anchor="end" {FONT} font-size="15" '
            f'fill="{DIM}">duplicate &amp; edit</text>\n')

def tbar(title, kicker=None, x=60, tsize=42):
    s = ""
    if kicker:
        s += (f'  <text x="{x}" y="86" {FONT} font-size="19" font-weight="700" '
              f'letter-spacing="3" fill="{BORDER}">{kicker}</text>\n')
    s += (f'  <text x="{x}" y="138" {FONT} font-size="{tsize}" font-weight="700" '
          f'fill="{TITLE}">{title}</text>\n'
          f'  <rect x="{x}" y="158" width="120" height="5" rx="2.5" fill="{BRAND}"/>\n')
    return s

def tbul(x, items, y0=212, dy=58, size=23):
    s, y = "", y0
    for txt in items:
        s += f'  <circle cx="{x+12}" cy="{y-8}" r="6" fill="{BORDER}"/>\n'
        s += (f'  <text x="{x+34}" y="{y}" {FONT} font-size="{size}" '
              f'fill="{BODY}">{txt}</text>\n')
        y += dy
    return s

def imgbox(x, y, w, h, label="image"):
    cx, cy = x + w/2, y + h/2
    r = min(w, h)
    s = (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" '
         f'fill="{BORDER}" fill-opacity="0.08" stroke="{BORDER}" stroke-opacity="0.75" '
         f'stroke-width="2" stroke-dasharray="11 8"/>\n')
    # simple photo glyph: sun + mountains
    s += (f'  <circle cx="{cx - r*0.16:.1f}" cy="{cy - h*0.14:.1f}" r="{r*0.06:.1f}" '
          f'fill="{BORDER}" fill-opacity="0.5"/>\n')
    s += (f'  <path d="M {x+w*0.16:.1f} {y+h*0.70:.1f} '
          f'L {cx - w*0.06:.1f} {cy:.1f} '
          f'L {cx + w*0.10:.1f} {y+h*0.52:.1f} '
          f'L {x+w*0.84:.1f} {y+h*0.70:.1f} Z" '
          f'fill="{BORDER}" fill-opacity="0.4"/>\n')
    s += (f'  <text x="{cx:.1f}" y="{y+h-22:.1f}" text-anchor="middle" {FONT} '
          f'font-size="17" letter-spacing="2" fill="{DIM}">{label.upper()}</text>\n')
    return s

# 4/1 - Title slide
slides["4/1"] = (head() + panel()
    + logo(452, 120, 56, LOGO_HERO)
    + f'  <text x="480" y="256" text-anchor="middle" {FONT} font-size="56" font-weight="700" fill="{TITLE}">[ Presentation Title ]</text>\n'
    + f'  <rect x="360" y="284" width="240" height="5" rx="2.5" fill="{BRAND}"/>\n'
    + f'  <text x="480" y="342" text-anchor="middle" {FONT} font-size="27" fill="{BODY}">[ Subtitle or one-line tagline ]</text>\n'
    + f'  <text x="480" y="398" text-anchor="middle" {FONT} font-size="20" fill="{DIM}">[ Presenter name &#8226; event &#8226; date ]</text>\n'
    + updot(884, 84) + tfoot("Title slide") + "</svg>\n")

# 4/2 - Section divider / subtitle
slides["4/2"] = (head() + panel()
    + f'  <text x="480" y="238" text-anchor="middle" {FONT} font-size="22" font-weight="700" letter-spacing="5" fill="{BORDER}">SECTION 00</text>\n'
    + f'  <text x="480" y="306" text-anchor="middle" {FONT} font-size="50" font-weight="700" fill="{TITLE}">[ Section heading ]</text>\n'
    + f'  <rect x="410" y="330" width="140" height="5" rx="2.5" fill="{BRAND}"/>\n'
    + f'  <text x="480" y="384" text-anchor="middle" {FONT} font-size="23" fill="{DIM}">[ one-line description of what&#8217;s coming ]</text>\n'
    + updot(884, 84) + tfoot("Section divider / subtitle") + "</svg>\n")

# 4/3 - Bullet points
slides["4/3"] = (head() + panel() + tbar("[ Slide title ]", "[ KICKER ]")
    + tbul(60, ["[ First key point ]", "[ Second key point ]",
                "[ Third key point ]", "[ Fourth key point ]",
                "[ Fifth key point ]"], y0=228, dy=54)
    + updot(884, 84) + tfoot("Bullet list") + "</svg>\n")

# 4/4 - Text left, image right
slides["4/4"] = (head() + panel() + tbar("[ Slide title ]", "[ KICKER ]")
    + f'  <text x="60" y="222" {FONT} font-size="24" font-weight="700" fill="{BODY}">[ Lead-in line ]</text>\n'
    + tbul(60, ["[ Supporting point ]", "[ Supporting point ]",
                "[ Supporting point ]"], y0=270, dy=56)
    + imgbox(520, 196, 380, 258, "image")
    + updot(884, 84) + tfoot("Text left / image right") + "</svg>\n")

# 4/5 - Image left, text right
slides["4/5"] = (head() + panel() + tbar("[ Slide title ]", "[ KICKER ]")
    + imgbox(60, 196, 380, 258, "image")
    + f'  <text x="470" y="222" {FONT} font-size="24" font-weight="700" fill="{BODY}">[ Lead-in line ]</text>\n'
    + tbul(470, ["[ Supporting point ]", "[ Supporting point ]",
                 "[ Supporting point ]"], y0=270, dy=56)
    + updot(884, 84) + tfoot("Image left / text right") + "</svg>\n")

# 4/6 - Two columns
slides["4/6"] = (head() + panel() + tbar("[ Slide title ]", "[ KICKER ]")
    + f'  <text x="60" y="220" {FONT} font-size="24" font-weight="700" fill="{TITLE}">[ Column A ]</text>\n'
    + tbul(60, ["[ Point ]", "[ Point ]", "[ Point ]"], y0=262, dy=54)
    + f'  <text x="500" y="220" {FONT} font-size="24" font-weight="700" fill="{TITLE}">[ Column B ]</text>\n'
    + tbul(500, ["[ Point ]", "[ Point ]", "[ Point ]"], y0=262, dy=54)
    + updot(884, 84) + tfoot("Two columns") + "</svg>\n")

# 4/7 - Big quote / statement
slides["4/7"] = (head() + panel()
    + f'  <text x="150" y="250" {FONT} font-size="160" font-weight="700" fill="{BRAND}" fill-opacity="0.45">&#8220;</text>\n'
    + f'  <text x="480" y="272" text-anchor="middle" {FONT} font-size="38" font-weight="700" fill="{TITLE}">[ A bold statement or a</text>\n'
    + f'  <text x="480" y="324" text-anchor="middle" {FONT} font-size="38" font-weight="700" fill="{TITLE}">memorable quote goes here ]</text>\n'
    + f'  <text x="480" y="392" text-anchor="middle" {FONT} font-size="22" fill="{DIM}">[ &#8212; Attribution, title ]</text>\n'
    + updot(884, 84) + tfoot("Quote / statement") + "</svg>\n")

# 4/8 - Full-width image / diagram
slides["4/8"] = (head() + panel() + tbar("[ Slide title ]", "[ KICKER ]")
    + imgbox(60, 190, 840, 250, "full-width image / diagram")
    + updot(884, 84) + tfoot("Full-width image") + "</svg>\n")

# write out
for path, svg in slides.items():
    sec, num = path.split("/")
    os.makedirs(os.path.join(OUT, sec), exist_ok=True)
    with open(os.path.join(OUT, sec, num + ".svg"), "w") as f:
        f.write(svg)
    print("wrote", path, len(svg), "bytes")
