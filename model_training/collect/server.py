# server.py - Flask server for collecting GSL training data
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Create samples directory if it doesn't exist
SAMPLES_DIR = '../samples'
os.makedirs(SAMPLES_DIR, exist_ok=True)

@app.route('/')
def index():
    """Serve the data collection HTML page"""
    return send_from_directory('.', 'data_collection.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Upload single frame sample (static signs)"""
    data = request.json
    label = data.get('label', '').strip()
    landmarks = data.get('landmarks', [])
    
    if not label or len(landmarks) != 63:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Save to JSONL
    filepath = os.path.join(SAMPLES_DIR, f'{label}.jsonl')
    with open(filepath, 'a') as f:
        json.dump({'landmarks': landmarks}, f)
        f.write('\n')
    
    return jsonify({'success': True, 'message': f'Saved sample for {label}'})

@app.route('/upload_sequence', methods=['POST'])
def upload_sequence():
    """Upload sequence of frames (dynamic signs like Z)"""
    data = request.json
    label = data.get('label', '').strip()
    sequence = data.get('sequence', [])  # List of landmark arrays
    
    if not label or not sequence:
        return jsonify({'error': 'Invalid data'}), 400
    
    # Validate each frame has 63 values
    for i, frame in enumerate(sequence):
        if len(frame) != 63:
            return jsonify({'error': f'Frame {i} has {len(frame)} values (need 63)'}), 400
    
    # Save sequence to JSONL
    filepath = os.path.join(SAMPLES_DIR, f'{label}_seq.jsonl')
    with open(filepath, 'a') as f:
        json.dump({'sequence': sequence, 'label': label}, f)
        f.write('\n')
    
    return jsonify({'success': True, 'message': f'Saved sequence for {label} ({len(sequence)} frames)'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
