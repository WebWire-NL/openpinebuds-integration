# Prior art: were we the first? (2026-09-19)

Checked with GitHub code/issue search (browser via CDP + REST API) across all of GitHub.

## Short answer

- **Not first for the names.** The module headers already exist publicly in other BES SDK trees.
- **First, as far as this search goes, for the DWARF-level extraction** of the prebuilt blobs: the
  machine-readable inventory, "which exported functions has no header anywhere" and the
  reconstructed declarations. No repo or issue mentions DWARF, `readelf`, symbol reachability or
  the blobs' debug info at all.
- **The implementations are nowhere public.** Only declarations exist elsewhere; the withheld
  `speech/`, ANC and codec sources are absent from every public SDK tree checked.

## Repos that already carry these headers

Query `anc_adj_mc_run_mono` / `adj_mc_filter_estimate` on GitHub code search returns 14 files; the
relevant ones (and their SDK trees):

| repo | entries | .c | .h | .a | carries |
|---|---:|---:|---:|---:|---|
| `Derek-Vencer/tws_earbuds` | 8,450 | 1,505 | 3,916 | 47 | `multimedia/inc/audio/process/adj_mc/inc/adj_mc.h` with exactly the four functions we reconstructed |
| `sprlightning/BES2700IHC-SDK` | 7,417 | 1,358 | 2,033 | 234 | `services/multimedia/speech/inc/speech_3mic_ns.h`, `triple_mic_denoise3.h`, `anc_process.h` |
| `sprlightning/audio_prj_collections` | 10,993 | - | - | - | BES2700IHC + BES2600IHC trees, `out/best1306/...` build artifacts |
| `hall/little-buddy` | 2,550 | 583 | 910 | 7 | the same `best2300p_libmultimedia_cp_anc.a` we analysed, plus the FDK-AAC source tree |
| `atc1441/MiBand10-BES2700iMP-BEST1503-Hacking`, `qqq5127/BES_2300`, `DyLanCao/2300_audio_open_sdk`, `frap129/PineBuds-SDK`, `JRowe47/OpenPineBuds`, `Hi-LinkDuino/RM56`, `Qian/Fanjianghua/HP-H300BT`, `forzalife/L15`, `KoenCai/best2600YP_DML`, `Derek-Vencer/best1307`, `superhui888/bes2600_sdk`, `7477as/BES2600IHC`, `Qiangest/PineBuds-Pro-Plus` | - | - | - | - | the same speech/ANC headers from later chip generations |

`pine64/OpenPineBuds` itself ships many of these headers (`services/multimedia/speech/inc/…`) and
calls `anc_adj_mc_run_mono` from `services/bt_app/app_bt_stream.cpp`.

## How much of our list was already public

Headers of `Derek-Vencer/tws_earbuds` (309 multimedia headers) plus `hall/little-buddy` (910):

| set | already declared publicly |
|---|---:|
| all 529 recovered names | 232 |
| the 180 external header-less names | **5** (the `adj_mc` four plus one) |

So of the 180 external functions published here as "declared nowhere", **175 appear in no public
header or code** we could find. Caveat: bare identifiers like `MatrixInversion` or `DmatGen` match
unrelated numerical code, so the structured overlap test above is the reliable figure, not a
per-name string search.

## The implementations really are unpublished

Zero hits for `multimedia/speech/src/`, `adj_mc.c`, `speech_3mic_ns.c`, `wind_detection_2mic.c`,
`anc_process_best2300p.c`, `triple_mic_denoise3.c` and `hw_iir_process_best2300p.c` in the trees of
`Derek-Vencer/tws_earbuds`, `sprlightning/BES2700IHC-SDK`, `sprlightning/audio_prj_collections`,
`DyLanCao/2300_audio_open_sdk`, `qqq5127/BES_2300` and `hall/little-buddy`.

## The closest prior art

[`OneDeuxTriSeiGo/openpinebuds-source-analysis`](https://github.com/OneDeuxTriSeiGo/openpinebuds-source-analysis)
(2024) documents file provenance for the relicensing effort: upstream/alternative sources, moved
sources, and reconstruction results split into "no sources", "full/partial FOSS sources" and
"full/partial closed sources". It **declares `symbols.rst`, "Symbol Reachability by File", and the
file is empty (84 bytes, heading only)** - the symbol-level analysis was intended and never
written. That is the gap this work fills.

## What the upstream threads say

- **#41 "ANC Support"**: *"In both cases the code for doing the ANC is the binary blob bes provide.
  We cant just (easily) reverse engineer the code from the production firmware as its stripped
  down."* - the community's working assumption is that the ANC code cannot be inspected. The
  production firmware is indeed stripped, but the prebuilt SDK archives are not: they keep `-g`
  DWARF. Also referenced there: Ralim's `dev_tools/anc_decoder` (Rust), which parses the ANC struct
  out of a firmware dump - config extraction, not interface recovery.
- **#18 "Add license"**: *"No matter what I've asked, its been silence from them on this; it appears
  they do not want any transfer of their existing code/binary blobs to a different licence. It seems
  they are ok with source-available of it (and given this SDK is all over csdn, its not really a
  secret)."* - and a note that FDK-AAC's licence needs legal reading before redistribution.
- **#76 "Tracking Issue for Relicensing Effort"** (2023-12): "BES Relicensing: In Progress", with the
  per-file analysis repo linked.
- **#92 / #93**: the formal relicensing requests to BES - per file, the declared licence, the
  licence wanted, and a diff against the reconstructed source. #93 lists "partially open sourced
  files", #92 "originally open sourced files".

## Consequence for our release

`docs/headerless-api.md` says "no shipped header declares" - that is true of
`pine64/OpenPineBuds`, not of the internet. The novelty is the DWARF route and the 175-name residue,
not the module headers. The list remains a natural annex to #92/#93, and it is the only artefact
that names what the SDK implements *and never documented anywhere*.

Generated by hand from the searches; re-run with the queries in this file.
