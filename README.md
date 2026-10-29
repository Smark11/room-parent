# Room Parent HQ

A small static site for a 4th-grade room parent: a home page, an events hub with one page
per class party, a toolkit of field-trip checklists, sign-up templates, and message templates,
and a set of print-ready PDF handouts.

Live site: https://smark11.github.io/room-parent/

## Pages

- `index.html` — home: what a room parent does, key dates, countdown to the next event
- `events/index.html` — events hub
- `events/halloween.html` — **The Case of the Missing Candy**, the fully built Halloween whodunit:
  research, eleven concepts, story, how the deduction works, four suspects, four video scripts,
  run of show, four stations, finale, snacks, decor, inclusion, crew, budget, downloads, printables,
  checklist, backup plans
- `events/secret-agent.html` — **Operation: Fourth Grade**, the Secret Agent Academy party
- `resources.html` — field-trip chaperone guide, sign-up templates, message templates
- `party.html` — redirect to the secret-agent page (old link)

## Printables

`printables/halloween/*.html` are print-designed pages (US Letter) that share `printables/print.css`.
`downloads/halloween/*.pdf` are rendered from them, plus `all-printables.zip`.

To rebuild after editing (needs Google Chrome installed):

    python3 printables/build.py

The script also regenerates `printables/halloween/video-scripts.html`, the four `script-*.html`
files, and `suspect-statement-forms.html; `evidence-chart.html` is the one-page clue-by-suspect matrix; `jar-sign.html` is the candy-jar label with lid seals (the plain label was removed from `signs-and-labels.html`)` from the scripts on `events/halloween.html` and the
`FORMS` table at the top of `build.py`. Edit scripts on the page and suspect answers in `FORMS`.

## Personalize it

Open `assets/site.js` and edit the `CONFIG` block at the top (teacher name, school, class name,
student count, party date, your name, contact email). Every page updates automatically.
Printables carry their own text; edit the HTML in `printables/halloween/` and rebuild.

## Interactive bits

- Station rotation timer with a bell (put it on the projector)
- Pigpen cipher renderer (`assets/pigpen.js`) and a Caesar cipher tool
- Budget table that recalculates as you uncheck items
- Planning checklists that remember your progress in the browser
- Copy buttons on every template
- Light/dark mode toggle, print styles

No build step for the site itself. Open `index.html` in a browser or push to GitHub Pages.
