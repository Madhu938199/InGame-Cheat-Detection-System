/**
 * REST API Client for Multiplayer In-Game Cheat Detection System
 */

const BASE_URL = '';

export async function fetchMe() {
  const res = await fetch(`${BASE_URL}/api/auth/me`);
  return res.json();
}

export async function login(username, password) {
  const res = await fetch(`${BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  return res.json();
}

export async function register(username, password, role = 'player') {
  const res = await fetch(`${BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password, role })
  });
  return res.json();
}

export async function logout() {
  const res = await fetch(`${BASE_URL}/api/auth/logout`, {
    method: 'POST'
  });
  return res.json();
}

export async function getRooms() {
  const res = await fetch(`${BASE_URL}/api/rooms`);
  return res.json();
}

export async function getRoomDetail(roomId) {
  const res = await fetch(`${BASE_URL}/api/rooms/${roomId}`);
  return res.json();
}

export async function createRoom(roomName) {
  const res = await fetch(`${BASE_URL}/api/rooms`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ room_name: roomName })
  });
  return res.json();
}

export async function joinRoom(roomId) {
  const res = await fetch(`${BASE_URL}/api/rooms/${roomId}/join`, {
    method: 'POST'
  });
  return res.json();
}

export async function quickFillRoom(roomId) {
  const res = await fetch(`${BASE_URL}/api/rooms/${roomId}/quick-fill`, {
    method: 'POST'
  });
  return res.json();
}

export async function startRoomGame(roomId) {
  const res = await fetch(`${BASE_URL}/api/rooms/${roomId}/start`, {
    method: 'POST'
  });
  return res.json();
}

export async function submitLiveGameplay(stats) {
  const res = await fetch(`${BASE_URL}/api/gameplay/submit-live`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(stats)
  });
  return res.json();
}

export async function getDashboardData() {
  const res = await fetch(`${BASE_URL}/api/detection/dashboard`);
  return res.json();
}

export async function getModeratorQueue() {
  const res = await fetch(`${BASE_URL}/api/moderator/queue`);
  return res.json();
}

export async function submitModeratorReview(data) {
  const res = await fetch(`${BASE_URL}/api/moderator/review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return res.json();
}

export async function getModelInfo() {
  const res = await fetch(`${BASE_URL}/api/model/info`);
  return res.json();
}
