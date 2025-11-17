"""
Game database for competitive GSL learning
Handles user stats, leaderboards, game rooms, and Ghanaian cultural content
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
GAME_DATA_FILE = DATA_DIR / 'game_data.json'
CULTURAL_CONTENT_FILE = DATA_DIR / 'cultural_content.json'


class GameDatabase:
    """Manages competitive gaming data"""
    
    def __init__(self):
        self.game_data = self._load_game_data()
        self.cultural_content = self._load_cultural_content()
        self.active_games = {}  # room_id -> game_state
        self.pending_challenges = {}  # challenge_id -> challenge_data
    
    def _load_game_data(self) -> Dict:
        """Load game data from JSON"""
        if GAME_DATA_FILE.exists():
            with open(GAME_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'users': {},  # user_id -> user_stats
            'leaderboard': [],
            'game_history': []
        }
    
    def _save_game_data(self):
        """Save game data to JSON"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(GAME_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.game_data, f, indent=2, ensure_ascii=False)
    
    def _load_cultural_content(self) -> Dict:
        """Load Ghanaian cultural content"""
        if CULTURAL_CONTENT_FILE.exists():
            with open(CULTURAL_CONTENT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._initialize_cultural_content()
    
    def _initialize_cultural_content(self) -> Dict:
        """Initialize activity-based content for games"""
        content = {
            'activities': [
                {'name': 'CLAPPING', 'description': 'Clapping hands together'},
                {'name': 'WAVING', 'description': 'Waving hand in greeting'},
                {'name': 'POINTING', 'description': 'Pointing at something'},
                {'name': 'THUMBS_UP', 'description': 'Giving thumbs up'},
                {'name': 'PEACE_SIGN', 'description': 'Making peace sign'},
            ]
        }
        
        # Save initialized content
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(CULTURAL_CONTENT_FILE, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        return content
    
    # ========================
    # USER MANAGEMENT
    # ========================
    
    def get_or_create_user(self, user_id: int, username: str = None, first_name: str = None) -> Dict:
        """Get user stats or create new user"""
        user_id_str = str(user_id)
        
        if user_id_str not in self.game_data['users']:
            self.game_data['users'][user_id_str] = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'total_games': 0,
                'wins': 0,
                'total_points': 0,
                'cultural_mastery': 0,
                'streak': 0,
                'achievements': [],
                'created_at': datetime.now().isoformat(),
                'last_played': None
            }
            self._save_game_data()
        
        return self.game_data['users'][user_id_str]
    
    def update_user_stats(self, user_id: int, points: int, won: bool = False):
        """Update user statistics after a game"""
        user = self.get_or_create_user(user_id)
        
        user['total_games'] += 1
        user['total_points'] += points
        user['last_played'] = datetime.now().isoformat()
        
        if won:
            user['wins'] += 1
            user['streak'] += 1
        else:
            user['streak'] = 0
        
        # Check for achievements
        self._check_achievements(user)
        
        self._save_game_data()
        self._update_leaderboard()
    
    def _check_achievements(self, user: Dict):
        """Check and award achievements"""
        achievements = []
        
        if user['total_games'] >= 1 and 'first_game' not in user['achievements']:
            achievements.append({'id': 'first_game', 'name': '🎮 First Steps', 'desc': 'Played first game'})
        
        if user['wins'] >= 10 and 'ten_wins' not in user['achievements']:
            achievements.append({'id': 'ten_wins', 'name': '🏆 Winner', 'desc': '10 wins achieved'})
        
        if user['streak'] >= 5 and 'streak_5' not in user['achievements']:
            achievements.append({'id': 'streak_5', 'name': '🔥 Hot Streak', 'desc': '5 game win streak'})
        
        if user['total_points'] >= 1000 and 'point_master' not in user['achievements']:
            achievements.append({'id': 'point_master', 'name': '⭐ Point Master', 'desc': '1000 points earned'})
        
        # Add new achievements to user
        for achievement in achievements:
            if achievement['id'] not in user['achievements']:
                user['achievements'].append(achievement['id'])
    
    # ========================
    # LEADERBOARD
    # ========================
    
    def _update_leaderboard(self):
        """Update global leaderboard"""
        users = list(self.game_data['users'].values())
        
        # Sort by total points descending
        sorted_users = sorted(users, key=lambda x: x['total_points'], reverse=True)
        
        # Take top 50
        self.game_data['leaderboard'] = [
            {
                'user_id': user['user_id'],
                'username': user.get('username', 'Anonymous'),
                'first_name': user.get('first_name', 'User'),
                'total_points': user['total_points'],
                'wins': user['wins'],
                'total_games': user['total_games']
            }
            for user in sorted_users[:50]
        ]
        
        self._save_game_data()
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top players"""
        return self.game_data['leaderboard'][:limit]
    
    def get_user_rank(self, user_id: int) -> Tuple[int, Dict]:
        """Get user's rank on leaderboard"""
        for rank, player in enumerate(self.game_data['leaderboard'], start=1):
            if player['user_id'] == user_id:
                return rank, player
        
        # User not on leaderboard yet
        user = self.get_or_create_user(user_id)
        return None, user
    
    # ========================
    # GAME ROOMS
    # ========================
    
    def create_game_room(self, host_id: int, game_mode: str, cultural_category: str = None) -> str:
        """Create a new game room"""
        import random
        # Create a simple 4-digit room code
        room_code = str(random.randint(1000, 9999))
        room_id = f"room_{room_code}"
        
        self.active_games[room_id] = {
            'room_id': room_id,
            'room_code': room_code,
            'host_id': host_id,
            'players': [host_id],
            'player_names': {},
            'game_mode': game_mode,
            'cultural_category': cultural_category,
            'status': 'waiting',
            'created_at': time.time(),
            'questions': [],
            'current_question': 0,
            'scores': {str(host_id): 0},
            'answers': {},
            'players_answered': set()
        }
        
        return room_id
    
    def join_game_room(self, room_id: str, user_id: int, username: str = None) -> bool:
        """Join an existing game room"""
        if room_id not in self.active_games:
            return False
        
        room = self.active_games[room_id]
        
        if room['status'] != 'waiting':
            return False
        
        # Limit to 2 players
        if len(room['players']) >= 2:
            return False
        
        if user_id not in room['players']:
            room['players'].append(user_id)
            room['scores'][str(user_id)] = 0
            room['player_names'][str(user_id)] = username or f"Player {len(room['players'])}"
        
        return True
    
    def find_room_by_code(self, room_code: str) -> Optional[str]:
        """Find room ID by room code"""
        for room_id, room in self.active_games.items():
            if room.get('room_code') == room_code:
                return room_id
        return None
    
    def start_game(self, room_id: str) -> bool:
        """Start the game in a room"""
        if room_id not in self.active_games:
            return False
        
        room = self.active_games[room_id]
        room['status'] = 'playing'
        
        # Generate questions based on game mode
        room['questions'] = self._generate_questions(
            room['game_mode'],
            room.get('cultural_category')
        )
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"start_game: Generated {len(room['questions'])} questions for room {room_id}, mode={room['game_mode']}")
        
        # Initialize scores
        for player_id in room['players']:
            room['scores'][str(player_id)] = 0
        
        return True
    
    def _generate_questions(self, game_mode: str, cultural_category: str = None) -> List[Dict]:
        """Generate quiz questions based on game mode"""
        import random
        from database import db
        import logging
        logger = logging.getLogger(__name__)
        
        questions = []
        
        if game_mode == 'activities':
            # Get all available words from database (same as solo practice)
            all_words = list(db.get_category('words').keys())
            
            logger.info(f"_generate_questions: Found {len(all_words)} words in database: {all_words}")
            
            if len(all_words) < 4:
                # Not enough words
                logger.error(f"_generate_questions: Not enough words! Need at least 4, found {len(all_words)}")
                return []
            
            # Select 5 random words for multiplayer questions
            question_words = random.sample(all_words, min(5, len(all_words)))
            
            for word in question_words:
                # Get correct answer
                correct_answer = word
                
                # Get video path
                word_info = db.search(word)
                video_path = word_info['path'] if word_info else None
                
                # Generate wrong answers (3 other random words)
                wrong_answers = [w for w in all_words if w != word]
                wrong_options = random.sample(wrong_answers, min(3, len(wrong_answers)))
                
                # Create options list
                options = [correct_answer] + wrong_options
                random.shuffle(options)
                
                questions.append({
                    'type': 'activity',
                    'question': f"What sign is this?",
                    'correct_answer': correct_answer,
                    'options': options,
                    'video_sign': word
                })
        
        return questions
    
    def submit_answer(self, room_id: str, user_id: int, answer: str, time_taken: float) -> Dict:
        """Submit answer and calculate points"""
        if room_id not in self.active_games:
            return {'success': False, 'message': 'Game room not found'}
        
        room = self.active_games[room_id]
        current_q = room['questions'][room['current_question']]
        
        # Calculate points based on correctness and speed (exact match, case-insensitive)
        is_correct = answer.upper().strip() == current_q['correct_answer'].upper().strip()
        
        points = 0
        if is_correct:
            # Base points for correct answer
            points = 100
            
            # Speed bonus (max 50 points)
            if time_taken < 5:
                points += 50
            elif time_taken < 10:
                points += 30
            elif time_taken < 15:
                points += 10
        
        # Update score
        user_id_str = str(user_id)
        if user_id_str in room['scores']:
            room['scores'][user_id_str] += points
        
        # Store answer
        if user_id_str not in room['answers']:
            room['answers'][user_id_str] = []
        room['answers'][user_id_str].append({
            'question_idx': room['current_question'],
            'answer': answer,
            'is_correct': is_correct,
            'points': points,
            'time_taken': time_taken
        })
        
        return {
            'success': True,
            'is_correct': is_correct,
            'points': points,
            'total_score': room['scores'][user_id_str],
            'correct_answer': current_q['correct_answer']
        }
    
    def next_question(self, room_id: str) -> Optional[Dict]:
        """Move to next question"""
        if room_id not in self.active_games:
            return None
        
        room = self.active_games[room_id]
        room['current_question'] += 1
        
        if room['current_question'] >= len(room['questions']):
            # Game over
            room['status'] = 'finished'
            return self._finalize_game(room_id)
        
        return room['questions'][room['current_question']]
    
    def _finalize_game(self, room_id: str) -> Dict:
        """Finalize game and determine winner"""
        room = self.active_games[room_id]
        
        # Determine winner
        sorted_scores = sorted(
            room['scores'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        winner_id = int(sorted_scores[0][0]) if sorted_scores else None
        winner_score = sorted_scores[0][1] if sorted_scores else 0
        
        # Update user stats
        for player_id in room['players']:
            won = player_id == winner_id
            self.update_user_stats(player_id, room['scores'][str(player_id)], won)
        
        # Save game history
        self.game_data['game_history'].append({
            'room_id': room_id,
            'game_mode': room['game_mode'],
            'players': room['players'],
            'scores': room['scores'],
            'winner_id': winner_id,
            'winner_score': winner_score,
            'played_at': datetime.now().isoformat()
        })
        self._save_game_data()
        
        result = {
            'winner_id': winner_id,
            'winner_score': winner_score,
            'final_scores': sorted_scores,
            'stats': {
                'total_questions': len(room['questions']),
                'game_mode': room['game_mode']
            }
        }
        
        # Remove game from active games to prevent stale state access
        del self.active_games[room_id]
        
        return result
    
    def get_game_state(self, room_id: str) -> Optional[Dict]:
        """Get current game state"""
        return self.active_games.get(room_id)
    
    def get_current_question(self, room_id: str) -> Optional[Dict]:
        """Get current question"""
        if room_id not in self.active_games:
            return None
        
        room = self.active_games[room_id]
        if room['current_question'] >= len(room['questions']):
            return None
        
        return room['questions'][room['current_question']]
    
    # ========================
    # CULTURAL CONTENT
    # ========================
    
    def get_random_proverb(self) -> Dict:
        """Get a random Ghanaian proverb"""
        import random
        return random.choice(self.cultural_content['proverbs'])
    
    def get_cultural_categories(self) -> List[str]:
        """Get available cultural categories"""
        return list(self.cultural_content.keys())
    
    def get_category_content(self, category: str) -> List[Dict]:
        """Get content from a specific category"""
        return self.cultural_content.get(category, [])
    
    # ========================
    # SOLO PRACTICE MODE
    # ========================
    
    def create_solo_practice(self, user_id: int) -> str:
        """Create a solo practice session with 3 questions from words"""
        import random
        from database import db
        
        room_id = f"solo_{user_id}_{int(time.time())}"
        
        # Get all available words from database
        all_words = list(db.get_category('words').keys())
        
        if len(all_words) < 4:
            # Not enough words for practice
            return None
        
        # Select 3 random words for questions
        question_words = random.sample(all_words, min(3, len(all_words)))
        
        questions = []
        for word in question_words:
            # Get correct answer
            correct_answer = word
            
            # Get video path
            word_info = db.search(word)
            video_path = word_info['path'] if word_info else None
            
            # Generate wrong answers (3 other random words)
            wrong_answers = [w for w in all_words if w != word]
            wrong_options = random.sample(wrong_answers, min(3, len(wrong_answers)))
            
            # Create options list
            options = [correct_answer] + wrong_options
            random.shuffle(options)
            
            questions.append({
                'question': f"What sign is this?",
                'video_sign': word,
                'correct_answer': correct_answer,
                'options': options,
                'video_path': video_path
            })
        
        self.active_games[room_id] = {
            'room_id': room_id,
            'game_mode': 'solo_practice',
            'players': [user_id],
            'status': 'playing',
            'questions': questions,
            'current_question': 0,
            'scores': {str(user_id): 0},
            'answers': {},
            'created_at': time.time()
        }
        
        return room_id
    
    def submit_solo_answer(self, room_id: str, user_id: int, answer: str) -> Dict:
        """Submit answer for solo practice"""
        if room_id not in self.active_games:
            return {'success': False, 'error': 'Game not found'}
        
        room = self.active_games[room_id]
        current_q = room['questions'][room['current_question']]
        
        # Case-insensitive comparison
        is_correct = answer.upper() == current_q['correct_answer'].upper()
        
        # Award points if correct
        if is_correct:
            points = 100  # Base points for solo practice
            room['scores'][str(user_id)] += points
        
        # Move to next question
        room['current_question'] += 1
        
        # Check if game is finished
        is_finished = room['current_question'] >= len(room['questions'])
        
        if is_finished:
            room['status'] = 'finished'
            # Update user stats
            total_score = room['scores'][str(user_id)]
            self.update_user_stats(user_id, total_score, won=total_score >= 200)
        
        return {
            'success': True,
            'correct': is_correct,
            'correct_answer': current_q['correct_answer'],
            'points_earned': 100 if is_correct else 0,
            'current_score': room['scores'][str(user_id)],
            'is_finished': is_finished,
            'total_questions': len(room['questions']),
            'question_number': room['current_question']
        }


# Singleton instance
game_db = GameDatabase()
