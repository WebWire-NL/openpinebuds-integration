# Contributors

## This repository

- **[@WebWire-NL](https://github.com/WebWire-NL)** - analysis, tooling and documentation: the
  closed-blob survey (`docs/closed-blobs.md`), the API surface in both directions
  (`docs/sdk-surface.md`), the DWARF prototype recovery (`docs/anc-prototypes.md`),
  the header-less API publication (`docs/headerless-api.md`, `data/headerless-api.json`,
  `include/anc_reconstructed/`), the prior-art check (`docs/prior-art.md`), and the fork/patch
  survey, patch replay verification and vendored patch series (`patches/`, `docs/fork-survey.md`,
  `docs/patch-status.md`).

Commits are authored as `WebWire-NL <16407727+WebWire-NL@users.noreply.github.com>`.

## Upstream work vendored here

The `patches/*.patch` series are other people's work, kept as replayable series so the fixes can be
applied and bisected. Credit belongs to the original authors:

| fork / branch | author | what it adds |
|---|---|---|
| `erik-smit/EriksPineBuds` `main` | [@erik-smit](https://github.com/erik-smit) | touch controls, BLE config service, parametric EQ, Android companion app |
| `nnonickreal/openqore-sdk` `main` | [@nnonickreal](https://github.com/nnonickreal) | BES2300P/Soundcore port, ANC with aud section, ADC driver, OTA from source |
| `hugohabthroxy/OpenPineBuds` `main` | [@hugohabthroxy](https://github.com/hugohabthroxy) | BLE advertising on the open_source target, cueing service, host tooling |
| `RTIS-Lab/OpenPineBuds` `main` | [@RTIS-Lab](https://github.com/RTIS-Lab) | mic streaming / remote logging over RFCOMM |
| `wojtas999/OpenPineBuds` `wojtas` | [@wojtas999](https://github.com/wojtas999) | mic streaming feature branch |
| `arin-s/DOOMBuds` `main` | [@arin-s](https://github.com/arin-s) | doomgeneric port, SRAM/segment reclaim |
| `shymega/OpenPineBuds` `cmake`, `rust-support` | [@shymega](https://github.com/shymega) | CMake conversion (upstream PR #60), Rust support |
| `nicka101/OpenPineBuds` `cmake` | [@nicka101](https://github.com/nicka101) | CMake targets for utils/platform/rtos |
| `Haxk20/OpenPineBuds` `anc-testing` | [@Haxk20](https://github.com/Haxk20) | ANC switching fix, testing branch |
| `SilentBob347/OpenPineBuds` `anc-tuning`, `anc-testing` | [@SilentBob347](https://github.com/SilentBob347) | ANC tuning and test branches |
| `BreezeLabsAG/OpenPineBuds` `ph_dsp_bypass`, `SPEECH_TX_EQ_approach`, `SPEECH_TX_MIC_CALIBRATION_approach` | [@BreezeLabsAG](https://github.com/BreezeLabsAG) | DSP bypass, speech TX EQ, mic calibration approaches |
| `ThatcherC/OpenPineBuds` `build-from-mp3s` | [@ThatcherC](https://github.com/ThatcherC) | building sound files from mp3s |
| `jdc-cunningham/OpenPineBuds` `main`, `mbyzhang/OpenPineBuds` `main`, `Zoey-Tan/OpenPineBuds` `main` | [@jdc-cunningham](https://github.com/jdc-cunningham), [@mbyzhang](https://github.com/mbyzhang), [@Zoey-Tan](https://github.com/Zoey-Tan) | smaller fixes carried on top of upstream |

Upstream is [`pine64/OpenPineBuds`](https://github.com/pine64/OpenPineBuds); the patches are
replayed against it, not redistributed as a fork. The BES `*.a` archives analysed here remain
BES's proprietary work, and the declarations published under `include/anc_reconstructed/` are
interface metadata, not code.
