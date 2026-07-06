# Security Login Analytics Investigation

Senior Data Analyst assignment package for investigating suspicious authentication behavior and a product KPI spike.

## What is included

- `presentation/security_login_analytics_investigation.pptx` - final PowerPoint deck
- `presentation/security_login_analytics_investigation.pdf` - PDF export of the deck
- `presentation/security_login_analytics_investigation_short.pptx` - short interview-ready version with the key findings and design decisions
- `notebooks/security_login_analytics_investigation.ipynb` - notebook entry point
- `notebooks/security_login_analytics_investigation.py` - cleaned, reproducible analysis script
- `notebooks/original_colab_export.py` - original Colab-exported notebook script
- `docs/task_explanation.md` - assignment prompt and expected deliverables
- `data/README.md` - data setup instructions

## Assignment objective

The assignment evaluates the ability to analyze login activity, identify suspicious authentication patterns, explain business/security impact, and design dashboards for both security and product analytics.

The work covers two cases:

1. Login attempts database
   - Identify at least five suspicious login anomalies.
   - Explain why each case is a red flag.
   - Support findings with notebook-generated visualizations.
   - Recommend additional data fields and suspicious patterns to monitor.

2. Surge in new customer accounts
   - Investigate possible drivers of a new-signup spike.
   - Design a KPI dashboard to monitor acquisition quality and business impact.

## Analytical approach

The analysis uses an interpretable, baseline-first workflow:

1. Understand the business risk.
2. Inspect data quality.
3. Establish normal login behavior.
4. Engineer behavioral features.
5. Investigate anomalies with evidence, alternatives, confidence, and uncertainty.
6. Translate findings into dashboard and production architecture recommendations.

This approach intentionally starts with heuristics rather than machine learning because the dataset has no labels, limited context, and needs defensible explanations for SOC review.

## Key findings

| Finding | Confidence | Why it matters |
|---|---:|---|
| `user_097` brute-force burst | 95% | 48 attempts at the exact same second from one IP |
| `user_003` nightly probe | 90% | 33 attempts from the same IP at exactly 20:00 |
| Shared-IP multi-user spray | 92% | 20 users from one IP at the same timestamp |
| High IP velocity | 70% | Useful signal, but threshold needs calibration |
| Off-hours access | 65% | Weak alone, stronger when paired with IP/device novelty |

## How to run the notebook

1. Create a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the assignment workbook to:

```text
data/logins_db_for_assignment.xlsx
```

4. Open and run:

```text
notebooks/security_login_analytics_investigation.ipynb
```

The cleaned script writes generated charts and summary outputs to `analysis_outputs/`.

## Public-repo data note

The raw login workbook is not committed by default because this package is intended for a public repository and the data contains user/IP-level login events. Add the workbook locally only when reproducing the notebook.

## Presentation narrative

The full deck is structured as a technical design review:

- Business risk and assignment understanding
- Analytical strategy and decision log
- Data quality and exploratory baseline
- Feature engineering rationale
- Threat kill chain and anomaly investigations
- Statistical confidence and explainability
- Dashboard design and product KPI case
- Production architecture, monitoring, limitations, and recommendations

The short deck condenses the same story into a 16-slide review covering:

- Executive summary and assignment scope
- Decision log and data quality summary
- Baseline spike and behavioral features
- Threat kill chain mapping
- Five anomaly findings with confidence scores
- Product KPI dashboard perspective
- Explainability, cost, production architecture, and conclusion
