# Belief-updating pilot: setup guide

Two task versions (trust in colleagues, health-practice claims), one survey page, one Google Sheet in your Drive, one admin dashboard.

**Files**
- `index.html` : the survey (GitHub Pages). Edit the `CONFIG` block at the top.
- `Code.gs` : Google Apps Script backend. Writes to your Sheet. Serves data only to the admin key.
- `admin.html` : dashboard (GitHub Pages). Asks for the script URL and your key at runtime.
- `simulate.py` : design simulation (power, false-positive rate, effect of noisy weight ratings).
- `PREREG_DRAFT.md` : pre-registration skeleton to complete before collecting data.

## 1. Backend (15 minutes)
1. Create a new Google Sheet in your Drive. Name it "Belief pilot data".
2. Extensions > Apps Script. Delete the default code. Paste in `Code.gs`. Save.
3. Run `setup` once (select it in the function dropdown, click Run). Approve the permissions. This creates the tabs `participants`, `trials`, `pid_map`.
4. Project Settings (gear icon) > Script properties > Add property: `ADMIN_KEY` = a long random string. Keep it private. Do not put it in the repo.
5. Deploy > New deployment > type Web app. Execute as: **Me**. Who has access: **Anyone**. Copy the Web app URL.
6. Test: open `<URL>?action=ping` in a browser. You should see `{"ok":true,...}`.

## 2. Frontend
1. In `index.html` set `SCRIPT_URL` (the Web app URL), `CONTACT_EMAIL` (shown to participants, so use an address you are happy to publish), `NETWORK_COMPLETION_CODE`, and later `PROLIFIC_COMPLETION_URL`.
2. In `admin.html` set `SCRIPT_URL` to the same URL.
3. Put `index.html` and `admin.html` in a GitHub repo and enable Pages. The admin page is public, but it shows nothing without the key.
4. Open the survey on your phone and laptop and complete it yourself once per task (`?task=trust` and `?task=health`). Check that rows appear in the Sheet and the dashboard shows you.

**Important:** I tested everything against a mock of the Apps Script backend, not a live Google deployment. Do step 4 before you recruit anyone. If a row is missing or a column looks wrong, tell me what you see.

## 3. Recruitment
- **Prolific:** create the study with the survey URL. Prolific appends `PROLIFIC_PID`, `STUDY_ID` and `SESSION_ID` automatically. Paste the study's completion URL into `PROLIFIC_COMPLETION_URL`. The Prolific ID is stored only in the `pid_map` tab, never in analysis data or the dashboard.
- **Network:** share `index.html?ref=anything`. Participants get a completion code at the end.
- **Balancing:** the page asks the backend which task has fewer participants and assigns that one. Add `?task=trust` or `?task=health` to force a version.
- **Sample:** 40 analysable participants per task (80 total). Recruit about 15% extra for exclusions. Check Prolific's current minimum pay and fees. Roughly 12 minutes of participation at a fair hourly rate comes to about £150 to £200 in total.

## 4. Timeline to the 10 November deadline
| Dates | Step |
|---|---|
| 18 to 20 Oct | Deploy, self-test, fix anything that breaks |
| 21 to 22 Oct | Soft test with 5 to 8 friends. Check the dashboard. Complete and post the pre-registration (before any real data) |
| 23 Oct to 1 Nov | Collect. Watch the dashboard daily. Top up Prolific if exclusions run high |
| 2 to 5 Nov | Analyse. Export CSVs for any offline modelling. Write one honest paragraph for the SOP |
| 6 to 9 Nov | Final SOP edits. Submit with a buffer |

## 5. Ethics and data
- No names, emails or free text are collected. Participants are told the people and practices are fictional. The debrief repeats this and states that no further reports were available.
- This is minimal-risk, but it has had no formal ethics review. In the application, call it an informal pilot. If you want to publish it, you will need review through an institution.
- Do not share the Sheet. The `pid_map` tab links Prolific IDs to random IDs.

## 6. How to read the dashboard
- **Section 2** asks whether the paradigm works: does source credibility move the weight rating, and is the weight rating more than a restatement of the update?
- **Section 3** is the main test: after the total remaining gap is accounted for, does the discounted part of the earlier gap predict how much people revise later?
- **Section 4** shows the pass/fail criteria stated in advance. If criterion 1 or 2 fails, the split cannot be measured with this design. That is a finding about the paradigm.
- With about 80 participants this is a pilot. Report effect sizes and intervals, not "significant" or "not significant".

## 7. What the simulation says (`python3 simulate.py`)
Power to detect the split effect with 80 participants (both tasks pooled), assuming the model in the dashboard is correct:

| True effect | Weight-rating noise 0 | noise 0.10 | noise 0.20 |
|---|---|---|---|
| 0 (false-positive rate) | 6% | 2% | 6% |
| 0.10 | 86% | 61% | 31% |
| 0.20 | 100% | 99% | 81% |

The effect sizes are arbitrary units, not estimates from the literature. The result mainly shows that noisy self-reported weights can cut power sharply, so a small true effect is unlikely to show up in a sample of 80.
