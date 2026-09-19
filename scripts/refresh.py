#!/usr/bin/env python3
"""Refresh the OpenPineBuds fork survey (every fork, every branch) + patch snapshots.

Needs an authenticated `gh` CLI. Writes docs/fork-survey.md, patches/*.patch,
patches/manifest.json. Usage: scripts/refresh.py [--patches-only]
"""
import json, re, subprocess, sys, time, pathlib, datetime, collections

UPSTREAM = "pine64/OpenPineBuds"
ROOT = pathlib.Path(__file__).resolve().parent.parent

# forks that the /forks API never lists: forks of forks (invisible to a shallow survey)
EXTRA_FORKS = [
    ("kuleuven-emedia", "OpenPineBuds", "fork of hugohabthroxy's fork"),
    ("YoonLee-lab", "EriksPineBuds", "fork of erik-smit's fork"),
]

# branches worth snapshotting as applyable patches (git am)
SOURCES = [
    ("erik-smit", "EriksPineBuds", "main", "touch controls + BLE config service + parametric EQ + Android app"),
    ("nnonickreal", "openqore-sdk", "main", "BES2300P/Soundcore port: ANC with aud section, ADC driver, OTA from source"),
    ("hugohabthroxy", "OpenPineBuds", "main", "BLE advertising on open_source target + cueing service + host tooling"),
    ("RTIS-Lab", "OpenPineBuds", "main", "mic streaming / remote logging over RFCOMM + capture scripts"),
    ("wojtas999", "OpenPineBuds", "wojtas", "mic streaming feature branch (invisible on main)"),
    ("arin-s", "DOOMBuds", "main", "doomgeneric port; SRAM/segment reclaim tricks"),
    ("shymega", "OpenPineBuds", "cmake", "CMake conversion (upstream PR #60)"),
    ("shymega", "OpenPineBuds", "rust-support", "CMake + Rust support"),
    ("nicka101", "OpenPineBuds", "cmake", "independent copy of the CMake work"),
    ("Haxk20", "OpenPineBuds", "anc-testing", "ANC testing branch (older lineage)"),
    ("ThatcherC", "OpenPineBuds", "build-from-mp3s", "original sound-file build system work"),
    ("BreezeLabsAG", "OpenPineBuds", "ph_dsp_bypass", "mic-path DSP bypass modes"),
    ("BreezeLabsAG", "OpenPineBuds", "SPEECH_TX_EQ_approach", "SPEECH_TX_EQ override experiment"),
    ("BreezeLabsAG", "OpenPineBuds", "SPEECH_TX_MIC_CALIBRATION_approach", "mic calibration experiment"),
    ("SilentBob347", "OpenPineBuds", "anc-tuning", "hand ANC tuning in tgt_hardware.c"),
    ("SilentBob347", "OpenPineBuds", "anc-testing", "audio-section ANC test"),
    ("mbyzhang", "OpenPineBuds", "main", "ANC FB mic for BT audio (talk-through)"),
    ("jdc-cunningham", "OpenPineBuds", "main", "FR tuning experiments vs measured headphones"),
    ("Zoey-Tan", "OpenPineBuds", "main", "HFP sample-rate experiment + macOS flash scripts"),
]

def gh(args, tries=4):
    for i in range(tries):
        r = subprocess.run(["gh", "api", *args], capture_output=True, text=True, timeout=180)
        if r.returncode == 0:
            return json.loads(r.stdout)
        time.sleep(2 * (i + 1))
    raise RuntimeError(r.stderr.strip()[:200])

def filter_binary(patch):
    """Drop binary-file sections so patches stay textual and git am-able."""
    idx = patch.find("\ndiff --git ")
    if idx == -1:
        return patch
    head, body = patch[:idx + 1], patch[idx + 1:]
    kept = [s for s in re.split(r"(?m)^(?=diff --git )", body)
            if "GIT binary patch" not in s and not re.search(r"(?m)^Binary files .* differ$", s)]
    return head + "".join(kept)

