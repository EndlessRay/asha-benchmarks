"""Usage figures for the benchmarks v2 and nonmaleficence manuscripts (run 2026-10-29), one filter, staff excluded.

Human filter: scripts/audits/traction_chart.py human_where() + bench_prelude_sql() (benchmark sessions, load-test
windows, test accounts, machine principals). Added here: DNAi staff accounts (users.email LIKE '%@dnai.systems'),
and admin or system roles (team members' personal accounts), which human_where() does not remove. Anonymous visitors (empty or NULL user_id) are kept. Asha sessions only (sessions.agent_id = 'asha').
Usage: python3 scripts/audits/usage_paper_figures.py   (needs SSH to the 5090; about 10 minutes)
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import traction_chart as tc  # noqa: E402

H = tc.human_where("m")
NOSTAFF = ("(m.user_id IS NULL OR m.user_id = '' OR m.user_id NOT IN "
           "(SELECT user_id::text FROM users WHERE email LIKE '%@dnai.systems' OR role IN ('admin', 'system')))")
REG = "(m.user_id IS NOT NULL AND m.user_id <> '' AND m.user_id IN (SELECT user_id::text FROM users))"
ASHA = "EXISTS (SELECT 1 FROM sessions s WHERE s.session_id = m.session_id AND s.agent_id = 'asha')"
WINDOWS = {"YTD": "m.timestamp >= '2026-01-01' AND m.timestamp < '2026-10-30'",
           "SINCE_LAUNCH": "m.timestamp >= '2025-12-01' AND m.timestamp < '2026-10-30'"}


def block(tag: str, where: str) -> str:
    return f"""
\\echo @{tag}
WITH q AS (SELECT m.session_id, m.user_id, length(m.content) AS n FROM messages m WHERE m.role = 'user' AND {where}),
     s AS (SELECT session_id, count(*) AS k FROM q GROUP BY 1),
     r AS (SELECT m.is_emergency, m.task_gravity FROM messages m WHERE m.role = 'assistant' AND {where})
SELECT (SELECT count(*) FROM q), (SELECT count(*) FROM s),
       (SELECT count(DISTINCT user_id) FROM q WHERE {REG.replace('m.user_id', 'user_id')}),
       (SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY n) FROM q),
       (SELECT round(100.0 * avg((k >= 2)::int), 1) FROM s),
       (SELECT round(100.0 * avg(coalesce(is_emergency, false)::int), 2) FROM r), (SELECT count(*) FROM r),
       (SELECT count(*) FROM r WHERE task_gravity IS NOT NULL),
       (SELECT round(100.0 * avg((task_gravity < 0.70)::int), 1) FROM r WHERE task_gravity IS NOT NULL),
       (SELECT round(100.0 * avg((task_gravity >= 0.70 AND task_gravity < 0.88)::int), 1) FROM r WHERE task_gravity IS NOT NULL),
       (SELECT round(100.0 * avg((task_gravity >= 0.88 AND task_gravity < 0.95)::int), 1) FROM r WHERE task_gravity IS NOT NULL),
       (SELECT round(100.0 * avg((task_gravity >= 0.95)::int), 1) FROM r WHERE task_gravity IS NOT NULL),
       (SELECT round(100.0 * avg((abs(task_gravity - 0.50) < 1e-9)::int), 1) FROM r WHERE task_gravity IS NOT NULL);
"""


blocks = []
for w, cond in WINDOWS.items():
    blocks.append(block(f"{w}|all_human|staff_in", f"{H}\n AND {cond} AND {ASHA}"))
    blocks.append(block(f"{w}|all_human|staff_out", f"{H}\n AND {cond} AND {ASHA} AND {NOSTAFF}"))
    blocks.append(block(f"{w}|registered|staff_out", f"{H}\n AND {cond} AND {ASHA} AND {NOSTAFF} AND {REG}"))
cmd = ["ssh", "-o", "ConnectTimeout=10", "-o", "LogLevel=ERROR", tc.SSH_HOST,
       "sudo docker exec -i citadel-postgres psql -U asha -d asha_ledger -At -F','"]
out = subprocess.run(cmd, input=tc.bench_prelude_sql() + "".join(blocks), capture_output=True, text=True, timeout=1800)
if out.returncode != 0:
    sys.exit(out.stderr[-2000:])
print("| Window | Population | Staff | Questions | Sessions | Registered askers | Median chars | Sessions with follow-up | "
      "Emergency flag (replies) | Replies with gravity | <0.70 | 0.70-0.88 | 0.88-0.95 | >=0.95 | at 0.50 |")
print("|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
tag = None
for line in out.stdout.splitlines():
    if line.startswith("@"):
        tag = line[1:].split("|")
        continue
    if tag and line.count(",") == 12:
        v = line.split(",")
        print(f"| {tag[0]} | {tag[1]} | {tag[2]} | {int(v[0]):,} | {int(v[1]):,} | {int(v[2]):,} | {float(v[3]):.0f} | {v[4]}% | "
              f"{v[5]}% of {int(v[6]):,} | {int(v[7]):,} | {v[8]}% | {v[9]}% | {v[10]}% | {v[11]}% | {v[12]}% |")
        tag = None
