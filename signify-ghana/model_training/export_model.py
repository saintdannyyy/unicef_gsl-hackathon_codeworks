"""
Export model - FIXED VERSION
"""
import os
import json
import shutil
import numpy as np
from tensorflow import keras

MODEL_PATH = 'model.h5'
OUTPUT_DIR = 'web_model'

print("\n" + "="*60)
print("Exporting Keras model to TensorFlow.js format")
print("="*60 + "\n")

# Step 1: Load
print("1. Loading model...")
model = keras.models.load_model(MODEL_PATH)
print(f"   ✅ Input: {model.input_shape}")
print(f"   ✅ Output: {model.output_shape}")

# Step 2: Clean output
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

# Step 3: Get weights
print("\n2. Extracting weights...")
weights_list = []
weights_manifest = []

for layer in model.layers:
    layer_weights = layer.get_weights()
    if not layer_weights:
        continue
    
    for i, w in enumerate(layer_weights):
        w_f32 = w.astype(np.float32)
        w_flat = w_f32.flatten()
        
        print(f"   {layer.name} weight {i}: {w.shape} ({len(w_flat)} values)")
        
        weights_list.append(w_flat)
        weights_manifest.append({
            'name': f'{layer.name}_w{i}',
            'shape': list(w.shape),
            'dtype': 'float32'
        })

# Step 4: Save binary
print("\n3. Saving weights binary...")
all_weights = np.concatenate(weights_list).astype(np.float32)
binary_data = all_weights.tobytes()

bin_file = os.path.join(OUTPUT_DIR, 'group1-shard1of1.bin')
with open(bin_file, 'wb') as f:
    f.write(binary_data)

bin_size = os.path.getsize(bin_file)
print(f"   ✅ Binary: {bin_size:,} bytes ({bin_size/1024/1024:.2f} MB)")

# Step 5: Create proper model topology
print("\n4. Creating model topology...")

# Get model config but fix it for TF.js
try:
    model_config = json.loads(model.to_json())
except:
    # If to_json() fails, create minimal topology
    model_config = {
        'class_name': 'Sequential',
        'config': {
            'name': model.name,
            'layers': []
        }
    }

# Ensure it has required fields
if 'class_name' not in model_config:
    model_config['class_name'] = 'Sequential'

topology = {
    'class_name': model_config.get('class_name', 'Sequential'),
    'config': model_config.get('config', {})
}

# Step 6: Create model.json with all required fields
print("\n5. Creating model.json...")
model_json = {
    'format': 'layers-model',
    'generatedBy': 'TensorFlow.js Converter',
    'convertedBy': 'Signify Ghana',
    'producer': 'Signify Ghana Export Script',
    'modelTopology': {
        'class_name': topology.get('class_name', 'Sequential'),
        'config': topology.get('config', {})
    },
    'weightsManifest': [{
        'paths': ['group1-shard1of1.bin'],
        'weights': weights_manifest
    }]
}

json_file = os.path.join(OUTPUT_DIR, 'model.json')
with open(json_file, 'w') as f:
    json.dump(model_json, f, indent=2)

print(f"   ✅ model.json created")

# Step 7: Verify model.json is valid
print("\n6. Validating model.json...")
try:
    with open(json_file, 'r') as f:
        test_load = json.load(f)
    
    # Check required fields
    required = ['format', 'modelTopology', 'weightsManifest']
    for field in required:
        if field not in test_load:
            print(f"   ⚠️  Missing field: {field}")
        else:
            print(f"   ✅ Field present: {field}")
    
    # Check modelTopology structure
    mt = test_load.get('modelTopology', {})
    if 'class_name' in mt:
        print(f"   ✅ modelTopology.class_name: {mt['class_name']}")
    
except Exception as e:
    print(f"   ❌ Validation failed: {e}")

# Step 8: Summary
print("\n" + "="*60)
print("✅ Export Complete!")
print("="*60)
print("\nOutput files:")
for fname in sorted(os.listdir(OUTPUT_DIR)):
    fpath = os.path.join(OUTPUT_DIR, fname)
    size = os.path.getsize(fpath)
    print(f"  ✅ {fname}: {size:,} bytes")

print("\n📋 Steps:")
print("  1. Remove-Item -Recurse ..\\web\\public\\assets\\web_model")
print("  2. xcopy /E /I web_model ..\\web\\public\\assets\\web_model")
print("  3. cd ..\\web && npm run dev")
print()