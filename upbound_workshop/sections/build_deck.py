#!/usr/bin/env python3
"""Generate the 'Upbound Project Foundations' deck (960x540 SVGs) in the
jboero Upbound template style. Real logo embedded as base64 (survives <img>
loading, which blocks external refs). Purple = Upbound/Crossplane, blue = K8s.
"""
import os, math, base64, io
from PIL import Image

OUT = "/home/claude/upbound-deck/sections"
AVATAR = "/home/claude/upbound-deck/images/upbound_avatar.png"

# ---- palette (from template) + additions ----
DEEP   = "#140B33"; BORDER = "#8B6CFF"; TITLE = "#B9A6FF"
BODY   = "#EDE9FF"; DIM    = "#7C6FAE"; BRAND = "#6B5BCD"; WHITE = "#FFFFFF"
K8S    = "#326CE5"; K8SDK  = "#2A50A0"           # kubernetes blue
CODEBG = "#0C0722"; MONO_T = "#CFC6FF"
GREEN  = "#63D39B"; RED    = "#F0728C"
FONT = 'font-family="Helvetica, Arial, sans-serif"'
MONO = 'font-family="Menlo, Consolas, monospace"'
ARR = "&#8594;"; ARRLR = "&#8596;"; EM = "&#8212;"; DOT = "&#8226;"

# ---- logo data URIs (scaled to keep files small) ----
def datauri(size):
    im = Image.open(AVATAR).convert("RGBA").resize((size, size), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, format="PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
LOGO_CORNER = datauri(80)
LOGO_HERO   = datauri(240)

def logo(x, y, w, uri=LOGO_CORNER):
    return f'  <image href="{uri}" x="{x}" y="{y}" width="{w}" height="{w}"/>\n'

def head():
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" '
            'viewBox="0 0 960 540">\n')

def panel(op=0.9):
    return (f'  <rect x="20" y="20" width="920" height="500" rx="24" fill="{DEEP}" '
            f'fill-opacity="{op}" stroke="{BORDER}" stroke-opacity="0.35" stroke-width="2"/>\n')

def corner():                       # logo replaces the old 'up' dot motif
    return logo(872, 40, 52)

def footer(idx, total, note="Upbound Project Foundations"):
    return (f'  <text x="60" y="500" {FONT} font-size="15" fill="{DIM}">{note} {DOT} upbound.io</text>\n'
            f'  <text x="900" y="500" text-anchor="end" {FONT} font-size="15" fill="{DIM}">{idx} / {total}</text>\n')

def title_bar(title, kicker=None, tsize=40):
    s = ""
    if kicker:
        s += (f'  <text x="60" y="84" {FONT} font-size="18" font-weight="700" '
              f'letter-spacing="3" fill="{BORDER}">{kicker.upper()}</text>\n')
    s += (f'  <text x="60" y="134" {FONT} font-size="{tsize}" font-weight="700" fill="{TITLE}">{title}</text>\n'
          f'  <rect x="60" y="152" width="120" height="5" rx="2.5" fill="{BRAND}"/>\n')
    return s

def bullets(items, y0=210, dy=58, size=24):
    s = ""; y = y0
    for h, sub in items:
        s += f'  <circle cx="72" cy="{y-8}" r="6" fill="{BORDER}"/>\n'
        s += f'  <text x="94" y="{y}" {FONT} font-size="{size}" font-weight="700" fill="{BODY}">{h}</text>\n'
        if sub:
            s += f'  <text x="94" y="{y+25}" {FONT} font-size="18" fill="{DIM}">{sub}</text>\n'
        y += dy
    return s

def node(x, y, w, h, label, sub=None, fill=DEEP, stroke=BORDER, tcol=BODY, scol=DIM,
         rx=12, dash=False, sw=2, lsize=19, ssize=13):
    d = ' stroke-dasharray="7 6"' if dash else ''
    s = (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
         f'fill-opacity="0.97" stroke="{stroke}" stroke-width="{sw}"{d}/>\n')
    cy = y + h/2 + (2 if sub else 7)
    s += (f'  <text x="{x+w/2}" y="{cy}" text-anchor="middle" {FONT} font-size="{lsize}" '
          f'font-weight="700" fill="{tcol}">{label}</text>\n')
    if sub:
        s += (f'  <text x="{x+w/2}" y="{cy+20}" text-anchor="middle" {FONT} font-size="{ssize}" '
              f'fill="{scol}">{sub}</text>\n')
    return s

