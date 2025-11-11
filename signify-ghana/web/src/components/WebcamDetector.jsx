// WebcamDetector - MediaPipe Hands + TF.js inference component
import { useEffect, useRef, useState, useCallback } from "react";
import { Hands } from "@mediapipe/hands";
import { Camera } from "@mediapipe/camera_utils";
import * as tf from "@tensorflow/tfjs";
import { loadSignModel, predictSign } from "../utils/modelLoader";

const CONFIDENCE_THRESHOLD = 0.6;
const MODEL_PATH = "/assets/web_model/model.json";
const LABELS_PATH = "/labels.json";

export default function WebcamDetector() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const cameraRef = useRef(null);
  const handsRef = useRef(null);
  const modelRef = useRef(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [labels, setLabels] = useState([]);
  const [error, setError] = useState(null);
  const [model, setModel] = useState(null);

  // Load model and labels on mount
  useEffect(() => {
    const initializeModel = async () => {
      try {
        const model = await loadSignModel();
        setModel(model);
        console.log("✅ Model initialized");
      } catch (error) {
        console.error("❌ Model init failed:", error);
        setError(`Model loading failed: ${error.message}`);
      }
    };

    initializeModel();

    return () => {
      // Cleanup on unmount
      stopCamera();
      if (modelRef.current) {
        modelRef.current.dispose();
      }
    };
  }, []);

  const loadModelAndLabels = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Load labels first
      const labelsResponse = await fetch(LABELS_PATH);
      if (!labelsResponse.ok) {
        throw new Error("Labels file not found. Train the model first.");
      }
      const labelsData = await labelsResponse.json();
      setLabels(labelsData);

      // Load TF.js model
      const model = await tf.loadLayersModel(MODEL_PATH);
      modelRef.current = model;

      console.log("✅ Model loaded:", model);
      console.log("✅ Labels loaded:", labelsData);

      setIsLoading(false);
    } catch (err) {
      console.error("Model loading error:", err);
      setError(`Failed to load model: ${err.message}`);
      setIsLoading(false);
    }
  };

  const startCamera = async () => {
    if (!modelRef.current || !labels.length) {
      setError("Model not ready. Please refresh the page.");
      return;
    }

    try {
      setError(null);

      // Request camera permission
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: 640,
          height: 480,
          facingMode: "user",
        },
      });

      if (!videoRef.current) return;

      videoRef.current.srcObject = stream;
      await videoRef.current.play();

      // Set canvas dimensions
      if (canvasRef.current) {
        canvasRef.current.width = 640;
        canvasRef.current.height = 480;
      }

      // Initialize MediaPipe Hands
      const hands = new Hands({
        locateFile: (file) => {
          return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
        },
      });

      hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.7,
      });

      hands.onResults(onHandsResults);
      handsRef.current = hands;

      // Start camera loop
      const camera = new Camera(videoRef.current, {
        onFrame: async () => {
          if (handsRef.current && videoRef.current) {
            await handsRef.current.send({ image: videoRef.current });
          }
        },
        width: 640,
        height: 480,
      });

      cameraRef.current = camera;
      camera.start();
      setIsRunning(true);
    } catch (err) {
      console.error("Camera error:", err);
      setError(`Camera access denied: ${err.message}`);
    }
  };

  const stopCamera = () => {
    if (cameraRef.current) {
      cameraRef.current.stop();
      cameraRef.current = null;
    }

    if (videoRef.current?.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }

    setIsRunning(false);
    setPrediction(null);
  };

  const onHandsResults = useCallback(
    (results) => {
      if (!canvasRef.current) return;

      const ctx = canvasRef.current.getContext("2d");
      if (!ctx) return;

      // Clear and draw video frame
      ctx.save();
      ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
      ctx.drawImage(
        results.image,
        0,
        0,
        canvasRef.current.width,
        canvasRef.current.height
      );

      // Draw hand landmarks if detected
      if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
        const landmarks = results.multiHandLandmarks[0];

        // Draw connections
        ctx.strokeStyle = "#00FF00";
        ctx.lineWidth = 2;
        drawHandConnections(ctx, landmarks);

        // Draw landmarks as circles
        ctx.fillStyle = "#FF0000";
        landmarks.forEach((point) => {
          ctx.beginPath();
          ctx.arc(
            point.x * canvasRef.current.width,
            point.y * canvasRef.current.height,
            5,
            0,
            Math.PI * 2
          );
          ctx.fill();
        });

        // Run prediction
        handlePrediction(landmarks);
      } else {
        // No hand detected - clear prediction
        setPrediction(null);
      }

      ctx.restore();
    },
    [labels]
  );

  const drawHandConnections = (ctx, landmarks) => {
    // Hand skeleton connections (MediaPipe hand model)
    const connections = [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4], // Thumb
      [0, 5],
      [5, 6],
      [6, 7],
      [7, 8], // Index
      [0, 9],
      [9, 10],
      [10, 11],
      [11, 12], // Middle
      [0, 13],
      [13, 14],
      [14, 15],
      [15, 16], // Ring
      [0, 17],
      [17, 18],
      [18, 19],
      [19, 20], // Pinky
      [5, 9],
      [9, 13],
      [13, 17], // Palm
    ];

    connections.forEach(([start, end]) => {
      const p1 = landmarks[start];
      const p2 = landmarks[end];
      ctx.beginPath();
      ctx.moveTo(
        p1.x * canvasRef.current.width,
        p1.y * canvasRef.current.height
      );
      ctx.lineTo(
        p2.x * canvasRef.current.width,
        p2.y * canvasRef.current.height
      );
      ctx.stroke();
    });
  };

  const handlePrediction = async (landmarks) => {
    if (!model || !labels) return;

    const result = await predictSign(model, landmarks, labels);
    if (result) {
      setPrediction(result);
      // Speak the prediction
      if ("speechSynthesis" in window) {
        const utterance = new SpeechSynthesisUtterance(result.label);
        window.speechSynthesis.speak(utterance);
      }
    }
  };

  // Auto-speak on new prediction (TTS)
  useEffect(() => {
    if (prediction && window.speechSynthesis) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(prediction.label);
      utterance.lang = "en-US";
      utterance.rate = 0.9;
      utterance.volume = 0.8;
      window.speechSynthesis.speak(utterance);
    }
  }, [prediction?.label]); // Only trigger on label change

  const speakAgain = () => {
    if (!prediction) return;

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(prediction.label);
    utterance.lang = "en-US";
    utterance.rate = 0.9;
    window.speechSynthesis.speak(utterance);
  };

  return (
    <div className="webcam-detector">
      {isLoading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading AI model...</p>
        </div>
      )}

      {error && (
        <div className="error-state">
          <p>⚠️ {error}</p>
          <button onClick={loadModelAndLabels} className="btn-secondary">
            Retry
          </button>
        </div>
      )}

      {!isLoading && !error && (
        <>
          <div className="camera-section">
            <div className="camera-container">
              <video ref={videoRef} style={{ display: "none" }} />
              <canvas ref={canvasRef} className="camera-canvas" />
              {!isRunning && (
                <div className="camera-overlay">
                  <p>Camera not started</p>
                </div>
              )}
            </div>

            <div className="controls">
              {!isRunning ? (
                <button onClick={startCamera} className="btn-primary btn-large">
                  📹 Start Camera
                </button>
              ) : (
                <button onClick={stopCamera} className="btn-danger btn-large">
                  ⏹️ Stop Camera
                </button>
              )}
            </div>
          </div>

          <div className="prediction-section">
            <h3>Recognition Result</h3>
            {prediction ? (
              <div className="prediction-card active">
                <div className="prediction-label">{prediction.label}</div>
                <div className="prediction-confidence">
                  Confidence: {(prediction.confidence * 100).toFixed(1)}%
                </div>
                <button onClick={speakAgain} className="btn-secondary">
                  🔊 Speak Again
                </button>
              </div>
            ) : (
              <div className="prediction-card empty">
                <p>Show a sign to the camera</p>
                {labels.length > 0 && (
                  <div className="prediction-hint">
                    <strong>Available signs:</strong>
                    <br />
                    {labels.join(", ")}
                  </div>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
