import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import confetti from "canvas-confetti";
import {
  ArrowLeft,
  Star,
  Flame,
  Video,
  SkipForward,
  CheckCircle,
  X,
  Lightbulb,
  Hand,
  Trophy,
  Sparkles,
  Eye,
  RotateCcw,
  Users,
  Send,
  MessageCircle,
} from "lucide-react";
import SignDetector from "../components/SignDetector";

interface PracticeItem {
  sign: string;
  category: "alphabet" | "number" | "word";
  videoUrl?: string;
  description?: string;
}

type FeedbackState =
  | "idle"
  | "checking"
  | "correct"
  | "incorrect"
  | "encouraging";

export default function Practice() {
  const navigate = useNavigate();
  const location = useLocation();

  // Get practice items from navigation state or use defaults
  const [practiceItems] = useState<PracticeItem[]>(
    location.state?.items || [
      { sign: "A", category: "alphabet" },
      { sign: "B", category: "alphabet" },
      { sign: "C", category: "alphabet" },
      { sign: "1", category: "number" },
      { sign: "2", category: "number" },
    ]
  );

  const [currentIndex, setCurrentIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [attempts, setAttempts] = useState(0);
  const [feedback, setFeedback] = useState<FeedbackState>("idle");
  const [showVideo, setShowVideo] = useState(false);
  const [consecutiveCorrect, setConsecutiveCorrect] = useState(0);
  const [currentPrediction, setCurrentPrediction] = useState<string | null>(
    null
  );
  const [currentConfidence, setCurrentConfidence] = useState(0);
  const [showChallengeModal, setShowChallengeModal] = useState(false);

  const currentItem = practiceItems[currentIndex];
  const progress = ((currentIndex + 1) / practiceItems.length) * 100;

  // Handle successful sign detection
  const handleMatch = () => {
    setFeedback("correct");
    setScore(score + 10);
    setConsecutiveCorrect(consecutiveCorrect + 1);

    // Play success sound
    playSound("success");

    // Trigger confetti celebration
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ["#58cc02", "#89e219", "#ffc800"],
    });

    // Extra confetti for streak
    if (consecutiveCorrect >= 2) {
      setTimeout(() => {
        confetti({
          particleCount: 50,
          angle: 60,
          spread: 55,
          origin: { x: 0 },
        });
        confetti({
          particleCount: 50,
          angle: 120,
          spread: 55,
          origin: { x: 1 },
        });
      }, 200);
    }

    // Move to next sign after celebration
    setTimeout(() => {
      if (currentIndex < practiceItems.length - 1) {
        setCurrentIndex(currentIndex + 1);
        setAttempts(0);
        setFeedback("idle");
        setShowVideo(false);
        setCurrentPrediction(null);
        setCurrentConfidence(0);
      } else {
        // Practice complete!
        confetti({
          particleCount: 200,
          spread: 120,
          origin: { y: 0.5 },
        });

        setTimeout(() => {
          navigate("/practice-complete", {
            state: {
              score,
              total: practiceItems.length,
              accuracy: Math.round((score / (practiceItems.length * 10)) * 100),
            },
          });
        }, 1500);
      }
    }, 2500);
  };

  const handleSignDetected = (sign: string, confidence: number) => {
    setCurrentPrediction(sign);
    setCurrentConfidence(confidence);
  };

  // Handle when user checks their sign
  const handleCheck = () => {
    if (!currentPrediction) return;

    setAttempts(attempts + 1);
    setFeedback("checking");

    setTimeout(() => {
      if (
        currentPrediction.toUpperCase() === currentItem.sign.toUpperCase() &&
        currentConfidence >= 60
      ) {
        handleMatch();
      } else {
        setFeedback("incorrect");
        setConsecutiveCorrect(0);

        // After 2 attempts, show encouragement
        if (attempts >= 1) {
          setTimeout(() => {
            setFeedback("encouraging");
          }, 2000);
        } else {
          setTimeout(() => {
            setFeedback("idle");
          }, 2000);
        }
      }
    }, 1000);
  };

  // Skip to next sign
  const handleSkip = () => {
    if (currentIndex < practiceItems.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setAttempts(0);
      setFeedback("idle");
      setShowVideo(false);
      setConsecutiveCorrect(0);
      setCurrentPrediction(null);
      setCurrentConfidence(0);
    }
  };

  // Challenge friend via Telegram
  const handleChallengeButton = () => {
    setShowChallengeModal(true);
  };

  const sendTelegramChallenge = (friendContact: string) => {
    // Create challenge message
    const challengeText = `🤟 GSL Sign Language Challenge! 🤟\n\nI challenge you to beat my score of ${score} points!\n\n📚 Practice: ${
      practiceItems.length
    } signs\n⭐ My Score: ${score}\n🎯 Accuracy: ${Math.round(
      (score / (practiceItems.length * 10)) * 100
    )}%\n\nJoin me on GSL Learning App and accept this challenge!`;

    // Encode challenge data
    const challengeData = btoa(
      JSON.stringify({
        score,
        category: currentItem.category,
        total: practiceItems.length,
        challenger: "You",
        timestamp: Date.now(),
      })
    );

    // Deep link to app with challenge
    const appLink = `${window.location.origin}/challenge/${challengeData}`;

    // Open Telegram with pre-filled message
    const telegramUrl = `https://t.me/share/url?url=${encodeURIComponent(
      appLink
    )}&text=${encodeURIComponent(challengeText)}`;

    window.open(telegramUrl, "_blank");
    setShowChallengeModal(false);
  };

  const playSound = (type: "success" | "error") => {
    // Simple audio feedback using Web Audio API
    const audioContext = new AudioContext();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    if (type === "success") {
      oscillator.frequency.value = 523.25; // C5
      oscillator.start();
      oscillator.frequency.exponentialRampToValueAtTime(
        659.25,
        audioContext.currentTime + 0.1
      ); // E5
      gainNode.gain.exponentialRampToValueAtTime(
        0.01,
        audioContext.currentTime + 0.3
      );
    } else {
      oscillator.frequency.value = 200;
      gainNode.gain.exponentialRampToValueAtTime(
        0.01,
        audioContext.currentTime + 0.2
      );
    }

    setTimeout(() => oscillator.stop(), 300);
  };

  const encouragementMessages = [
    "Almost there! Try again!",
    "You've got this! One more time!",
    "So close! Keep going!",
    "Don't give up! You can do it!",
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Duolingo-style Progress Bar - GREEN */}
      <div className="bg-[#58cc02] shadow-lg sticky top-0 z-10">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between mb-3">
            <button
              onClick={() => navigate(-1)}
              className="text-white font-bold hover:opacity-80 flex items-center gap-2"
            >
              <ArrowLeft size={24} />
            </button>

            <div className="flex items-center gap-4">
              {/* Streak Counter - ORANGE flame */}
              <div className="flex items-center gap-2 bg-[#ff9600] px-4 py-2 rounded-2xl shadow-md">
                <Flame className="text-white" size={20} />
                <span className="font-black text-white text-lg">
                  {consecutiveCorrect}
                </span>
              </div>

              {/* Score - YELLOW star */}
              <div className="flex items-center gap-2 bg-[#ffc800] px-4 py-2 rounded-2xl shadow-md">
                <Star className="text-white" size={20} />
                <span className="font-black text-white text-lg">{score}</span>
              </div>

              {/* Challenge Friend Button */}
              <button
                onClick={handleChallengeButton}
                className="flex items-center gap-2 bg-white hover:bg-gray-100 text-[#58cc02] font-bold px-4 py-2 rounded-2xl shadow-md transition-colors"
              >
                <Users size={20} />
                <span>Challenge</span>
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="relative h-4 bg-white/30 rounded-full overflow-hidden">
            <motion.div
              className="absolute h-full bg-white shadow-inner"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
            <div className="absolute inset-0 flex items-center justify-center text-xs font-black text-[#58cc02]">
              {currentIndex + 1} / {practiceItems.length}
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Current Sign Display - GREEN Duolingo style */}
          <motion.div
            key={currentItem.sign}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white border-2 border-[#e5e5e5] rounded-3xl shadow-xl overflow-hidden mb-6"
          >
            {/* Large Sign Label */}
            <div className="bg-[#58cc02] text-white py-6 text-center">
              <div className="text-7xl font-black mb-2">{currentItem.sign}</div>
              <div className="text-xl font-bold flex items-center justify-center gap-2">
                <Hand size={24} />
                <span>Practice this sign</span>
              </div>
            </div>

            {/* Practice Area */}
            <div className="p-6">
              {/* Video Tutorial (Optional) */}
              <AnimatePresence>
                {showVideo && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="mb-6"
                  >
                    <div className="bg-black rounded-2xl overflow-hidden border-4 border-[#e5e5e5]">
                      <video
                        src={
                          currentItem.videoUrl ||
                          `/videos/${currentItem.category}s/${currentItem.sign}.mp4`
                        }
                        controls
                        autoPlay
                        muted
                        loop
                        className="w-full h-full object-contain"
                      />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Camera + Status Side by Side */}
              <div className="grid grid-cols-2 gap-6 mb-6">
                {/* Sign Detector Component - Left */}
                <div className="relative border-4 border-[#e5e5e5] rounded-2xl overflow-hidden">
                  <SignDetector
                    targetSign={currentItem.sign}
                    onSignDetected={handleSignDetected}
                    onMatch={handleMatch}
                    confidenceThreshold={60}
                  />

                  {/* Feedback Overlays */}
                  <AnimatePresence>
                    {/* Checking */}
                    {feedback === "checking" && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="absolute inset-0 bg-[#1cb0f6]/95 flex items-center justify-center"
                      >
                        <div className="text-center text-white">
                          <Sparkles
                            className="mx-auto mb-4 animate-pulse"
                            size={96}
                          />
                          <p className="text-4xl font-black">Analyzing...</p>
                        </div>
                      </motion.div>
                    )}

                    {/* Correct - GREEN */}
                    {feedback === "correct" && (
                      <motion.div
                        initial={{ scale: 0.5, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="absolute inset-0 bg-[#58cc02] flex items-center justify-center"
                      >
                        <div className="text-center text-white">
                          <CheckCircle
                            className="mx-auto mb-4"
                            size={140}
                            strokeWidth={3}
                          />
                          <p className="text-5xl font-black mb-3">Perfect!</p>
                          <div className="flex items-center justify-center gap-3">
                            <Trophy className="text-[#ffc800]" size={40} />
                            <p className="text-3xl font-bold">+10 XP</p>
                          </div>
                        </div>
                      </motion.div>
                    )}

                    {/* Incorrect - RED */}
                    {feedback === "incorrect" && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.5 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0 }}
                        className="absolute inset-0 bg-[#ff4b4b] flex items-center justify-center"
                      >
                        <div className="text-center text-white">
                          <X
                            className="mx-auto mb-4"
                            size={120}
                            strokeWidth={4}
                          />
                          <p className="text-4xl font-black">Not quite!</p>
                          <p className="text-2xl font-bold mt-2">Try again</p>
                        </div>
                      </motion.div>
                    )}

                    {/* Encouraging - ORANGE */}
                    {feedback === "encouraging" && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="absolute inset-0 bg-[#ff9600]/95 flex items-center justify-center"
                      >
                        <div className="text-center text-white p-8">
                          <Lightbulb className="mx-auto mb-4" size={100} />
                          <p className="text-3xl font-black mb-4">
                            {
                              encouragementMessages[
                                Math.floor(
                                  Math.random() * encouragementMessages.length
                                )
                              ]
                            }
                          </p>
                          <p className="text-xl font-bold mb-6">
                            Need help? Watch the tutorial!
                          </p>
                          <button
                            onClick={() => {
                              setShowVideo(true);
                              setFeedback("idle");
                            }}
                            className="bg-white text-[#ff9600] px-8 py-4 rounded-2xl font-black text-xl hover:scale-105 transition-transform flex items-center gap-2 mx-auto shadow-lg"
                          >
                            <Video size={28} />
                            <span>Watch Tutorial</span>
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* Status & Instructions - Right */}
                <div className="bg-[#f7f7f7] rounded-2xl p-8 flex flex-col justify-center border-4 border-[#e5e5e5]">
                  {/* Target Sign Reminder */}
                  <div className="bg-white border-4 border-[#58cc02] rounded-2xl p-6 text-center mb-6 shadow-lg">
                    <div className="text-sm text-[#58cc02] font-bold mb-2 uppercase tracking-wide">
                      Your Challenge:
                    </div>
                    <div className="text-7xl font-black text-[#58cc02]">
                      {currentItem.sign}
                    </div>
                  </div>

                  <div className="text-center mb-8">
                    <div className="flex justify-center mb-4">
                      {feedback === "idle" && (
                        <Eye className="text-gray-600" size={80} />
                      )}
                      {feedback === "checking" && (
                        <Sparkles
                          className="text-[#1cb0f6] animate-pulse"
                          size={80}
                        />
                      )}
                      {feedback === "correct" && (
                        <CheckCircle className="text-[#58cc02]" size={80} />
                      )}
                      {feedback === "incorrect" && (
                        <RotateCcw className="text-[#ff9600]" size={80} />
                      )}
                      {feedback === "encouraging" && (
                        <Lightbulb className="text-[#ff9600]" size={80} />
                      )}
                    </div>
                    <div className="text-2xl font-bold text-gray-800 mb-4">
                      {feedback === "idle" && "Show your sign when ready"}
                      {feedback === "checking" && "Checking your sign..."}
                      {feedback === "correct" && "Amazing! Next sign..."}
                      {feedback === "incorrect" && "Oops! Try again"}
                      {feedback === "encouraging" && "Need some help?"}
                    </div>
                    <div className="text-gray-600 font-bold flex items-center justify-center gap-2">
                      <RotateCcw size={18} />
                      <span>Attempt {attempts + 1}</span>
                    </div>
                  </div>

                  {/* Current Detection */}
                  {currentPrediction && feedback === "idle" && (
                    <div className="bg-white rounded-2xl p-5 text-center shadow-md border-2 border-[#e5e5e5]">
                      <div className="text-sm text-gray-600 font-bold mb-2 uppercase tracking-wide">
                        Detecting:
                      </div>
                      <div className="text-4xl font-black text-[#1cb0f6]">
                        {currentPrediction}
                      </div>
                      <div className="text-sm text-gray-500 mt-2 font-bold">
                        Confidence: {currentConfidence}%
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Action Buttons - Duolingo Style */}
              <div className="grid grid-cols-3 gap-4">
                {/* Show/Hide Video - BLUE */}
                <button
                  onClick={() => setShowVideo(!showVideo)}
                  className="bg-[#1cb0f6] hover:bg-[#1899d6] text-white font-black py-5 rounded-2xl text-lg flex items-center justify-center gap-2 transition-all shadow-lg border-b-4 border-[#1899d6] hover:border-b-2 active:border-b-0"
                >
                  <Video size={24} />
                  <span>{showVideo ? "Hide" : "Show"}</span>
                </button>

                {/* Check Sign - GREEN */}
                <button
                  onClick={handleCheck}
                  disabled={
                    feedback === "checking" ||
                    feedback === "correct" ||
                    !currentPrediction
                  }
                  className="bg-[#58cc02] hover:bg-[#58a700] disabled:bg-gray-400 disabled:border-gray-500 text-white font-black py-5 rounded-2xl text-lg transition-all shadow-lg border-b-4 border-[#58a700] hover:border-b-2 active:border-b-0 disabled:border-b-4 flex items-center justify-center gap-2"
                >
                  <CheckCircle size={24} />
                  <span>CHECK</span>
                </button>

                {/* Skip - GRAY */}
                <button
                  onClick={handleSkip}
                  disabled={feedback === "checking" || feedback === "correct"}
                  className="bg-[#e5e5e5] hover:bg-[#d0d0d0] disabled:bg-gray-300 text-gray-700 font-black py-5 rounded-2xl text-lg transition-all shadow-lg border-b-4 border-[#afafaf] hover:border-b-2 active:border-b-0 disabled:border-b-4 flex items-center justify-center gap-2"
                >
                  <span>SKIP</span>
                  <SkipForward size={24} />
                </button>
              </div>
            </div>
          </motion.div>

          {/* Navigation */}
          <div className="flex justify-between">
            <button
              onClick={() => navigate(-1)}
              className="px-6 py-3 bg-white border-2 border-[#e5e5e5] hover:bg-gray-50 rounded-2xl font-bold flex items-center gap-2 shadow-md"
            >
              <ArrowLeft size={20} />
              <span>Back</span>
            </button>

            {/* Exit Button */}
            <button
              onClick={() => navigate("/learn")}
              className="px-6 py-3 bg-[#ff4b4b] hover:bg-[#ea2b2b] text-white rounded-2xl font-black shadow-lg border-b-4 border-[#ea2b2b] hover:border-b-2"
            >
              Exit Practice
            </button>
          </div>
        </div>
      </div>

      {/* Challenge Modal */}
      <AnimatePresence>
        {showChallengeModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowChallengeModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-3xl p-8 max-w-md w-full shadow-2xl"
            >
              <div className="text-center mb-6">
                <Users className="mx-auto mb-4 text-[#58cc02]" size={80} />
                <h2 className="text-3xl font-black text-gray-800 mb-2">
                  Challenge a Friend!
                </h2>
                <p className="text-gray-600 font-bold">
                  Share your score and challenge them to beat it
                </p>
              </div>

              <div className="bg-[#f7f7f7] rounded-2xl p-6 mb-6 border-2 border-[#e5e5e5]">
                <div className="flex justify-between items-center mb-3">
                  <span className="text-gray-600 font-bold">Your Score:</span>
                  <div className="flex items-center gap-2">
                    <Star className="text-[#ffc800]" size={24} />
                    <span className="text-2xl font-black text-[#58cc02]">
                      {score}
                    </span>
                  </div>
                </div>
                <div className="flex justify-between items-center mb-3">
                  <span className="text-gray-600 font-bold">Signs:</span>
                  <span className="text-xl font-black text-gray-800">
                    {practiceItems.length}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600 font-bold">Streak:</span>
                  <div className="flex items-center gap-2">
                    <Flame className="text-[#ff9600]" size={24} />
                    <span className="text-xl font-black text-gray-800">
                      {consecutiveCorrect}
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => sendTelegramChallenge("")}
                className="w-full bg-[#0088cc] hover:bg-[#006699] text-white font-black py-5 rounded-2xl text-xl flex items-center justify-center gap-3 transition-all shadow-lg border-b-4 border-[#006699] hover:border-b-2 mb-3"
              >
                <Send size={28} />
                <span>Share on Telegram</span>
              </button>

              <button
                onClick={() => setShowChallengeModal(false)}
                className="w-full bg-[#e5e5e5] hover:bg-[#d0d0d0] text-gray-700 font-bold py-4 rounded-2xl transition-all"
              >
                Cancel
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
