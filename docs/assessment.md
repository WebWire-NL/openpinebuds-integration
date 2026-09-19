# Assessment: what is worth landing, and how

Survey date 2026-09-19, upstream `pine64/OpenPineBuds` @ `81b9afc7`.

## Verdicts

### Worth landing (in rough priority order)

1. **`shymega` CMake conversion** (branch `cmake`, 16 commits, replays cleanly). Upstream PR #60
   is still open/WIP; a maintainer called the build-system work "one of the prerequisites for
   further work" (issue #94, 2026-04). Touches ~2060 files, so it is a large but mechanical
   review, and it is the cheapest unblock for everything else.
2. **BLE config transport** — merge `hugohabthroxy` (17 commits, replays cleanly: enables BLE on
   the `open_source` target, removes the `IBRT_MASTER`/`advSwitch` gates, adds a GATT service +
   host tooling) with the firmware side of `erik-smit` (GATT service `0xFFC0`, NV persistence,
   TWS sync). Upstream ships `BLE ?= 0`, i.e. there is no way to configure the buds today.
   Publish **one** GATT spec (both forks wrote one) before merging, and keep the Android app in
   its own repo.
3. **EQ** — `erik-smit` solves upstream issue #109 ("EQ - how to add it?"): biquad chain, 8 bands,
   5 filter types, 10 presets, live preview with 500 ms debounce, NV persistence, TWS sync.
   Port the firmware-side DSP/preset code (+ the `suggested_anc_gains`/EF606 coefficient work
   already merged upstream) and leave the UI as a client.
4. **ANC via the aud NV section** — `nnonickreal` reports working ANC *and* transparency once the
   audio section is used, plus an ADC driver and OTA built from source instead of blobs. The
   patch is aimed at Soundcore hardware (different codec/DAC paths), so treat it as a *lead*, not
   a merge: it is the strongest available hint for the PineBuds' biggest open problem
   (upstream ANC is still "currently non functional, WIP", issue #41).
5. **`mbyzhang` FB-mic talk-through** (1 commit, 6 files, replays cleanly). Tiny, obviously
   useful, easy to review — a cheap win and a test of the merge process.
6. **Mic streaming / remote logging** — `RTIS-Lab` (5 commits, replays cleanly) gives RFCOMM
   mic capture + remote logs, which is what any future audio/sensor work needs.

### Worth as reference data, not as a merge

- **`SilentBob347` / `hrfried` ANC branches** — hand-tuned `tgt_hardware.c` values and an
  "annotate target" commit. Harvest numbers and the audio-section test, not the branch.
- **`BreezeLabsAG` branches** — mic-path DSP bypass modes (`normal/breathing/passthrough`),
  `SPEECH_TX_EQ` override, mic calibration. Useful negative/partial results; the
  `ph_dsp_bypass` branch is built on a devcontainer-refactor lineage and does not replay onto
  `main`'s merge base.
- **`arin-s/DOOMBuds`** (19 commits) — a game port, not a feature, but it documents real memory
  wins: SRAM raised to the advertised 992 KB, `.audio` segment dropped for −84 KB, static heap,
  CPU at 300 MHz, sleep disabled. Feed those into the RAM budget discussion.
- **`jdc-cunningham`** — measured FR values (MDR-7506, Galaxy Buds) for the tuning blob in
  `tgt_hardware.c`.
- **`Zoey-Tan`** — HFP at 44.1 kHz fails, reverted to 8 kHz: a useful negative result to record,
  plus macOS flash scripts.

### Not worth anything as a source

- The **38 forks with 0 unique commits**. Includes `gcostello65/OpenConeBuds` (renamed, no work),
  `marfrit` (his ANC work is already upstream), `pughb/Open-OAE-Buds` (interesting goal, but its
  branches are empty relative to main) and `SilentBob347/OpenPineBuds` `main`.
- Related but separate projects, to watch rather than merge: `hall/little-buddy` (independent
  minimal firmware, releases + 11 language packs), `Qiangest/PineBuds-Pro-Plus` (in-ear audio
  sensing research), `nnonickreal/openqore` + `besota`, `Ralim/bestool`.

## Risks that apply to every candidate

1. **Licensing is unresolved and blocks publication.** Upstream has no licence; ~800 files carry
   BES's "confidential and proprietary" header and ~23 closed `.a` blobs are still linked by the
   open build. BES re-licensing has been stalled since 2023 (issues #76/#92/#93/#94; April 2026:
   "It doesn't look like BES will co-operate"). Nothing landed here can be called open source
   until that changes.
2. **Provenance of AI-generated code.** `erik-smit` states most of its changes were produced by
   Claude Code, and other forks add "vibe-coded" scripts. An upstream contribution/DCO policy is
   needed *before* merging, or the already-fragile relicensing position gets worse.
3. **RAM is a hard constraint, not a bug.** BLE requires disabling ANC/trace/core-dump
   (`hugohabthroxy`); DOOMBuds reclaimed ~84 KB by dropping the `.audio` segment. Every merge has
   to be measured against a memory budget, and the trade-offs should be build flags.
4. **There is no test infrastructure.** Upstream CI only compiles `config/open_source`. Without a
   feature-flag build matrix and a hardware-in-the-loop smoke test over `bestool`, none of the
   above can be validated beyond "it compiled".
5. **Patch drift.** 12/15 patches replay today; upstream takes ~2-6 commits per quarter. Re-run
   `scripts/refresh.py` and `scripts/verify_patches.py` monthly, and prefer rebasing a work fork
   over carrying patch files.

## Suggested roadmap

- **P0** — build matrix + releases: build `open_source` (and DOOMBuds' RAM tricks) with
  `BLE`, `ANC_APP`, `AUDIO_SECTION_ENABLE`, `LDAC` on/off as a CI matrix; publish versioned
  artifacts (upstream has zero releases today); add a `bestool` HIL smoke test. Land CMake.
- **P1** — one BLE configuration protocol (GATT spec doc + `erik-smit`/`hugohabthroxy` merge),
  companion app in its own repo.
- **P2** — EQ from the firmware side, then presets/UI.
- **P3** — ANC: retry the aud-section approach on PineBuds hardware, measure with upstream's
  merged gain presets + EF606 coefficients, use the tuning data from the ANC branches, add
  transparency through the FB-mic route.
- **P4** — mic/sensor platform: RFCOMM mic streaming as a supported debug target, then
  breathing/OAE/in-ear sensing experiments on top.
