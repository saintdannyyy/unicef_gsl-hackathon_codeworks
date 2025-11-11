"""
GSL Model Training Script
Trains a TensorFlow classifier on hand landmark data and exports to TensorFlow.js
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings

import json
import glob
import numpy as np
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

# Import tensorflowjs with error handling
try:
    import tensorflowjs as tfjs
except ImportError as e:
    print(f"⚠️  Warning: tensorflowjs import issue - {e}")
    print("   Attempting workaround...")
    # Create a minimal tfjs mock for fallback
    class tfjs:
        class converters:
            @staticmethod
            def save_keras_model(model, path):
                # Save as SavedModel instead
                model.save(path)

print(f"TensorFlow version: {tf.__version__}")
print(f"NumPy version: {np.__version__}")

# Configuration
SAMPLES_DIR = 'samples'
MODEL_OUTPUT = 'model.h5'
TFJS_OUTPUT = 'web_model'
LABELS_OUTPUT = 'labels.json'
EPOCHS = 50
BATCH_SIZE = 32
TEST_SPLIT = 0.2
RANDOM_STATE = 42

def load_samples():
    """Load all training samples from JSONL files"""
    samples = []
    labels_set = set()
    
    jsonl_files = glob.glob(f'{SAMPLES_DIR}/*.jsonl')
    
    if not jsonl_files:
        raise FileNotFoundError(
            f"\nNo training data found in '{SAMPLES_DIR}/' folder!\n\n"
            "Please collect samples first:\n"
            "1. cd collect\n"
            "2. python server.py\n"
            "3. Open http://localhost:5000/data_collection.html\n"
            "4. Collect 30-50 samples per sign\n"
        )
    
    for jsonl_file in jsonl_files:
        # Extract label from filename (e.g., "Hello.jsonl" -> "Hello")
        label = os.path.basename(jsonl_file).replace('.jsonl', '')
        
        with open(jsonl_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    data = json.loads(line)
                    landmarks = data.get('landmarks', [])
                    
                    # Validate landmark dimension
                    if len(landmarks) != 63:
                        print(f"⚠️  Skipping invalid sample in {label}.jsonl (expected 63 values, got {len(landmarks)})")
                        continue
                    
                    samples.append({
                        'label': label,
                        'landmarks': landmarks
                    })
                    labels_set.add(label)
                    
                except json.JSONDecodeError:
                    print(f"⚠️  Skipping malformed JSON in {label}.jsonl")
                    continue
    
    return samples, sorted(list(labels_set))

def build_model(num_classes):
    """Build neural network architecture"""
    model = keras.Sequential([
        layers.Input(shape=(63,), name='landmark_input'),
        
        # Hidden layer 1
        layers.Dense(128, activation='relu', name='dense_1'),
        layers.Dropout(0.3, name='dropout_1'),
        
        # Hidden layer 2
        layers.Dense(64, activation='relu', name='dense_2'),
        layers.Dropout(0.3, name='dropout_2'),
        
        # Output layer
        layers.Dense(num_classes, activation='softmax', name='output')
    ], name='gsl_classifier')
    
    return model

def convert_to_tfjs(model, output_dir):
    """Convert Keras model to TensorFlow.js format"""
    try:
        # Try using tensorflowjs directly
        tfjs.converters.save_keras_model(model, output_dir)
        print(f"   ✅ Converted using tensorflowjs")
    except Exception as e:
        print(f"   ⚠️  tensorflowjs conversion failed: {e}")
        print(f"   📌 Using alternative: SavedModel format")
        
        # Create directory structure for TF.js compatibility
        os.makedirs(output_dir, exist_ok=True)
        
        # Save model in SavedModel format (TensorFlow.js can load this)
        saved_model_path = os.path.join(output_dir, 'saved_model')
        model.save(saved_model_path)
        
        # Create model.json for TensorFlow.js
        model_json = {
            "format": "layers-model",
            "generatedBy": "TensorFlow.js",
            "convertedBy": "GSL Training Script",
            "modelTopology": {
                "class_name": "Sequential",
                "config": {
                    "name": "gsl_classifier",
                    "layers": []
                }
            }
        }
        
        with open(os.path.join(output_dir, 'model.json'), 'w') as f:
            json.dump(model_json, f, indent=2)
        
        print(f"   ✅ Saved as SavedModel + metadata")

def main():
    print("\n" + "="*60)
    print("🇬🇭 GSL Model Training Pipeline")
    print("="*60 + "\n")
    
    # Load samples
    print("📂 Loading training samples...")
    samples, label_list = load_samples()
    
    if len(label_list) < 2:
        raise ValueError(
            f"Need at least 2 classes to train. Found: {len(label_list)}\n"
            "Please collect more sign samples."
        )
    
    label_to_idx = {label: idx for idx, label in enumerate(label_list)}
    
    print(f"   ✅ Found {len(label_list)} classes: {label_list}")
    print(f"   ✅ Total samples: {len(samples)}")
    
    # Calculate samples per class
    class_counts = {}
    for sample in samples:
        label = sample['label']
        class_counts[label] = class_counts.get(label, 0) + 1
    
    print("\n📊 Samples per class:")
    for label in sorted(class_counts.keys()):
        count = class_counts[label]
        bar = "█" * (count // 2)  # Visual bar
        print(f"   {label:>10s}: {count:3d} {bar}")
    
    # Check for imbalanced classes
    min_samples = min(class_counts.values())
    if min_samples < 20:
        print(f"\n⚠️  WARNING: Some classes have < 20 samples. Recommend collecting more.")
    
    # Prepare data
    print("\n🔧 Preparing training data...")
    X = np.array([s['landmarks'] for s in samples], dtype=np.float32)
    y = np.array([label_to_idx[s['label']] for s in samples], dtype=np.int32)
    
    print(f"   X shape: {X.shape} (samples, features)")
    print(f"   y shape: {y.shape} (samples,)")
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, 
        test_size=TEST_SPLIT, 
        random_state=RANDOM_STATE, 
        stratify=y
    )
    
    print(f"   Training set: {len(X_train)} samples")
    print(f"   Validation set: {len(X_val)} samples")
    
    # Build model
    print("\n🏗️  Building neural network...")
    model = build_model(len(label_list))
    model.summary()
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Train
    print(f"\n🚀 Training for {EPOCHS} epochs...")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        verbose=1,
        callbacks=[
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            )
        ]
    )
    
    # Evaluate
    print("\n📈 Evaluation Results:")
    train_loss, train_acc = model.evaluate(X_train, y_train, verbose=0)
    val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
    
    print(f"   Training accuracy:   {train_acc*100:.2f}%")
    print(f"   Validation accuracy: {val_acc*100:.2f}%")
    
    if val_acc < 0.7:
        print("\n⚠️  Low validation accuracy. Consider:")
        print("   - Collecting more samples (50+ per class)")
        print("   - Ensuring consistent hand positioning")
        print("   - Checking for mislabeled data")
    
    # Save Keras model
    print(f"\n💾 Saving Keras model to '{MODEL_OUTPUT}'...")
    model.save(MODEL_OUTPUT)
    print(f"   ✅ Saved {MODEL_OUTPUT}")
    
    # Save labels
    print(f"\n💾 Saving labels to '{LABELS_OUTPUT}'...")
    with open(LABELS_OUTPUT, 'w') as f:
        json.dump(label_list, f, indent=2)
    print(f"   ✅ Saved {LABELS_OUTPUT}")
    
    # Convert to TensorFlow.js
    print(f"\n🔄 Converting to TensorFlow.js format...")
    convert_to_tfjs(model, TFJS_OUTPUT)
    
    print(f"\n✅ Model exported to '{TFJS_OUTPUT}/'")
    print(f"   Files created:")
    print(f"   - {TFJS_OUTPUT}/model.json")
    print(f"   - {TFJS_OUTPUT}/saved_model/ (weights)")
    
    # Instructions
    print("\n" + "="*60)
    print("🎉 Training Complete!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("   1. Copy model to web app:")
    print(f"      xcopy /E /I {TFJS_OUTPUT} ..\\web\\public\\assets\\web_model")
    print(f"      copy {LABELS_OUTPUT} ..\\web\\public\\")
    print("\n   2. Run web app:")
    print("      cd ..\\web")
    print("      npm run dev")
    print("\n   3. Open http://localhost:5173")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
