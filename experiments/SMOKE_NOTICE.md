# Smoke / synthetic metrics — not for thesis primary numbers

The `metrics.json` files currently under this folder were produced by **CPU smoke tests** on synthetic line images (`scripts/prepare_smoke_data.py`) and/or a tiny randomly initialized TrOCR checkpoint.

**Do not publish these CER/WER values in the thesis.**

Replace them by running the GPU full protocol:

See `docs/GPU_PROTOCOL.md` and `bash scripts/run_gpu_protocol.sh`.

After GPU runs, E1–E4 must show `"n_samples": 2915`.
