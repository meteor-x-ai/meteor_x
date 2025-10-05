# 🌠 MeteorX — Meteor Impact Simulation Game

**Real-time multiplayer game where you defend Earth from meteor strikes using AI-powered impact calculations!**

[![Deploy](https://img.shields.io/badge/Deploy-Railway-blueviolet)](https://meteorx-production.up.railway.app)
[![Frontend](https://img.shields.io/badge/Frontend-Netlify-00C7B7)](https://profound-faloodeh-f91fc7.netlify.app)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org)
[![Vue](https://img.shields.io/badge/Vue-3-42b883)](https://vuejs.org)

---

## 🎮 Features

- 🚀 **Real-time multiplayer** — Play with friends using WebSocket rooms
- 🤖 **AI-powered** — Google Gemini generates realistic meteor scenarios
- 🎯 **Strategic gameplay** — Choose between IGNORE, EVACUATION, BUNKER, or ROCKET
- 🌍 **Realistic physics** — Accurate impact calculations based on mass, speed, and angle
- 🔥 **Beautiful UI** — Modern Vue 3 interface with particle effects

---

## 🛠️ Tech Stack

### Backend
- **Flask** — Python web framework
- **Flask-SocketIO** — Real-time WebSocket communication
- **Firebase Admin** — Authentication & Firestore database
- **Google Gemini AI** — Meteor generation & casualty calculations
- **Gunicorn + Gevent** — Production server

### Frontend
- **Vue 3** — Progressive JavaScript framework
- **TypeScript** — Type-safe development
- **Vite** — Lightning-fast build tool
- **Particles.js** — Interactive backgrounds

---

## 🚀 Quick Start (Local Development)

### Prerequisites

Make sure you have installed:
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Firebase project** with Firestore enabled
- **Google Gemini API key** ([Get one](https://makersuite.google.com/app/apikey))

---

## 📦 Backend Setup

### 1️⃣ Navigate to backend folder
```bash
cd backend
```

### 2️⃣ Create virtual environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure environment variables
Create a `.env` file in the `backend/` folder:

```bash
# backend/.env
GEMINI_API_KEY=your_gemini_api_key_here
FRONTEND_URL=http://localhost:5173
```

### 5️⃣ Add Firebase credentials
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Project Settings → Service Accounts → Generate New Private Key
3. Save the JSON file as `backend/firebase-adminsdk.json`

**OR** set as environment variable:
```bash
export FIREBASE_CREDENTIALS='{"type":"service_account",...}'  # Full JSON
```

### 6️⃣ Run the backend server
```bash
python app.py
```

✅ **Backend running at:** `http://localhost:5000`

---

## 🎨 Frontend Setup

### 1️⃣ Navigate to frontend folder
```bash
cd frontend
```

### 2️⃣ Install dependencies
```bash
npm install
```

### 3️⃣ Configure API endpoint
Update `frontend/src/repository/backendPath.ts`:

```typescript
// For local development
export const BACKEND_URL = "http://localhost:5000";

// For production
// export const BACKEND_URL = "https://meteorx-production.up.railway.app";
```

### 4️⃣ Run development server
```bash
npm run dev
```

✅ **Frontend running at:** `http://localhost:5173`

---

## 🎯 How to Play

### 1. **Create Account**
- Click "Sign Up" on the main page
- Enter username and password
- You're in! 🎉

### 2. **Create or Join Room**
- Create a new 4-player room (you become admin)
- OR join existing room with a code

### 3. **Start Game** (Admin only)
- Wait for 4 players to join
- Click "Start Game"
- Each player gets a defense card: 🚀 ROCKET, 🏚️ BUNKER, 🚶 EVACUATION, or ❌ IGNORE

### 4. **Defend Earth**
- AI generates a random meteor with real physics
- Analyze: mass, speed, angle, composition, distance
- Choose your card wisely!
- Correct choice = Earth saved ✅
- Wrong choice = -1 HP ❌
- Game over at 0 HP 💀

### 5. **Win Condition**
- Survive as many meteor strikes as possible
- Learn which defense works for each scenario
- Compete with friends for high scores!

---

## 📊 Project Structure

```
meteor_x/
├── backend/                    # Python Flask backend
│   ├── app.py                 # Main Flask app + SocketIO
│   ├── services/
│   │   ├── gemini_service.py  # AI meteor generation
│   │   └── meteor_generation.py
│   ├── firebase-adminsdk.json # Firebase credentials (git-ignored)
│   ├── requirements.txt       # Python dependencies
│   └── Procfile              # Railway deployment config
│
├── frontend/                  # Vue 3 frontend
│   ├── src/
│   │   ├── views/            # Page components
│   │   ├── components/       # Reusable components
│   │   ├── repository/       # API calls
│   │   ├── services/         # WebSocket & math services
│   │   └── router.ts         # Vue Router
│   ├── public/               # Static assets
│   ├── package.json
│   └── vite.config.ts
│
├── data/                     # Meteor scenarios dataset
│   ├── MeteorX_4.xlsx
│   └── scenarios.csv
│
└── README.md                 # You are here! 👋
```

---

## 🔥 Advanced Configuration

### Running with Production Server (Gunicorn)
```bash
cd backend
gunicorn --worker-class gevent -w 1 --timeout 120 app:app
```

### Building Frontend for Production
```bash
cd frontend
npm run build
# Output in frontend/dist/
```

### Environment Variables Reference

#### Backend `.env`
```bash
# Required
GEMINI_API_KEY=your_api_key          # Google Gemini API key
FIREBASE_CREDENTIALS='{...}'         # Firebase JSON (alternative to file)

# Optional
FRONTEND_URL=http://localhost:5173   # CORS allowed origin
ALLOWED_ORIGINS=http://localhost:5173,https://yourdomain.com
```

---

## 🐛 Troubleshooting

### ❌ "CORS policy" error
**Solution:** Make sure `FRONTEND_URL` in backend `.env` matches your frontend URL.

### ❌ Firebase initialization error
**Solution:** 
1. Check `firebase-adminsdk.json` exists in `backend/`
2. OR set `FIREBASE_CREDENTIALS` environment variable
3. Verify Firebase project has Firestore enabled

### ❌ "Gemini API key invalid"
**Solution:** 
1. Get new key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Update `GEMINI_API_KEY` in `.env`
3. Restart backend server

### ❌ WebSocket connection failed
**Solution:**
1. Check backend is running on port 5000
2. Update `backendPath.ts` with correct backend URL
3. Ensure gevent is installed (`pip install gevent`)

### ❌ "Module not found" errors
**Solution:**
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend  
cd frontend && npm install
```

---

## 🚀 Deploy to Production

### Backend (Railway)
1. Push code to GitHub
2. Connect Railway to your repo
3. Set environment variables in Railway dashboard:
   - `GEMINI_API_KEY`
   - `FIREBASE_CREDENTIALS` (full JSON)
   - `FRONTEND_URL` (your Netlify URL)
4. Railway auto-deploys! 🎉

### Frontend (Netlify)
1. Push code to GitHub
2. Connect Netlify to your repo
3. Build settings:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
4. Update `backendPath.ts` with Railway backend URL
5. Redeploy! 🚀

---

## 🤝 Contributing

Contributions welcome! 

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🌟 Star History

If this project helped you, give it a ⭐ on GitHub!

---

## 📧 Contact

Questions? Reach us at: [GitHub Issues](https://github.com/meteor-x-ai/meteor_x/issues)

---

**Made with ❤️ and lots of ☕ by the MeteorX team**

🌠 **Defend Earth. Save Humanity. Play MeteorX!** 🌍
