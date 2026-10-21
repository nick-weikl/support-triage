# Internal IT Ticket Triage

A learning project using TypeSafe AI's Jev model to categorize internal IT
requests, assess urgency, detect missing information, and select follow-up
questions.

## Features

- Hardware, identity/access, network, software, and other categories
- Team assignment using Python routing rules
- Urgency scoring from 0 to 2
- Separate checks for missing routing and urgency information
- Suggested clarification questions
- Follow-up answers incorporated into subsequent analysis
- SQLite ticket history with review filters

## Stack

- Python
- Streamlit
- TypeSafe Python SDK
- SQLite

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your TypeSafe API key to `.env`, then start the app:

```bash
python -m streamlit run app.py
```

The app initializes its local database automatically.

## How Jev is used

Each analysis sends the employee's report and urgency rubric as shared state.

- Choice selects the primary category and a follow-up question.
- Score estimates urgency against three descriptive levels.
- Nouls estimate whether routing or urgency information is insufficient.

Questions in a single request are evaluated independently. Python combines
their answers into routing and display decisions.

Follow-up analysis sends the original report and accumulated questions and
answers. Jev does not retain conversation history between requests.

## Decision thresholds

Check the source files for the current values:

- Minimum category confidence: <CURRENT VALUE>
- Missing routing information threshold: <CURRENT VALUE>
- Missing urgency information threshold: <CURRENT VALUE>

These are experimental thresholds evaluated on a small synthetic dataset.

## Evaluation

```bash
python evaluate.py
```

The evaluation reports category accuracy, urgency differences, and
clarification accuracy. It also saves detailed results to
`data/evaluation_results.json`.

Each run makes API calls and replaces the previous evaluation output.

## Limitations

Model confidence does not guarantee correctness. Urgency is provisional when
important context is missing.

Follow-up updates replace the ticket's stored analysis. Previous model
predictions are not retained as an audit history.

This is a local learning prototype. Authentication, production access
controls, and real help-desk integrations are outside its current scope.

## Secrets and local data

The API key is loaded from `.env`. Environment files and SQLite databases
are excluded from version control. Use fictional tickets in committed
evaluation data.