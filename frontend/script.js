let socket;
let currentUser = null;
let currentMatchState = null;
let timerInterval = null;

// Screens
const authScreen = document.getElementById('auth-container');
const lobbyScreen = document.getElementById('lobby-container');
const gameScreen = document.getElementById('game-container');
const challengeModal = document.getElementById('challenge-modal');

console.log("Tic Tac Toe Script Loaded");

// Init Sequence
checkAuth();

function checkAuth() {
    fetch('/api/me')
        .then(res => {
            if (!res.ok) throw new Error("Not logged in");
            return res.json();
        })
        .then(data => {
            if (data.username) {
                currentUser = data.username;
                initSocket();
                showScreen('lobby');
                document.getElementById('user-display').textContent = currentUser;
            } else {
                showScreen('auth');
            }
        })
        .catch(err => {
            console.log("Auth Check:", err.message);
            showScreen('auth');
        });
}

function showScreen(name) {
    authScreen.classList.add('hidden');
    lobbyScreen.classList.add('hidden');
    gameScreen.classList.add('hidden');
    if (name === 'auth') authScreen.classList.remove('hidden');
    if (name === 'lobby') lobbyScreen.classList.remove('hidden');
    if (name === 'game') gameScreen.classList.remove('hidden');
}

// ------ AUTHENTICATION LOGIC ------ //
let isLoginMode = true;
const tabLogin = document.getElementById('tab-login');
const tabRegister = document.getElementById('tab-register');
const authSubmit = document.getElementById('auth-submit');
const errorMsg = document.getElementById('auth-error');

tabLogin.onclick = () => { isLoginMode = true; tabLogin.classList.add('active'); tabRegister.classList.remove('active'); authSubmit.textContent = "Log In"; errorMsg.textContent=""; }
tabRegister.onclick = () => { isLoginMode = false; tabRegister.classList.add('active'); tabLogin.classList.remove('active'); authSubmit.textContent = "Register"; errorMsg.textContent=""; }

authSubmit.onclick = () => {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    
    const url = isLoginMode ? '/api/login' : '/api/register';
    
    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user, password: pass })
    }).then(res => res.json()).then(data => {
        if (data.error) {
            errorMsg.textContent = data.error;
        } else {
            document.getElementById('password').value = ""; // clear password securely
            if (isLoginMode) {
                checkAuth(); // load user & init socket
            } else {
                errorMsg.textContent = "Registration successful! Please log in.";
                errorMsg.style.color = "#4ade80";
                setTimeout(() => tabLogin.onclick(), 1500);
            }
        }
    });
};

document.getElementById('logout-btn').onclick = () => {
    fetch('/api/logout', { method: 'POST' }).then(() => {
        currentUser = null;
        if(socket) socket.disconnect();
        showScreen('auth');
    });
};

// ------ LOBBY & SOCKET LOGIC ------ //
function initSocket() {
    if(socket) return;
    socket = io();
    
    socket.on('lobby_update', (data) => {
        const list = document.getElementById('active-users-list');
        list.innerHTML = "";
        data.users.forEach(u => {
            if (u === currentUser) return; // don't show self
            const div = document.createElement('div');
            div.className = 'user-item';
            div.innerHTML = `<span class="user-name">${u}</span> <button class="btn challenge-btn" data-user="${u}">Challenge</button>`;
            list.appendChild(div);
        });
        
        document.querySelectorAll('.challenge-btn').forEach(btn => {
            btn.onclick = (e) => {
                socket.emit('challenge_user', { target: e.target.getAttribute('data-user') });
                e.target.textContent = "Sent...";
                e.target.disabled = true;
            };
        });
    });

    socket.on('challenge_received', (data) => {
        document.getElementById('challenger-name').textContent = data.from;
        challengeModal.classList.remove('hidden');
        
        document.getElementById('accept-challenge-btn').onclick = () => {
            socket.emit('accept_challenge', { challenger: data.from });
            challengeModal.classList.add('hidden');
        };
        
        document.getElementById('decline-challenge-btn').onclick = () => {
            challengeModal.classList.add('hidden');
        };
    });

    socket.on('game_started', (state) => {
        currentMatchState = state;
        showScreen('game');
        document.getElementById('match-title').textContent = `${state.player_x} vs ${state.player_o}`;
        renderBoard();
        startTimerLocal(state.time_left);
    });

    socket.on('game_update', (state) => {
        currentMatchState = state;
        renderBoard();
        if (!state.game_over) {
            startTimerLocal(state.time_left);
        } else {
            clearInterval(timerInterval);
        }
    });
}

