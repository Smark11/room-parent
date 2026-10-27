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
  <div class="box soft" style="margin-top:4px"><h4>Making the script yours</h4><p class="small" style="margin:0">Words in <span style="background:rgba(255,217,61,.45);padding:0 3px;border-radius:3px">[brackets]</span> are adjustable. The facts the kids check (shoe size, where you were, what you wore, how you feel about squishies) live on your <strong>Suspect Statement form</strong>, not in this video; your answer card tells you what to write there. The box at the top of your script lists the one or two things the video has to agree with, and the lines you should keep word for word. Everything else is flavor. Swap in your real life, your real subject, your real habits. Wear whatever you like. True details get the biggest laughs.</p></div>
  <h3 style="margin-top:10px;font-size:12pt">The ask (email or text to each suspect)</h3>
  <div class="box soft ask" style="white-space:pre-wrap">''' + html.escape(ask or "") + '''</div>
  <p class="small muted">The Custodian gets a different ask: "You're a suspect who declined to comment. That's it. That's the whole job. Please act shifty in the hallway on Oct 30."</p>
</section>'''

# ---------- 1b. suspect statement forms ----------
# One questionnaire per suspect. Four answers are scripted (they are the four traits the clues test);
# the rest are suggestions. The Custodian's is pre-stamped. The Chief's stays hidden until deliberation.
FORMS = [
  dict(key="principal", who="The Principal", form="S-1",
       q1="In a meeting. A meeting about the next meeting.", q2="Everyone at the meeting. All nine of them.",
       q3="10", q4="An orange sweater. School spirit.", q5="Tick LOVE THEM. Explain: “I own ONE. It’s a cat. It’s for stress.”",
       q6="Tick DEFINE “INSIDE.”", q7="No. Absolutely not. No.", q8="I did not say squishies.",
       note="Your meeting alibi is what clears you (Clue 2, the timeline). Everything else keeps you looking guilty, which is the job."),
  dict(key="gym-teacher", who="The Gym Teacher", form="S-2",
       q1="The gym. Where I always am.", q2="The dodgeballs.",
       q3="10", q4="Orange. It’s a school color. Half the building wears orange.", q5="Tick DON’T GET THEM. Explain: “You squeeze it. It goes back. That’s it.”",
       q6="Tick YES. Add: “To return a kickball. Once.”", q7="No. If I wanted to steal something, I’d steal a good jump rope.", q8="I just don’t understand the obsession these days.",
       note="Not getting squishies is what clears you (Clue 4, the witness). Don’t soften it."),
  dict(key="librarian", who="The Librarian", form="S-3",
       q1="Shelving. Alone. In the back. 2:00 to 2:30, every day.", q2="No witnesses. That sounded worse than I meant it to.",
       q3="7", q4="My orange cardigan.", q5="Tick LOVE THEM. Explain: “One on every cart. Shelving is stressful.”",
       q6="Tick YES. Add: “Overdue books.”", q7="No. If I had, they would be alphabetized by now.", q8="Whoever took them... check their feet.",
       note="Your shoe size is what clears you (Clue 1, the footprint is a 10). Write 7 whatever your real size is."),
  dict(key="custodian", who="The Custodian", form="S-4", declined=True,
       note="Nothing to fill in. The form is pre-stamped DECLINED TO COMMENT and the Bureau’s own records are printed on it. Sign the bottom if you like. On Oct 30, act shifty in the hallway."),
  dict(key="chief", who="The Chief (Mrs. Driscoll)", form="S-5",
       q1="In my classroom. Teaching. I live here, basically.", q2="Twenty children.",
       q3="10", q4="An orange sweater. It’s festive.", q5="Write “Don’t be ridiculous,” cross it out with ONE line so it can still be read, then tick LOVE THEM and write “Fine. Love them.”",
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
def form_page(f):
    who = html.escape(f["who"])
    declined = f.get("declined")
    official = ('<div class="records"><b>From Bureau records (suspect declined to comment)</b>'
                'Shoe size: <strong>10</strong> (boot closet). &nbsp; At 2:15: <strong>in the building</strong> (sign-in log). &nbsp; '
                'Wearing: <strong>blue</strong> uniform, every day. &nbsp; Squishies: <strong>loves them</strong> (seen squeezing one in the boiler room).</div>'
                if declined else
                '<div class="official"><b>Official use only</b>Cleared by: <span class="chk"></span> Clue 1 footprint &nbsp; <span class="chk"></span> Clue 2 timeline &nbsp; <span class="chk"></span> Clue 3 orange sweater &nbsp; <span class="chk"></span> Clue 4 witness</div>')
    return f"""<section class="page form">
  {'<div class="declined">Declined to comment</div>' if declined else ''}
  <div class="fhdr"><div><span class="tape"><span>Suspect statement</span></span><div class="case">Mrs. Driscoll's Detective Bureau · Case #1031 · Form {f['form']}</div></div><div><span class="stamp" style="font-size:9pt">Official</span></div></div>
  <h1>Suspect Statement</h1>
  <p class="small muted" style="margin-bottom:4px">Answer every question. Print clearly. This will be read by detectives aged nine and ten. They notice everything.</p>
  <div class="two"><div class="q"><label>Name</label><div class="ans"></div></div><div class="q"><label>Job at this school</label><div class="ans filled">{who}</div></div></div>
  <div class="q"><label>1. Where were you yesterday at 2:15 PM?</label><div class="ans"></div><div class="ans"></div></div>
  <div class="q"><label>2. Who can confirm that?</label><div class="ans"></div></div>
  <div class="two"><div class="q"><label>3. Shoe size <small>(we will check)</small></label><div class="ans"></div></div><div class="q"><label>4. What were you wearing yesterday? <small>Color counts.</small></label><div class="ans"></div></div></div>
  <div class="q"><label>5. Squishies. How do you feel about them?</label><div class="opts"><span class="chk"></span> Love them &nbsp;&nbsp; <span class="chk"></span> Don't get them &nbsp;&nbsp; <span class="chk"></span> What is a squishy?</div><div class="ans"></div></div>
  <div class="q"><label>6. Have you ever been inside Mrs. Driscoll's room?</label><div class="opts"><span class="chk"></span> Yes &nbsp;&nbsp; <span class="chk"></span> No &nbsp;&nbsp; <span class="chk"></span> Define "inside" &nbsp;&nbsp; <span class="blank" style="min-width:2.2in"></span></div></div>
  <div class="q"><label>7. Did you take the Jar?</label><div class="ans"></div></div>
  <div class="q"><label>8. Anything else the detectives should know?</label><div class="ans"></div><div class="ans"></div><div class="ans"></div></div>
  <div class="two"><div class="q"><label>Signature</label><div class="ans"></div></div><div class="q"><label>Date</label><div class="ans"></div></div></div>
  {official}
</section>"""

def answer_card(f):
    who = html.escape(f["who"])
    if f.get("declined"):
        body = f'<p>{html.escape(f["note"])}</p>'
    else:
        rows = [("1. Where were you at 2:15?", f["q1"], True), ("2. Who can confirm that?", f["q2"], False),
                ("3. Shoe size", f["q3"], True), ("4. What were you wearing?", f["q4"], True),
                ("5. Squishies?", f["q5"], True), ("6. Inside Mrs. Driscoll's room?", f["q6"], False),
                ("7. Did you take the Jar?", f["q7"], False), ("8. Anything else?", f["q8"], False)]
        tr = "".join(f'<tr><td>{"<span class=star>★</span> " if st else ""}{html.escape(q)}</td><td>{html.escape(a)}</td></tr>' for q, a, st in rows)
        body = (f'<p class="small">Fill out the attached form in your own handwriting. The four answers marked <span class="star">★</span> are scripted, because the detectives check them against printed evidence: copy those exactly. '
                f'The rest are suggestions; write anything you like, and true is funnier. Hand the form back to whoever sent you this by [Oct 23], with your video.</p>'
                f'<table>{tr}</table><p class="why"><strong>Why these answers:</strong> {html.escape(f["note"])}</p>')
    return f"""<section class="page acard">
  <span class="eyebrow grape">Answer card · {who}</span>
  <h1 style="font-size:20pt;margin:4px 0 6px">Your Suspect Statement: what to write</h1>
  {body}
  <div class="footer-note static"><span>The Case of the Missing Candy · Answer card · {who}</span><span>Keep this card. Hand in the form.</span></div>
</section>"""

forms_guide = """<section class="page">
  <span class="eyebrow">Ties the clues to the suspects</span>
  <h1>Suspect statement forms</h1>
  <p class="muted small" style="margin-bottom:8px">A one-page questionnaire each suspect fills in by hand. Four of its answers are the four traits the clues test, and we script those; everything else is theirs. The kids compare each clue to the forms, so no real person has to wear, own, or be anything.</p>
  <div class="two">
    <div class="box soft"><h4>Who fills one out</h4><ul class="small" style="margin:0">
      <li><strong>The Principal, the Gym Teacher, the Librarian:</strong> send each their script, their answer card, and a blank form together. Forms come back with the videos by [Oct 23].</li>
      <li><strong>The Custodian:</strong> nothing to do. The form is pre-stamped DECLINED TO COMMENT with the Bureau's "records" printed on it.</li>
      <li><strong>The Chief (teacher):</strong> fills one out too, from her answer card. It matches every clue. It stays in the Detective's folder until deliberation.</li></ul></div>
    <div class="box soft"><h4>Where they go on the day</h4><ul class="small" style="margin:0">
      <li>Four forms (not the Chief's) go on the suspect board beside the WANTED posters, from 1:30. Squads can walk over and read them any time.</li>
      <li>The typed summary of the same four forms is the suspect table in every case file, so squads can cross off at their station without leaving it.</li>
      <li>At 2:28, when a squad has crossed off all four, the Detective produces the fifth form. See below.</li></ul></div>
  </div>
  <table class="howtbl" style="margin:4px 0 10px"><thead><tr><th>Form question</th><th>Clue that tests it</th><th>Answer that gets someone cleared</th></tr></thead><tbody>
    <tr><td>3. Shoe size</td><td>Clue 1 · Evidence Lab: footprint = 27 cm = size 10</td><td>The Librarian wrote 7</td></tr>
    <tr><td>1. Where at 2:15?</td><td>Clue 2 · Ghostbuster Lab: "seen in hall at 2:15"</td><td>The Principal wrote "in a meeting"</td></tr>
    <tr><td>4. What were you wearing?</td><td>Clue 3 · Cipher Room: "snagged my orange sweater"</td><td>The Custodian's records say blue</td></tr>
    <tr><td>5. Squishies?</td><td>Clue 4 · Mummy Witness: the thief loves squishies</td><td>The Gym Teacher ticked "don't get them"</td></tr>
  </tbody></table>
  <div class="box"><h4>The deliberation script (2:28)</h4><p class="small" style="margin:0 0 4px">A squad says: "Everyone's crossed off." The Detective, loud enough for the room:</p>
  <p class="small" style="margin:0 0 4px">"Then your list is too short. Four clues, four facts about the thief. Size 10. In the building at 2:15. Orange sweater. Loves squishies. Who else was in this building yesterday?" <em>(Let them guess. Someone will say the Chief. The Chief: "I am NOT a suspect.")</em></p>
  <p class="small" style="margin:0 0 4px">"Chief, you filled out a statement form like everyone else. For completeness. I have it right here." <em>(Pin it to the board next to the other four. Read it aloud, including the crossed-out "Don't be ridiculous.")</em> "Detectives, check it against your clues. Then write your warrants."</p>
  <p class="small muted" style="margin:0">Optional tell for the sharp ones: the Chief wears something orange all party (a scarf from the bin is fine), and keeps one squishy on her desk, "confiscated."</p></div>
</section>"""

forms_parts = []
for f in FORMS:
    forms_parts.append(answer_card(f) + "\n" + form_page(f))
forms_section = forms_guide + "\n" + "\n".join(forms_parts)

forms_html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Suspect Statement Forms</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../print.css">
<style>{FORM_CSS} .footer-note.static {{ position: static; margin-top: 12px; }}</style>
</head>
<body>
<div class="toolbar"><b>📝 Suspect statement forms</b><span class="muted">11 pages · the guide, then an answer card and a blank form for each of the five suspects</span><span class="grow"></span><a href="../../events/halloween.html#downloads">← Back to the plan</a><a href="../../downloads/halloween/suspect-statement-forms.pdf" download>⬇ PDF</a><button class="primary" onclick="window.print()">🖨 Print</button></div>
{forms_section}
</body>
</html>
"""
(SRC / "suspect-statement-forms.html").write_text(forms_html)
print("generated suspect-statement-forms.html")

SCRIPT_CSS = ".script p { font-size: 10.5pt; margin: 0 0 .4em; } .script .dir { font-size: 9.5pt; } .adj { background: rgba(255,217,61,.45); border-radius: 3px; padding: 0 2px; } .yours { font-size: 8.5pt; margin: 0 0 8px; padding: 7px 12px; line-height: 1.35; } .footer-note.static { position: static; margin-top: 12px; } .ask { font-size: 9pt; line-height: 1.4; } .yours h4 { font-size: 10pt; margin-bottom: 4px; } .yours ul { margin: 0; padding-left: 1.1em; } .yours li { margin-bottom: 2px; } .yours .legend { margin: 4px 0 0; font-weight: 800; } .script .card { margin-bottom: 8px; }"
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

# the recruiter's pack: guide, four scripts, then the forms guide and every answer card + form
vs = shell("Video Scripts and Statement Forms · The recruiter's pack", "🎥 Video scripts + statement forms",
           "the recording guide, all four scripts, then the statement-form guide and an answer card + form for each of the five suspects",
           "video-scripts", guide + "\n" + "\n".join(parts) + "\n" + forms_section)
(SRC / "video-scripts.html").write_text(vs)
print("generated video-scripts.html")

# one file per suspect: guide, that person's script, their answer card, their blank form
SOLO = [("ivs1", "script-principal", "The Principal", "principal"), ("ivs3", "script-gym-teacher", "The Gym Teacher", "gym-teacher"),
        ("ivs4", "script-librarian", "The Librarian", "librarian"), ("ivs5", "script-chief", "The Chief (teacher)", "chief")]
for (id_, when, note), (id2, fname, who, fkey) in zip(scripts, SOLO):
    assert id_ == id2
    part = parts[[x[0] for x in scripts].index(id_)]
    f = next(x for x in FORMS if x["key"] == fkey)
    solo = shell(f"Video Script and Statement Form · {who}", f"🎥 {who}",
                 "the recording guide, this person's script, their answer card, and a blank statement form. Send just this file.",
                 fname, guide + "\n" + part + "\n" + answer_card(f) + "\n" + form_page(f))
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
