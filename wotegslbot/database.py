"""
Video database handler for GSL Bot
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
import difflib
from config import CATEGORIES, DICTIONARY_FILE, SUPPORTED_VIDEO_FORMATS, SUPPORTED_IMAGE_FORMATS


class VideoDatabase:
    """Manages GSL video dictionary"""
    
    def __init__(self):
        self.dictionary = self._load_dictionary()
        self._scan_videos()
    
    def _load_dictionary(self) -> Dict:
        """Load dictionary from JSON file"""
        if DICTIONARY_FILE.exists():
            with open(DICTIONARY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'alphabets': {},
            'numbers': {},
            'words': {}
        }
    
    def _save_dictionary(self):
        """Save dictionary to JSON file"""
        DICTIONARY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DICTIONARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.dictionary, f, indent=2, ensure_ascii=False)
    
    def _scan_videos(self):
        """Scan video and image directories and update dictionary"""
        for category, category_dir in CATEGORIES.items():
            if not category_dir.exists():
                continue
            
            for media_file in category_dir.iterdir():
                if media_file.suffix.lower() in SUPPORTED_VIDEO_FORMATS + SUPPORTED_IMAGE_FORMATS:
                    word = media_file.stem.upper()
                    
                    if word not in self.dictionary[category]:
                        self.dictionary[category][word] = {
                            'path': str(media_file),
                            'filename': media_file.name,
                            'description': f'Sign for {word}',
                            'category': category,
                            'type': 'video' if media_file.suffix.lower() in SUPPORTED_VIDEO_FORMATS else 'image'
                        }
        
        self._save_dictionary()
    
    def search(self, query: str) -> Optional[Dict]:
        """
        Search for a sign by word
        Returns video info if found, None otherwise
        """
        query = query.upper().strip()
        
        # Search in all categories
        for category, items in self.dictionary.items():
            if query in items:
                return items[query]
        
        return None
    
    def fuzzy_search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Fuzzy search for similar signs
        Returns list of closest matches
        """
        query = query.upper().strip()
        all_words = []
        
        # Collect all available words
        for category, items in self.dictionary.items():
            for word, info in items.items():
                all_words.append({
                    'word': word,
                    'info': info,
                    'category': category
                })
        
        # Find closest matches
        words_only = [item['word'] for item in all_words]
        matches = difflib.get_close_matches(query, words_only, n=max_results, cutoff=0.4)
        
        # Return full info for matches
        results = []
        for match in matches:
            for item in all_words:
                if item['word'] == match:
                    results.append(item)
                    break
        
        return results
    
    def get_category(self, category: str) -> Dict:
        """Get all signs in a category"""
        return self.dictionary.get(category, {})
    
    def get_all_words(self) -> List[str]:
        """Get list of all available words"""
        all_words = []
        for category, items in self.dictionary.items():
            all_words.extend(items.keys())
        return sorted(all_words)
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        return {
            'total_signs': sum(len(items) for items in self.dictionary.values()),
            'alphabets': len(self.dictionary.get('alphabets', {})),
            'numbers': len(self.dictionary.get('numbers', {})),
            'words': len(self.dictionary.get('words', {})),
        }
    
    def add_video(self, word: str, category: str, video_path: str, description: str = None):
        """Add a new video to the dictionary"""
        word = word.upper()
        
        if category not in self.dictionary:
            self.dictionary[category] = {}
        
        self.dictionary[category][word] = {
            'path': video_path,
            'filename': Path(video_path).name,
            'description': description or f'Sign for {word}',
            'category': category
        }
        
        self._save_dictionary()


# Singleton instance
db = VideoDatabase()
