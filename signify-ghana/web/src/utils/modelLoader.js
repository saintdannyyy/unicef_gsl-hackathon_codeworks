/**
 * Load TensorFlow SavedModel format for browser inference
 */
import * as tf from "@tensorflow/tfjs";

export async function loadSignModel() {
  console.log("📂 Loading model...");

  try {
    // TensorFlow.js can load SavedModel directly
    const model = await tf.loadGraphModel("/assets/web_model/model.json");

    console.log("✅ Model loaded successfully");
    return model;
  } catch (error) {
    console.error("❌ Failed to load model:", error);

    // Fallback: try alternative path
    try {
      console.log("📌 Trying alternative model path...");
      const model = await tf.loadGraphModel(
        window.location.origin + "/assets/web_model/model.json"
      );
      console.log("✅ Model loaded from alternative path");
      return model;
    } catch (err2) {
      console.error("❌ Alternative path also failed:", err2);
      throw new Error(`Model loading failed: ${error.message}`);
    }
  }
}

export function preprocessHandLandmarks(landmarks) {
  /**
   * Convert hand landmarks to model input format
   * Input: 21 hand points × 3 coords (x, y, z) = 63 values
   */
  if (!landmarks || landmarks.length < 21) {
    return null;
  }

  // Flatten to 63 values
  const flatLandmarks = [];
  for (let i = 0; i < 21; i++) {
    const point = landmarks[i];
    flatLandmarks.push(point.x, point.y, point.z || 0);
  }

  return tf.tensor2d([flatLandmarks], [1, 63]);
}

export async function predictSign(model, landmarks, labels) {
  /**
   * Predict sign from hand landmarks
   * Returns: { label, confidence, allPredictions }
   */
  try {
    const input = preprocessHandLandmarks(landmarks);
    if (!input) return null;

    const predictions = await model.predict(input);
    const predArray = await predictions.array();
    const probs = predArray[0];

    // Get top prediction
    const maxIdx = probs.indexOf(Math.max(...probs));
    const confidence = probs[maxIdx];
    const label = labels[maxIdx];

    // Cleanup tensors
    input.dispose();
    predictions.dispose();

    return {
      label,
      confidence: (confidence * 100).toFixed(2),
      allPredictions: probs,
    };
  } catch (error) {
    console.error("❌ Prediction failed:", error);
    return null;
  }
}
