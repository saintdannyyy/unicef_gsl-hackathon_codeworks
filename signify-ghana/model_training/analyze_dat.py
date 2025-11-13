"""
Analyze collected training data quality
"""
import os
import json
import numpy as np
from collections import defaultdict

SAMPLES_DIR = 'samples'

def analyze_data():
    stats = defaultdict(lambda: {'count': 0, 'type': 'unknown', 'variance': 0, 'lengths': []})
    
    print("\n" + "="*70)
    print("📊 DATA QUALITY ANALYSIS")
    print("="*70 + "\n")
    
    for filename in sorted(os.listdir(SAMPLES_DIR)):
        if not filename.endswith('.jsonl'):
            continue
        
        label = filename.replace('.jsonl', '')
        is_sequence = '_seq' in label
        
        filepath = os.path.join(SAMPLES_DIR, filename)
        samples = []
        lengths = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if is_sequence:
                        seq = data.get('sequence', [])
                        samples.append(seq)
                        lengths.append(len(seq))
                    else:
                        landmarks = data.get('landmarks', [])
                        samples.append(landmarks)
                        lengths.append(len(landmarks))
                except json.JSONDecodeError:
                    continue
        
        # Calculate variance (diversity of samples)
        variance = 0
        if samples and len(samples) > 1:
            try:
                if is_sequence:
                    # For sequences, calculate variance of flattened first frame
                    first_frames = []
                    for s in samples:
                        if len(s) > 0:
                            flat = np.array(s[0]).flatten() if len(s) > 0 else np.zeros(63)
                            first_frames.append(flat)
                    
                    if len(first_frames) > 1:
                        # Ensure all same length
                        max_len = max(len(f) for f in first_frames)
                        padded = []
                        for f in first_frames:
                            if len(f) < max_len:
                                f = np.pad(f, (0, max_len - len(f)), 'constant')
                            padded.append(f[:max_len])
                        
                        variance = np.mean(np.std(padded, axis=0))
                else:
                    # For static, ensure all same length
                    max_len = max(len(s) for s in samples)
                    padded = []
                    for s in samples:
                        arr = np.array(s)
                        if len(arr) < max_len:
                            arr = np.pad(arr, (0, max_len - len(arr)), 'constant')
                        padded.append(arr[:max_len])
                    
                    if len(padded) > 1:
                        variance = np.mean(np.std(padded, axis=0))
            except Exception as e:
                variance = 0
                print(f"⚠️  Could not calculate variance for {label}: {e}")
        
        stats[label] = {
            'count': len(samples),
            'type': 'dynamic' if is_sequence else 'static',
            'variance': variance,
            'status': '✅' if len(samples) >= 40 else '⚠️' if len(samples) >= 20 else '❌',
            'avg_length': np.mean(lengths) if lengths else 0,
            'min_length': min(lengths) if lengths else 0,
            'max_length': max(lengths) if lengths else 0
        }
    
    # Print results
    print(f"{'Sign':<15} {'Type':<10} {'Samples':<10} {'Variance':<12} {'Avg Len':<10} {'Status'}")
    print("-" * 80)
    
    for label in sorted(stats.keys()):
        s = stats[label]
        avg_len = f"{s['avg_length']:.1f}" if s['type'] == 'dynamic' else f"{int(s['avg_length'])}"
        print(f"{label:<15} {s['type']:<10} {s['count']:<10} {s['variance']:<12.4f} {avg_len:<10} {s['status']}")
    
    # Summary
    total_samples = sum(s['count'] for s in stats.values())
    total_classes = len(stats)
    avg_per_class = total_samples / total_classes if total_classes > 0 else 0
    
    print("\n" + "="*70)
    print(f"📈 SUMMARY")
    print("="*70)
    print(f"Total Classes: {total_classes}")
    print(f"Total Samples: {total_samples}")
    print(f"Average per Class: {avg_per_class:.1f}")
    
    # Static vs Dynamic breakdown
    static_classes = [k for k, v in stats.items() if v['type'] == 'static']
    dynamic_classes = [k for k, v in stats.items() if v['type'] == 'dynamic']
    
    print(f"\nStatic Signs: {len(static_classes)}")
    print(f"Dynamic Signs: {len(dynamic_classes)}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    weak_classes = [k for k, v in stats.items() if v['count'] < 40]
    if weak_classes:
        print(f"\n⚠️  Need more samples (target: 40+):")
        for cls in weak_classes[:15]:
            count = stats[cls]['count']
            needed = 40 - count
            print(f"   • {cls}: {count} samples (need {needed} more)")
        if len(weak_classes) > 15:
            print(f"   ... and {len(weak_classes) - 15} more classes")
    
    low_variance = [k for k, v in stats.items() if v['variance'] < 0.01 and v['count'] > 5]
    if low_variance:
        print(f"\n⚠️  Low diversity - vary angles/lighting/position:")
        print(f"   {', '.join(low_variance[:10])}")
        if len(low_variance) > 10:
            print(f"   ... and {len(low_variance) - 10} more")
    
    # Check for problematic sequence lengths
    seq_issues = [(k, v) for k, v in stats.items() if v['type'] == 'dynamic' and (v['min_length'] < 10 or v['max_length'] > 100)]
    if seq_issues:
        print(f"\n⚠️  Sequence length issues:")
        for label, s in seq_issues:
            print(f"   • {label}: {s['min_length']}-{s['max_length']} frames (target: 20-60)")
    
    # Overall quality
    if avg_per_class >= 40 and not weak_classes:
        print("\n✅ Data quality looks EXCELLENT! Ready for training.")
    elif avg_per_class >= 30:
        print("\n⚠️  Data quality is GOOD. Consider collecting more for weak classes.")
    else:
        print("\n❌ Need more data. Aim for 40+ samples per class.")
    
    # Training suggestions
    print("\n🎯 NEXT STEPS:")
    if avg_per_class >= 30:
        print("   1. python train_hybrid_model.py")
        print("   2. python export_manual.py")
        print("   3. Test in web app")
    else:
        print("   1. cd collect")
        print("   2. python server.py")
        print("   3. Visit http://localhost:5000")
        print("   4. Collect more samples for weak classes")
    
    print("\n" + "="*70 + "\n")
    
    return stats

if __name__ == '__main__':
    analyze_data()