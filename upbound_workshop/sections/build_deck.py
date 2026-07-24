#!/usr/bin/env python3
"""Generate the 'Upbound Project Foundations' deck (960x540 SVGs) in the
jboero Upbound template style. Real logo embedded as base64 (survives <img>
loading, which blocks external refs). Purple = Upbound/Crossplane, blue = K8s.

Two layout rules this deck follows:

  1. CAMERA CORNER. The bottom-right box (see CAM) is reserved for a
     green-screened webcam overlay of the presenter, so no content may land
     there. Slide numbers therefore live bottom-LEFT, and wide diagrams /
     tables / footnotes are kept left of CAM[0] once they drop below CAM[1].
     Run with DECK_GUIDE=1 to draw the reserved box while editing.

  2. ROLES. Every step is attributed to who performs it: control-plane admin,
     platform builder, GitOps approver, or developer. See the ROLES block.

Slide numbers are assigned automatically from ORDER, so inserting a slide
never desyncs the footers.
"""
import os, math, base64, io
from PIL import Image

HERE   = os.path.dirname(os.path.abspath(__file__))
OUT    = HERE
AVATAR = os.path.join(os.path.dirname(HERE), "images", "upbound_avatar.png")

# ---- palette (from template) + additions ----
DEEP   = "#140B33"; BORDER = "#8B6CFF"; TITLE = "#B9A6FF"
BODY   = "#EDE9FF"; DIM    = "#7C6FAE"; BRAND = "#6B5BCD"; WHITE = "#FFFFFF"
K8S    = "#326CE5"; K8SDK  = "#2A50A0"           # kubernetes blue
CODEBG = "#0C0722"; MONO_T = "#CFC6FF"
GREEN  = "#63D39B"; RED    = "#F0728C"; AMBER = "#FFC98A"; SKY = "#8AD3FF"
FONT = 'font-family="Helvetica, Arial, sans-serif"'
MONO = 'font-family="Menlo, Consolas, monospace"'
ARR = "&#8594;"; ARRLR = "&#8596;"; EM = "&#8212;"; DOT = "&#8226;"

# ---- roles: (label, colour) ----
R_ADMIN = ("CONTROL-PLANE ADMIN", SKY)
R_BUILD = ("PLATFORM BUILDER",    TITLE)
R_GITOPS= ("GITOPS / APPROVER",   AMBER)
R_DEV   = ("DEVELOPER",           GREEN)

# ---- reserved webcam corner (x0, y0, x1, y1) ----
CAM = (690, 326, 940, 520)

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

def camguide():
    """Dashed outline of the reserved webcam box; only with DECK_GUIDE=1."""
    if not os.environ.get("DECK_GUIDE"):
        return ""
    x0, y0, x1, y1 = CAM
    return (f'  <rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" '
            f'stroke="{RED}" stroke-width="2" stroke-dasharray="8 6" opacity="0.9"/>\n')

# Slide numbers are substituted at write time from ORDER.
NUMTOK = "__NUM__"

def footer(note="Upbound Project Foundations"):
    """Bottom-LEFT footer: the bottom-right corner belongs to the webcam."""
    return (f'  <text x="60" y="500" {FONT} font-size="15" fill="{DIM}">'
            f'{NUMTOK}  {DOT}  {note} {DOT} upbound.io</text>\n')

def title_bar(title, kicker=None, tsize=40):
    s = ""
    if kicker:
        s += (f'  <text x="60" y="84" {FONT} font-size="18" font-weight="700" '
              f'letter-spacing="3" fill="{BORDER}">{kicker.upper()}</text>\n')
    s += (f'  <text x="60" y="134" {FONT} font-size="{tsize}" font-weight="700" fill="{TITLE}">{title}</text>\n'
          f'  <rect x="60" y="152" width="120" height="5" rx="2.5" fill="{BRAND}"/>\n')
    return s

def chip(x, y, label, col, size=12, anchor="start"):
    """Small role pill. (x,y) is the top-left, or top-RIGHT when anchor='end'."""
    w = 24 + len(label) * size * 0.75
    if anchor == "end":
        x = x - w
    h = size + 13
    return (f'  <rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{h/2:.0f}" '
            f'fill="{col}" fill-opacity="0.15" stroke="{col}" stroke-opacity="0.7" stroke-width="1.5"/>\n'
            f'  <text x="{x+w/2:.0f}" y="{y+h-8:.0f}" text-anchor="middle" {FONT} font-size="{size}" '
            f'font-weight="700" letter-spacing="1.2" fill="{col}">{label}</text>\n')

