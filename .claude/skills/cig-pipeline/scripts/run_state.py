#!/usr/bin/env python3
"""
run_state.py -- audit log + loop guardrail for the CIG pipeline.

Keeps a JSON run record of every gate round and computes the loop decision so
the orchestration is deterministic and auditable. Pure stdlib.

Exit-bar policy (locked with the user):
  PASS      -> 0 blockers AND 0 majors  (minors allowed; they become the
               human punch-list). This is the analog of nice-cig-writer's
               "no failing category" bar.
  ESCALATE  -> not PASS but round >= max_rounds (default 3): stop looping and
               hand to the human anyway, with remaining findings.
  CONTINUE  -> not PASS and rounds remain: run one mechanical-revise cycle.

Commands:
  init   run.json --guide PATH [--mode create|review] [--max-rounds 3]
  record run.json --round N --verdict READY|NOT_READY \
                  --blockers B --majors M --minors m \
                  [--report PATH] [--redlined PATH] [--action "..."]
  decide run.json --blockers B --majors M           # prints PASS|CONTINUE|ESCALATE
  show   run.json                                    # prints the run summary
"""
import sys, json, argparse, os

DEFAULT_MAX = 3


def load(p):
    return json.load(open(p)) if os.path.exists(p) else {}


def save(p, d):
    json.dump(d, open(p, 'w'), indent=2)


def decide(blockers, majors, rnd, max_rounds):
    if blockers == 0 and majors == 0:
        return "PASS"
    if rnd >= max_rounds:
        return "ESCALATE"
    return "CONTINUE"


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("init"); pi.add_argument("state")
    pi.add_argument("--guide", default=""); pi.add_argument("--mode", default="create")
    pi.add_argument("--max-rounds", type=int, default=DEFAULT_MAX)

    pr = sub.add_parser("record"); pr.add_argument("state")
    pr.add_argument("--round", type=int, required=True)
    pr.add_argument("--verdict", required=True)
    pr.add_argument("--blockers", type=int, required=True)
    pr.add_argument("--majors", type=int, required=True)
    pr.add_argument("--minors", type=int, default=0)
    pr.add_argument("--report", default=""); pr.add_argument("--redlined", default="")
    pr.add_argument("--action", default="")

    pd = sub.add_parser("decide"); pd.add_argument("state")
    pd.add_argument("--blockers", type=int, required=True)
    pd.add_argument("--majors", type=int, required=True)

    ps = sub.add_parser("show"); ps.add_argument("state")

    a = ap.parse_args()

    if a.cmd == "init":
        save(a.state, {"guide": a.guide, "mode": a.mode,
                       "max_rounds": a.max_rounds, "rounds": [], "status": "open"})
        print(f"initialized {a.state} (mode={a.mode}, max_rounds={a.max_rounds})")
        return

    d = load(a.state)
    if not d:
        sys.exit(f"no run state at {a.state} -- run 'init' first")

    if a.cmd == "record":
        d["rounds"].append({
            "round": a.round, "verdict": a.verdict,
            "blockers": a.blockers, "majors": a.majors, "minors": a.minors,
            "report": a.report, "redlined": a.redlined, "action": a.action})
        dec = decide(a.blockers, a.majors, a.round, d["max_rounds"])
        d["status"] = {"PASS": "passed", "ESCALATE": "escalated",
                       "CONTINUE": "revising"}[dec]
        d["last_decision"] = dec
        save(a.state, d)
        print(dec)
        return

    if a.cmd == "decide":
        rnd = len(d["rounds"])
        print(decide(a.blockers, a.majors, rnd, d["max_rounds"]))
        return

    if a.cmd == "show":
        print(f"Guide : {d.get('guide')}")
        print(f"Mode  : {d.get('mode')}   Max rounds: {d.get('max_rounds')}")
        print(f"Status: {d.get('status')}   Last decision: {d.get('last_decision','-')}")
        print("Rounds:")
        for r in d["rounds"]:
            print(f"  #{r['round']}: {r['verdict']:9} "
                  f"B={r['blockers']} M={r['majors']} m={r['minors']}"
                  + (f"  [{r['action']}]" if r['action'] else ''))
        return


if __name__ == "__main__":
    main()
