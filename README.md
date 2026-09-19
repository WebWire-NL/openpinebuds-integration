# OpenPineBuds fork integration workspace

Working notes + applyable snapshots of every divergent fork of
[`pine64/OpenPineBuds`](https://github.com/pine64/OpenPineBuds) (community firmware for the
PineBuds Pro, BES2300YP), so the good bits can be reviewed and landed upstream instead of
being re-invented.

Snapshot taken **2026-09-19** against upstream `main` @ `81b9afc7` (last push 2026-07-29,
198 stars, 47 forks visible via API, 18 open issues, **no licence**).

## Contents

| path | what |
|---|---|
| [`docs/fork-survey.md`](docs/fork-survey.md) | all 47 forks: ahead/behind vs upstream, last push, recent commit subjects |
| [`docs/assessment.md`](docs/assessment.md) | which fork work is worth landing, which is only reference material, risks, roadmap |
| [`docs/patch-status.md`](docs/patch-status.md) | replay result for every patch (`git am --3way` onto its recorded base) |
| [`patches/manifest.json`](patches/manifest.json) | per-source: fork, branch, base/head SHA, ahead/behind, files changed |
| `patches/*.patch` | commit-for-commit patches (binary sections stripped) |

## Result of the survey

Only **9 of 47 forks contain any unique commits**; 38 are byte-copies (several are contributor
forks whose work is already upstream).

| fork | ahead | what it brings |
|---|---:|---|
| erik-smit/EriksPineBuds | 49 | configurable per-bud touch controls, BLE GATT config service (`0xFFC0`), 8-band parametric EQ + presets + QR sharing, Android companion app, GitHub releases, docs |
| nnonickreal/openqore-sdk | 37 | BES2300P port to Soundcore: **working ANC/transparency via the aud NV section**, ADC driver, DAC configs from stock firmware, OTA built from source |
| arin-s/DOOMBuds | 19 | doomgeneric port; memory reclamation (SRAM to 992 KB, `-84 KB` `.audio` segment, static heap) |
| hugohabthroxy/OpenPineBuds | 17 | BLE advertising on the `open_source` target (upstream ships `BLE ?= 0`), RAM trade-offs documented, cueing GATT service + host tooling |
| RTIS-Lab/OpenPineBuds | 5 | mic streaming + remote logging over RFCOMM, capture/analysis scripts |
| shymega (branches) | 16/17 | CMake conversion (upstream PR #60) and a Rust-support branch |
| BreezeLabsAG (branches) | 1-6 | mic-path DSP bypass and speech-TX EQ/calibration experiments |
| SilentBob347, hrfried (branches) | 1-5 | hand ANC tuning / audio-section tests |
| mbyzhang, jdc-cunningham, Zoey-Tan, dacmot | 1-3 | FB-mic talk-through, FR tuning data, HFP sample-rate negative result, README |

## Using a patch

```sh
git clone https://github.com/pine64/OpenPineBuds && cd OpenPineBuds
base=$(jq -r '.sources[] | select(.file=="patches/hugohabthroxy-OpenPineBuds-main.patch") | .base' \
        /path/to/patches/manifest.json)
git checkout -b try-hugo "$base"
git am --3way /path/to/patches/hugohabthroxy-OpenPineBuds-main.patch
```

12/15 patches replay commit-for-commit; the three that do not are listed in
`docs/patch-status.md` with the commit that collides (they carry a side-branch lineage or large
parallel merges). Prefer working on a fork of upstream and rebasing over carrying these patches.

## Refreshing

```sh
scripts/refresh.py                    # re-survey forks + re-download patches (needs `gh` auth)
scripts/verify_patches.py [/path/to/OpenPineBuds-clone]   # replay check
```

## Licence / status of this repo

**No licence is granted for anything here.** Upstream OpenPineBuds carries no open-source
licence (it is BES "shared source", with BES proprietary headers on ~800 files and ~23 closed
`.a` blobs still linked by the open build), and the relicensing effort is stalled on BES
co-operation (upstream issues #18, #76, #92, #93, #94). The patches are third-party diffs whose
context lines derive from that unlicensed code, so this repo is deliberately **private**
working material, not a distribution. Make it public only after upstream's licensing question
is settled.
