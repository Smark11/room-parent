#!/usr/bin/env python3
"""Build the Halloween handouts.

1. Generate printables/halloween/video-scripts.html from the four scripts on events/halloween.html
   (so the PDF never drifts from the page).
2. Render every printables/halloween/*.html to downloads/halloween/*.pdf with headless Chrome.
3. Zip the PDFs into downloads/halloween/all-printables.zip.

Run from the repo root:  python3 printables/build.py
"""
import html, os, re, subprocess, sys, zipfile, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "printables" / "halloween"
OUT = ROOT / "downloads" / "halloween"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT.mkdir(parents=True, exist_ok=True)

# ---------- 1. video scripts ----------
page = (ROOT / "events" / "halloween.html").read_text()
def pre(id_):
    m = re.search(r'<pre id="%s">(.*?)</pre>' % id_, page, re.S)
    return html.unescape(m.group(1)) if m else None

def script_html(text):
    lines = text.split("\n")
    title = lines[0]
    rest = lines[1:]
    out = []
    card = ""
    for ln in rest:
        s = ln.strip()
        if not s: continue
        if s.startswith("Room parent adds title card:"):
            card = s.split(":", 1)[1].strip().strip('"'); continue
        esc = html.escape(s)
        if re.fullmatch(r"\((beat|pause|long pause|very long pause[^)]*|pause\.?[^)]*)\)", s, re.I) or s.lower().startswith("(beat") or s.lower().startswith("(pause") or s.lower().startswith("(long pause") or s.lower().startswith("(very long pause"):
            out.append(f'<p class="beat">{esc}</p>')
        elif s.startswith("("):
            out.append(f'<p class="dir">{esc}</p>')
        else:
            out.append(f"<p>{esc}</p>")
    m = re.match(r"(.*?)\s{2,}\((.*)\)\s*$", title)
    t, meta = (m.group(1), m.group(2)) if m else (title, "")
    return t.strip(), meta, card, "\n".join(out)

scripts = [("ivs1", "Video 1 · plays after Station 1", "The only interview with real information, and it arrives by accident. Deadpan. Hold the beats."),
           ("ivs3", "Video 2 · plays after Station 2", "Zero information. Genuinely does not understand squishies and is a little offended to be asked."),
           ("ivs4", "Video 3 · plays after Station 3", "Zero information, whispered throughout. Accidentally sounds guilty three times."),
           ("ivs5", "Video 4 · plays after the arrest warrants are read", "Starts defensive, cracks fast, ends with the location of the loot.")]
ask = pre("askstaff")
parts = []
for id_, when, note in scripts:
    t, meta, card, body = script_html(pre(id_))
    parts.append(f'''<section class="page script">
  <span class="eyebrow grape">{html.escape(when)}</span>
  <div class="title">{html.escape(t)}</div>
  <div class="small muted" style="margin-bottom:8px">{html.escape(meta)} · {html.escape(note)}</div>
  <div class="card">TITLE CARD · {html.escape(card)}</div>
  {body}
  <div class="footer-note"><span>The Case of the Missing Candy · {html.escape(t)}</span><span>Two takes max. Send the slightly flubbed one.</span></div>
</section>''')

guide = '''<section class="page">
  <span class="eyebrow">Send with the script</span>
  <h1>Self-recording guide</h1>
  <p class="muted">Reality-TV confessional style: you sit alone and talk to the camera, deadpan. Every script is a self-contained monologue with no interviewer, so you can prop up your own phone and record it in five minutes whenever you have a free moment.</p>
  <div class="two">
    <div class="box soft"><h4>Setup</h4><ul class="small" style="margin:0">
      <li><strong>Nobody films you.</strong> Prop your phone horizontal against a stack of books or a mug, at face height, about an arm's length away. Sit in a chair against a plain wall or a bookshelf.</li>
      <li><strong>Light:</strong> face a window or a lamp. Don't sit with a window behind you.</li>
      <li><strong>Eyeline:</strong> look just to the side of the lens, as if a producer is sitting next to the phone. Glancing at the lens once or twice is fine.</li>
      <li><strong>Tone:</strong> deadpan beats hammy. You are a sincere person who has nothing to hide and is slightly annoyed to be asked.</li></ul></div>
    <div class="box soft"><h4>Recording</h4><ul class="small" style="margin:0">
      <li><strong>The script:</strong> read it from a second screen or a printout taped just under the phone. The <em>(beat)</em> and <em>(pause)</em> marks are where the laughs live. Hold them longer than feels natural.</li>
      <li><strong>Takes:</strong> two max. Send the slightly flubbed one. Don't edit anything.</li>
      <li><strong>Length:</strong> 60 to 90 seconds. Start recording, wait two seconds, begin. Stop two seconds after the last line.</li>
      <li><strong>Send it:</strong> text or AirDrop the raw video to the room parent. They add the title card and load it onto the classroom laptop.</li></ul></div>
  </div>
  <h3 style="margin-top:16px">The ask (email or text to each suspect)</h3>
  <div class="box soft" style="white-space:pre-wrap;font-size:10pt">''' + html.escape(ask or "") + '''</div>
  <p class="small muted">The Custodian gets a different ask: "You're a suspect who declined to comment. That's it. That's the whole job. Please act shifty in the hallway on Oct 30."</p>
</section>'''

vs = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Video Scripts · Four confessionals</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../print.css">
<style>.script p {{ font-size: 11pt; margin: 0 0 .45em; }} .script .dir {{ font-size: 10pt; }}</style>
</head>
<body>
<div class="toolbar"><b>🎥 Video scripts</b><span class="muted">5 pages · the self-recording guide and all four confessional scripts (generated from the plan page)</span><span class="grow"></span><a href="../../events/halloween.html#downloads">← Back to the plan</a><a href="../../downloads/halloween/video-scripts.pdf" download>⬇ PDF</a><button class="primary" onclick="window.print()">🖨 Print</button></div>
{guide}
{chr(10).join(parts)}
</body>
</html>
'''
(SRC / "video-scripts.html").write_text(vs)
print("generated video-scripts.html")

# ---------- 2. PDFs ----------
if not os.path.exists(CHROME):
    sys.exit("Chrome not found at " + CHROME)
failed = []
for src in sorted(SRC.glob("*.html")):
    pdf = OUT / (src.stem + ".pdf")
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
           "--run-all-compositor-stages-before-draw", "--virtual-time-budget=10000",
           "--no-pdf-header-footer", f"--print-to-pdf={pdf}", src.as_uri()]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not pdf.exists() or pdf.stat().st_size < 1000:
        failed.append((src.name, r.stderr[-400:]))
    else:
        print(f"  {pdf.name:32s} {pdf.stat().st_size/1024:7.0f} KB")
if failed:
    for f in failed: print("FAILED", f)
    sys.exit(1)

# ---------- 3. zip ----------
zpath = OUT / "all-printables.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    for pdf in sorted(OUT.glob("*.pdf")):
        z.write(pdf, "halloween-printables/" + pdf.name)
print("zip", zpath.name, round(zpath.stat().st_size/1024), "KB")