def arrow(x1, y1, x2, y2, label=None, color=BORDER, dash=False, lx=0, ly=-7, lsize=13):
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    d = ' stroke-dasharray="7 6"' if dash else ''
    s = (f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2.5"{d}/>\n'
         f'  <path d="M 0 0 l -13 -6 l 0 12 z" fill="{color}" '
         f'transform="translate({x2} {y2}) rotate({ang:.1f})"/>\n')
    if label:
        mx, my = (x1 + x2)/2 + lx, (y1 + y2)/2 + ly
        s += (f'  <text x="{mx:.0f}" y="{my:.0f}" text-anchor="middle" {FONT} '
              f'font-size="{lsize}" fill="{TITLE}">{label}</text>\n')
    return s

def band(x, y, w, h, label, dash=False):
    d = ' stroke-dasharray="9 7"' if dash else ''
    s = (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{BORDER}" '
         f'fill-opacity="0.06" stroke="{DIM}" stroke-opacity="0.8" stroke-width="2"{d}/>\n'
         f'  <text x="{x+16}" y="{y-10}" {FONT} font-size="15" font-weight="700" '
         f'letter-spacing="2" fill="{DIM}">{label}</text>\n')
    return s

def codebox(x, y, w, lines, size=16, lh=24):
    h = 20 + lh*len(lines)
    s = (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{CODEBG}" '
         f'stroke="{BORDER}" stroke-opacity="0.4" stroke-width="1.5"/>\n')
    ty = y + 30
    for ln in lines:
        s += (f'  <text x="{x+18}" y="{ty}" {MONO} font-size="{size}" fill="{MONO_T}"'
              f' xml:space="preserve">{ln}</text>\n')
        ty += lh
    return s, h

def esc(t):
    return t.replace("&", "&amp;")

slides = {}

# ===================== COLUMN 1 — framing & vocabulary =====================
# 1/1 Title
slides["1/1"] = (head() + panel(0.86)
    + logo(400, 70, 160, LOGO_HERO)
    + f'  <text x="480" y="300" text-anchor="middle" {FONT} font-size="46" font-weight="700" fill="{TITLE}">Building Your First</text>\n'
    + f'  <text x="480" y="352" text-anchor="middle" {FONT} font-size="46" font-weight="700" fill="{TITLE}">Upbound Project</text>\n'
    + f'  <rect x="360" y="374" width="240" height="5" rx="2.5" fill="{BRAND}"/>\n'
    + f'  <text x="480" y="424" text-anchor="middle" {FONT} font-size="23" fill="{BODY}">From an empty folder to a working infrastructure API</text>\n'
    + f'  <text x="480" y="462" text-anchor="middle" {FONT} font-size="18" fill="{DIM}">Project Foundations {DOT} Builder&#8217;s Workshop</text>\n'
    + "</svg>\n")

# 1/2 What are we building
slides["1/2"] = (head() + panel() + corner() + title_bar("What are we actually building?", "The big idea")
    + bullets([
        ("You&#8217;re building a self-service API", "Not configuring a tool &#8212; you&#8217;re defining infrastructure as an API"),
        ("You, the platform builder: define what &amp; how", "The request&#8217;s shape (XRD) and the logic behind it (Composition)"),
        ("Your users: submit one short request", "One kubectl apply in, real cloud resources out"),
        ("It all lives in one project folder", "The unit you build and ship into a control plane"),
    ], y0=214, dy=68)
    + footer(2, 14) + "</svg>\n")

