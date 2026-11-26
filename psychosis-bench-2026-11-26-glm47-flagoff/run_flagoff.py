"""Run the psychosis-bench two-judge harness with the Asha arm's evaluation flag off.

Usage: python3 run_flagoff.py --harness-dir <dir with run_bench_two_judges.py> -- <harness arguments>

Sets eval_mode=None on every AshaArm, then calls the harness's main() with the remaining arguments. Nothing else in
the harness changes.
"""

import argparse
import hashlib
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness-dir", required=True)
    args, rest = ap.parse_known_args()
    if rest and rest[0] == "--":
        rest = rest[1:]
    hdir = Path(args.harness_dir).resolve()
    for name in ("run_bench_two_judges.py", "model_clients.py"):
        print(f"{name} sha256 {hashlib.sha256((hdir / name).read_bytes()).hexdigest()}", flush=True)
    sys.path.insert(0, str(hdir))

    import model_clients

    original_init = model_clients.AshaArm.__init__

    def init_flag_off(self, *a, **kw):
        kw["eval_mode"] = None
        original_init(self, *a, **kw)
        if self.eval_mode is not None:
            raise RuntimeError("eval_mode is still set")

    model_clients.AshaArm.__init__ = init_flag_off

    import run_bench_two_judges

    if run_bench_two_judges.AshaArm is not model_clients.AshaArm:
        raise RuntimeError("harness imported a different AshaArm")
    sys.argv = ["run_bench_two_judges.py", *rest]
    print("eval_mode forced to None on AshaArm", flush=True)
    return run_bench_two_judges.main()


if __name__ == "__main__":
    sys.exit(main())
