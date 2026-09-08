# Analysis Log — Customer Churn, Payment Method & Age

Append-only. Entries are never edited after the next one is written; corrections
go in a new entry with a `Supersedes:` line. The log is the audit trail — a
tidied log is a worthless one.

**Dataset:** telecom subscription, n = 7,043
**Analyst:** Adejori Eniola
**Repo:** github.com/aDataMage/[repo]

---

## Conventions

| Field | Rule |
|---|---|
| **Prediction** | Written *before* running. If absent, say so explicitly — `[none: exploratory]`. |
| **Result** | Rates with numerator and denominator. Never a bare percentage. |
| **Verdict** | One of: `SUPPORTED` · `KILLED — evidence` · `KILLED — underpowered` · `UNRESOLVED` |
| **Rules out** | What this entry closes off. The point of the log. |
| **Constraints** | Cell counts, intervals, design limits. What the entry cannot support. |
| **Next test** | Mandatory. An entry without one is abandoned, not closed. |

Effect sizes: report **pp** (absolute) for anything that sizes a decision, and
the **ratio** alongside it for mechanism. Never a ratio without its base rate.

Causal language: `linking` prose only where a mechanism is established.
Everything in this log is observational — default to `anchoring`.

---

## E-001 · Age effect within contract type

**Question:** Does the age→churn effect hold once contract type is held fixed?

**Prediction:** Age effect attenuates but persists.

**Method:** Stratified churn rates by age band within each contract level;
compared `churn ~ age + contract` against `churn ~ age * contract`.

**Result:** The additive model reports a single age slope that describes no
observed subgroup. Stratified, the age gap is large within month-to-month and
near-zero within two-year contracts.

**Verdict:** `SUPPORTED` — interaction, not a uniform effect.

**Rules out:** Reporting one adjusted age coefficient. No single number exists;
any figure produced is an artefact of the sample's contract mix.

**Note:** Contract is structurally barred from confounding age — nothing sold
changes a customer's age. Temporal order settles this before any test is run.

**Next test:** → E-002

---

## E-002 · Tenure as confounder of the senior effect

**Question:** Conditioning on month-to-month partly conditions on short tenure.
Are seniors on month-to-month also newer, making the age effect tenure in
costume?

**Prediction:** If tenure explains it, seniors concentrate at low tenure.

**Result:** Seniors on month-to-month average **21.1 months** vs **16.7** for
under-65s. Direction is opposite to what the confounding story requires.

**Verdict:** `KILLED — evidence`. Negative confounding: tenure suppresses the
senior effect rather than manufacturing it. Adjusting should *widen* the gap.

**Rules out:** "It's just tenure" as an explanation of the senior gap.

**Constraints:** Two means only. Not yet checked for bimodality — a short-tenure
senior cluster with a long-tenure tail would produce this mean and still drive
the churn. Medians and IQR outstanding.

**Next test:** tenure distribution by age band within month-to-month (median,
IQR, histogram); then `churn ~ senior + tenure` within month-to-month, expecting
the senior coefficient to grow.

---

## E-003 · Payment method as mechanism for the senior effect

**Question:** Does payment method explain elevated senior churn on
month-to-month?

**Prediction (pre-registered):** Mailed check highest, then credit card, then
bank withdrawal — effort-based mechanism, manual payment as a monthly
opportunity to reconsider.

**Result — month-to-month:**

| Method | Senior | Non-senior | Gap |
|---|---|---|---|
| Bank Withdrawal | 350/426 = 82.2% | 845/1,814 = 46.6% | **+35.6pp** (1.76×) |
| Credit Card | 78/98 = 79.6% | 252/1,038 = 24.3% | **+55.3pp** (3.28×) |
| Mailed Check | 13/18 = 72.2% | 117/216 = 54.2% | +18.0pp — unreadable |

**Verdict:** `KILLED — evidence`, on two counts.

1. **Predicted ordering absent.** Among non-seniors the order is mailed check >
   bank withdrawal > credit card, not the effort ordering. Among seniors mailed
   check is *lowest* of the three.
2. **Payment cannot be the mechanism.** Seniors run 72–82% across all three
   methods. For payment to explain the age effect there would have to be a
   method where senior churn is low. There isn't one.

