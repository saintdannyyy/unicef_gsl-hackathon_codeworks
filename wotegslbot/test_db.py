"""Quick test to check database loading"""
from database import db

print("Testing database...")
print(f"\nAll categories: {list(db.dictionary.keys())}")

words = db.get_category('words')
print(f"\nWords category: {words}")
print(f"Number of words: {len(words)}")

if words:
    for word, info in words.items():
        print(f"  - {word}: {info}")

stats = db.get_statistics()
print(f"\nStatistics: {stats}")