# 1/3 Five building blocks
slides["1/3"] = (head() + panel() + corner() + title_bar("The five building blocks", "Vocabulary")
    + bullets([
        (f"Composite Resource Definition {EM} XRD", "The new resource TYPE you invent (the menu)"),
        (f"Composite Resource {EM} XR", "One request filled out against that type (the order)"),
        ("Composition", "The implementation that fulfils the request (the kitchen)"),
        ("Provider", "Ships cloud resource types &amp; reconciles them (the pantry)"),
        (f"Managed Resource {EM} MR", "One real cloud object, e.g. an actual S3 bucket (the dish)"),
    ], y0=196, dy=55, size=22)
    + f'  <text x="60" y="476" {FONT} font-size="15" fill="{DIM}">&#8220;X&#8221; = Composite (CR was taken by Kubernetes). A CRD is how Kubernetes registers a new type &#8212; the XRD generates one.</text>\n'
    + footer(3, 14) + "</svg>\n")

# ===================== COLUMN 2 — relationships & structure =====================
# 2/1 Relationship diagram (SETUP left / APPLY right, User outside)
d = head() + panel() + title_bar("How the pieces connect", "Relationships")
# bands
d += band(150, 206, 340, 252, "SETUP  &#8212;  DONE ONCE")
d += band(620, 206, 286, 252, "APPLY  &#8212;  EVERY DEPLOYMENT", dash=True)
# setup nodes (vertical stack)
d += node(210, 222, 210, 46, "XRD", "type you defined", stroke=BORDER, tcol=BODY, lsize=18, ssize=12)
d += node(210, 280, 210, 38, "CRD", "Kubernetes plumbing", fill="#101a33", stroke=K8S, tcol="#BCD3FF", scol="#7FA0D8", lsize=17, ssize=11)
d += node(210, 352, 210, 46, "Composition", "the logic", stroke=BORDER, tcol=BODY, lsize=17, ssize=12)
d += node(210, 410, 210, 40, "Provider", None, stroke=BORDER, tcol=BODY, lsize=17)
# apply nodes
d += node(650, 240, 226, 48, "XR", "the request", stroke=BORDER, tcol=BODY, lsize=18, ssize=12)
d += node(650, 372, 226, 48, "MR", "real cloud infra", stroke=BORDER, tcol=BODY, lsize=18, ssize=12)
# user (outside, above APPLY)
d += node(690, 158, 146, 40, "User", None, fill="#241a4d", stroke=BORDER, tcol=BODY, lsize=17)
# internal setup arrows
d += arrow(315, 268, 315, 280, None, dash=True)
d += f'  <text x="372" y="278" {FONT} font-size="12" fill="{DIM}">compiles 1:1</text>\n'
d += arrow(315, 398, 315, 410, None)
d += f'  <text x="378" y="407" {FONT} font-size="12" fill="{DIM}">uses types &#183; M:N</text>\n'
# user -> XR
d += arrow(763, 198, 763, 240, "writes &#183; 1:N", lx=48, ly=8, lsize=12)
# cross arrows
d += arrow(650, 256, 422, 248, "must match &#183; N:1", lx=0, ly=-9, lsize=12)
d += arrow(650, 280, 422, 372, "fulfilled by &#183; N:1", lx=34, ly=-6, lsize=12)
d += arrow(420, 376, 648, 392, "declares &#183; 1:N", lx=0, ly=-9, lsize=12)
d += arrow(420, 430, 648, 402, "reconciles &#183; 1:N", lx=-6, ly=16, lsize=12)
d += f'  <text x="60" y="488" {FONT} font-size="14" fill="{DIM}">Purple = Upbound/Crossplane {DOT} blue = Kubernetes {DOT} the SETUP side is always the &#8220;1&#8221;, the APPLY side the &#8220;N&#8221;.</text>\n'
d += corner() + footer(4, 14) + "</svg>\n"
slides["2/1"] = d

# 2/2 Cardinality table
def crow(y, a, card, why, cc=TITLE):
    s = (f'  <text x="72" y="{y}" {FONT} font-size="18" fill="{BODY}">{a}</text>\n'
         f'  <text x="452" y="{y}" text-anchor="middle" {FONT} font-size="18" font-weight="700" fill="{cc}">{card}</text>\n'
         f'  <text x="536" y="{y}" {FONT} font-size="16" fill="{DIM}">{why}</text>\n')
    return s
