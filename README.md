# Room Parent HQ

A small static site for a 4th-grade room parent: a home page, a fully built-out
secret-agent class party plan, and a toolkit of field-trip checklists, sign-up
templates, and message templates.

Live site: https://smark11.github.io/room-parent/

## Pages

- `index.html` — home: what a room parent does, key dates, countdown to the next party
- `party.html` — **Operation: Fourth Grade**, a Secret Agent Academy party: run of show,
  six stations, vault finale, snacks, decor, awards, volunteer roles, budget,
  printables, planning checklist, backup plans, and other themes
- `resources.html` — field-trip chaperone guide, sign-up templates, message templates

## Personalize it

Open `assets/site.js` and edit the `CONFIG` block at the top (teacher name, school,
class name, party date, your name, contact email). Every page updates automatically.

Key dates on the home page and the template text on the resources page are plain HTML;
edit them directly.

## Interactive bits

- Station rotation timer with a bell (party page, put it on the projector)
- Caesar cipher encoder/decoder for making the Code Breakers puzzles
- Budget table that recalculates as you uncheck items
- Planning checklists that remember your progress in the browser
- Copy buttons on every template
- Light/dark mode toggle, print styles for the party plan

No build step. Open `index.html` in a browser or push to GitHub Pages.
