import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Camera,
  CameraOff,
  Mic,
  MicOff,
  Volume2,
  ArrowLeft,
  Copy,
  RefreshCw,
  Sparkles,
  AlertCircle,
} from "lucide-react";

type TranslateMode = "sign-to-text" | "text-to-sign";

export default function TranslateEnhanced() {
  const navigate = useNavigate();
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  const [mode, setMode] = useState<TranslateMode>("sign-to-text");
  const [cameraActive, setCameraActive] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [inputText, setInputText] = useState("");
  const [translatedText, setTranslatedText] = useState("");
  const [confidence, setConfidence] = useState(0);
  const [showCopied, setShowCopied] = useState(false);
  const [detectedWords, setDetectedWords] = useState<string[]>([]);

  useEffect(() => {
    // Initialize speech recognition
    if ("webkitSpeechRecognition" in window) {
      const recognition = new (window as any).webkitSpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;

      recognition.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0])
          .map((result) => result.transcript)
          .join("");

        setInputText(transcript);
      };

      recognitionRef.current = recognition;
    }

    return () => stopCamera();
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: "user" },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setCameraActive(true);
      }
    } catch (error) {
      console.error("Camera error:", error);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
    setIsRecording(false);
  };

  const toggleRecording = () => {
    if (!isRecording) {
      startCamera();
      setIsRecording(true);
      // Start sign detection
      simulateSignDetection();
    } else {
      stopCamera();
    }
  };

  const simulateSignDetection = () => {
    // Simulate detecting signs over time
    const words = ["HELLO", "HOW", "ARE", "YOU"];
    let index = 0;

    const interval = setInterval(() => {
      if (index < words.length) {
        setDetectedWords((prev) => [...prev, words[index]]);
        setTranslatedText((prev) =>
          prev ? `${prev} ${words[index]}` : words[index]
        );
        setConfidence(Math.random() * 20 + 80);
        index++;
      } else {
        clearInterval(interval);
        setIsRecording(false);
        stopCamera();
      }
    }, 2000);
  };

  const toggleVoiceInput = () => {
    if (!isListening && recognitionRef.current) {
      recognitionRef.current.start();
      setIsListening(true);
    } else if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const speakText = (text: string) => {
    if ("speechSynthesis" in window && text) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.lang = "en-US";
      window.speechSynthesis.speak(utterance);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(translatedText);
    setShowCopied(true);
    setTimeout(() => setShowCopied(false), 2000);
  };

  const clearAll = () => {
    setTranslatedText("");
    setInputText("");
    setDetectedWords([]);
    setConfidence(0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate("/")}
              className="flex items-center gap-2 text-gray-600 hover:text-gray-800"
            >
              <ArrowLeft size={20} />
              Back
            </button>
            <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
              <Sparkles className="text-purple-600" />
              GSL Translator
            </h1>
            <div className="w-20" /> {/* Spacer */}
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">
          {/* Mode Selector */}
          <div className="bg-white rounded-2xl p-2 shadow-lg mb-8 inline-flex">
            <button
              onClick={() => {
                setMode("sign-to-text");
                clearAll();
              }}
              className={`px-8 py-4 rounded-xl font-bold text-lg transition-all ${
                mode === "sign-to-text"
                  ? "bg-purple-600 text-white shadow-lg"
                  : "text-gray-600 hover:text-gray-800"
              }`}
            >
              🤟 Sign to Text
            </button>
            <button
              onClick={() => {
                setMode("text-to-sign");
                clearAll();
              }}
              className={`px-8 py-4 rounded-xl font-bold text-lg transition-all ${
                mode === "text-to-sign"
                  ? "bg-purple-600 text-white shadow-lg"
                  : "text-gray-600 hover:text-gray-800"
              }`}
            >
              📝 Text to Sign
            </button>
          </div>

          {/* Main Content */}
          <div className="grid md:grid-cols-2 gap-8">
            {/* Input Section */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white rounded-3xl p-8 shadow-xl"
            >
              <h2 className="text-2xl font-bold text-gray-800 mb-6">
                {mode === "sign-to-text"
                  ? "📹 Show Your Signs"
                  : "✍️ Enter Text"}
              </h2>

              {mode === "sign-to-text" ? (
                <div className="space-y-6">
                  {/* Camera Feed */}
                  <div className="aspect-video bg-black rounded-2xl overflow-hidden relative">
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      muted
                      className="w-full h-full object-cover mirror"
                    />

                    {!cameraActive && (
                      <div className="absolute inset-0 flex items-center justify-center bg-gray-900">
                        <div className="text-center text-white">
                          <CameraOff
                            size={64}
                            className="mx-auto mb-4 opacity-50"
                          />
                          <p className="text-lg">Camera ready to start</p>
                        </div>
                      </div>
                    )}

                    {/* Recording Indicator */}
                    {isRecording && (
                      <div className="absolute top-4 left-4 bg-red-500 text-white px-4 py-2 rounded-full flex items-center gap-2 animate-pulse">
                        <div className="w-3 h-3 bg-white rounded-full" />
                        Recording
                      </div>
                    )}

                    {/* Confidence Meter */}
                    {cameraActive && confidence > 0 && (
                      <div className="absolute bottom-4 left-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg p-3">
                        <div className="flex justify-between text-sm mb-2">
                          <span className="font-bold">
                            Detection Confidence
                          </span>
                          <span
                            className={
                              confidence > 80
                                ? "text-green-600 font-bold"
                                : "text-yellow-600"
                            }
                          >
                            {Math.round(confidence)}%
                          </span>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full transition-all ${
                              confidence > 80 ? "bg-green-500" : "bg-yellow-500"
                            }`}
                            style={{ width: `${confidence}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Camera Control */}
                  <button
                    onClick={toggleRecording}
                    className={`w-full font-bold py-4 rounded-xl text-xl transition-all ${
                      isRecording
                        ? "bg-red-500 hover:bg-red-600 text-white"
                        : "bg-purple-600 hover:bg-purple-700 text-white"
                    }`}
                  >
                    {isRecording ? (
                      <>
                        <CameraOff className="inline mr-2" size={24} />
                        Stop Recording
                      </>
                    ) : (
                      <>
                        <Camera className="inline mr-2" size={24} />
                        Start Recording
                      </>
                    )}
                  </button>

                  {/* Detected Words Timeline */}
                  {detectedWords.length > 0 && (
                    <div className="bg-purple-50 rounded-xl p-4">
                      <h3 className="font-bold text-sm text-gray-700 mb-3">
                        Detected Signs:
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {detectedWords.map((word, i) => (
                          <motion.div
                            key={i}
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="bg-white px-4 py-2 rounded-lg font-bold text-purple-600 shadow-sm"
                          >
                            {word}
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Text Input */}
                  <textarea
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Type or speak your message..."
                    className="w-full h-64 p-6 border-2 border-gray-200 rounded-2xl text-xl resize-none focus:outline-none focus:border-purple-400 transition-colors"
                  />

                  {/* Voice Input Button */}
                  <button
                    onClick={toggleVoiceInput}
                    className={`w-full font-bold py-4 rounded-xl text-xl transition-all ${
                      isListening
                        ? "bg-red-500 hover:bg-red-600 text-white animate-pulse"
                        : "bg-blue-600 hover:bg-blue-700 text-white"
                    }`}
                  >
                    {isListening ? (
                      <>
                        <MicOff className="inline mr-2" size={24} />
                        Stop Listening
                      </>
                    ) : (
                      <>
                        <Mic className="inline mr-2" size={24} />
                        Use Voice Input
                      </>
                    )}
                  </button>
                </div>
              )}
            </motion.div>

            {/* Output Section */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white rounded-3xl p-8 shadow-xl"
            >
              <h2 className="text-2xl font-bold text-gray-800 mb-6">
                {mode === "sign-to-text" ? "📝 Translation" : "🤟 Sign Videos"}
              </h2>

              {mode === "sign-to-text" ? (
                <div className="space-y-6">
                  {/* Translated Text Display */}
                  <div className="min-h-64 p-6 bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl">
                    {translatedText ? (
                      <p className="text-2xl text-gray-800 leading-relaxed">
                        {translatedText}
                      </p>
                    ) : (
                      <p className="text-xl text-gray-400 text-center py-20">
                        Your translation will appear here...
                      </p>
                    )}
                  </div>

                  {/* Action Buttons */}
                  {translatedText && (
                    <div className="flex gap-4">
                      <button
                        onClick={() => speakText(translatedText)}
                        className="flex-1 bg-green-500 hover:bg-green-600 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2"
                      >
                        <Volume2 size={20} />
                        Speak
                      </button>

                      <button
                        onClick={copyToClipboard}
                        className="flex-1 bg-blue-500 hover:bg-blue-600 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 relative"
                      >
                        <Copy size={20} />
                        Copy
                        <AnimatePresence>
                          {showCopied && (
                            <motion.div
                              initial={{ opacity: 0, y: -10 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0 }}
                              className="absolute -top-12 bg-gray-800 text-white px-3 py-1 rounded text-sm"
                            >
                              Copied! ✓
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </button>

                      <button
                        onClick={clearAll}
                        className="bg-gray-300 hover:bg-gray-400 text-gray-700 font-bold py-3 px-6 rounded-lg"
                      >
                        <RefreshCw size={20} />
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Sign Video Display */}
                  <div className="aspect-video bg-gray-900 rounded-2xl overflow-hidden flex items-center justify-center">
                    <div className="text-center text-white">
                      <p className="text-xl mb-4">
                        🎬 Sign videos will play here
                      </p>
                      <p className="text-sm text-gray-400">Coming soon...</p>
                    </div>
                  </div>

                  <button
                    className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-4 rounded-xl text-xl"
                    disabled
                  >
                    Generate Sign Video
                  </button>
                </div>
              )}
            </motion.div>
          </div>

          {/* Tips Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-12 bg-white rounded-2xl p-8 shadow-lg"
          >
            <h3 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
              <AlertCircle className="text-blue-500" />
              Tips for Best Results
            </h3>

            <div className="grid md:grid-cols-3 gap-6">
              <div className="flex gap-4">
                <div className="text-4xl">💡</div>
                <div>
                  <h4 className="font-bold text-lg mb-2">Good Lighting</h4>
                  <p className="text-gray-600">
                    Ensure your hands are well-lit and clearly visible
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="text-4xl">🤚</div>
                <div>
                  <h4 className="font-bold text-lg mb-2">Clear Gestures</h4>
                  <p className="text-gray-600">
                    Make deliberate, clear hand movements
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="text-4xl">🎯</div>
                <div>
                  <h4 className="font-bold text-lg mb-2">Camera Position</h4>
                  <p className="text-gray-600">
                    Keep hands centered in the frame
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      <style>{`
        .mirror {
          transform: scaleX(-1);
        }
      `}</style>
    </div>
  );
}