d = head() + panel() + corner() + title_bar("How many of each?", "Cardinality")
d += (f'  <text x="72" y="196" {FONT} font-size="14" font-weight="700" letter-spacing="1" fill="{DIM}">RELATIONSHIP</text>\n'
      f'  <text x="452" y="196" text-anchor="middle" {FONT} font-size="14" font-weight="700" letter-spacing="1" fill="{DIM}">COUNT</text>\n'
      f'  <text x="536" y="196" {FONT} font-size="14" font-weight="700" letter-spacing="1" fill="{DIM}">IN PLAIN TERMS</text>\n'
      f'  <line x1="72" y1="206" x2="900" y2="206" stroke="{BORDER}" stroke-opacity="0.3" stroke-width="1.5"/>\n')
rows = [
    (f"XRD {ARR} CRD", "1 : 1", "one XRD compiles into one generated CRD", GREEN),
    (f"XRD {ARR} XR", "1 : N", "one type, many live requests", TITLE),
    (f"XRD {ARR} Composition", "1 : N", "one type, one-or-more implementations", TITLE),
    (f"Composition {ARR} XR", "1 : N", "one composition serves many requests", TITLE),
    (f"XR {ARR} MR", "1 : N", "one request, several real cloud objects", TITLE),
    (f"Provider {ARR} MR", "1 : N", "one provider manages many resources", TITLE),
    (f"Composition {ARRLR} Provider", "M : N", "compositions span providers, and vice-versa", "#FFC98A"),
]
y = 234
for a, c, w, cc in rows:
    d += crow(y, a, c, w, cc); y += 34
d += f'  <text x="72" y="{y+14}" {FONT} font-size="15" fill="{DIM}">Nothing you author is 1:1 &#8212; the lone 1:1 is the mechanical XRD{ARR}CRD compile step.</text>\n'
d += footer(5, 14) + "</svg>\n"
slides["2/2"] = d

# 2/3 Directory tree
tree = [
    ("upbound-hello-world/", "", BODY),
    ("&#9500;&#9472; upbound.yaml", "project config &#183; entry point", BODY),
    ("&#9500;&#9472; apis/", "YOUR API &#8212; built once  (SETUP)", TITLE),
    ("&#9474;  &#9492;&#9472; storagebuckets/", "", BODY),
    ("&#9474;     &#9500;&#9472; definition.yaml", "XRD &#183; the type", BODY),
    ("&#9474;     &#9492;&#9472; composition.yaml", "Composition &#183; the logic", BODY),
    ("&#9492;&#9472; examples/", "requests  (APPLY)", "#FFC98A"),
    ("   &#9492;&#9472; storagebucket/", "", BODY),
    ("      &#9492;&#9472; example.yaml", "XR &#183; one request", BODY),
]
d = head() + panel() + corner() + title_bar("The project is a directory tree", "Structure")
y = 212
for path, note, col in tree:
    d += f'  <text x="72" y="{y}" {MONO} font-size="19" fill="{col}" xml:space="preserve">{path}</text>\n'
    if note:
        d += f'  <text x="470" y="{y}" {FONT} font-size="16" fill="{DIM}">{note}</text>\n'
    y += 31
d += f'  <text x="72" y="{y+12}" {FONT} font-size="16" fill="{DIM}">apis/ = what you set up once  {DOT}  examples/ = the requests that run again and again.</text>\n'
d += footer(6, 14) + "</svg>\n"
slides["2/3"] = d

# ===================== COLUMN 3 — the build steps =====================
def step_slide(kick, title, cmd_lines, pts, idx, note_line=None):
    s = head() + panel() + corner() + title_bar(title, kick)
    cb, h = codebox(60, 188, 840, cmd_lines)
    s += cb
    y = 188 + h + 46
    s += bullets(pts, y0=y, dy=52, size=21)
    if note_line:
        s += f'  <text x="60" y="474" {FONT} font-size="15" fill="{DIM}">{note_line}</text>\n'
    s += footer(idx, 14) + "</svg>\n"
    return s

