#!/usr/bin/env python3
"""Build the Halloween handouts.

1. Generate printables/halloween/video-scripts.html, the four script-*.html files, and
   suspect-statement-forms.html from the scripts on events/halloween.html and the FORMS table below.
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
    in_box = False
    def mark(esc):
        # [bracketed] words are adjustable: highlight them
        return re.sub(r"\[([^\]]+)\]", r'<span class="adj">[\1]</span>', esc)
    for ln in rest:
        s = ln.strip()
        if not s:
            if in_box: out.append("</ul></div>"); in_box = False
            continue
        if s.startswith("Room parent adds title card:"):
            card = s.split(":", 1)[1].strip().strip('"'); continue
        if s.startswith("MAKE IT YOURS"):
            out.append('<div class="box soft yours"><h4>' + html.escape(s) + '</h4><ul>'); in_box = True; continue
        if in_box:
            item = s[1:].strip() if s.startswith("•") else s
            if item.startswith("Words in [brackets]"):
                out.append('</ul><p class="legend">' + mark(html.escape(item)) + '</p></div>'); in_box = False
            else:
                out.append("<li>" + mark(html.escape(item)) + "</li>")
            continue
        esc = mark(html.escape(s))
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
  <div class="footer-note static"><span>The Case of the Missing Candy · {html.escape(t)}</span><span>Two takes max. Send the slightly flubbed one.</span></div>
</section>''')

guide = '''<section class="page">
  <span class="eyebrow">Send with the script</span>
  <h1>Self-recording guide</h1>
  <p class="muted small" style="margin-bottom:8px">Reality-TV confessional style: you sit and talk to the camera, deadpan. No interviewer, so prop up your own phone, or let whoever sent you this hold it, and record it in five minutes whenever you have a free moment.</p>
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
      <li><strong>Send it:</strong> text or AirDrop the raw video to whoever sent you the script. They add the title card and load it onto the classroom laptop.</li></ul></div>
  </div>
  <div class="box soft" style="margin-top:4px"><h4>Making the script yours</h4><p class="small" style="margin:0">Words in <span style="background:rgba(255,217,61,.45);padding:0 3px;border-radius:3px">[brackets]</span> are adjustable. The facts the kids check (shoe size, where you were, what you wore, how you feel about squishies) live on your <strong>Suspect Statement form</strong>, not in this video. The box at the top of your script gives you the four answers to write on the form, the one or two things the video has to agree with, and the lines to keep word for word. Everything else is flavor. Swap in your real life, your real subject, your real habits. Wear whatever you like. True details get the biggest laughs.</p></div>
  <h3 style="margin-top:10px;font-size:12pt">The ask (email or text to each suspect)</h3>
  <div class="box soft ask" style="white-space:pre-wrap">''' + html.escape(ask or "") + '''</div>
  <p class="small muted" style="margin:4px 0 0">The Custodian gets a different ask: "You're a suspect who declined to comment. That's it. That's the whole job. Please act shifty in the hallway on Oct 30."</p>
</section>'''

# ---------- 1b. suspect statement forms ----------
# The scripted statement answers per suspect (the four traits the clues test), used for the answer-key page.
# The same answers are repeated in each script's MAKE IT YOURS box on events/halloween.html.
FORMS = [
  dict(key="principal", who="The Principal", form="S-1",
       q1="In a meeting. A meeting about the next meeting.", q2="Everyone at the meeting. All nine of them.",
       q3="9", q4="An orange sweater. School spirit.", q5="Tick LOVE THEM. Explain: “I own ONE. It’s a cat. It’s for stress.”",
       q6="Tick DEFINE “INSIDE.”", q7="No. Absolutely not. No.", q8="I did not say squishies.",
       note="Your meeting alibi is what clears you (Clue 2, the timeline). Everything else keeps you looking guilty, which is the job."),
  dict(key="reading-specialist", who="The Reading Specialist", form="S-2",
       q1="The reading room. Where I always am.", q2="Twenty-two chapter books. They don’t talk.",
       q3="9", q4="Orange. It’s a school color. Half the building wears orange.", q5="Tick DON’T GET THEM. Explain: “You squeeze it. It goes back. That’s it.”",
       q6="Tick YES. Add: “To pull a reading group. Daily.”", q7="No. If I wanted to steal something, I’d steal a good chapter book.", q8="I just don’t understand the obsession these days.",
       note="Not getting squishies is what clears you (Clue 4, the witness). Don’t soften it."),
  dict(key="librarian", who="The Librarian", form="S-3",
       q1="Shelving. Alone. In the back. 2:00 to 2:30, every day.", q2="No witnesses. That sounded worse than I meant it to.",
       q3="7", q4="My orange cardigan.", q5="Tick LOVE THEM. Explain: “One on every cart. Shelving is stressful.”",
       q6="Tick YES. Add: “Overdue books.”", q7="No. If I had, they would be alphabetized by now.", q8="Whoever took them... check their feet.",
       note="Your shoe size is what clears you (Clue 1, the footprint is a 9). Write 7 whatever your real size is."),
  dict(key="custodian", who="The Custodian", form="S-4", declined=True,
       note="Nothing to fill in. The form is pre-stamped DECLINED TO COMMENT and the Bureau’s own records are printed on it. Sign the bottom if you like. On Oct 30, act shifty in the hallway."),
  dict(key="chief", who="The Chief (Mrs. Driscoll)", form="S-5",
       q1="In my classroom. Teaching. I live here, basically.", q2="Twenty children.",
       q3="9", q4="An orange sweater. It’s festive.", q5="Write “Don’t be ridiculous,” cross it out with ONE line so it can still be read, then tick LOVE THEM and write “Fine. Love them.”",
       q6="Write: “It’s MY room.”", q7="The Chief is never a suspect.", q8="I would like it noted that I am not a suspect.",
       note="You match all four clues on purpose. This form stays in the Detective’s folder until deliberation (2:28). When a squad has crossed off everyone, the Detective produces it, pins it to the board, and the room turns on you. Keep it off the wall until then."),
]
FORM_CSS = """
.form { position: relative; padding-top: 10px; }
.form .fhdr { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
.form .case { font-family: "Fredoka", sans-serif; font-size: 8.5pt; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin-top: 8px; }
.form h1 { font-size: 24pt; margin: 0 0 2px; }
.form .q { margin: 7px 0 0; }
.form label { display: block; font-family: "Fredoka", sans-serif; font-weight: 600; font-size: 10.5pt; }
.form label small { font-weight: 400; color: var(--muted); font-size: 8.5pt; }
.form .ans { border-bottom: 1.5px solid var(--ink); height: 1.8em; }
.form .ans.filled { font-weight: 800; font-size: 12pt; padding-top: .3em; }
.form .opts { font-size: 10pt; margin: 4px 0 2px; }
.form .opts .chk { margin-left: 2px; }
.form .official { border: 1.5px dashed var(--line); border-radius: 8px; padding: 6px 10px; font-size: 9pt; margin-top: 12px; }
.form .official b { font-family: "Fredoka", sans-serif; letter-spacing: .1em; text-transform: uppercase; font-size: 8pt; color: var(--muted); display: block; }
.form .declined { position: absolute; left: 50%; top: 46%; transform: translate(-50%,-50%) rotate(-16deg); border: 5px solid var(--coral-dark); color: var(--coral-dark); font-family: "Fredoka", sans-serif; font-weight: 700; font-size: 30pt; letter-spacing: .08em; padding: 6px 22px; border-radius: 6px; opacity: .9; white-space: nowrap; }
.form .records { border: 2px solid var(--ink); border-radius: 10px; padding: 8px 12px; margin-top: 12px; font-size: 10pt; }
.form .records b { font-family: "Fredoka", sans-serif; display: block; margin-bottom: 2px; }
.acard table { width: 100%; border-collapse: collapse; margin: 6px 0 8px; }
.acard td { font-size: 10pt; padding: 5px 8px; vertical-align: top; border-bottom: 1px solid var(--line); }
.acard td:first-child { width: 2.1in; font-family: "Fredoka", sans-serif; font-weight: 600; }
.acard .star { color: var(--coral-dark); }
.acard .why { font-size: 9.5pt; }
.howtbl td, .howtbl th { font-size: 9.5pt; padding: 4px 8px; vertical-align: top; }
"""
def form_page():
    return """<section class="page form">
  <div class="fhdr"><div><span class="tape"><span>Suspect statement</span></span><div class="case">Mrs. Driscoll's Detective Bureau · Case #1031</div></div><div><span class="stamp" style="font-size:9pt">Official</span></div></div>
  <h1>Suspect Statement</h1>
  <p class="small muted" style="margin-bottom:4px">Answer every question. Print clearly. This will be read by detectives aged nine and ten. They notice everything.</p>
  <div class="two"><div class="q"><label>Name</label><div class="ans"></div></div><div class="q"><label>Job at this school</label><div class="ans"></div></div></div>
  <div class="q"><label>1. Where were you yesterday at 2:15 PM?</label><div class="ans"></div><div class="ans"></div></div>
  <div class="q"><label>2. Who can confirm that?</label><div class="ans"></div></div>
  <div class="two"><div class="q"><label>3. Shoe size <small>(we will check)</small></label><div class="ans"></div></div><div class="q"><label>4. What were you wearing yesterday? <small>Color counts.</small></label><div class="ans"></div></div></div>
  <div class="q"><label>5. Squishies. How do you feel about them?</label><div class="opts"><span class="chk"></span> Love them &nbsp;&nbsp; <span class="chk"></span> Don't get them &nbsp;&nbsp; <span class="chk"></span> What is a squishy?</div><div class="ans"></div></div>
  <div class="q"><label>6. Have you ever been inside Mrs. Driscoll's room?</label><div class="opts"><span class="chk"></span> Yes &nbsp;&nbsp; <span class="chk"></span> No &nbsp;&nbsp; <span class="chk"></span> Define "inside" &nbsp;&nbsp; <span class="blank" style="min-width:2.2in"></span></div></div>
  <div class="q"><label>7. Did you take the Jar?</label><div class="ans"></div></div>
  <div class="q"><label>8. Anything else the detectives should know?</label><div class="ans"></div><div class="ans"></div><div class="ans"></div></div>
  <div class="two"><div class="q"><label>Signature</label><div class="ans"></div></div><div class="q"><label>Date</label><div class="ans"></div></div></div>
  <div class="official"><b>Official use only</b>Cleared by: <span class="chk"></span> Clue 1 footprint &nbsp; <span class="chk"></span> Clue 2 timeline &nbsp; <span class="chk"></span> Clue 3 orange sweater &nbsp; <span class="chk"></span> Clue 4 witness</div>
</section>"""

def answer_key_page():
    rows = ""
    for f in FORMS:
        if f.get("declined"):
            rows += f'<tr><td><strong>{html.escape(f["who"])}</strong></td><td colspan="4">Write DECLINED TO COMMENT across the form yourself, then add "From Bureau records: shoe size 9, in the building at 2:15, blue uniform, loves squishies (seen squeezing one in the boiler room)."</td><td>Nothing. Act shifty on Oct 30.</td></tr>'
        else:
            rows += (f'<tr><td><strong>{html.escape(f["who"])}</strong></td><td>{html.escape(f["q1"])}</td><td>{html.escape(f["q3"])}</td><td>{html.escape(f["q4"])}</td>'
                     f'<td>{html.escape(f["q5"])}</td><td>{html.escape(f["q7"])} / {html.escape(f["q8"])}</td></tr>')
    return f"""<section class="page">
  <span class="eyebrow">Recruiter only · do not post</span>
  <h1>Statement answer key</h1>
  <p class="muted small" style="margin-bottom:8px">Every suspect fills out the same one-page Suspect Statement. Four answers are scripted because the clues test them (Q1 where at 2:15, Q3 shoe size, Q4 what they wore, Q5 squishies); each person's script box lists theirs. The rest of the form is theirs to answer however they like. Collect the forms with the videos by [Oct 23]. Four go on the suspect board; the Chief's stays in the Detective's folder until deliberation (2:28).</p>
  <table class="howtbl"><thead><tr><th>Suspect</th><th>Q1 · At 2:15</th><th>Q3 · Shoe</th><th>Q4 · Wore</th><th>Q5 · Squishies</th><th>Suggested Q7 / Q8</th></tr></thead><tbody>{rows}</tbody></table>
  <table class="howtbl" style="margin-top:12px"><thead><tr><th>Form question</th><th>Clue that tests it</th><th>Who it clears</th></tr></thead><tbody>
    <tr><td>Q3 shoe size</td><td>Clue 1 · Evidence Lab: footprint 26 cm = size 9</td><td>The Librarian (7)</td></tr>
    <tr><td>Q1 where at 2:15</td><td>Clue 2 · Ghostbuster Lab: "seen in hall at 2:15"</td><td>The Principal (in a meeting)</td></tr>
    <tr><td>Q4 what they wore</td><td>Clue 3 · Cipher Room: "snagged my orange sweater"</td><td>The Custodian (blue)</td></tr>
    <tr><td>Q5 squishies</td><td>Clue 4 · Mummy Witness: the thief loves squishies</td><td>The Reading Specialist (doesn't get them)</td></tr>
  </tbody></table>
  <div class="box" style="margin-top:12px"><h4>The deliberation script (2:28)</h4><p class="small" style="margin:0 0 4px">A squad says "everyone's crossed off." The Detective, for the room: "Then your list is too short. Size 9. In the building at 2:15. Orange sweater. Loves squishies. Who else was in this building yesterday?" <em>(Someone says the Chief. The Chief: "I am NOT a suspect.")</em></p>
  <p class="small" style="margin:0">"Chief, you filled out a statement form like everyone else. For completeness. I have it right here." <em>(Pin it beside the other four. Read it aloud, including the crossed-out "Don't be ridiculous.")</em> "Detectives, check it against your clues. Then write your warrants."</p></div>
</section>"""

forms_html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Suspect Statement Form</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../print.css">
<style>{FORM_CSS}</style>
</head>
<body>
<div class="toolbar"><b>📝 Suspect statement form</b><span class="muted">1 page · the same form for every suspect. Print five.</span><span class="grow"></span><a href="../../events/halloween.html#downloads">← Back to the plan</a><a href="../../downloads/halloween/suspect-statement-forms.pdf" download>⬇ PDF</a><button class="primary" onclick="window.print()">🖨 Print</button></div>
{form_page()}
</body>
</html>
"""
(SRC / "suspect-statement-forms.html").write_text(forms_html)
print("generated suspect-statement-forms.html")

SCRIPT_CSS = ".script p { font-size: 10pt; margin: 0 0 .35em; } .script .dir { font-size: 9pt; } .adj { background: rgba(255,217,61,.45); border-radius: 3px; padding: 0 2px; } .yours { font-size: 8pt; margin: 0 0 8px; padding: 6px 12px; line-height: 1.3; } .footer-note.static { position: static; margin-top: 10px; } .ask { font-size: 8.5pt; line-height: 1.35; } .yours h4 { font-size: 10pt; margin-bottom: 4px; } .yours ul { margin: 0; padding-left: 1.1em; } .yours li { margin-bottom: 2px; } .yours .legend { margin: 4px 0 0; font-weight: 800; } .script .card { margin-bottom: 8px; }"
def shell(title, toolbar_label, toolbar_note, pdf_name, body):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../print.css">
<style>{SCRIPT_CSS}{FORM_CSS}</style>
</head>
<body>
<div class="toolbar"><b>{toolbar_label}</b><span class="muted">{toolbar_note}</span><span class="grow"></span><a href="../../events/halloween.html#downloads">← Back to the plan</a><a href="../../downloads/halloween/{pdf_name}.pdf" download>⬇ PDF</a><button class="primary" onclick="window.print()">🖨 Print</button></div>
{body}
</body>
</html>
"""

# the recruiter's pack: guide, answer key, four scripts, the blank form
vs = shell("Video Scripts · The recruiter's pack", "🎥 Video scripts (recruiter's pack)",
           "the recording guide, the statement answer key, all four scripts, and the one-page statement form",
           "video-scripts", guide + "\n" + answer_key_page() + "\n" + "\n".join(parts) + "\n" + form_page())
(SRC / "video-scripts.html").write_text(vs)
print("generated video-scripts.html")

# one file per suspect: guide, that person's script (its box lists their form answers), the blank form
SOLO = [("ivs1", "script-principal", "The Principal"), ("ivs3", "script-reading-specialist", "The Reading Specialist"),
        ("ivs4", "script-librarian", "The Librarian"), ("ivs5", "script-chief", "The Chief (teacher)")]
for (id_, when, note), (id2, fname, who) in zip(scripts, SOLO):
    assert id_ == id2
    part = parts[[x[0] for x in scripts].index(id_)]
    solo = shell(f"Video Script · {who}", f"🎥 {who}",
                 "the recording guide, this person's script, and the one-page statement form. Send just this file.",
                 fname, guide + "\n" + part + "\n" + form_page())
    (SRC / f"{fname}.html").write_text(solo)
    print("generated", fname + ".html")

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
