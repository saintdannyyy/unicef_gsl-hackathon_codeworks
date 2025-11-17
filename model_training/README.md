# model_training — Signify Ghana (GSL) ML pipeline

This folder contains the data collection UI and scripts to train/export lightweight GSL classifiers for browser inference (TF.js). Use this README to collect landmarks, train models and export for the web frontend.

Contents

- collect/ — small Flask data-collection UI (data_collection.html + server.py)
- samples/ — example JSONL landmark files collected during the hack
- train_hybrid_model.py — training script (dense / sequence hybrid)
- export_manual.py — helper to export / convert models for TF.js
- analyze_dat.py — dataset inspection & summary tools
- requirements.txt — Python dependencies

Quick summary

1. Collect landmark samples using the browser UI (MediaPipe → JSONL).
2. Train a classifier with train_hybrid_model.py.
3. Export model to TF.js with export_manual.py (or tensorflowjs_converter).
4. Copy exported model + labels.json to frontend: sign_language/wote/public/assets/web_model/ and labels.json.

Recommended environment (Windows PowerShell)

```powershell
cd "c:\Users\HP\Documents\Hackathon\Unicef Startup Lab\codeworks\model_training"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

1. Data collection

- Start the collection server:

```powershell
cd collect
python server.py
```

- Open http://localhost:5000
- Enter a label (e.g. "A", "hello") and capture 30–50 samples per sign (more for motion signs).
- Output: one JSONL file per label or combined lines in `samples/` (each line = {"label":"X","landmarks":[...]}).

Data format

- Each sample is a flat list of floats:
  - static signs: 63 values (21 keypoints × 3 coords)
  - motion signs: fixed-length sequences (e.g., 10 frames → 630 values)
- Example JSONL line:

```json
{"label":"A","landmarks":[0.12,0.55,-0.02,...]}
```

2. Inspect dataset

```powershell
python analyze_dat.py --dir samples
```

Checks class counts, sequence lengths, missing/empty files.

3. Train model

- Basic usage (example):

```powershell
python train_hybrid_model.py --data ./samples --out ./model --epochs 50 --batch_size 32 --seq_len 10
```

- Notes:
  - --seq_len: window size for motion signs (if script supports sequence mode).
  - Use --validation_split or provide separate validation set if available.
  - For faster training, run on a machine with GPU and a proper TF installation.

Expected outputs

- Saved Keras model (e.g., model.h5 / SavedModel) in `--out` directory
- `labels.json` mapping class indices to labels

4. Export to TF.js
   Option A — use provided helper:

```powershell
python export_manual.py --input ./model --out ../sign_language/wote/public/assets/web_model
```

Option B — tensorflowjs (if installed):

```powershell
tensorflowjs_converter --input_format=keras model.h5 ../sign_language/wote/public/assets/web_model
```

After export

- Ensure files exist:
  - sign_language/wote/public/assets/web_model/model.json
  - sign_language/wote/public/assets/web_model/group1-shard\*bin
- Copy labels.json to sign_language/wote/public/labels.json
- Start frontend dev server and verify model loads in browser (network tab).

Tips & best practices

- Collect 30–50 samples per static class; 50–150 for motion signs or noisy classes.
- Normalize landmarks consistently (same preprocessing in training and inference).
- Keep classes balanced or use class-weighting during training.
- Use small dense models for browser inference to keep latency < 100ms.
- If TF.js fails to load in browser: check CORS, correct path, and that model.json references existing shard files.

Troubleshooting

- "Model JSON not found" — verify path and filenames; model.json must be at the declared URL.
- TF / GPU issues — use CPU-only environment or match CUDA/cuDNN versions with TF build.
- Low accuracy — collect more diverse samples (lighting, hand orientation, skin tones).
- Sequence/motion issues — ensure fixed-length sequences (pad/truncate consistently).

Advanced

- Replace train_hybrid_model.py with experiment scripts (LSTM, Conv1D) as needed.
- Quantize TF.js model for smaller download size (tensorflowjs_converter flags).
- Integrate CI to auto-train/export when new labeled data is added.

License & attribution

- This codebase was developed for the UNICEF Startup Lab (Signify Ghana). Follow repository LICENSE in project root.

Contact

- Open an issue in the main repo for questions or model export help.