**Rules out:** Payment method as the route through which age acts. The
interaction widened under stratification rather than dissolving.

**Constraints:** Every senior mailed-check cell is n ≤ 18. Two-year senior
mailed check is 0/8 — 95% interval roughly 0–37%. No mailed-check claim,
including "mailed check interacts with contract," is testable in this data.

**Next test:** → E-004

---

## E-004 · The credit-card advantage and where it stops

**Question:** The card advantage is large among non-seniors and absent among
seniors. Is it specific to month-to-month, or a main effect of payment method?

**Result — bank withdrawal vs credit card, by contract and age:**

| Contract | Non-senior BW | Non-senior CC | Senior BW | Senior CC |
|---|---|---|---|---|
| Month-to-month | 46.6% | 24.3% | 82.2% | 79.6% |
| One-year | 85/610 = 13.9% | 40/598 = 6.7% | 17/187 = 9.1% | 12/73 = 16.4% |
| Two-year | 29/658 = 4.4% | 13/831 = 1.6% | 3/214 = 1.4% | 3/111 = 2.7% |

**Reading:** Non-seniors get roughly a **2× reduction** from card at every
contract length — a main effect, not month-to-month-specific. Seniors get
nothing at any contract length, and in the two thin cells it slightly reverses.

**Verdict:** `UNRESOLVED — direction consistent across three cells.`

**Reframe:** This is likely not two findings. Whatever protective factor
card-on-file *marks*, seniors appear not to have it. Single claim, testable.

**Constraints:** Senior one-year card n=73 (12 churners); senior two-year card
n=111 (3 churners). Neither supports a claim alone. What supports it is that
three independent cells point the same way. State it as direction consistency —
never quote the reversal as a finding.

**Standing caveat — carry into every downstream artefact:**
Card-on-file is not randomly assigned. Customers who set up automatic card
payment differ in intent to stay, financial habits and digital comfort — none
of which the dataset holds. The card plausibly **marks** low-churn customers
rather than **making** them. This rules out "move customers to autopay" as a
recommendation, which is the standard and probably wrong reading of this result.

**Next test:** characterise the senior card population against the non-senior
card population on every other observable — tenure, service mix, offer type,
referrals, monthly charge, support contacts. If they differ systematically, the
difference is the candidate mechanism. If they don't, selection on unobservables
is the remaining explanation and the finding stays descriptive.

## E-005 · Internet speed and location

**Question:** Should retention treat low-speed customers as a distinct
risk segment, or is speed only marking where they live?

**Hypothesis:** Slower connections raise churn because the service
fails at its core job often enough to accumulate into a switching
decision. Location shapes which speeds are available but does not
otherwise act on churn.

**Rival:** Location acts through channels other than speed — local
competitor presence, urban/rural demographics, regional pricing —
and slow areas happen to be areas with those characteristics. Speed
is a marker, not a cause.

**Discriminating prediction:**
Within a location, customers on slower tiers churn more than
customers on faster tiers, and the within-location gap is of similar
size to the crude gap.
- If the within-location gap collapses toward zero → rival supported,
  location confounds.
- If the gap varies systematically by location type → moderation, not
  a uniform speed effect.
- Direction check: the crude gap must be negative (faster = less
  churn). If it is positive, the framing is wrong before any of the
  above applies.

**Abandonment condition:** within-location gap under ~3pp with
adequate cell counts kills speed as a driver outright.

**Run:** [notebook §]
---

## Open question carried forward

If card-on-file is a **marker** rather than a **cause**, a retention team cannot
act by moving customers onto it — that intervention changes the marker without
changing what it marks. The usable form of a marker is targeting, not treatment:
it identifies who to route where. Whether that justifies an intervention depends
on what the senior card population turns out to lack. Unanswered until E-005.

---

## Hypotheses killed

Kept visible deliberately. A log containing only survivors is a reconstruction.

| ID | Hypothesis | Cause of death |
|---|---|---|
| E-002 | Senior effect is tenure in disguise | Evidence — bias runs the wrong way |
| E-003 | Effort-based payment ordering | Evidence — predicted ordering absent |
| E-003 | Payment method as mechanism for age | Evidence — no low-churn senior method |
| E-003 | Mailed check × contract interaction | Underpowered — n ≤ 18 in every senior cell |