slides["3/1"] = step_slide("Build &#183; step 1", "Initialize the project",
    ["$ up project init upbound-hello-world --scratch"],
    [("Scaffolds the project &amp; writes upbound.yaml", "The entry point that says what this project is"),
     ("--scratch starts empty", "Every piece we add after this is deliberate, nothing hidden")],
    7)

slides["3/2"] = step_slide("Build &#183; step 2", "Add a dependency (a Provider)",
    ["$ up dependency add \\",
     "    'xpkg.upbound.io/upbound/provider-aws-s3:>=v2.0.0'"],
    [("Providers connect the control plane to a cloud", "They ship the resource types &#8212; S3, VMs, databases"),
     ("They own auth &amp; the resource lifecycle", "Without a provider, nothing real can be created")],
    8)

slides["3/3"] = step_slide("Build &#183; step 3", "Generate an example XR",
    ["$ up example generate --type xr \\",
     "    --api-group platform.example.com --kind StorageBucket \\",
     "    --api-version v1alpha1 --name example \\",
     "    --namespace default --scope namespace"],
    [("Writes a sample request to examples/", "This is the request we WISH existed"),
     ("Design the API by using it first", "Next step derives the type from this example")],
    9, note_line="Request-first design: fill in spec.parameters (region, versioning, acl) &#8212; the knobs your users get.")

slides["3/4"] = step_slide("Build &#183; step 4", "Generate the XRD",
    ["$ up xrd generate examples/storagebucket/example.yaml"],
    [("Infers field names &amp; types from the example", "Writes the XRD to apis/ as definition.yaml"),
     ("The XRD compiles into a Kubernetes CRD", "That&#8217;s what makes kubectl get storagebuckets work"),
     ("Not a CRD &#8212; it adds Composition wiring", "A plain CRD would register the type but stay inert")],
    10)

slides["3/5"] = step_slide("Build &#183; step 5", "Generate the Composition",
    ["$ up composition generate apis/storagebuckets/definition.yaml"],
    [("Maps your parameters to real Managed Resources", "Your 3 fields in &#8594; the provider&#8217;s 40-field bucket out"),
     ("Handles resource relationships &amp; policy", "Best practices baked in, cloud detail hidden"),
     ("Without it the XRD is an API that does nothing", "The Composition is the body behind the contract")],
    11)

# ===================== COLUMN 4 — synthesis & close =====================
# 4/1 Build order vs run order
d = head() + panel() + corner() + title_bar("Build order &#8800; run order", "The key insight")
# build row
d += f'  <text x="60" y="212" {FONT} font-size="20" font-weight="700" fill="{TITLE}">How you BUILD it (this workshop)</text>\n'
bx = [("Example XR", 60), ("XRD", 250), ("Composition", 400)]
prev = None
for label, x in bx:
    w = 150 if label != "XRD" else 110
    d += node(x, 232, w, 52, label, None, stroke=BORDER, tcol=BODY, lsize=18)
    if prev:
        d += arrow(prev, 258, x-8, 258, color=BRAND)
    prev = x + (150 if label != "XRD" else 110)
d += f'  <text x="600" y="264" {FONT} font-size="16" fill="{DIM}">bottom-up,</text>\n'
d += f'  <text x="600" y="284" {FONT} font-size="16" fill="{DIM}">example-driven</text>\n'
# run row
d += f'  <text x="60" y="352" {FONT} font-size="20" font-weight="700" fill="{TITLE}">How it RUNS (in production)</text>\n'
rx = [("XR", 60, 90, BORDER), ("XRD", 200, 90, BORDER), ("Composition", 340, 150, BORDER),
      ("Provider", 540, 110, BORDER), ("MRs", 700, 90, BRAND)]
