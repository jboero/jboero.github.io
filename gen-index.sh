#!/bin/bash
# gen-index.sh — Generate a themed index.html for a directory listing.
# Usage: ./gen-index.sh [path]   (defaults to ./)
# Skips dotfiles/dotdirs, the script itself, and existing index.html.

TARGET="${1:-.}"
TARGET="$(cd "$TARGET" && pwd)"
DIRNAME="$(basename "$TARGET")"

# Collect entries
declare -a DIRS=()
declare -a FILES=()

while IFS= read -r name; do
    [[ -z "$name" ]] && continue
    [[ "$name" == .* ]] && continue
    [[ "$name" == "gen-index.sh" ]] && continue
    [[ "$name" == "index.html" ]] && continue
    if [[ -d "$TARGET/$name" ]]; then
        DIRS+=("$name")
    else
        FILES+=("$name")
    fi
done < <(ls -1 "$TARGET" | sort -f)

# Helper: pick an icon for a file based on extension
icon_for() {
    local name="$1"
    if [[ -d "$TARGET/$name" ]]; then
        echo "folder"
    else
        case "${name##*.}" in
            html|htm)   echo "html";;
            css)        echo "css";;
            js|ts|jsx|tsx) echo "js";;
            py)         echo "python";;
            sh|bash|zsh|fish) echo "terminal";;
            md|txt|rst) echo "doc";;
            json|yaml|yml|toml|xml) echo "config";;
            png|jpg|jpeg|gif|svg|webp|ico) echo "image";;
            mp4|webm|avi|mov) echo "video";;
            zip|tar|gz|bz2|xz|7z) echo "archive";;
            *)          echo "file";;
        esac
    fi
}

# Helper: human-readable file size
human_size() {
    local f="$TARGET/$1"
    if [[ -d "$f" ]]; then
        echo "—"
    else
        local bytes
        bytes=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null || echo 0)
        if (( bytes >= 1073741824 )); then
            printf "%.1f GB" "$(echo "scale=1; $bytes/1073741824" | bc)"
        elif (( bytes >= 1048576 )); then
            printf "%.1f MB" "$(echo "scale=1; $bytes/1048576" | bc)"
        elif (( bytes >= 1024 )); then
            printf "%.1f KB" "$(echo "scale=1; $bytes/1024" | bc)"
        else
            echo "${bytes} B"
        fi
    fi
}

# Helper: modification date
mod_date() {
    stat -c '%Y' "$TARGET/$1" 2>/dev/null || stat -f '%m' "$TARGET/$1" 2>/dev/null
}

# Build table rows
build_rows() {
    local items=("$@")
    for name in "${items[@]}"; do
        local icon
        icon="$(icon_for "$name")"
        local size
        size="$(human_size "$name")"
        local ts
        ts="$(mod_date "$name")"
        local href="$name"
        [[ -d "$TARGET/$name" ]] && href="$name/"

        cat <<ROWEOF
      <tr>
        <td class="icon-cell"><span class="icon icon-${icon}"></span></td>
        <td class="name-cell"><a href="${href}">${name}</a></td>
        <td class="size-cell">${size}</td>
        <td class="date-cell" data-ts="${ts}"></td>
      </tr>
ROWEOF
    done
}

# --- Write index.html ---
cat > "$TARGET/index.html" <<'HTMLEOF'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
HTMLEOF

cat >> "$TARGET/index.html" <<HTMLEOF
<title>Index of /${DIRNAME}</title>
HTMLEOF

