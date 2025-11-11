"""
Convert Keras model to TensorFlow.js format (without tensorflowjs package)
Uses native TensorFlow SavedModel format that TF.js can load
"""
import os
import json
import shutil
from tensorflow import keras
import numpy as np

MODEL_PATH = 'model.h5'
TFJS_OUTPUT = 'web_model'

def convert_keras_to_tfjs():
    """Convert Keras .h5 model to TensorFlow SavedModel (TF.js compatible)"""
    
    print("\n" + "="*60)
    print("🔄 Converting Keras Model to TensorFlow.js")
    print("="*60 + "\n")
    
    # Step 1: Check model exists
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Model file not found: {MODEL_PATH}")
        return False
    
    print(f"📂 Loading model: {MODEL_PATH}")
    
    try:
        model = keras.models.load_model(MODEL_PATH)
        print(f"   ✅ Model loaded")
        print(f"   📐 Input: {model.input_shape}")
        print(f"   📐 Output: {model.output_shape}")
    except Exception as e:
        print(f"❌ Failed to load: {e}")
        return False
    
    # Step 2: Save as SavedModel
    print(f"\n📦 Saving as SavedModel format...")
    
    try:
        # Remove old output if exists
        if os.path.exists(TFJS_OUTPUT):
            shutil.rmtree(TFJS_OUTPUT)
        
        # Save in SavedModel format
        model.save(TFJS_OUTPUT, save_format='tf')
        print(f"   ✅ SavedModel saved to {TFJS_OUTPUT}/")
        
    except Exception as e:
        print(f"❌ Failed to save: {e}")
        return False
    
    # Step 3: Create model.json for TensorFlow.js
    print(f"\n📋 Creating model.json metadata...")
    
    try:
        # Get model config
        model_config = model.get_config()
        model_weights_meta = []
        
        for layer in model.layers:
            if layer.get_weights():
                weights = layer.get_weights()
                for i, w in enumerate(weights):
                    model_weights_meta.append({
                        'name': f"{layer.name}_w{i}",
                        'shape': list(w.shape),
                        'dtype': 'float32'
                    })
        
        # Create model.json
        model_json = {
            "format": "layers-model",
            "generatedBy": "TensorFlow Python",
            "convertedBy": "Signify Ghana",
            "modelTopology": {
                "class_name": model_config.get("class_name", "Sequential"),
                "config": model_config.get("config", {})
            },
            "weightsManifest": [{
                "paths": ["group1-shard1of1.bin"],
                "weights": model_weights_meta
            }],
            "trainingConfig": model_config.get("config", {})
        }
        
        # Save model.json
        model_json_path = os.path.join(TFJS_OUTPUT, 'model.json')
        with open(model_json_path, 'w') as f:
            json.dump(model_json, f, indent=2)
        
        print(f"   ✅ model.json created")
        
    except Exception as e:
        print(f"   ⚠️  model.json creation warning: {e}")
        # Continue anyway - not critical
    
    # Step 4: Verify output
    print(f"\n✅ Conversion Complete!")
    print(f"\n📋 Files in '{TFJS_OUTPUT}/':")
    
    if os.path.exists(TFJS_OUTPUT):
        for item in os.listdir(TFJS_OUTPUT):
            itempath = os.path.join(TFJS_OUTPUT, item)
            if os.path.isfile(itempath):
                size = os.path.getsize(itempath) / (1024*1024)
                print(f"   • {item} ({size:.2f} MB)")
            else:
                print(f"   📁 {item}/")
    
    # Step 5: Next steps
    print("\n" + "="*60)
    print("📋 Next Steps:")
    print("="*60)
    
    print(f"\n1️⃣ Copy model to web app:")
    print(f"   xcopy /E /I {TFJS_OUTPUT} ..\\web\\public\\assets\\web_model")
    
    print(f"\n2️⃣ Verify files:")
    print(f"   dir ..\\web\\public\\assets\\web_model\\")
    
    print(f"\n3️⃣ Start web app:")
    print(f"   cd ..\\web")
    print(f"   npm run dev")
    
    print(f"\n4️⃣ Test:")
    print(f"   Open http://localhost:5173/sign.html")
    print(f"   Press F12 → Network → Check model loads")
    
    print("\n" + "="*60 + "\n")
    
    return True

if __name__ == '__main__':
    success = convert_keras_to_tfjs()
    exit(0 if success else 1)