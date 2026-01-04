#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, random, time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

def canon(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def write_text(path: Path, s: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(s, encoding="utf-8")

def write_json(path: Path, obj: Any) -> None:
    write_text(path, json.dumps(obj, indent=2, ensure_ascii=False) + "\n")

def file_sha256(path: Path) -> str:
    return sha256_hex(path.read_bytes())

def append_ledger(out_dir: Path, entry: Dict[str, Any]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    entry = dict(entry)
    entry.setdefault("ts", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    with (out_dir / "ledger.ndjson").open("a", encoding="utf-8") as f:
        f.write(canon(entry) + "\n")

@dataclass(frozen=True)
class Thresholds:
    baseline_acc_min: float = 0.70
    delta_min: float = 0.05
    neg_acc_max: float = 0.60

def accuracy(y: List[int], p: List[int]) -> float:
    return sum(1 for yi, pi in zip(y, p) if yi == pi) / max(1, len(y))

def synth_labels(rng: random.Random, n: int = 400) -> List[int]:
    return [1 if rng.random() < 0.5 else 0 for _ in range(n)]

def simulate_preds(rng: random.Random, y: List[int], err: float) -> List[int]:
    out: List[int] = []
    for yi in y:
        out.append(1 - yi if rng.random() < err else yi)
    return out

def prereg(seed: int) -> Dict[str, Any]:
    t = Thresholds()
    obj = {
        "seed": seed,
        "thresholds": {
            "baseline_acc_min": t.baseline_acc_min,
            "delta_min": t.delta_min,
            "neg_acc_max": t.neg_acc_max,
        },
        "metric": "accuracy",
        "conditions": ["baseline", "ablation", "negative_control"],
        "notes": "Synthetic demo harness. Stdlib only.",
    }
    aeq = sha256_hex(canon(obj).encode("utf-8"))[:12]
    cid = sha256_hex(f"{aeq}:{seed}".encode("utf-8"))[:12]
    obj["AEQ"] = aeq
    obj["CID"] = cid
    return obj

def run_once(out_dir: Path, seed: int, blind: bool, reveal: bool) -> int:
    rng = random.Random(seed)
    pr = prereg(seed)
    out_dir.mkdir(parents=True, exist_ok=True)

    prereg_path = out_dir / "prereg.json"
    write_json(prereg_path, pr)
    append_ledger(out_dir, {"event":"prereg_written","file":"prereg.json","sha256":file_sha256(prereg_path),"AEQ":pr["AEQ"],"CID":pr["CID"]})

    labels = {"baseline":"baseline","ablation":"ablation","negative_control":"negative_control"}
    blind_map_path = out_dir / "blind_map.json"
    if blind:
        conds = pr["conditions"][:]
        rng.shuffle(conds)
        labels = {cond: f"C{idx+1}" for idx, cond in enumerate(conds)}
        write_json(blind_map_path, {"seed": seed, "map_real_to_blind": labels})
        append_ledger(out_dir, {"event":"blind_map_written","file":"blind_map.json","sha256":file_sha256(blind_map_path)})

    y = synth_labels(rng, 400)
    base = simulate_preds(rng, y, 0.20)
    ablt = simulate_preds(rng, y, 0.27)
    neg  = simulate_preds(rng, y, 0.50)

    base_acc = accuracy(y, base)
    ablt_acc = accuracy(y, ablt)
    neg_acc  = accuracy(y, neg)
    delta = base_acc - ablt_acc

    t = Thresholds()
    gates = {
        "baseline_acc_min": {"value": base_acc, "min": t.baseline_acc_min, "pass": base_acc >= t.baseline_acc_min},
        "delta_min": {"value": delta, "min": t.delta_min, "pass": delta >= t.delta_min},
        "neg_acc_max": {"value": neg_acc, "max": t.neg_acc_max, "pass": neg_acc <= t.neg_acc_max},
    }
    overall = all(v["pass"] for v in gates.values())

    results = {
        "AEQ": pr["AEQ"],
        "CID": pr["CID"],
        "seed": seed,
        "blind": blind,
        "metrics": {
            labels["baseline"]: base_acc,
            labels["ablation"]: ablt_acc,
            labels["negative_control"]: neg_acc,
            "delta(baseline-ablation)": delta,
        },
        "gates": gates,
        "overall_pass": overall,
    }

    results_path = out_dir / "results.json"
    write_json(results_path, results)
    append_ledger(out_dir, {"event":"results_written","file":"results.json","sha256":file_sha256(results_path),"overall_pass":overall})

    manifest = {
        "AEQ": pr["AEQ"],
        "CID": pr["CID"],
        "files": {
            "prereg.json": file_sha256(prereg_path),
            "results.json": file_sha256(results_path),
            "ledger.ndjson": file_sha256(out_dir / "ledger.ndjson"),
            **({"blind_map.json": file_sha256(blind_map_path)} if blind else {}),
        },
    }
    write_json(out_dir / "artifacts_manifest.json", manifest)

    if reveal and blind and blind_map_path.exists():
        print("BLIND MAP (reveal):")
        print(blind_map_path.read_text(encoding="utf-8"))

    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0 if overall else 2

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="outputs")
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--blind", action="store_true")
    ap.add_argument("--reveal", action="store_true")
    a = ap.parse_args()
    return run_once(Path(a.out), a.seed, a.blind, a.reveal)

if __name__ == "__main__":
    raise SystemExit(main())
