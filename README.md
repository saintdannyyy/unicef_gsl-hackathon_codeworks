# Wote — Ghana Sign Language (GSL) Learning Platform

**Wote** is a comprehensive open-source platform for learning and practicing Ghanaian Sign Language (GSL). It provides an integrated suite of tools for beginners to learn signs, practice with AI-powered feedback, play competitive multiplayer games, and contribute to a growing community dictionary.

🏆 **Built for UNICEF Startup Lab — Awarded 3rd Place & Best AI Implementation**

## Key Features

✨ **Telegram Bot** (`wote_gslbot/`)

- Solo practice mode (3-question quick quizzes with instant feedback)
- 2-player synchronized multiplayer matches with real-time leaderboard
- Integrated GSL dictionary with 100+ signs
- Works via polling (easy demo setup) or webhooks

🌐 **Web Frontend** (`wote_web/` — React + TypeScript)

- Learn module with structured lessons (alphabets, numbers, common words)
- Practice modes (quiz, freestyle, challenge)
- Live webcam sign detection using MediaPipe + TensorFlow.js
- Beautiful Duolingo-style UI with progress tracking and star rewards
- Mock detection mode for reliable demos

🤖 **ML Training Pipeline** (`model_training/`)

- Browser-based data collection UI for landmark annotation
- Hybrid neural network training (dense + sequence models)
- Export to TensorFlow.js for browser inference
- Dataset analysis and quality validation tools

📱 **Supports Multiple Media Formats**

- Videos: `.mp4`, `.mov`, `.avi`
- Images: `.png`, `.jpg`, `.jpeg`

## Repository Structure

```
codeworks/
├── wote_gslbot/                    # Telegram bot + game engine
│   ├── bot_enhanced.py             # Main bot (polling + webhook support)
│   ├── game_database.py            # Game rooms, scoring, leaderboard logic
│   ├── database.py                 # Media and dictionary scanner
│   ├── config.py                   # Configuration with env vars
│   ├── requirements.txt            # Python dependencies
│   ├── data/                       # Media assets
│   │   ├── dictionary.json         # GSL dictionary entries
│   │   ├── game_data.json          # Game questions
│   │   └── videos/                 # Sign videos and images
│   ├── DEMO_GUIDE.md               # Step-by-step demo instructions
│   ├── VISUAL_SHOWCASE.md          # Feature showcase
│   └── __pycache__/
│
├── wote_web/                       # React web frontend (git submodule)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.tsx            # Landing page
│   │   │   ├── Learn.tsx           # Lesson categories + progress
│   │   │   ├── Lesson.tsx          # Individual lesson items with video
│   │   │   ├── Practice.tsx        # Mode selection (quiz/freestyle/challenge)
│   │   │   ├── PracticeEnhanced.tsx # Quiz UI with sign detection
│   │   │   ├── PracticeComplete.tsx # Score screen
│   │   │   └── Translate.tsx       # Dictionary lookup
│   │   ├── components/
│   │   │   ├── Header.tsx          # Navigation bar
│   │   │   └── WebcamDetector.tsx  # MediaPipe sign detection
│   │   └── App.tsx
│   ├── public/
│   │   ├── videos/
│   │   │   ├── alphabets/          # A-Z sign videos
│   │   │   ├── numbers/            # 0-9 sign videos
│   │   │   └── words/              # Common word videos
│   │   └── labels.json             # Label mappings
│   ├── index.html
│   └── eslint.config.js
│
├── model_training/                 # ML pipeline for GSL models
│   ├── train_hybrid_model.py       # Training script (hybrid architecture)
│   ├── export_manual.py            # TF.js model export helper
│   ├── analyze_dat.py              # Dataset analysis tools
│   ├── requirements.txt            # Python dependencies
│   ├── collect/
│   │   ├── server.py               # Flask data collection server
│   │   └── data_collection.html    # Browser-based annotation UI
│   ├── samples/                    # Example JSONL landmark files
│   └── README.md                   # ML pipeline documentation
│
├── demo/                           # Demo videos & thumbnails
│   ├── demo_playthrough.mp4        # 2-player game demo
│   ├── demo_sign_detection.mp4     # Sign detection demo
│   ├── thumbnail_playthrough.png
│   └── thumbnail_detection.png
│
├── docs/                           # Documentation & presentations
│   └── SignifyGhana_Presentation.pdf
│
├── .gitmodules                     # Git submodule config
├── README.md                       # This file
└── .env.example                    # Environment variables template
```