def survey():
    forks = [f for f in gh(["--paginate", f"repos/{UPSTREAM}/forks?per_page=100"])]
    extra = {f"{o}/{n}": note for o, n, note in EXTRA_FORKS}
    all_names = [f["full_name"] for f in forks] + [k for k in extra if k not in
                                                  [f["full_name"] for f in forks]]
    meta = {f["full_name"]: f for f in forks}

    tips = collections.defaultdict(list)
    for name in all_names:
        try:
            for b in gh(["--paginate", f"repos/{name}/branches?per_page=100"]):
                tips[b["commit"]["sha"]].append(f"{name}:{b['name']}")
        except Exception as e:
            print(f"WARN could not list branches of {name}: {e}", file=sys.stderr)
    print(f"{len(all_names)} forks, {sum(len(v) for v in tips.values())} branches, "
          f"{len(tips)} unique tips", flush=True)

    results = {}
    for i, (sha, refs) in enumerate(sorted(tips.items()), 1):
        owner, br = refs[0].split("/")[0], refs[0].split(":", 1)[1]
        d = gh([f"repos/{UPSTREAM}/compare/main...{owner}:{br}"])
        results[sha] = {"ahead": d["ahead_by"], "behind": d["behind_by"],
                        "last": "; ".join(c["commit"]["message"].split("\n")[0]
                                          for c in d.get("commits", [])[-3:])[:150],
                        "refs": refs}
        print(f"[{i}/{len(tips)}] ahead={d['ahead_by']:3} {refs[0]}", flush=True)

    per_fork = collections.defaultdict(list)
    for sha, r in results.items():
        for ref in r["refs"]:
            fork, br = ref.split(":", 1)
            per_fork[fork].append((r["ahead"], r["behind"], br))
    rows = []
    for name in all_names:
        brs = per_fork.get(name, [])
        best = max((a for a, b, br in brs), default=0)
        main = next(((a, b) for a, b, br in brs if br == "main"), (None, None))
        worked = [f"{br}(+{a})" for a, b, br in sorted(brs, reverse=True) if a > 0]
        f = meta.get(name, {})
        rows.append({"fork": name, "best": best, "main": main, "branches": worked,
                     "pushed": (f.get("pushed_at") or "")[:10],
                     "extra": extra.get(name, "")})
    rows.sort(key=lambda r: (-r["best"], r["fork"].lower()))

    stamp = datetime.date.today().isoformat()
    up = gh([f"repos/{UPSTREAM}"])
    lic = up["license"]["spdx_id"] if up.get("license") else "none"
    empty = [r for r in rows if r["best"] == 0]
    L = [f"# OpenPineBuds forks - survey {stamp}", "",
         f"Upstream [`{UPSTREAM}`](https://github.com/{UPSTREAM}) last push `{up['pushed_at'][:10]}`, "
         f"{up['stargazers_count']} stars, {up['forks_count']} forks counted by GitHub "
         f"({len(rows)} actually inspected, incl. 2 forks-of-forks the API does not list), "
         f"{up['open_issues_count']} open issues, licence: {lic}.", "",
         "Every branch of every fork is compared against upstream `main` (branch tips are "
         "deduplicated: a branch set forked around the network is one effort, not many).", "",
         "| fork | best ahead | main a/b | branches with unique commits | last push | note |",
         "|---|---:|---|---|---|---|"]
    for r in rows:
        ma = f"{r['main'][0]}/{r['main'][1]}" if r["main"][0] is not None else "-"
        L.append(f"| [{r['fork']}](https://github.com/{r['fork']}) | {r['best']} | {ma} | "
                 f"{', '.join(r['branches'][:6]) or '-'} | {r['pushed']} | {r['extra']} |")
    L += ["", f"**{len(rows) - len(empty)} of {len(rows)} forks contain unique commits on some branch; "
              f"{len(empty)} are byte-copies of upstream on every branch.**", "",
          "Forks with nothing unique anywhere: " + ", ".join(r["fork"] for r in empty), "",
          f"Unique branch tips with work: {sum(1 for r in results.values() if r['ahead'] > 0)}.", "",
          "Generated by `scripts/refresh.py`.", ""]
    (ROOT / "docs" / "fork-survey.md").write_text("\n".join(L))

    manifest, seen = [], {}
    for owner, repo, branch, why in SOURCES:
        d = gh([f"repos/{UPSTREAM}/compare/main...{owner}:{branch}"])
        base = d["merge_base_commit"]["sha"]
        head = d["commits"][-1]["sha"] if d.get("commits") else None
        fname = f"{owner}-{repo}-{branch}.patch"
        if (base, head) in seen:
            manifest.append({"fork": f"{owner}/{repo}", "branch": branch, "file": None,
                             "duplicate_of": seen[(base, head)], "why": why,
                             "ahead": d["ahead_by"], "behind": d["behind_by"],
                             "base": base, "head": head})
            print(f"skip duplicate {owner}/{repo}:{branch} == {seen[(base, head)]}")
            continue
        seen[(base, head)] = fname
        out = subprocess.run(["gh", "api", "-H", "Accept: application/vnd.github.patch",
                              f"repos/{UPSTREAM}/compare/main...{owner}:{branch}"],
                             capture_output=True, text=True, encoding="latin-1", timeout=300)
        if out.returncode or not out.stdout.strip():
            print(f"WARN no patch for {owner}/{repo}:{branch}", file=sys.stderr)
            continue
        (ROOT / "patches" / fname).write_text(filter_binary(out.stdout), encoding="latin-1")
        manifest.append({"fork": f"{owner}/{repo}", "branch": branch, "file": f"patches/{fname}",
                         "why": why, "ahead": d["ahead_by"], "behind": d["behind_by"],
                         "base": base, "head": head, "files_changed": len(d.get("files", []))})
        print(f"patched {fname} ({d['ahead_by']} commits)", flush=True)
    (ROOT / "patches" / "manifest.json").write_text(json.dumps(
        {"generated": stamp, "upstream_last_push": up["pushed_at"], "sources": manifest}, indent=2) + "\n")
    print(f"forks={len(rows)} empty={len(empty)} patches={sum(1 for m in manifest if m.get('file'))} "
          f"dupes={sum(1 for m in manifest if m.get('duplicate_of'))}")

if __name__ == "__main__":
    survey()
