let selectedUserId = null;
let selectedUsername = null;
// Agar io load nahi hua toh dummy socket bana do, taaki click na ruke
const socket = (typeof io !== 'undefined') ? io() : { emit: ()=>{}, on: ()=>{} };
const myId = parseInt(document.getElementById('user-data').dataset.myId);

// Poori list pe ek hi click lagaya, button pe alag se nahi
document.getElementById('user-list').addEventListener('click', (e) => {
    const btn = e.target.closest('.user-item');
    if (!btn) return;

    selectedUserId = btn.dataset.userId;
    selectedUsername = btn.dataset.username;

    document.getElementById('chat-header').innerText = "Chatting with " + selectedUsername;
    document.getElementById('message-input').disabled = false;
    document.getElementById('send-btn').disabled = false;
    document.getElementById('chat-messages').innerHTML = "";
    document.getElementById('typing-indicator').innerText = ""; // <-- naya user select pe typing saaf karo
    document.querySelectorAll('.user-item').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    fetch(`/get_messages/${selectedUserId}`)
      .then(res => res.json())
      .then(data => {
        data.forEach(m => {
          addMessage(m.message, m.sender_id == myId, m.time); // <-- time add kiya
        });
      });

    socket.emit('join', { room: getRoomId() });
});

function getRoomId() {
    const ids = [myId, parseInt(selectedUserId)].sort((a,b) => a-b);
    return "room_" + ids[0] + "_" + ids[1];
}

// --- addMessage me TIME add kiya ---
function addMessage(msg, isMe, time) {
    const div = document.createElement('div');
    div.className = "mb-2 " + (isMe ? "text-end" : "text-start");
    div.innerHTML = `<span class="badge ${isMe ? 'bg-primary' : 'bg-secondary'} p-2" style="font-size: 14px;">${msg}</span>
                     <div style="font-size:11px; color:grey;">${time || ''}</div>`;
    document.getElementById('chat-messages').appendChild(div);
    document.getElementById('chat-messages').scrollTop = 99999;
}

function sendMessage() {
    const input = document.getElementById('message-input');
    const msg = input.value.trim();
    if (!msg || !selectedUserId) return;
    socket.emit('send_message', { room: getRoomId(), message: msg });
    // --- apne message me abhi ka time dikhao ---
    addMessage(msg, true, new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}));
    input.value = "";
}

document.getElementById('send-btn').onclick = sendMessage;
document.getElementById('message-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// --- TYPING BHEJNA ---
let typingTimeout;
document.getElementById('message-input').addEventListener('input', () => {
    if (!selectedUserId) return;
    socket.emit('typing', { room: getRoomId() });
});

// --- TYPING RECEIVE KARNA ---
socket.on('user_typing', (data) => {
    const indicator = document.getElementById('typing-indicator');
    indicator.innerText = data.username + " is typing...";
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        indicator.innerText = "";
    }, 1500);
});

socket.on('receive_message', (data) => {
    if (data.sender_id != myId) {
        document.getElementById('typing-indicator').innerText = ""; // message aate hi typing hatao
        addMessage(data.message, false, data.time); // <-- time add kiya
    }
});

// Page khulte hi server se aayi online list se dot green karo
socket.on('online_users_list', (data) => {
    data.online_ids.forEach(id => {
        const dot = document.getElementById('dot-' + id);
        if (dot) dot.style.background = 'limegreen';
    });
});

// Jab koi online/offline ho toh dot badlo
socket.on('user_status', (data) => {
    const dot = document.getElementById('dot-' + data.user_id);
    if (dot) {
        dot.style.background = data.status === 'online' ? 'limegreen' : 'grey';
    }
});