## Quick Start

### Prerequisites

- **Python** 3.10+ (for bot and ML pipeline)
- **Node.js** 18+ (for web frontend)
- **npm** or **yarn** (frontend package manager)
- **Telegram Bot Token** (from @BotFather)
- **Git** with submodule support

### 1. Clone with Submodules

```bash
git clone https://github.com/saintdannyyy/Unicef-Startup-Lab-Hackathon
cd codeworks
git submodule update --init --recursive
```

This clones the main repo and the `wote_web` frontend submodule.

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# Get your token from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
```

Or set it via PowerShell:

```powershell
$env:TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
```

### 3. Run the Telegram Bot

**Fastest way to demo (polling mode):**

```powershell
cd wote_gslbot
python -m pip install -r requirements.txt
python bot_enhanced.py
```

The bot will start polling for updates. No webhook/ngrok needed for demos!

**Note:** Stop other Telegram clients (Desktop/Web) using the same token to avoid conflicts.

### 4. Run the Web Frontend

**In a new terminal:**

```powershell
cd wote_web
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`

**To expose to judges (use ngrok):**

```bash
ngrok http 5173
```

### 5. Optional — Webhook Mode

For production deployments, use webhook instead of polling:

```powershell
# Create a Flask adapter (example in wote_gslbot/DEMO_GUIDE.md)
python webhook_adapter.py
```

Then expose with ngrok and set the webhook URL in Telegram BotFather settings.

## Core Features Explained

### Telegram Bot (`wote_gslbot/`)

**Game Modes:**

1. **Solo Practice** — 3-question quick quiz

   - Random questions from dictionary
   - Instant feedback (correct/incorrect)
   - Score tracking

2. **Multiplayer (2-Player)** — Synchronized 5-question match

   - Create room with friend
   - Both answer same questions simultaneously
   - Speed + accuracy scoring
   - Leaderboard with rank and stars

3. **Dictionary** — Browse 100+ GSL signs
   - Video/image for each sign
   - Phonetic description
   - Usage examples

**Key Implementation Details:**

- ✅ Exact answer matching (case-insensitive, no substring matches)
- ✅ Robust room/callback ID handling with underscores
- ✅ Active game lifecycle management (prevents stale-state errors)
- ✅ Supports both image and video media types
- ✅ Environment-based configuration (TELEGRAM_BOT_TOKEN required)

### Web Frontend (`wote_web/`)

**Pages:**

| Page             | Purpose        | Features                                             |
| ---------------- | -------------- | ---------------------------------------------------- |
| Home             | Landing page   | Intro, quick links to Learn/Practice                 |
| Learn            | Lesson browser | Categories (alphabets, numbers, words) with progress |
| Lesson           | Video viewer   | Individual signs with video playback + detector      |
| Practice         | Mode selector  | Quiz, Freestyle, Challenge modes                     |
| PracticeEnhanced | Quiz UI        | Live feedback, score tracking, star rewards          |
| PracticeComplete | Results screen | Score summary, retry/home buttons                    |
| Translate        | Dictionary     | Search signs, filter by category                     |

**Sign Detection:**

- Uses **MediaPipe** for hand landmark detection
- **TensorFlow.js** for sign classification in browser
- **Mock mode** fallback for demos (when MediaPipe unavailable)
- Real-time webcam feedback with confidence scores

### ML Pipeline (`model_training/`)

**Workflow:**

1. **Collect** — Browser-based UI captures hand landmarks via MediaPipe
2. **Train** — Hybrid neural network (dense + LSTM layers)
3. **Export** — Convert to TensorFlow.js for browser
4. **Deploy** — Copy model to frontend `public/` folder

**Supported Model Types:**

- Dense neural network (for static signs)
- LSTM sequence model (for dynamic gestures)
- Hybrid (uses both for robust classification)

## Configuration & Customization

### Adding New Signs

1. **For Bot Dictionary:**

   - Add video/image file to `wote_gslbot/data/videos/words/`
   - Name by sign meaning (e.g., `HELLO.mp4`, `GOODBYE.png`)
   - Update `wote_gslbot/data/dictionary.json` with metadata

2. **For Web Lessons:**
   - Add to appropriate folder: `wote_web/public/videos/alphabets/`, `numbers/`, or `words/`
   - Files auto-discovered by frontend

### Environment Setup

Create `.env` or set environment variables:

```env
# Required
TELEGRAM_BOT_TOKEN=<your_bot_token_from_BotFather>