document.getElementById('play-ai-btn').onclick = () => {
    if(socket) socket.emit('start_ai_game');
};

document.getElementById('quit-btn').onclick = () => {
    currentMatchState = null;
    clearInterval(timerInterval);
    showScreen('lobby');
};

// ------ GAME LOGIC ------ //
const cells = document.querySelectorAll('.cell');
const statusText = document.getElementById('status-text');
const loading = document.getElementById('loading');

cells.forEach(cell => {
    cell.onclick = () => {
        if (!currentMatchState || currentMatchState.game_over) return;
        
        // Ensure it's our turn
        const isMyTurn = (currentMatchState.current_turn === 'X' && currentMatchState.player_x === currentUser) || 
                         (currentMatchState.current_turn === 'O' && currentMatchState.player_o === currentUser);
                         
        if (!isMyTurn) return;
        
        const index = parseInt(cell.getAttribute('data-index'));
        if (currentMatchState.board[index] !== '') return;

        // Optimistic UI mapping
        currentMatchState.board[index] = currentMatchState.current_turn; 
        renderBoard(); 

        socket.emit('make_move', { match_id: currentMatchState.match_id, index: index });
    };
});

function renderBoard() {
    // Move count & Sudden Death Alert
    const moveCounter = document.getElementById('move-counter');
    moveCounter.textContent = `Moves: ${currentMatchState.move_count}`;
    if (currentMatchState.move_count >= 20) {
        moveCounter.textContent += " | SUDDEN DEATH!";
        moveCounter.style.color = "var(--secondary)";
    } else {
        moveCounter.style.color = "var(--text-dim)";
    }

    // Top text indicator
    if (currentMatchState.game_over) {
        statusText.classList.remove('hidden');
        loading.classList.add('hidden');
        statusText.textContent = currentMatchState.winner.includes('timeout') 
            ? `${currentMatchState.winner}` 
            : `🎉 ${currentMatchState.winner} Won! 🎉`;
    } else {
        const isMyTurn = (currentMatchState.current_turn === 'X' && currentMatchState.player_x === currentUser) || 
                         (currentMatchState.current_turn === 'O' && currentMatchState.player_o === currentUser);
        if (isMyTurn) {
            statusText.classList.remove('hidden');
            loading.classList.add('hidden');
            statusText.textContent = "Your Turn!";
        } else {
            statusText.classList.add('hidden');
            loading.classList.remove('hidden');
            document.getElementById('loading-txt').textContent = currentMatchState.player_o === 'AI' ? "AI is thinking..." : "Opponent's turn...";
        }
    }

    // Cells
    cells.forEach((cell, i) => {
        const val = currentMatchState.board[i];
        cell.className = "cell"; // reset
        if (val === 'X') { 
            cell.textContent = 'X'; 
            cell.classList.add('x'); 
            // Determine Age
            const idx = currentMatchState.moves_x.indexOf(i);
            if (i === currentMatchState.pending_removal_x) cell.classList.add('fading');
            else if (idx === currentMatchState.moves_x.length - 1) cell.classList.add('vibrant');
            else cell.classList.add('aged');
        }
        else if (val === 'O') { 
            cell.textContent = 'O'; 
            cell.classList.add('o'); 
            // Determine Age
            const idx = currentMatchState.moves_o.indexOf(i);
            if (i === currentMatchState.pending_removal_o) cell.classList.add('fading');
            else if (idx === currentMatchState.moves_o.length - 1) cell.classList.add('vibrant');
            else cell.classList.add('aged');
        }
        else { cell.textContent = ''; }
    });
}

function startTimerLocal(secondsLeft) {
    clearInterval(timerInterval);
    const bar = document.getElementById('timer-bar');
    // Using 10 seconds total width reference since time limit translates visually
    let t = secondsLeft;
    
    // reset instantly
    bar.style.transition = 'none';
    bar.style.width = `${(t/10)*100}%`;
    bar.className = 'timer-bar';
    
    setTimeout(() => {
        bar.style.transition = 'width 1s linear, background 0.3s';
    }, 50);

    timerInterval = setInterval(() => {
        t -= 1;
        if (t <= 0) {
            t = 0;
            clearInterval(timerInterval);
        }
        bar.style.width = `${(t/10)*100}%`;
        
        if (t <= 3) bar.className = 'timer-bar danger';
        else if (t <= 5) bar.className = 'timer-bar warning';
        else bar.className = 'timer-bar';
    }, 1000);
}
