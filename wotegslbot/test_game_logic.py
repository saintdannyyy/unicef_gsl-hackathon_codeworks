"""Test game logic without Telegram"""
from game_database import game_db

print("=" * 50)
print("Testing Multiplayer Game Logic")
print("=" * 50)

# Create game room
print("\n1. Creating game room...")
room_id = game_db.create_game_room(host_id=12345, game_mode='activities')
print(f"✓ Room created: {room_id}")

game_state = game_db.get_game_state(room_id)
print(f"  Room code: {game_state['room_code']}")
print(f"  Players: {game_state['players']}")

# Join game
print("\n2. Player 2 joining...")
success = game_db.join_game_room(room_id, user_id=67890, username="Player2")
print(f"✓ Joined: {success}")

game_state = game_db.get_game_state(room_id)
print(f"  Players: {game_state['players']}")

# Start game
print("\n3. Starting game...")
success = game_db.start_game(room_id)
print(f"✓ Started: {success}")

game_state = game_db.get_game_state(room_id)
print(f"  Status: {game_state['status']}")
print(f"  Questions generated: {len(game_state['questions'])}")

if game_state['questions']:
    print("\n4. Questions:")
    for i, q in enumerate(game_state['questions'], 1):
        print(f"  Q{i}: {q['question']}")
        print(f"      Correct: {q['correct_answer']}")
        print(f"      Options: {q['options']}")
        print(f"      Video: {q.get('video_sign', 'N/A')}")
else:
    print("\n❌ ERROR: No questions generated!")
    print("This is the bug causing the game to end immediately!")

print("\n" + "=" * 50)
print("Test Complete")
print("=" * 50)