cat >> "$TARGET/index.html" <<'HTMLEOF'
<style>
  :root {
    --bg: #0d1117;
    --surface: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --text-dim: #8b949e;
    --accent: #58a6ff;
    --accent2: #f778ba;
    --accent3: #7ee787;
    --glow: rgba(88, 166, 255, 0.15);
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    padding: 2rem;
  }
  /* Animated gradient border at top */
  body::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent), var(--accent2), var(--accent3), var(--accent));
    background-size: 300% 100%;
    animation: gradient-slide 4s linear infinite;
    z-index: 100;
  }
  @keyframes gradient-slide {
    0% { background-position: 0% 50%; }
    100% { background-position: 300% 50%; }
  }

  .container {
    max-width: 900px;
    margin: 0 auto;
  }
  header {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
  }
  header h1 {
    font-size: 1.4rem;
    font-weight: 600;
    color: var(--text);
  }
  header h1 .prompt { color: var(--accent3); }
  header h1 .path { color: var(--accent); }
  header .subtitle {
    font-size: 0.8rem;
    color: var(--text-dim);
    margin-top: 0.4rem;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    background: var(--surface);
  }
  thead th {
    text-align: left;
    padding: 0.7rem 1rem;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-dim);
    border-bottom: 1px solid var(--border);
    background: var(--bg);
    cursor: pointer;
    user-select: none;
  }
  thead th:hover { color: var(--accent); }
  tbody tr {
    border-bottom: 1px solid var(--border);
    transition: background 0.15s;
  }
  tbody tr:last-child { border-bottom: none; }
  tbody tr:hover {
    background: var(--glow);
  }
  td {
    padding: 0.6rem 1rem;
    font-size: 0.85rem;
    white-space: nowrap;
  }
  .icon-cell { width: 2.5rem; text-align: center; }
  .size-cell, .date-cell { color: var(--text-dim); text-align: right; }
  .name-cell a {
    color: var(--accent);
    text-decoration: none;
    transition: color 0.15s;
  }
  .name-cell a:hover {
    color: var(--accent2);
    text-decoration: underline;
  }

  /* Icons via CSS — no external deps */
  .icon {
    display: inline-block;
    width: 18px; height: 18px;
    vertical-align: middle;
    border-radius: 3px;
  }
  .icon-folder   { background: var(--accent);  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpath d='M10 4H4a2 2 0 00-2 2v12a2 2 0 002 2h16a2 2 0 002-2V8a2 2 0 00-2-2h-8l-2-2z'/%3E%3C/svg%3E") center/contain no-repeat; -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpath d='M10 4H4a2 2 0 00-2 2v12a2 2 0 002 2h16a2 2 0 002-2V8a2 2 0 00-2-2h-8l-2-2z'/%3E%3C/svg%3E") center/contain no-repeat; }
  .icon-file     { background: var(--text-dim); mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpath d='M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm4 18H6V4h7v5h5v11z'/%3E%3C/svg%3E") center/contain no-repeat; -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='currentColor'%3E%3Cpath d='M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm4 18H6V4h7v5h5v11z'/%3E%3C/svg%3E") center/contain no-repeat; }
  .icon-html     { background: #e44d26; }
  .icon-css      { background: #264de4; }
  .icon-js       { background: #f7df1e; border-radius: 3px; }
  .icon-python   { background: #3776ab; }
  .icon-terminal { background: var(--accent3); }
  .icon-doc      { background: var(--text-dim); }
  .icon-config   { background: #f0883e; }
  .icon-image    { background: var(--accent2); }
  .icon-video    { background: #bc8cff; }
  .icon-archive  { background: #f0883e; }

  footer {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
    font-size: 0.7rem;
    color: var(--text-dim);
    display: flex;
    justify-content: space-between;
  }

  /* Scanline overlay for extra retro flavor */
  body::after {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.03) 2px,
      rgba(0,0,0,0.03) 4px
    );
    pointer-events: none;
    z-index: 99;
  }

  @media (max-width: 600px) {
    body { padding: 1rem; }
    .date-cell { display: none; }
    td { padding: 0.5rem 0.6rem; }
  }
</style>
</head>
<body>
<div class="container">
HTMLEOF

# Header
ITEM_COUNT=$(( ${#DIRS[@]} + ${#FILES[@]} ))
cat >> "$TARGET/index.html" <<HTMLEOF
  <header>
    <h1><span class="prompt">\$</span> ls <span class="path">/${DIRNAME}</span></h1>
    <div class="subtitle">${ITEM_COUNT} items &mdash; generated $(date '+%Y-%m-%d %H:%M')</div>
  </header>
  <table>
    <thead>
      <tr>
        <th></th>
        <th>Name</th>
        <th style="text-align:right">Size</th>
        <th style="text-align:right">Modified</th>
      </tr>
    </thead>
    <tbody>
HTMLEOF

# Parent link if not filesystem root
if [[ "$TARGET" != "/" ]]; then
    cat >> "$TARGET/index.html" <<'HTMLEOF'
      <tr>
        <td class="icon-cell"><span class="icon icon-folder"></span></td>
        <td class="name-cell"><a href="../">..</a></td>
        <td class="size-cell">&mdash;</td>
        <td class="date-cell">&mdash;</td>
      </tr>
HTMLEOF
fi

# Directories first, then files
build_rows "${DIRS[@]}" >> "$TARGET/index.html"
build_rows "${FILES[@]}" >> "$TARGET/index.html"

cat >> "$TARGET/index.html" <<'HTMLEOF'
    </tbody>
  </table>
  <footer>
    <span>gen-index.sh</span>
    <span id="clock"></span>
  </footer>
</div>
<script>
  // Format timestamps
  document.querySelectorAll('.date-cell[data-ts]').forEach(el => {
    const ts = parseInt(el.dataset.ts, 10);
    if (!ts) return;
    const d = new Date(ts * 1000);
    el.textContent = d.toLocaleDateString('en-US', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  });
  // Live clock in footer
  const clock = document.getElementById('clock');
  if (clock) setInterval(() => {
    clock.textContent = new Date().toLocaleTimeString();
  }, 1000);
</script>
</body>
</html>
HTMLEOF

echo "Generated: $TARGET/index.html (${#DIRS[@]} dirs, ${#FILES[@]} files)"