prev = None
for label, x, w, st in rx:
    fill = BRAND if label == "MRs" else DEEP
    tcol = WHITE if label == "MRs" else BODY
    d += node(x, 372, w, 52, label, None, fill=fill, stroke=st, tcol=tcol, lsize=16)
    if prev:
        d += arrow(prev, 398, x-8, 398, color=BORDER)
    prev = x + w
d += f'  <text x="60" y="470" {FONT} font-size="16" fill="{DIM}">You author inside-out (start from an example); at runtime it flows top-down. Hold both pictures and every command makes sense.</text>\n'
d += footer(12, 14) + "</svg>\n"
slides["4/1"] = d

# 4/2 Dependency check
d = head() + panel() + corner() + title_bar("Can X exist without Y?", "Dependency check")
d += (f'  <text x="72" y="196" {FONT} font-size="14" font-weight="700" letter-spacing="1" fill="{DIM}">CAN THIS &#8230; WITHOUT THIS</text>\n'
      f'  <text x="560" y="196" text-anchor="middle" {FONT} font-size="14" font-weight="700" letter-spacing="1" fill="{DIM}">?</text>\n'
      f'  <text x="620" y="196" {FONT} font-size="14" font-weight="700" letter-spacing="1" fill="{DIM}">WHY</text>\n'
      f'  <line x1="72" y1="206" x2="900" y2="206" stroke="{BORDER}" stroke-opacity="0.3" stroke-width="1.5"/>\n')
dep = [
    ("Managed Resource", "Provider", "NO", RED, "type + reconciliation come from it"),
    ("Composition", "Provider", "NO", RED, "no MR types to compose without one"),
    ("XRD", "Composition", "YES", GREEN, "valid API &#8212; but it does nothing"),
    ("Live XR", "XRD", "NO", RED, "type isn&#8217;t registered &#8594; rejected"),
    ("Composition", "XRD", "NO", RED, "it targets one XRD-defined type"),
]
y = 240
for a, b, ans, col, why in dep:
    d += f'  <text x="72" y="{y}" {FONT} font-size="19" fill="{BODY}">{a}  <tspan fill="{DIM}" font-size="16">without</tspan>  {b}</text>\n'
    d += f'  <text x="560" y="{y}" text-anchor="middle" {FONT} font-size="19" font-weight="700" fill="{col}">{ans}</text>\n'
    d += f'  <text x="620" y="{y}" {FONT} font-size="16" fill="{DIM}">{why}</text>\n'
    y += 40
d += f'  <text x="72" y="{y+16}" {FONT} font-size="17" fill="{TITLE}">The throughline: the thing you author always needs the thing beneath it to exist first.</text>\n'
d += footer(13, 14) + "</svg>\n"
slides["4/2"] = d

# 4/3 Recap
slides["4/3"] = (head() + panel(0.86) + logo(430, 66, 100, LOGO_HERO)
    + f'  <text x="480" y="212" text-anchor="middle" {FONT} font-size="34" font-weight="700" fill="{TITLE}">You built a self-service API</text>\n'
    + f'  <rect x="390" y="230" width="180" height="5" rx="2.5" fill="{BRAND}"/>\n'
    + bullets([
        ("A project  (upbound.yaml + structure)", ""),
        ("A cloud dependency  (the Provider)", ""),
        ("An API type  (the XRD &#8594; a generated CRD)", ""),
        ("Implementation logic  (the Composition)", ""),
      ], y0=286, dy=44, size=21)
    + f'  <text x="480" y="486" text-anchor="middle" {FONT} font-size="18" fill="{DIM}">Next: a composition function to give your API real behavior.</text>\n'
    + "</svg>\n")

# ---- write ----
import shutil
for c in ("1", "2", "3", "4"):
    shutil.rmtree(os.path.join(OUT, c), ignore_errors=True)
for path, svg in slides.items():
    sec, num = path.split("/")
    os.makedirs(os.path.join(OUT, sec), exist_ok=True)
    with open(os.path.join(OUT, sec, num + ".svg"), "w") as f:
        f.write(svg)
    print("wrote", path, len(svg), "bytes")
