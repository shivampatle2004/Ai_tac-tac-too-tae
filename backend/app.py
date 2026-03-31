from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from models import db, User
from game_engine import GameEngine
from minimax import get_best_move
import os
import uuid
import time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='/')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-123')
db_url = os.environ.get('DATABASE_URL', 'sqlite:///local_tictactoe.db')
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=True)

# Application State
active_games = {} # match_id -> GameEngine
user_sockets = {} # username -> sid

# Background task for checking timeouts globally
def timer_task():
    while True:
        socketio.sleep(1)
        for match_id, game in list(active_games.items()):
            if not game.game_over:
                if game.check_timeout():
                    socketio.emit('game_update', game.get_state(), room=match_id)

socketio.start_background_task(timer_task)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Missing credentials'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username exists'}), 400
    
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'status': 'Registration successful'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')):
        session['username'] = user.username
        user.is_active = True
        db.session.commit()
        broadcast_lobby()
        return jsonify(user.to_dict())
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/me', methods=['GET'])
def me():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            return jsonify(user.to_dict())
    return jsonify({'error': 'Not logged in'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    if 'username' in session:
        user = User.query.filter_by(username=session.pop('username')).first()
        if user:
            user.is_active = False
            db.session.commit()
            broadcast_lobby()
    return jsonify({'status': 'Logged out'})


def broadcast_lobby():
    with app.app_context():
        active_users = [u.username for u in User.query.filter_by(is_active=True).all()]
    socketio.emit('lobby_update', {'users': active_users})

@socketio.on('connect')
def on_connect():
    username = session.get('username')
    if username:
        user_sockets[username] = request.sid
        user = User.query.filter_by(username=username).first()
        if user:
            user.is_active = True
            db.session.commit()
        broadcast_lobby()

@socketio.on('disconnect')
def on_disconnect():
    username = session.get('username')
    if username:
        if username in user_sockets:
            del user_sockets[username]
        user = User.query.filter_by(username=username).first()
        if user:
            user.is_active = False
            db.session.commit()
        broadcast_lobby()

@socketio.on('start_ai_game')
def start_ai_game():
    username = session.get('username')
    if not username: return
    
    match_id = str(uuid.uuid4())
    game = GameEngine(match_id, player_x=username, player_o='AI')
    active_games[match_id] = game
    
    join_room(match_id)
    emit('game_started', game.get_state())

@socketio.on('challenge_user')
def challenge_user(data):
    challenger = session.get('username')
    target = data.get('target')
    if target in user_sockets:
        socketio.emit('challenge_received', {'from': challenger}, to=user_sockets[target])

@socketio.on('accept_challenge')
def accept_challenge(data):
    player_o = session.get('username')
    player_x = data.get('challenger')
    
    match_id = str(uuid.uuid4())
    game = GameEngine(match_id, player_x=player_x, player_o=player_o)
    active_games[match_id] = game
    
    # Both join room
    join_room(match_id)
    if player_x in user_sockets:
        socketio.server.enter_room(user_sockets[player_x], match_id)
        
    socketio.emit('game_started', game.get_state(), room=match_id)

@socketio.on('make_move')
def handle_move(data):
    username = session.get('username')
    match_id = data.get('match_id')
    index = data.get('index')
    
    if match_id not in active_games:
        return emit('error', {'msg': 'Game not found'})
        
    game = active_games[match_id]
    
    success, msg, _ = game.make_move(index, username)
    if not success:
        return emit('error', {'msg': msg})
        
    socketio.emit('game_update', game.get_state(), room=match_id)
    
    # Check if AI needs to play
    if not game.game_over and game.player_o == 'AI' and game.current_turn == 'O':
        # Add realistic delay
        time.sleep(0.8)
        # Verify no timeout occurred during sleep
        if not game.check_timeout():
            ai_index = get_best_move(game.board, game.player_moves_o, game.player_moves_x, max_depth=6)
            game.make_move(ai_index, 'AI')
            socketio.emit('game_update', game.get_state(), room=match_id)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