def role_tag(role, x=850, y=64):
    """Right-aligned role pill for the header strip (clear of the corner logo)."""
    return chip(x, y, role[0], role[1], size=12, anchor="end")

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
    # label+sub are centred as a pair so the sub never rides the bottom border
    cy = y + h/2 + (-2 if sub else 7)
    s += (f'  <text x="{x+w/2}" y="{cy}" text-anchor="middle" {FONT} font-size="{lsize}" '
          f'font-weight="700" fill="{tcol}">{label}</text>\n')
    if sub:
        s += (f'  <text x="{x+w/2}" y="{cy+18}" text-anchor="middle" {FONT} font-size="{ssize}" '
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

def band(x, y, w, h, label, dash=False, lcol=DIM):
    d = ' stroke-dasharray="9 7"' if dash else ''
    s = (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{BORDER}" '
         f'fill-opacity="0.06" stroke="{DIM}" stroke-opacity="0.8" stroke-width="2"{d}/>\n'
         f'  <text x="{x+16}" y="{y-10}" {FONT} font-size="15" font-weight="700" '
         f'letter-spacing="2" fill="{lcol}">{label}</text>\n')
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

def rolecard(x, y, w, h, role, phase, lines):
    """Card for the roles slide: name, phase tag, and two short duty lines."""
    name, col = role
    s = (f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{col}" '
         f'fill-opacity="0.07" stroke="{col}" stroke-opacity="0.55" stroke-width="2"/>\n'
         f'  <text x="{x+18}" y="{y+36}" {FONT} font-size="17" font-weight="700" fill="{col}">{name}</text>\n'
         f'  <text x="{x+w-16}" y="{y+34}" text-anchor="end" {FONT} font-size="11" '
         f'font-weight="700" letter-spacing="2" fill="{col}" opacity="0.75">{phase}</text>\n')
    ty = y + 66
    for ln in lines:
        s += f'  <text x="{x+18}" y="{ty}" {FONT} font-size="15" fill="{BODY}">{ln}</text>\n'
        ty += 22
    return s

slides = {}

# ===================== COLUMN 1 — framing & vocabulary =====================
# 1/1 Title. Left-aligned so the bottom-right stays clear for the camera.
slides["1/1"] = (head() + panel(0.86)
    + logo(60, 64, 120, LOGO_HERO)
    + f'  <text x="60" y="268" {FONT} font-size="46" font-weight="700" fill="{TITLE}">Building Your First</text>\n'
    + f'  <text x="60" y="324" {FONT} font-size="46" font-weight="700" fill="{TITLE}">Upbound Project</text>\n'
    + f'  <rect x="60" y="346" width="240" height="5" rx="2.5" fill="{BRAND}"/>\n'
    + f'  <text x="60" y="396" {FONT} font-size="23" fill="{BODY}">From an empty folder to a working infrastructure API</text>\n'
    + f'  <text x="60" y="436" {FONT} font-size="18" fill="{DIM}">Project Foundations {DOT} Builder&#8217;s Workshop</text>\n'
    + camguide() + "</svg>\n")

# 1/2 What are we building
slides["1/2"] = (head() + panel() + corner() + title_bar("What are we actually building?", "The big idea")
    + bullets([
        ("You&#8217;re building a self-service API", "Not configuring a tool &#8212; you&#8217;re defining infrastructure as an API"),
        ("The platform builder defines what &amp; how", "The request&#8217;s shape (XRD) and the logic behind it (Composition)"),
        ("Developers submit one short request", "One kubectl apply in, real cloud resources out"),
        ("It all lives in one project folder", "The unit you build and ship into a control plane"),
    ], y0=214, dy=68)
    + camguide() + footer() + "</svg>\n")

# 1/3 Five building blocks
slides["1/3"] = (head() + panel() + corner() + title_bar("The five building blocks", "Vocabulary")
    + bullets([
        (f"Composite Resource Definition {EM} XRD", "The new resource TYPE you invent (the menu)"),
        (f"Composite Resource {EM} XR", "One request filled out against that type (the order)"),
        ("Composition", "The implementation that fulfils the request (the kitchen)"),
        ("Provider", "Ships cloud resource types &amp; reconciles them (the pantry)"),
        (f"Managed Resource {EM} MR", "One real cloud object, e.g. an actual S3 bucket (the dish)"),
    ], y0=192, dy=54, size=22)
    + f'  <text x="60" y="460" {FONT} font-size="15" fill="{DIM}">&#8220;X&#8221; = Composite &#8212; CR was already taken by Kubernetes.</text>\n'
    + f'  <text x="60" y="480" {FONT} font-size="15" fill="{DIM}">A CRD registers a new type with Kubernetes; the XRD generates one.</text>\n'
    + camguide() + footer() + "</svg>\n")

# 1/4 Who does what (roles)
slides["1/4"] = (head() + panel() + corner() + title_bar("Who does what?", "Roles")
    + rolecard(60, 196, 300, 118, R_ADMIN, "SETUP",
               ["Creates the control plane, installs", "providers, credentials and RBAC"])
    + rolecard(378, 196, 300, 118, R_BUILD, "SETUP",
               ["Authors the project: XRD,", "Composition and functions"])
    + rolecard(60, 330, 300, 118, R_GITOPS, "SHIP",
               ["Reviews and merges the PR, then", "promotes dev " + ARR + " staging " + ARR + " prod"])
    + rolecard(378, 330, 300, 118, R_DEV, "APPLY",
               ["Writes one XR and applies it,", "gets real infrastructure back"])
    + f'  <text x="60" y="480" {FONT} font-size="15" fill="{DIM}">This workshop stands in the platform builder&#8217;s shoes.</text>\n'
    + camguide() + footer() + "</svg>\n")

# ===================== COLUMN 2 — relationships & structure =====================
# 2/1 Relationship diagram. Narrowed and pushed left so the camera corner is free;
# bands are labelled with the role that owns each side.
d = head() + panel() + title_bar("How the pieces connect", "Relationships")
d += band(60, 206, 234, 252, "SETUP " + DOT + " PLATFORM BUILDER", lcol=TITLE)
d += band(468, 206, 200, 252, "APPLY " + DOT + " DEVELOPER", dash=True, lcol=GREEN)
# setup nodes (vertical stack) - the arrows run left of centre so their
# captions get their own space in the gaps between boxes
d += node(84, 214, 186, 46, "XRD", "type you defined", stroke=BORDER, tcol=BODY, lsize=18, ssize=12)
d += node(84, 288, 186, 46, "CRD", "Kubernetes plumbing", fill="#101a33", stroke=K8S, tcol="#BCD3FF", scol="#7FA0D8", lsize=17, ssize=11)
d += node(84, 352, 186, 46, "Composition", "the logic", stroke=BORDER, tcol=BODY, lsize=17, ssize=12)
d += node(84, 416, 186, 36, "Provider", None, stroke=BORDER, tcol=BODY, lsize=17)
# apply nodes
d += node(488, 240, 160, 48, "XR", "the request", stroke=BORDER, tcol=BODY, lsize=18, ssize=12)
d += node(488, 372, 160, 48, "MR", "real cloud infra", stroke=BORDER, tcol=BODY, lsize=18, ssize=12)
# the developer sits outside the bands, upper right (above the camera box)
d += node(706, 158, 134, 40, "Developer", None, fill="#241a4d", stroke=GREEN, tcol=BODY, lsize=15)
# internal setup arrows
d += arrow(120, 260, 120, 288, None, dash=True)
d += f'  <text x="212" y="279" text-anchor="middle" {FONT} font-size="11" fill="{DIM}">compiles 1:1</text>\n'
d += arrow(120, 398, 120, 416, None)
d += f'  <text x="212" y="411" text-anchor="middle" {FONT} font-size="11" fill="{DIM}">uses types {DOT} M:N</text>\n'
# developer -> XR
d += arrow(760, 198, 656, 252, "writes {} 1:N".format(DOT), lx=28, ly=-12, lsize=12)
# cross arrows
d += arrow(488, 256, 272, 242, "must match {} N:1".format(DOT), lx=0, ly=-9, lsize=12)
d += arrow(488, 280, 272, 370, "fulfilled by {} N:1".format(DOT), lx=0, ly=-8, lsize=12)
d += arrow(270, 378, 486, 392, "declares {} 1:N".format(DOT), lx=0, ly=-10, lsize=12)
d += arrow(270, 434, 486, 404, "reconciles {} 1:N".format(DOT), lx=0, ly=18, lsize=12)
d += f'  <text x="60" y="478" {FONT} font-size="14" fill="{DIM}">Purple = Upbound/Crossplane {DOT} blue = Kubernetes {DOT} SETUP is the &#8220;1&#8221;, APPLY the &#8220;N&#8221;.</text>\n'
d += corner() + camguide() + footer() + "</svg>\n"
slides["2/1"] = d

# 2/2 Directory tree
tree = [
    ("upbound-hello-world/", "", BODY),
    ("&#9500;&#9472; upbound.yaml", "project config &#183; entry point", BODY),
    ("&#9500;&#9472; apis/", "YOUR API &#8212; built once  (SETUP)", TITLE),
    ("&#9474;  &#9492;&#9472; storagebuckets/", "", BODY),
    ("&#9474;     &#9500;&#9472; definition.yaml", "XRD &#183; the type", BODY),
    ("&#9474;     &#9492;&#9472; composition.yaml", "Composition &#183; the logic", BODY),
    ("&#9492;&#9472; examples/", "requests  (APPLY)", AMBER),
    ("   &#9492;&#9472; storagebucket/", "", BODY),
    ("      &#9492;&#9472; example.yaml", "XR &#183; one request", BODY),
]
d = head() + panel() + corner() + title_bar("The project is a directory tree", "Structure")
d += role_tag(R_BUILD)
y = 204
for path, note, col in tree:
    d += f'  <text x="72" y="{y}" {MONO} font-size="19" fill="{col}" xml:space="preserve">{path}</text>\n'
    if note:
        d += f'  <text x="470" y="{y}" {FONT} font-size="16" fill="{DIM}">{note}</text>\n'
    y += 29
d += f'  <text x="72" y="470" {FONT} font-size="16" fill="{DIM}">apis/ = set up once  {DOT}  examples/ = the requests that run again and again.</text>\n'
d += camguide() + footer() + "</svg>\n"
slides["2/2"] = d

# 2/3 Cardinality table. Columns pulled left so rows clear the camera corner.
def crow(y, a, card, why, cc=TITLE):
    return (f'  <text x="72" y="{y}" {FONT} font-size="18" fill="{BODY}">{a}</text>\n'
            f'  <text x="340" y="{y}" text-anchor="middle" {FONT} font-size="18" font-weight="700" fill="{cc}">{card}</text>\n'
            f'  <text x="400" y="{y}" {FONT} font-size="15" fill="{DIM}">{why}</text>\n')
d = head() + panel() + corner() + title_bar("How many of each?", "Cardinality")
d += (f'  <text x="72" y="196" {FONT} font-size="14" font-weight="700" letter-spacing="1" fill="{DIM}">RELATIONSHIP</text>\n'
      f'  <text x="340" y="196" text-anchor="middle" {FONT} font-size="14" font-weight="700" letter-spacing="1" fill="{DIM}">COUNT</text>\n'
      f'  <text x="400" y="196" {FONT} font-size="14" font-weight="700" letter-spacing="1" fill="{DIM}">IN PLAIN TERMS</text>\n'
      f'  <line x1="72" y1="206" x2="676" y2="206" stroke="{BORDER}" stroke-opacity="0.3" stroke-width="1.5"/>\n')
rows = [
    (f"XRD {ARR} CRD", "1 : 1", "one XRD compiles into one CRD", GREEN),
    (f"XRD {ARR} XR", "1 : N", "one type, many live requests", TITLE),
    (f"XRD {ARR} Composition", "1 : N", "one type, one-or-more implementations", TITLE),
    (f"Composition {ARR} XR", "1 : N", "one composition serves many requests", TITLE),
    (f"XR {ARR} MR", "1 : N", "one request, several cloud objects", TITLE),
    (f"Provider {ARR} MR", "1 : N", "one provider manages many resources", TITLE),
    (f"Composition {ARRLR} Provider", "M : N", "many-to-many, in both directions", AMBER),
]
y = 234
for a, c, w, cc in rows:
    d += crow(y, a, c, w, cc); y += 34
d += f'  <text x="72" y="{y+14}" {FONT} font-size="15" fill="{DIM}">Nothing you author is 1:1 &#8212; the lone 1:1 is the XRD{ARR}CRD compile step.</text>\n'
d += camguide() + footer() + "</svg>\n"
slides["2/3"] = d

# ===================== COLUMN 3 — the build steps =====================
def step_slide(kick, title, cmd_lines, pts, note_line=None, role=R_BUILD):
    s = head() + panel() + corner() + title_bar(title, kick) + role_tag(role)
    cb, h = codebox(60, 188, 840, cmd_lines)
    s += cb
    y = 188 + h + 46
    s += bullets(pts, y0=y, dy=52, size=21)
    if note_line:
        s += f'  <text x="60" y="474" {FONT} font-size="15" fill="{DIM}">{note_line}</text>\n'
    s += camguide() + footer() + "</svg>\n"
    return s

slides["3/1"] = step_slide("Build &#183; step 1", "Initialize the project",
    ["$ up project init upbound-hello-world --scratch"],
    [("Scaffolds the project &amp; writes upbound.yaml", "The entry point that says what this project is"),
     ("--scratch starts empty", "Every piece we add after this is deliberate, nothing hidden")])

slides["3/2"] = step_slide("Build &#183; step 2", "Add a dependency (a Provider)",
    ["$ up dependency add \\",
     "    'xpkg.upbound.io/upbound/provider-aws-s3:>=v2.0.0'"],
    [("Providers connect the control plane to a cloud", "They ship the resource types &#8212; S3, VMs, databases"),
     ("They own auth &amp; the resource lifecycle", "Without a provider, nothing real can be created")],
    note_line="The admin installs the provider; you declare the dependency here.")

slides["3/3"] = step_slide("Build &#183; step 3", "Generate an example XR",
    ["$ up example generate --type xr \\",
     "    --api-group platform.example.com --kind StorageBucket \\",
     "    --api-version v1alpha1 --name example \\",
     "    --namespace default --scope namespace"],
    [("Writes a sample request to examples/", "This is the request we WISH existed"),
     ("Design the API by using it first", "Next step derives the type from this example")],
    note_line="Request-first design: fill in spec.parameters &#8212; the knobs your users get.")

slides["3/4"] = step_slide("Build &#183; step 4", "Generate the XRD",
    ["$ up xrd generate examples/storagebucket/example.yaml"],
    [("Infers field names &amp; types from the example", "Writes the XRD to apis/ as definition.yaml"),
     ("The XRD compiles into a Kubernetes CRD", "That&#8217;s what makes kubectl get storagebuckets work"),
     ("Not a CRD &#8212; it adds Composition wiring", "A plain CRD would register the type but stay inert")])

slides["3/5"] = step_slide("Build &#183; step 5", "Generate the Composition",
    ["$ up composition generate apis/storagebuckets/definition.yaml"],
    [("Maps your parameters to real Managed Resources", "Your 3 fields in &#8594; the provider&#8217;s 40-field bucket out"),
     ("Handles resource relationships &amp; policy", "Best practices baked in, cloud detail hidden"),
     ("Without it the XRD is an API that does nothing", "The Composition is the body behind the contract")])

# 3/6 Two more words: Function & Template (vocabulary the Composition adds)
d = head() + panel() + corner() + title_bar("Two more words: Function &amp; Template", "Vocabulary, part 2", tsize=34)
d += role_tag(R_BUILD)
d += f'  <text x="60" y="186" {FONT} font-size="18" fill="{DIM}">Both live inside the Composition &#8212; they are how its logic is actually written.</text>\n'
# mini pipeline: XR -> [ function -> function ] -> MRs  (kept above the camera box)
d += node(60, 214, 118, 56, "XR", "the request", stroke=BORDER, tcol=BODY, lsize=18, ssize=12)
d += arrow(178, 242, 232, 242, color=BRAND)
d += band(240, 214, 428, 56, "COMPOSITION &#8212; A PIPELINE OF FUNCTIONS")
d += node(256, 222, 192, 40, "function: patch-and-transform", None, stroke=BORDER, tcol=BODY, lsize=12)
d += arrow(452, 242, 470, 242, color=BORDER)
d += node(476, 222, 178, 40, "function: go-templating", None, stroke=BORDER, tcol=BODY, lsize=12)
d += arrow(670, 242, 724, 242, color=BORDER)
d += node(728, 214, 172, 56, "MRs", "real cloud infra", fill=BRAND, stroke=WHITE, tcol=WHITE, scol="#EDE9FF", lsize=18, ssize=12)
d += bullets([
    (f"Function {EM} a reusable step the pipeline runs", "e.g. patch-and-transform, KCL, Go-templating"),
    (f"Template {EM} a fill-in-the-blanks blueprint", "Your XR&#8217;s parameters fill it in to make a Managed Resource"),
], y0=340, dy=76, size=23)
d += f'  <text x="60" y="474" {FONT} font-size="15" fill="{DIM}">Kitchen metaphor: functions are the appliances {DOT} a template is the recipe card.</text>\n'
d += camguide() + footer() + "</svg>\n"
slides["3/6"] = d

# ===================== COLUMN 4 — synthesis & close =====================
# 4/1 Build order vs run order
d = head() + panel() + corner() + title_bar("Build order &#8800; run order", "The key insight")
# build row (platform builder)
d += f'  <text x="60" y="212" {FONT} font-size="20" font-weight="700" fill="{TITLE}">How the builder AUTHORS it (this workshop)</text>\n'
bx = [("Example XR", 60, 150), ("XRD", 250, 110), ("Composition", 400, 150)]
prev = None
for label, x, w in bx:
    d += node(x, 232, w, 52, label, None, stroke=BORDER, tcol=BODY, lsize=18)
    if prev:
        d += arrow(prev, 258, x-8, 258, color=BRAND)
    prev = x + w
d += f'  <text x="600" y="264" {FONT} font-size="16" fill="{DIM}">bottom-up,</text>\n'
d += f'  <text x="600" y="284" {FONT} font-size="16" fill="{DIM}">example-driven</text>\n'
# run row (developer request) - compressed to stay clear of the camera corner
d += f'  <text x="60" y="352" {FONT} font-size="20" font-weight="700" fill="{GREEN}">How a DEVELOPER&#8217;S request runs</text>\n'
rx = [("XR", 60, 76, BORDER), ("XRD", 152, 76, BORDER), ("Composition", 244, 130, BORDER),
      ("Provider", 390, 100, BORDER), ("MRs", 506, 80, BRAND)]
prev = None
for label, x, w, st in rx:
    fill = BRAND if label == "MRs" else DEEP
    tcol = WHITE if label == "MRs" else BODY
    d += node(x, 372, w, 52, label, None, fill=fill, stroke=st, tcol=tcol, lsize=16)
    if prev:
        d += arrow(prev, 398, x-8, 398, color=BORDER)
    prev = x + w
d += f'  <text x="60" y="470" {FONT} font-size="16" fill="{DIM}">You author inside-out; at runtime it flows top-down.</text>\n'
d += camguide() + footer() + "</svg>\n"
slides["4/1"] = d

# 4/2 Dependency check
d = head() + panel() + corner() + title_bar("Can X exist without Y?", "Dependency check")
d += (f'  <text x="72" y="196" {FONT} font-size="14" font-weight="700" letter-spacing="1" fill="{DIM}">CAN THIS &#8230; WITHOUT THIS</text>\n'
      f'  <text x="430" y="196" text-anchor="middle" {FONT} font-size="14" font-weight="700" letter-spacing="1" fill="{DIM}">?</text>\n'
      f'  <text x="478" y="196" {FONT} font-size="14" font-weight="700" letter-spacing="1" fill="{DIM}">WHY</text>\n'
      f'  <line x1="72" y1="206" x2="676" y2="206" stroke="{BORDER}" stroke-opacity="0.3" stroke-width="1.5"/>\n')
dep = [
    ("Managed Resource", "Provider", "NO", RED, "type &amp; controller come from it"),
    ("Composition", "Provider", "NO", RED, "no MR types to compose"),
    ("XRD", "Composition", "YES", GREEN, "valid API, but does nothing"),
    ("Live XR", "XRD", "NO", RED, "not registered &#8594; rejected"),
    ("Composition", "XRD", "NO", RED, "targets an XRD-defined type"),
]
y = 240
for a, b, ans, col, why in dep:
    d += f'  <text x="72" y="{y}" {FONT} font-size="19" fill="{BODY}">{a}  <tspan fill="{DIM}" font-size="16">without</tspan>  {b}</text>\n'
    d += f'  <text x="430" y="{y}" text-anchor="middle" {FONT} font-size="19" font-weight="700" fill="{col}">{ans}</text>\n'
    d += f'  <text x="478" y="{y}" {FONT} font-size="14" fill="{DIM}">{why}</text>\n'
    y += 40
d += f'  <text x="72" y="{y+16}" {FONT} font-size="17" fill="{TITLE}">You always need the thing beneath it to exist first.</text>\n'
d += camguide() + footer() + "</svg>\n"
slides["4/2"] = d

# 4/3 The hand-off chain - who performs each stage, in order
d = head() + panel() + corner() + title_bar("Who does what, in order", "The hand-off chain")
d += f'  <line x1="76" y1="200" x2="76" y2="412" stroke="{DIM}" stroke-opacity="0.45" stroke-width="2"/>\n'
chain = [
    (R_ADMIN,  "Provision the control plane", "Space, providers, credentials, RBAC"),
    (R_BUILD,  "Author the project",          "up project init " + ARR + " dependency add " + ARR + " generate"),
    (R_GITOPS, "Review, merge and publish",   "PR review &amp; policy gates, then build &amp; push"),
    (R_DEV,    "Apply one XR",                "kubectl apply -f example.yaml " + ARR + " real infra"),
]
y = 214
for i, (role, action, sub) in enumerate(chain, start=1):
    name, col = role
    d += (f'  <circle cx="76" cy="{y-6}" r="13" fill="{col}" fill-opacity="0.2" '
          f'stroke="{col}" stroke-width="2"/>\n'
          f'  <text x="76" y="{y-1}" text-anchor="middle" {FONT} font-size="13" '
          f'font-weight="700" fill="{col}">{i}</text>\n')
    d += chip(104, y - 24, name, col, size=12)
    d += f'  <text x="312" y="{y}" {FONT} font-size="20" font-weight="700" fill="{BODY}">{action}</text>\n'
    d += f'  <text x="312" y="{y+22}" {FONT} font-size="15" fill="{DIM}">{sub}</text>\n'
    y += 64
d += f'  <text x="60" y="478" {FONT} font-size="15" fill="{DIM}">Steps 1&#8211;3 happen once {DOT} step 4 repeats every single day.</text>\n'
d += camguide() + footer() + "</svg>\n"
slides["4/3"] = d

# 4/4 Recap
slides["4/4"] = (head() + panel(0.86) + logo(430, 66, 100, LOGO_HERO)
    + f'  <text x="480" y="212" text-anchor="middle" {FONT} font-size="34" font-weight="700" fill="{TITLE}">You built a self-service API</text>\n'
    + f'  <rect x="390" y="230" width="180" height="5" rx="2.5" fill="{BRAND}"/>\n'
    + bullets([
        ("A project  (upbound.yaml + structure)", ""),
        ("A cloud dependency  (the Provider)", ""),
        ("An API type  (the XRD &#8594; a generated CRD)", ""),
        ("Implementation logic  (the Composition)", ""),
      ], y0=286, dy=44, size=21)
    + f'  <text x="94" y="486" {FONT} font-size="18" fill="{DIM}">Next: a composition function to give your API real behavior.</text>\n'
    + camguide() + "</svg>\n")

# ---- write ----
# Display order drives the slide numbers, so inserts never desync the footers.
ORDER = ["1/1", "1/2", "1/3", "1/4",
         "2/1", "2/2", "2/3",
         "3/1", "3/2", "3/3", "3/4", "3/5", "3/6",
         "4/1", "4/2", "4/3", "4/4"]
assert set(ORDER) == set(slides), set(ORDER) ^ set(slides)
TOTAL = len(ORDER)

keep = set()
for i, key in enumerate(ORDER, start=1):
    sec, num = key.split("/")
    svg = slides[key].replace(NUMTOK, f"{i} / {TOTAL}")
    os.makedirs(os.path.join(OUT, sec), exist_ok=True)
    path = os.path.join(OUT, sec, num + ".svg")
    with open(path, "w") as f:
        f.write(svg)
    keep.add(os.path.abspath(path))
    print(f"wrote {key}  slide {i}/{TOTAL}  {len(svg)} bytes")

# drop any slide files that are no longer part of the deck
for sec in ("1", "2", "3", "4"):
    dirp = os.path.join(OUT, sec)
    if not os.path.isdir(dirp):
        continue
    for fn in os.listdir(dirp):
        p = os.path.abspath(os.path.join(dirp, fn))
        if fn.endswith(".svg") and p not in keep:
            os.remove(p); print("removed stale", p)