# Optional (defaults shown)
BOT_WEBHOOK_PORT=5000
DATABASE_PATH=./game_database.db
```

### Customizing Practice Questions

Edit `wote_gslbot/data/game_data.json` to add/modify quiz questions.

Format:

```json
{
  "questions": [
    {
      "id": "q1",
      "question": "What does this sign mean?",
      "answer": "HELLO",
      "image": "hello.png",
      "options": ["HELLO", "GOODBYE", "THANKS", "SORRY"]
    }
  ]
}
```

## Troubleshooting

| Issue                                      | Solution                                                                             |
| ------------------------------------------ | ------------------------------------------------------------------------------------ |
| `TELEGRAM_BOT_TOKEN not set`               | Set env var: `$env:TELEGRAM_BOT_TOKEN="..."` or add to `.env`                        |
| `Conflict: terminated by other getUpdates` | Close other Telegram clients (Desktop/Web) using same token                          |
| `MediaPipe wasm errors`                    | Enable mock detection mode in `WebcamDetector.tsx` or pin `@mediapipe/hands` version |
| `Not enough words`                         | Add ≥4 media files to `wote_gslbot/data/videos/words/`                               |
| Frontend won't connect to bot              | Ensure bot is running on localhost, check CORS settings                              |
| Model inference slow                       | Use mock detection or optimize model in `model_training/`                            |

## Demo Checklist

Before showing to judges:

- [ ] Bot running (polling mode, no ngrok needed)
- [ ] At least 5 reliable media assets in `wote_gslbot/data/videos/words/`
- [ ] Frontend running locally or via ngrok
- [ ] Two Telegram accounts for 2-player demo (or solo practice as fallback)
- [ ] Mock detection enabled if MediaPipe unstable on judge machine
- [ ] Test full flow: Learn → Practice → Quiz → Results

See `wote_gslbot/DEMO_GUIDE.md` for step-by-step walkthrough.

## API Documentation

### Telegram Bot Commands

```
/start — Show main menu
/play — Start solo practice (3 questions)
/multiplayer — 2-player mode
  /create_room — Create a room
  /join_room <room_id> — Join room
/dictionary — Browse all signs
/about — Project info & UNICEF award
```

### Game Database API (`wote_gslbot/game_database.py`)

```python
# Create a game
game = GameEngine.create_game(user_id, difficulty="easy")

# Submit answer
result = GameEngine.check_answer(game_id, answer)  # returns {"correct": bool, "score": int}

