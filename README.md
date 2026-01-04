# ML Eval Harness vΩ (Public Demo)

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
