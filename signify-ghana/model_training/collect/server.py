# server.py - Flask server for collecting GSL training data
from flask import Flask, request, jsonify, send_file
import json
import os

app = Flask(__name__)

# Create samples directory if it doesn't exist
SAMPLES_DIR = '../samples'
os.makedirs(SAMPLES_DIR, exist_ok=True)

@app.route('/')
def index():
    """Serve the data collection HTML page"""
    return send_file('data_collection.html')

@app.route('/upload_sample', methods=['POST'])
def upload_sample():
    """
    Accept hand landmark data and save to JSONL files.
    Each label gets its own file: samples/{label}.jsonl
    """
    data = request.get_json()
    label = data.get('label')
    landmarks = data.get('landmarks')
    
    # Validation
    if not label or not landmarks:
        return jsonify({'error': 'Missing label or landmarks'}), 400
    
    if len(landmarks) != 63:
        return jsonify({'error': f'Expected 63 landmarks, got {len(landmarks)}'}), 400
    
    # Append to per-label JSONL file
    fname = os.path.join(SAMPLES_DIR, f'{label}.jsonl')
    with open(fname, 'a') as f:
        f.write(json.dumps({'landmarks': landmarks}) + '\n')
    
    print(f'✓ Saved sample for label: {label}')
    return jsonify({'status': 'ok', 'label': label})

@app.route('/stats', methods=['GET'])
def get_stats():
    """Return statistics about collected samples"""
    stats = {}
    
    if os.path.exists(SAMPLES_DIR):
        for filename in os.listdir(SAMPLES_DIR):
            if filename.endswith('.jsonl'):
                label = filename.replace('.jsonl', '')
                filepath = os.path.join(SAMPLES_DIR, filename)
                
                with open(filepath, 'r') as f:
                    count = sum(1 for _ in f)
                
                stats[label] = count
    
    return jsonify(stats)

if __name__ == '__main__':
    print('🚀 GSL Data Collection Server')
    print(f'📁 Samples will be saved to: {os.path.abspath(SAMPLES_DIR)}')
    print('🌐 Open http://localhost:5000 in your browser')
    app.run(port=5000, debug=True)
