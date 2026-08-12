#!/usr/bin/env python3
"""Generate the 'Asterkube' deck (960x540 SVGs) in the Upbound template style.
Purple = brand; Kubernetes blue for K8s pieces; amber/green for Rust; red for C.
Real logo embedded as base64 so it survives <img>-loaded SVGs.
"""
import os, io, base64, math
from PIL import Image

HERE   = os.path.dirname(os.path.abspath(__file__))
OUT    = HERE
AVATAR = os.path.join(HERE, "..", "images", "upbound_avatar.png")

DEEP="#140B33"; BORDER="#8B6CFF"; TITLE="#B9A6FF"; BODY="#EDE9FF"; DIM="#7C6FAE"
BRAND="#6B5BCD"; WHITE="#FFFFFF"
K8S="#4F8DF0"; RUST="#E0955E"; GO="#6FD0E0"; GREEN="#63D39B"; RED="#F0728C"
CODEBG="#0C0722"; MONO_T="#CFC6FF"
FONT='font-family="Helvetica, Arial, sans-serif"'
MONO='font-family="Menlo, Consolas, monospace"'
DOT="&#8226;"; ARR="&#8594;"; EM="&#8212;"

def _logo_uri(size):
    im = Image.open(AVATAR).convert("RGBA").resize((size, size), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
LOGO_CORNER=_logo_uri(80); LOGO_HERO=_logo_uri(240)
def logo(x,y,w,uri=LOGO_CORNER): return f'  <image href="{uri}" x="{x}" y="{y}" width="{w}" height="{w}"/>\n'

def head(): return ('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" '
                    'width="960" height="540" viewBox="0 0 960 540">\n')
def panel(op=0.9): return (f'  <rect x="20" y="20" width="920" height="500" rx="24" fill="{DEEP}" '
    f'fill-opacity="{op}" stroke="{BORDER}" stroke-opacity="0.35" stroke-width="2"/>\n')
def corner(): return logo(872,40,52)
def footer(i,t): return (f'  <text x="60" y="500" {FONT} font-size="15" fill="{DIM}">Asterkube {DOT} '
    f'Secure Kubernetes without Linux or C</text>\n'
    f'  <text x="900" y="500" text-anchor="end" {FONT} font-size="15" fill="{DIM}">{i} / {t}</text>\n')
def title_bar(title,kicker=None,tsize=40):
    s=""
    if kicker: s+=(f'  <text x="60" y="84" {FONT} font-size="18" font-weight="700" letter-spacing="3" '
                   f'fill="{BORDER}">{kicker.upper()}</text>\n')
    s+=(f'  <text x="60" y="134" {FONT} font-size="{tsize}" font-weight="700" fill="{TITLE}">{title}</text>\n'
        f'  <rect x="60" y="152" width="120" height="5" rx="2.5" fill="{BRAND}"/>\n')
    return s
def bullets(items,y0=210,dy=58,size=24):
    s="";y=y0
    for h,sub in items:
        s+=f'  <circle cx="72" cy="{y-8}" r="6" fill="{BORDER}"/>\n'
        s+=f'  <text x="94" y="{y}" {FONT} font-size="{size}" font-weight="700" fill="{BODY}">{h}</text>\n'
        if sub: s+=f'  <text x="94" y="{y+25}" {FONT} font-size="18" fill="{DIM}">{sub}</text>\n'
        y+=dy
    return s
def node(x,y,w,h,label,sub=None,fill=DEEP,stroke=BORDER,tcol=BODY,scol=DIM,rx=12,lsize=19,ssize=13):
    s=(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" fill-opacity="0.97" '
       f'stroke="{stroke}" stroke-width="2"/>\n')
    cy=y+h/2+(2 if sub else 7)
    s+=(f'  <text x="{x+w/2}" y="{cy}" text-anchor="middle" {FONT} font-size="{lsize}" font-weight="700" '
        f'fill="{tcol}">{label}</text>\n')
    if sub: s+=(f'  <text x="{x+w/2}" y="{cy+20}" text-anchor="middle" {FONT} font-size="{ssize}" '
                f'fill="{scol}">{sub}</text>\n')
    return s
def arrow(x1,y1,x2,y2,label=None,color=BORDER,lx=0,ly=-8,lsize=13):
    ang=math.degrees(math.atan2(y2-y1,x2-x1))
    s=(f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2.5"/>\n'
       f'  <path d="M 0 0 l -13 -6 l 0 12 z" fill="{color}" transform="translate({x2} {y2}) rotate({ang:.1f})"/>\n')
    if label:
        mx,my=(x1+x2)/2+lx,(y1+y2)/2+ly
        s+=f'  <text x="{mx:.0f}" y="{my:.0f}" text-anchor="middle" {FONT} font-size="{lsize}" fill="{TITLE}">{label}</text>\n'
    return s
def codebox(x,y,w,lines,size=16,lh=25):
    h=22+lh*len(lines)
    s=(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{CODEBG}" stroke="{BORDER}" '
       f'stroke-opacity="0.4" stroke-width="1.5"/>\n')
    ty=y+32
    for ln in lines:
        s+=f'  <text x="{x+18}" y="{ty}" {MONO} font-size="{size}" fill="{MONO_T}" xml:space="preserve">{ln}</text>\n'
        ty+=lh
    return s,h

slides={}

# ================= COLUMN 1 =================
slides["1/1"]=(head()+panel(0.84)+logo(400,66,160,LOGO_HERO)
    +f'  <text x="480" y="286" text-anchor="middle" {FONT} font-size="70" font-weight="700" fill="{TITLE}">Asterkube</text>\n'
    +f'  <rect x="360" y="308" width="240" height="5" rx="2.5" fill="{BRAND}"/>\n'
    +f'  <text x="480" y="356" text-anchor="middle" {FONT} font-size="27" font-weight="700" fill="{BODY}">Secure Kubernetes without Linux or C</text>\n'
    +f'  <text x="480" y="398" text-anchor="middle" {FONT} font-size="19" fill="{DIM}">A bootable node on a memory-safe Rust kernel {EM} real kubelet v1.35.6 as PID 1</text>\n'
    +f'  <text x="480" y="454" text-anchor="middle" {FONT} font-size="18" fill="{DIM}">John Boero {DOT} Upbound Labs {DOT} built with Claude</text>\n'
    +"</svg>\n")

slides["1/2"]=(head()+panel()+corner()+title_bar("C is the attack surface","The problem")
    +bullets([
        ("CoreOS made the minimal, immutable K8s VM", "but it still rode Linux, systemd and glibc &#8212; all C"),
        ("Linux kernel: ~11&#8211;12k CVEs, ~half memory-safety", "exploited in the wild; billions in ransomware &amp; breaches"),
        ("GhostLock (CVE-2026-43499): a 15-year futex UAF", "any local user &#8594; root, container escape on most distros"),
        ("The lesson: memory-unsafe C is the liability", "and a VM guest is the ideal place to remove it"),
    ],y0=214,dy=68)+footer(2,14)+"</svg>\n")

slides["1/3"]=(head()+panel()+corner()+title_bar("A VM doesn&#8217;t need a C kernel","The insight")
    +bullets([
        ("The hypervisor already does the hard part", "device drivers, ECC, memory management, error detection"),
        ("It hands the guest simple virtual interfaces", "leaving room for a tiny, memory-safe kernel"),
        ("Asterinas: a Linux-ABI framekernel in Rust", "MPL-2.0 &#8212; runs the Linux syscall ABI, written safe"),
        ("asterkube turns it into a real K8s node", "&#8230; and strips C out of the entire image"),
    ],y0=214,dy=68)+footer(3,14)+"</svg>\n")

# ================= COLUMN 2 =================
# 2/1 stack comparison table
d=head()+panel()+corner()+title_bar("The stack","What changes")
d+=(f'  <text x="72" y="200" {FONT} font-size="15" font-weight="700" letter-spacing="1" fill="{DIM}">LAYER</text>\n'
    f'  <text x="392" y="200" {FONT} font-size="15" font-weight="700" letter-spacing="1" fill="{DIM}">TRADITIONAL</text>\n'
    f'  <text x="648" y="200" {FONT} font-size="15" font-weight="700" letter-spacing="1" fill="{DIM}">ASTERKUBE</text>\n'
    f'  <line x1="72" y1="212" x2="900" y2="212" stroke="{BORDER}" stroke-opacity="0.3" stroke-width="1.5"/>\n')
rows=[("Container runtime","containerd (Go)",GO,"containerd (Go)",GO),
      ("Orchestration","kubelet (Go)",GO,"kubelet (Go) + init",GO),
      ("Init","systemd (C)",RED,"(folded into kubelet)",DIM),
      ("Kernel","Linux (C)",RED,"Asterinas (Rust)",GREEN)]
y=254
for lay,tr,tc,ak,ac in rows:
    d+=f'  <text x="72" y="{y}" {FONT} font-size="21" fill="{BODY}">{lay}</text>\n'
    d+=f'  <text x="392" y="{y}" {FONT} font-size="21" font-weight="700" fill="{tc}">{tr}</text>\n'
    d+=f'  <text x="648" y="{y}" {FONT} font-size="21" font-weight="700" fill="{ac}">{ak}</text>\n'
    d+=f'  <line x1="72" y1="{y+18}" x2="900" y2="{y+18}" stroke="{BORDER}" stroke-opacity="0.12" stroke-width="1"/>\n'
    y+=52
d+=f'  <text x="72" y="{y+16}" {FONT} font-size="18" fill="{TITLE}">The Kubernetes node service <tspan font-style="italic">is</tspan> the operating system &#8212; no systemd, no separate init.</text>\n'
d+=footer(4,14)+"</svg>\n"; slides["2/1"]=d

# 2/2 architecture / boot chain
d=head()+panel()+corner()+title_bar("Architecture","Layout")
d+=node(60,214,168,66,"rubu","Rust bootloader",stroke=RUST,tcol=BODY,scol=RUST,lsize=20)
d+=node(270,214,196,66,"Asterinas","Rust framekernel",stroke=GREEN,tcol=BODY,scol=GREEN,lsize=20)
d+=node(508,214,178,66,"kubelet","Go &#183; init / PID 1",stroke=K8S,tcol=BODY,scol=K8S,lsize=20)
d+=node(728,214,172,66,"containerd","Go runtime",stroke=BORDER,tcol=BODY,lsize=19)
d+=arrow(228,247,268,247,"EFI handoff",lx=0,ly=-9,lsize=12)
d+=arrow(466,247,506,247)
d+=arrow(686,247,726,247)
d+=bullets([
    ("asterinas/  &#8212; git submodule", "kernel fork, ~50 commits, ~10k lines (MPL-2.0)"),
    ("kubernetes/  &#8212; build-fetched @ v1.35.6", "pinned tag, not vendored; real cmd/kubelet/app"),
    ("cmd/asterkube-init/  &#8212; original Go", "imports Kubernetes &#8212; it is not a fork of it"),
],y0=346,dy=48,size=20)
d+=footer(5,14)+"</svg>\n"; slides["2/2"]=d

# 2/3 the image breakdown
d=head()+panel()+corner()+title_bar("The image: ~40 MB, boots &lt; 5 s, zero C","The artifact")
img_lines=[
    ("kernel ELF (stripped)","5.3 MiB","",BODY),
    ("initramfs.cpio.zst (--ultra -22)","26.4 MiB","&#8722;40% vs gzip",BODY),
    ("bootable ISO (isohybrid)","40.6 MiB","",BODY),
    ("QCOW2 disk image","38.2 MiB","",BODY),
    ("SEP",None,None,None),
    ("usr/bin/kubelet","79.1 MiB","kubelet + init + runc + mount + DHCP",BODY),
    ("usr/bin/containerd","42.7 MiB","merged containerd + ctr",BODY),
    ("usr/bin/containerd-shim-runc-v2","13.9 MiB","",BODY),
    ("usr/lib64/","empty","&#9668; the zero-C proof",GREEN),
]
y=206
for name,size,note,col in img_lines:
    if name=="SEP":
        d+=f'  <line x1="90" y1="{y-8}" x2="880" y2="{y-8}" stroke="{BORDER}" stroke-opacity="0.2" stroke-width="1"/>\n'
        y+=14; continue
    d+=f'  <text x="90" y="{y}" {MONO} font-size="17" fill="{col}">{name}</text>\n'
    d+=f'  <text x="560" y="{y}" text-anchor="end" {MONO} font-size="17" fill="{col}">{size}</text>\n'
    if note: d+=f'  <text x="580" y="{y}" {FONT} font-size="15" fill="{DIM}">{note}</text>\n'
    y+=30
d+=f'  <text x="90" y="{y+10}" {FONT} font-size="16" fill="{TITLE}">Three static, CGO-free Go binaries are the entire userspace. Empty /lib64 = no C runtime.</text>\n'
d+=footer(6,14)+"</svg>\n"; slides["2/3"]=d

# ================= COLUMN 3 =================
slides["3/1"]=(head()+panel()+corner()+title_bar("Kernel work (Asterinas fork)","What&#8217;s inside &#183; 1")
    +bullets([
        ("Namespaces &amp; cgroups", "PID / net / user namespaces (rootless); cgroup v2 cpu/mem/pids"),
        ("Real seccomp-BPF", "a classic-BPF interpreter at the syscall gate (was a stub)"),
        ("astermac &#8212; native capability-MAC", "cross-tenant signal / file / network isolation, tenant labels"),
        ("A Service networking datapath", "ClusterIP DNAT + LB, SNAT, nftables-compatible netlink for kube-proxy"),
        ("OCI enablers + pure-Rust zstd", "bpf(), pivot_root, overlayfs, mqueue; ruzstd (no_std)"),
    ],y0=200,dy=55,size=21)+footer(7,14)+"</svg>\n")

slides["3/2"]=(head()+panel()+corner()+title_bar("Go node agent","What&#8217;s inside &#183; 2")
    +bullets([
        ("The kubelet fused with init as PID 1", "one multi-call binary: init / runc / mount / DHCP by argv[0]"),
        ("DHCP-first userspace networking", "RFC 2131 with lease renewal &#8212; no static config"),
        ("Zero-C container runtime", "static containerd + a pure-Go, CGO-free runc"),
        ("Boot-args cluster join", "kubeadm-style; apiserver pinned by IP + CA-hash"),
        ("Adversarial boot-time probes", "exercise every security guarantee &#8212; fail boot if one doesn&#8217;t hold"),
    ],y0=200,dy=55,size=21)+footer(8,14)+"</svg>\n")

slides["3/3"]=(head()+panel()+corner()+title_bar("Fully C-free boot with rubu","The last C")
    +bullets([
        ("GRUB2 is the only C left in the image", "&#8230; and rubu removes it"),
        ("rubu: a #![no_std] pure-Rust UEFI bootloader", "own crypto, own TCP/IP + TLS 1.3, own TPM CRB driver"),
        ("Verifies + measures the boot into a TPM", "PCRs 8/9, then Linux EFI-handover to Asterinas"),
        ("Chain: rubu &#8594; Asterinas &#8594; Go &#8212; zero C", "Verified: still joins the cluster and reaches Ready"),
    ],y0=214,dy=66)+footer(9,14)+"</svg>\n")

slides["3/4"]=(head()+panel()+corner()+title_bar("OS identity","Honest labeling")
    +bullets([
        ("Identifies truthfully as Asterinas", "/etc/os-release OSImage; kernel 5.13.0-asterinas"),
        ("Advertises kernel.asterinas.io/name", "the real kernel is surfaced to the cluster"),
        ("Keeps kubernetes.io/os=linux", "Linux-ABI compat (like gVisor / linuxulator), not a brand claim"),
        ("Changing it would break the ecosystem", "pod scheduling and OCI image matching depend on it"),
    ],y0=214,dy=66)+footer(10,14)+"</svg>\n")

# ================= COLUMN 4 =================
slides["4/1"]=(head()+panel()+corner()+title_bar("It joins a real cluster","Verified")
    +bullets([
        ("The zero-C node reaches Ready=True", "OSImage=Asterinas, kubernetes.io/os=linux"),
        ("Carries an experimental NoSchedule taint", "asterkube.io/experimental &#8212; opt-in workloads only"),
        ("Joins via a host-issued config disk", "cloud-init / Ignition model; installs CNI (ptp + portmap)"),
        ("Node cert minted via the cluster CSR API", "the CA key never leaves the cluster"),
    ],y0=214,dy=66)+footer(11,14)+"</svg>\n")

d=head()+panel()+corner()+title_bar("Try it (no build)","Boot it yourself")
cb,h=codebox(60,190,840,[
    "$ gh release download asterkube-v0.1 --repo jboero/asterkube",
    "$ sha256sum -c SHA256SUMS",
    "$ ./run-release.sh asterkube-node-v0.1.iso      # or the .qcow2",
])
d+=cb
d+=bullets([
    ("Needs only qemu-system-x86_64, OVMF and KVM", "boots in a few seconds and stays live until you power it down"),
    ("Or join your own cluster", "asterkube-join.sh mints a bundle; attach it as a virtio-blk config disk"),
],y0=190+h+46,dy=64,size=21)
d+=footer(12,14)+"</svg>\n"; slides["4/2"]=d

slides["4/3"]=(head()+panel()+corner()+title_bar("Honest status &amp; limits","It&#8217;s a PoC")
    +bullets([
        ("Not production-ready; largely AI-authored", "Asterinas maintainers gate anything going upstream"),
        ("astermac ships Permissive (log-only)", "armed but not blocking until set to Enforcing"),
        ("Minimal NAT datapath", "small global conntrack, no endpoint removal"),
        ("virtio-only; no ext4/btrfs or aarch64 yet", "great for VM workloads, not bare metal"),
    ],y0=214,dy=66)+footer(13,14)+"</svg>\n")

slides["4/4"]=(head()+panel(0.84)+logo(430,64,100,LOGO_HERO)
    +f'  <text x="480" y="212" text-anchor="middle" {FONT} font-size="32" font-weight="700" fill="{TITLE}">Secure Kubernetes without Linux or C</text>\n'
    +f'  <rect x="380" y="230" width="200" height="5" rx="2.5" fill="{BRAND}"/>\n'
    +f'  <text x="480" y="288" text-anchor="middle" {FONT} font-size="22" fill="{BODY}">github.com/jboero/asterkube  {DOT}  github.com/jboero/rubu</text>\n'
    +f'  <text x="480" y="326" text-anchor="middle" {FONT} font-size="20" fill="{DIM}">Read: &#8220;Secure Kubernetes Without Linux or C&#8221; {EM} Upbound Labs (Medium)</text>\n'
    +f'  <text x="480" y="404" text-anchor="middle" {FONT} font-size="20" fill="{BODY}">John Boero {DOT} Upbound Labs {DOT} built with Claude</text>\n'
    +f'  <text x="480" y="442" text-anchor="middle" {FONT} font-size="16" fill="{DIM}">asterkube Apache-2.0 {DOT} Asterinas MPL-2.0 {DOT} Kubernetes Apache-2.0</text>\n'
    +"</svg>\n")

import shutil
for c in ("1","2","3","4"): shutil.rmtree(os.path.join(OUT,c),ignore_errors=True)
for path,svg in slides.items():
    sec,num=path.split("/"); os.makedirs(os.path.join(OUT,sec),exist_ok=True)
    open(os.path.join(OUT,sec,num+".svg"),"w").write(svg); print("wrote",path,len(svg))