# Get leaderboard
leaderboard = GameEngine.get_leaderboard(limit=10)
```

### Web Frontend Routes

```
GET  /               — Home page
GET  /learn          — Lesson categories
GET  /lesson/:category — Individual lesson items
GET  /practice       — Mode selector
GET  /translate      — Dictionary search
POST /api/detect     — Sign detection (if API enabled)
```

## Contributing

We welcome contributions! Here's how:

1. **Add signs to dictionary:**

   - Add media to `wote_gslbot/data/videos/words/`
   - Update `wote_gslbot/data/dictionary.json`

2. **Improve models:**

   - Collect data using `model_training/collect/`
   - Train with `model_training/train_hybrid_model.py`
   - Export with `model_training/export_manual.py`

3. **Frontend features:**

   - Work in `wote_web/` submodule
   - Follow React/TypeScript conventions
   - Submit PR to `lordofcodess/sign_language`

4. **Report bugs:**
   - Open GitHub issue with reproduction steps
   - Include bot logs, browser console errors, screenshots

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│        Telegram Users                       │
└────────────┬────────────────────────────────┘
             │
    ┌────────▼────────┐
    │  Bot (Polling)  │
    │  bot_enhanced   │
    └────────┬────────┘
             │
    ┌────────▼────────────┐
    │  Game Engine        │
    │  game_database.py   │
    └────────┬────────────┘
             │
    ┌────────▼────────────┐
    │  Media/Dictionary   │
    │  database.py        │
    └─────────────────────┘

┌─────────────────────────────────────────────┐
│        Web Browser (React)                   │
├─────────────────────────────────────────────┤
│ ┌──────┬──────┬──────┬──────┬──────────┐   │
│ │Learn │Lesson│Practice │Translate   │   │
│ └──────┴──────┴──────┴──────┴──────────┘   │
│ ┌──────────────────────────────────────┐   │
│ │  WebcamDetector (MediaPipe/TF.js)   │   │
│ └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│    ML Pipeline (model_training)             │
├─────────────────────────────────────────────┤
│ Collect → Train → Export → Deploy           │
└─────────────────────────────────────────────┘
```

## Performance & Optimization

- **Bot:** Handles 100+ concurrent users with polling
- **Frontend:** Lightweight React (Vite bundling ~300KB gzipped)
- **Sign Detection:** ~100ms inference on modern browsers (CPU)
- **Database:** SQLite for local leaderboard/rooms (~10MB max)

For scaling:

- Use webhook + load balancer instead of polling
- Deploy frontend to CDN (Vercel, Netlify)
- Use cloud DB (Firebase/Supabase) for multiplayer leaderboard

## License

MIT — See LICENSE file or [opensource.org/licenses/MIT](https://opensource.org/licenses/MIT)

## Acknowledgements

## Presentation & Demo Videos

### 🎬 Bi-Directional Conversation Module

Experience the interactive two-way conversation flow with real-time sign detection and response:

<details>
<summary><strong>▶ Watch Demo: Bi-directional Conversation (2 min)</strong></summary>

https://github.com/saintdannyyy/pre-unicef_gsl-hackathon_codeworks/assets/videos/Bi-directional_converstaion_module.mp4

</details>

### 📚 Learning Module Demo

Walkthrough of the structured learning experience with lessons, practice modes, and sign detection:

<details>
<summary><strong>▶ Watch Demo: Learning Module (2 min)</strong></summary>

https://github.com/saintdannyyy/pre-unicef_gsl-hackathon_codeworks/assets/videos/Learning_module.mp4

</details>

### 📊 Presentation Slides

Complete presentation used for UNICEF Startup Lab judges:

- **📄 [TWILIGHT Presentation](./docs/TWILIGHT.pptx)** — Download and view (PowerPoint format)

---

## Acknowledgements

- **UNICEF Startup Lab** — 3rd Place, Best AI Implementation Award
- **MediaPipe & TensorFlow.js** — Sign detection frameworks
- **python-telegram-bot** — Bot framework
- **React & Vite** — Frontend framework
- All community contributors and testers

## Contact & Support

- 📧 **Issues:** [GitHub Issues](https://github.com/saintdannyyy/pre-unicef_gsl-hackathon_codeworks/issues)
- 💬 **Telegram:** Message maintainer for urgent demo support
- 📱 **Bot:** [@wote_gslbot](https://t.me/wote_gslbot) on Telegram

---

**Last Updated:** November 2025  
**Repository:** [github.com/saintdannyyy/pre-unicef_gsl-hackathon_codeworks](https://github.com/saintdannyyy/pre-unicef_gsl-hackathon_codeworks)  
**Award:** UNICEF Startup Lab 🏆 3rd Place | Best AI Implementation
