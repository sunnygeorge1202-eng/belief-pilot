# Pre-registration draft (complete and post on OSF before collecting data)

**Title:** Does the way earlier contradictory evidence was left unresolved predict later revision? A pilot.

**Status:** Pilot, feasibility and estimation. Not confirmatory. No formal ethics review (see README).

## Design
- Participants rate 4 fictional targets (colleagues or health practices, by assigned task). Each target: 3 supportive reports, 1 contradictory report (source credibility high or low), 1 further contradictory report (medium credibility).
- Credibility is within-person: two high, two low, block-randomised across positions.
- Measures per report: belief (0 to 100), confidence. After contradictory reports: weight rating (how much should this report count). After the first: choice to see another report. After the second: behavioural readout.

## Sample
Target 40 analysable participants per task. Stopping rule: stop when the target is reached or on [DATE], whichever comes first. Recruitment via Prolific and personal network.

## Exclusions (applied before looking at the main test)
Not completed; failed attention check; failed comprehension check after two attempts; completion time under 40% of the median; belief SD under 3 across all ratings. Target rows excluded from the main test when the gap before either contradictory report is under 10 points.

## Hypotheses
- **H1 (manipulation).** High-credibility sources receive higher weight ratings than low-credibility sources (difference at least 15 points, dz at least 0.5).
- **H2 (separability).** The weight rating is not redundant with the update (|r| with the proportion of gap revised below 0.8).
- **H3 (unresolved-state split).** For the same remaining gap at the second contradictory report, the discounted part of the earlier gap, (1 - weight) x gap, predicts revision at the second report beyond: earlier revision, source credibility, and confidence.
  - Predicted direction: **[DECIDE AND WRITE THIS BEFORE COLLECTING DATA, with a one-line reason]**.
- **Not predicted:** any difference between the trust and health tasks (exploratory).

## Analysis
OLS of revision at the second report on z-scored predictors, standard errors clustered by participant. Models M0 to M3 as in the dashboard. Out-of-sample comparison by leave-one-participant-out RMSE. Within-participant version as a robustness check. Report estimates and 95% intervals. No claim of significance is made from this sample.

## Interpretation rules
- H1 or H2 not met: the paradigm cannot separate weighting from updating, and H3 is not interpreted.
- H3: a negative or positive interval excluding 0 and a lower cross-validated RMSE than M1 would be reported as preliminary support. An interval including 0 and no RMSE gain would be reported as no evidence for the split in this paradigm.
- Rival accounts not tested here: volatility/history models (HGF), cognitive dissonance, motivated reasoning. These need offline modelling or other designs.
