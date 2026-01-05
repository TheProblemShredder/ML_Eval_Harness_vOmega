## What to open first (30 seconds)

- `run.py`
- `outputs_blind/ledger.ndjson`
- `outputs_unblind/ledger.ndjson`
- `outputs_blind/results.json`
- `outputs_unblind/results.json`
- `.github/workflows/ci.yml`

# ML Eval Harness vΩ (Public Demo)

![CI](https://github.com/TheProblemShredder/ML_Eval_Harness_vOmega/actions/workflows/ci.yml/badge.svg)


Verification-first eval scaffold (stdlib only):

- prereg thresholds
- baseline vs ablation delta gate
- negative control gate
- optional blinding + reveal
- deterministic IDs (AEQ/CID)
- append-only ledger outputs/ledger.ndjson
- CI asserts artifacts exist

Run:
  python3 run.py --out outputs --seed 123 --reveal
  python3 run.py --out outputs --seed 123 --blind --reveal

Artifacts:
- outputs_*/prereg.json            preregistered thresholds + AEQ/CID
- outputs_*/results.json           metrics + gate decisions
- outputs_*/ledger.ndjson          append-only audit trail
- outputs_*/artifacts_manifest.json sha256 for each artifact
- outputs_blind/blind_map.json     (blind mode) real->blind mapping

## Proof (reproducible run)

### Commands
```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e . pytest
pytest -q
python3 run.py --help
```

### Example output
See: `docs/example_output.txt`

## Quickstart

Run the commands in **Proof (reproducible run)** below.
