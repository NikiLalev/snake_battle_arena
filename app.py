from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid
import random
import time
import threading
import traceback

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Fix for PyInstaller - use threading mode which is more reliable
try:
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
except:
    # Fallback if threading doesn't work
    socketio = SocketIO(app, cors_allowed_origins="*")

# Game state
games = {}
players = {}

# Game settings
GRID_SIZE = 20
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

# Funny mean comments for dead players
MEAN_COMMENTS = [
    "You suck! 😂",
    "Haha you died! 💀",
    "Better luck next time, loser! 🐍",
    "That was embarrassing! 😆",
    "You call that snake skills? 🙄",
    "Even a turtle could play better! 🐢",
    "Your snake died of shame! 😂",
    "Did you forget how to use arrow keys? ⌨️",
    "That was painful to watch! 😬",
    "Maybe try checkers instead? 🔴",
    "RIP your dignity! ⚰️",
    "Your snake had commitment issues! 💔",
    "I've seen rocks move faster! 🪨",
    "That crash was epic! 💥",
    "Snake.exe has stopped working! 🖥️",
    "You got outplayed by a wall! 🧱",
    "Press F to pay respects... to your skills! F",
    "Your snake just rage quit! 😤",
    "That's what we call a 'tactical disaster'! 🎯",
    "Next time, try not dying! 💡",
    "Skill issue detected! 🚨",
    "Your snake went to the graveyard! 🪦",
    "That was a masterclass in how NOT to play! 📚",
    "Game over, man! Game over! 🎮",
    "You made that look so easy... to lose! 🤣"
]

