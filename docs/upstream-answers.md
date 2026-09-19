# Answers to recurring upstream questions

These were written to be posted in the upstream issue tracker. Two of the threads they
answer were closed *and locked* by the maintainers, so the text lives here instead - it is
the answer to the question people still ask.

| upstream | question | outcome |
|---|---|---|
| [#35](https://github.com/pine64/OpenPineBuds/issues/35) | microphone noise in the open firmware | posted |
| [#41](https://github.com/pine64/OpenPineBuds/issues/41) | ANC support / how to tune the closed ANC | posted |
| [#76](https://github.com/pine64/OpenPineBuds/issues/76) | relicensing effort, tracking issue | posted - the 498-file target list |
| [#92](https://github.com/pine64/OpenPineBuds/issues/92) / [#93](https://github.com/pine64/OpenPineBuds/issues/93) | relicensing requests to BES | covered by the #76 comment; the per-file annex is still offered, not yet posted |
| [#109](https://github.com/pine64/OpenPineBuds/issues/109) | "EQ - how to add it?" | **closed and locked** - answer below |
| [#88](https://github.com/pine64/OpenPineBuds/issues/88) | "Disable most touch features?" | **closed and locked** - answer below |
| [#126](https://github.com/pine64/OpenPineBuds/pull/126) | the prebuilt-library analysis itself | open PR |

Every answer here is written to be pasted as-is. Nothing quoted from the branches below is
included, only the commit/file pointers.

---

## How to add EQ (upstream #109)

This is implemented now, in a fork rather than here - worth knowing since the issue is about how to actually add it.

[erik-smit/EriksPineBuds](https://github.com/erik-smit/EriksPineBuds), branch `main` (49 commits ahead of upstream), carries a runtime-configurable parametric EQ. The moving parts:

- **`config/open_source/tgt_hardware.c`** - this is the file @FintasticMan pointed at. `audio_eq_sw_iir_cfg` is `const` here (the compile-time `IIR_TYPE_PEAK` bands around line 1027), so the only way to change EQ in this tree is to edit coefficients and reflash. The fork makes that global modifiable and zeroes `audio_eq_hw_dac_iir_cfg`.
- **`services/audio_process/audio_process.c`** - `audio_eq_set_cfg()` extended, built with `-DAUDIO_EQ_SW_IIR_UPDATE_CFG`. Note this file *is* in the tree; the closed part below it (`services/multimedia/audio/process`, the HW/SW IIR+FIR EQ objects) is not, which is why the config in `tgt_hardware.c` is the interface you get to drive.
- **A BLE GATT EQ service, `0xFFD0`**: `0xFFD1` config, `0xFFD2` preset, `0xFFD3` enable, `0xFFD4` capabilities, `0xFFD5` apply, `0xFFD6` status - with TWS sync between the buds, NV persistence, and an Android companion app for editing bands and sharing presets by QR code.
- Its `docs/EQ_GATT_SPEC.md` and `docs/EQ_IMPLEMENTATION_STATUS.md` describe the protocol and the known limits (including BLE security caveats documented in the fork's README).

EQ landed over that fork's releases: v1.1.0 → v1.3.0 (`Add configurable N-band equalizer`, then fixes for persistence at boot, slave/bud EQ sync, and more musical presets).

We keep it as a replayable patch series and record what replays cleanly: <https://github.com/WebWire-NL/openpinebuds-integration/blob/main/docs/patch-status.md>. Prefer the fork's branch as the source of truth - our patch is a reviewable snapshot, nothing more.


---

## Disabling most touch features (upstream #88)

Short answer: you don't have to hand-edit every gesture - and there is a ready-made patch series for exactly this.

Where touch lives in this tree:

- **`config/open_source/tgt_hardware.c`** - the touch panel is declared as GPIO keys: `cfg_hw_gpio_key_cfg[]` maps `HAL_KEY_CODE_FN1..FN4` to P0_3/P0_0/P0_1/P0_2 (lines ~95-130), and the `TOUCH_INT` pin function map is further down (line ~253). That is the wiring, not the behaviour - editing it just breaks the panel.
- The **gesture -> action mapping** is in the key handling path (`apps/key/app_key.cpp`, `apps/main/key_handler.cpp`). To strip actions you edit the mapping there, which means a rebuild and a reflash per trial.

If you would rather not rebuild per change: [erik-smit/EriksPineBuds](https://github.com/erik-smit/EriksPineBuds) `main` starts with exactly this feature (`Add configurable touch controls - Phase 1`, commit 1 of 49). Per-earbud and per-gesture - single tap, double tap, triple tap, long press - with the action stored in NV flash and set over BLE, no reflash:

- Service `0xFFC0`; `0xFFC1` = left bud config, `0xFFC2` = right bud, 16 bytes each = 4 gestures x 4 bytes; `0xFFC3` = version.
- The action set includes `OPB_ACTION_NONE = 0x0000` (plus a validator that rejects out-of-range actions), so "disable the vast majority of them" is literally setting those gestures to NONE. There is also `OPB_ACTION_MUTE_MIC`, `OPB_ACTION_TOGGLE_ANC` etc. if you want a couple left.
- Caveat documented in that fork: the config service only advertises on the `BES_ble` device, not the main audio one, and the fork's README notes its BLE security limitations.

We replay it as a patch series and record where it stops applying cleanly (2 of its 49 commits, the first conflict being `Fix BLE initialization crash and enable BLE stack`): the erik-smit series (fetched locally by `scripts/refresh.py`; the diffs are not distributed), <https://github.com/WebWire-NL/openpinebuds-integration/blob/main/docs/patch-status.md>. For this use case just build the fork's branch directly - our patch is a reviewable snapshot, not a substitute.

