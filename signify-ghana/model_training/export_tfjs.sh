#!/bin/bash
# export_tfjs.sh - Convert Keras model to TensorFlow.js format

echo "Converting Keras model to TensorFlow.js..."

tensorflowjs_converter \
    --input_format keras \
    model.h5 \
    ../web/public/assets/web_model

echo "✓ Model exported to ../web/public/assets/web_model/"
echo "✓ Copy labels.json to ../web/public/ manually"