@app.route('/')
def index():
    """Main game page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'ok', 'players': len(players), 'games': len(games)}

# Game classes
class Snake:
    def __init__(self, x, y, color):
        self.body = [(x, y)]
        self.direction = 'RIGHT'
        self.color = color
        self.alive = True
        self.score = 0
        self.just_died = False  # New field to track fresh deaths
    
    def move(self):
        if not self.alive or not self.body:
            return
            
        head = self.body[0]
        
        if self.direction == 'UP':
            new_head = (head[0], head[1] - 1)
        elif self.direction == 'DOWN':
            new_head = (head[0], head[1] + 1)
        elif self.direction == 'LEFT':
            new_head = (head[0] - 1, head[1])
        elif self.direction == 'RIGHT':
            new_head = (head[0] + 1, head[1])
        else:
            return
        
        self.body.insert(0, new_head)
    
    def check_collision(self, width, height, other_snakes):
        if not self.alive:
            return
            
        head = self.body[0]
        was_alive = self.alive
        
        # Wall collision
        if head[0] < 0 or head[0] >= width or head[1] < 0 or head[1] >= height:
            self.alive = False
        
        # Self collision
        elif head in self.body[1:]:
            self.alive = False
        
        # Other snakes collision
        else:
            for snake in other_snakes:
                if snake != self and head in snake.body:
                    self.alive = False
                    break
        
        # Mark as just died if it was alive and now isn't
        if was_alive and not self.alive:
            self.just_died = True

class Food:
    def __init__(self, width, height):
        self.x = random.randint(0, width - 1)
        self.y = random.randint(0, height - 1)
    
    def respawn(self, width, height, snakes):
        while True:
            self.x = random.randint(0, width - 1)
            self.y = random.randint(0, height - 1)
            
            # Make sure food doesn't spawn on snake
            collision = False
            for snake in snakes:
                if (self.x, self.y) in snake.body:
                    collision = True
                    break
            
            if not collision:
                break

class Game:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = {}
        self.snakes = {}
        self.food = Food(CANVAS_WIDTH // GRID_SIZE, CANVAS_HEIGHT // GRID_SIZE)
        self.game_running = False
        self.countdown_active = False
        self.game_started = False
        self.last_update = time.time()
        self.dead_players = set()  # Track players who have died
        self.game_winner = None  # Track the winner
    
    def add_player(self, player_id, player_name):
        colors = ['#ff4444', '#44ff44', '#4444ff', '#ffff44']
        color = colors[len(self.players) % len(colors)]
        
        # Starting positions
        start_positions = [(5, 5), (35, 5), (5, 25), (35, 25)]
        start_pos = start_positions[len(self.players) % len(start_positions)]
        
        self.players[player_id] = {
            'name': player_name,
            'color': color,
            'ready': False
        }
        
        self.snakes[player_id] = Snake(start_pos[0], start_pos[1], color)
    
    def remove_player(self, player_id):
        if player_id in self.players:
            del self.players[player_id]
        if player_id in self.snakes:
            del self.snakes[player_id]
    
    def start_game(self):
        if self.game_started or self.countdown_active:
            return False
            
        self.countdown_active = True
        self.game_started = True
        
        # Reset all snakes to starting positions
        start_positions = [(5, 5), (35, 5), (5, 25), (35, 25)]
        for i, (player_id, snake) in enumerate(self.snakes.items()):
            start_pos = start_positions[i % len(start_positions)]
            snake.body = [start_pos]
            snake.direction = 'RIGHT'
            snake.alive = True
            snake.score = 0
            snake.just_died = False
        
        # Reset death tracking
        self.dead_players.clear()
        self.game_winner = None
        
        # Start countdown in separate thread
        countdown_thread = threading.Thread(target=self.countdown, daemon=True)
        countdown_thread.start()
        return True
    
    def countdown(self):
        """Handle game countdown"""
        try:
            for i in range(3, 0, -1):
                socketio.emit('countdown', {'count': i}, room=self.room_id)
                time.sleep(1)
            
            socketio.emit('countdown', {'count': 0}, room=self.room_id)
            time.sleep(0.5)
            
            # Actually start the game
            self.game_running = True
            self.countdown_active = False
            self.last_update = time.time()
            
            # Send immediate game state to show movement has started
            game_state = {
                'snakes': {pid: {
                    'body': snake.body,
                    'color': snake.color,
                    'alive': snake.alive,
                    'score': snake.score
                } for pid, snake in self.snakes.items()},
                'food': {'x': self.food.x, 'y': self.food.y},
                'running': True
            }
            socketio.emit('game_state', game_state, room=self.room_id)
            
        except Exception as e:
            self.game_running = False
            self.countdown_active = False
            self.game_started = False

    def update(self):
        if not self.game_running:
            return
        
        # Move all snakes first
        for player_id, snake in self.snakes.items():
            if snake.alive:
                snake.move()
        
        # Check collisions
        width = CANVAS_WIDTH // GRID_SIZE
        height = CANVAS_HEIGHT // GRID_SIZE
        
        for snake in self.snakes.values():
            snake.check_collision(width, height, list(self.snakes.values()))
        
        # Handle death events
        for player_id, snake in self.snakes.items():
            if snake.just_died:
                snake.just_died = False  # Reset the flag
                self.dead_players.add(player_id)
                player_name = self.players[player_id]['name']
                
                # Emit death event to the specific player
                socketio.emit('player_died', {
                    'player_name': player_name
                }, room=player_id)
        
        # Check food collision and handle snake growth
        food_eaten = False
        for player_id, snake in self.snakes.items():
            if snake.alive and len(snake.body) > 0 and snake.body[0] == (self.food.x, self.food.y):
                snake.score += 10
                food_eaten = True
                # Don't remove tail when food is eaten (snake grows)
            else:
                # Remove tail if no food eaten (normal movement)
                if snake.alive and len(snake.body) > 1:
                    snake.body.pop()
        
        # Respawn food if it was eaten
        if food_eaten:
            self.food.respawn(width, height, list(self.snakes.values()))
        
        # Check if game should end
        alive_snakes = [(pid, s) for pid, s in self.snakes.items() if s.alive]
        if len(alive_snakes) <= 1 and len(self.snakes) > 1:
            self.game_running = False
            
            # Determine winner
            if len(alive_snakes) == 1:
                winner_id, winner_snake = alive_snakes[0]
                self.game_winner = {
                    'player_id': winner_id,
                    'player_name': self.players[winner_id]['name'],
                    'score': winner_snake.score
                }
                
                # Emit winner event to the winner
                socketio.emit('player_won', {
                    'player_name': self.game_winner['player_name'],
                    'score': self.game_winner['score']
                }, room=winner_id)
            
            # Reset flags to allow new game
            self.game_started = False
            self.countdown_active = False

# Socket events
@socketio.on('connect')
def on_connect():
    pass

@socketio.on('disconnect')
def on_disconnect():
    player_id = request.sid
    
    if player_id in players:
        room_id = players[player_id]['room']
        if room_id in games:
            games[room_id].remove_player(player_id)
            if not games[room_id].players:
                del games[room_id]
            else:
                # Send updated player list to remaining players
                updated_players = [{'id': pid, 'name': pdata['name'], 'color': pdata['color']} 
                                  for pid, pdata in games[room_id].players.items()]
                emit('player_left', {
                    'player_id': player_id,
                    'players': updated_players
                }, room=room_id)
        del players[player_id]

@socketio.on('create_room')
def on_create_room(data):
    try:
        player_name = data.get('playerName', 'Anonymous')
        if not player_name or not player_name.strip():
            emit('error', {'message': 'Player name is required'})
            return
            
        room_id = str(uuid.uuid4())[:8]
        
        games[room_id] = Game(room_id)
        games[room_id].add_player(request.sid, player_name.strip())
        
        players[request.sid] = {
            'name': player_name.strip(),
            'room': room_id
        }
        
        join_room(room_id)
        emit('room_created', {
            'roomId': room_id, 
            'playerName': player_name.strip(),
            'players': [{'id': request.sid, 'name': player_name.strip(), 'color': games[room_id].players[request.sid]['color']}]
        })
        
    except Exception as e:
        emit('error', {'message': 'Failed to create room'})

@socketio.on('join_room')
def on_join_room(data):
    try:
        room_id = data.get('roomId', '').strip()
        player_name = data.get('playerName', 'Anonymous').strip()
        
        if not room_id:
            emit('error', {'message': 'Room ID is required'})
            return
            
        if not player_name:
            emit('error', {'message': 'Player name is required'})
            return
        
        if room_id not in games:
            emit('error', {'message': 'Room not found'})
            return
        
        if len(games[room_id].players) >= 4:
            emit('error', {'message': 'Room is full (max 4 players)'})
            return
        
        games[room_id].add_player(request.sid, player_name)
        players[request.sid] = {
            'name': player_name,
            'room': room_id
        }
        
        join_room(room_id)
        
        # Send room info to joining player
        room_info = {
            'roomId': room_id,
            'players': [{'id': pid, 'name': pdata['name'], 'color': pdata['color']} 
                       for pid, pdata in games[room_id].players.items()],
            'isRoomCreator': False
        }
        emit('room_joined', room_info)
        
        # Notify other players and send updated player list
        updated_players = [{'id': pid, 'name': pdata['name'], 'color': pdata['color']} 
                          for pid, pdata in games[room_id].players.items()]
        emit('player_joined', {
            'player_id': request.sid, 
            'player_name': player_name,
            'players': updated_players
        }, room=room_id, include_self=False)
        
    except Exception as e:
        emit('error', {'message': 'Failed to join room'})

@socketio.on('start_game')
def on_start_game():
    player_id = request.sid
    
    if player_id not in players:
        emit('error', {'message': 'Player not found'})
        return
    
    room_id = players[player_id]['room']
    if room_id not in games:
        emit('error', {'message': 'Room not found'})
        return
    
    # Try to start the game (will fail if already started)
    if games[room_id].start_game():
        emit('game_started', room=room_id)
        
        # Send initial game state immediately
        game = games[room_id]
        initial_game_state = {
            'snakes': {pid: {
                'body': snake.body,
                'color': snake.color,
                'alive': snake.alive,
                'score': snake.score
            } for pid, snake in game.snakes.items()},
            'food': {'x': game.food.x, 'y': game.food.y},
            'running': False
        }
        socketio.emit('game_state', initial_game_state, room=room_id)
    else:
        emit('error', {'message': 'Game already in progress'})

@socketio.on('player_move')
def on_player_move(data):
    player_id = request.sid
    if player_id not in players:
        return
    
    room_id = players[player_id]['room']
    if room_id not in games or player_id not in games[room_id].snakes:
        return
    
    if not games[room_id].game_running:
        return
    
    direction = data['direction']
    snake = games[room_id].snakes[player_id]
    
    # Prevent reverse direction
    opposite = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
    if direction != opposite.get(snake.direction):
        snake.direction = direction

def send_mean_comments():
    """Send periodic mean comments to dead players"""
    while True:
        try:
            for room_id, game in list(games.items()):
                if game.game_running and game.dead_players:
                    # Send a random mean comment to a random dead player
                    if game.dead_players:
                        dead_player = random.choice(list(game.dead_players))
                        comment = random.choice(MEAN_COMMENTS)
                        socketio.emit('mean_comment', {
                            'comment': comment
                        }, room=dead_player)
            
            # Wait 3-8 seconds before sending another comment
            time.sleep(random.uniform(3.0, 8.0))
            
        except Exception as e:
            time.sleep(5)

def game_loop():
    """Main game loop"""
    while True:
        try:
            current_time = time.time()
            
            for room_id, game in list(games.items()):
                # Only update if game is actually running (not in countdown)
                if game.game_running and current_time - game.last_update > 0.2:  # 5 FPS
                    game.update()
                    game.last_update = current_time
                    
                    # Send game state to all players in room
                    game_state = {
                        'snakes': {pid: {
                            'body': snake.body,
                            'color': snake.color,
                            'alive': snake.alive,
                            'score': snake.score
                        } for pid, snake in game.snakes.items()},
                        'food': {'x': game.food.x, 'y': game.food.y},
                        'running': game.game_running
                    }
                    
                    socketio.emit('game_state', game_state, room=room_id)
            
            time.sleep(0.05)  # 20 FPS check rate
            
        except Exception as e:
            time.sleep(1)

# Start the game loop and mean comments thread
game_thread = threading.Thread(target=game_loop, daemon=True)
game_thread.start()

mean_comments_thread = threading.Thread(target=send_mean_comments, daemon=True)
mean_comments_thread.start()

if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except Exception as e:
        input("Press Enter to exit...")