const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const bestEl = document.getElementById('best');
const restartBtn = document.getElementById('restartBtn');

const groundY = canvas.height - 72;
const bestKey = 'runner-best-score';

const state = {
  running: false,
  gameOver: false,
  score: 0,
  best: Number(localStorage.getItem(bestKey)) || 0,
  speed: 360,
  spawnTimer: 1.2,
  clouds: [],
  obstacles: [],
  particles: [],
  lastTime: 0,
  flash: 0,
};

const player = {
  x: 130,
  y: groundY - 52,
  width: 42,
  height: 52,
  vy: 0,
  grounded: true,
};

function resetPlayer() {
  player.y = groundY - player.height;
  player.vy = 0;
  player.grounded = true;
}

function refreshHud() {
  scoreEl.textContent = String(Math.floor(state.score));
  bestEl.textContent = String(state.best);
}

function resetGame() {
  state.running = false;
  state.gameOver = false;
  state.score = 0;
  state.speed = 360;
  state.spawnTimer = 1.2;
  state.obstacles = [];
  state.particles = [];
  state.flash = 0;
  resetPlayer();
  refreshHud();
}

function startGame() {
  if (!state.running) {
    state.running = true;
    state.gameOver = false;
    if (state.score === 0) {
      state.spawnTimer = 1;
    }
  }
}

function updateBest() {
  const current = Math.floor(state.score);
  state.best = Math.max(state.best, current);
  localStorage.setItem(bestKey, String(state.best));
  refreshHud();
}

function createClouds() {
  state.clouds = Array.from({ length: 7 }, (_, index) => ({
    x: 100 + index * 170,
    y: 60 + (index % 3) * 55,
    w: 60 + (index % 4) * 16,
    h: 28 + (index % 3) * 10,
    speed: 18 + (index % 5) * 6,
  }));
}

function spawnObstacle() {
  const typeRoll = Math.random();
  const width = typeRoll > 0.65 ? 34 : 52;
  const height = typeRoll > 0.65 ? 34 : 62;

  state.obstacles.push({
    x: canvas.width + 20,
    y: groundY - height,
    width,
    height,
    color: typeRoll > 0.5 ? '#f59e0b' : '#ef4444',
    kind: typeRoll > 0.5 ? 'rock' : 'cactus',
  });
}

function addBurst(x, y, color) {
  for (let i = 0; i < 10; i += 1) {
    state.particles.push({
      x,
      y,
      vx: (Math.random() - 0.5) * 240,
      vy: (Math.random() - 0.7) * 200,
      radius: 3 + Math.random() * 4,
      color,
      life: 0.7 + Math.random() * 0.6,
    });
  }
}

function jump() {
  if (!state.running) {
    startGame();
  }

  if (player.grounded) {
    player.vy = -680;
    player.grounded = false;
    addBurst(player.x + player.width * 0.4, player.y + player.height, '#fef3c7');
  }
}

function gameOver() {
  state.running = false;
  state.gameOver = true;
  state.flash = 1;
  updateBest();
  addBurst(player.x + player.width / 2, player.y + player.height / 2, '#f87171');
}

function intersects(a, b) {
  return (
    a.x < b.x + b.width &&
    a.x + a.width > b.x &&
    a.y < b.y + b.height &&
    a.y + a.height > b.y
  );
}

function update(dt) {
  if (!state.running) {
    for (const cloud of state.clouds) {
      cloud.x -= cloud.speed * dt * 0.25;
      if (cloud.x + cloud.w < -60) {
        cloud.x = canvas.width + 30;
      }
    }
    return;
  }

  state.score += dt * 14;
  state.speed += dt * 3.5;
  state.flash = Math.max(0, state.flash - dt * 1.6);
  state.spawnTimer -= dt;

  if (state.spawnTimer <= 0) {
    spawnObstacle();
    state.spawnTimer = Math.max(0.7, 1.45 - state.score / 220);
  }

  for (const cloud of state.clouds) {
    cloud.x -= cloud.speed * dt;
    if (cloud.x + cloud.w < -60) {
      cloud.x = canvas.width + 30;
    }
  }

  player.vy += 1700 * dt;
  player.y += player.vy * dt;

  if (player.y >= groundY - player.height) {
    player.y = groundY - player.height;
    player.vy = 0;
    player.grounded = true;
  } else {
    player.grounded = false;
  }

  for (const obstacle of state.obstacles) {
    obstacle.x -= state.speed * dt;
  }

  state.obstacles = state.obstacles.filter((obstacle) => obstacle.x + obstacle.width > -20);

  for (const obstacle of state.obstacles) {
    if (intersects(player, obstacle)) {
      gameOver();
      break;
    }
  }

  for (const particle of state.particles) {
    particle.x += particle.vx * dt;
    particle.y += particle.vy * dt;
    particle.vy += 520 * dt;
    particle.life -= dt;
  }

  state.particles = state.particles.filter((particle) => particle.life > 0);
  refreshHud();
}

function drawBackground() {
  const sky = ctx.createLinearGradient(0, 0, 0, canvas.height);
  sky.addColorStop(0, '#7dd3fc');
  sky.addColorStop(0.5, '#dbeafe');
  sky.addColorStop(1, '#d8f3dc');
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = 'rgba(251, 191, 36, 0.9)';
  ctx.beginPath();
  ctx.arc(canvas.width - 120, 110, 42, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = 'rgba(15, 118, 110, 0.4)';
  ctx.beginPath();
  ctx.moveTo(0, 420);
  ctx.lineTo(160, 300);
  ctx.lineTo(300, 420);
  ctx.lineTo(470, 270);
  ctx.lineTo(630, 430);
  ctx.lineTo(760, 310);
  ctx.lineTo(960, 440);
  ctx.lineTo(960, 540);
  ctx.lineTo(0, 540);
  ctx.closePath();
  ctx.fill();

  for (const cloud of state.clouds) {
    ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
    ctx.beginPath();
    ctx.arc(cloud.x, cloud.y, 18, 0, Math.PI * 2);
    ctx.arc(cloud.x + 24, cloud.y - 8, 22, 0, Math.PI * 2);
    ctx.arc(cloud.x + 50, cloud.y, 18, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawGround() {
  ctx.fillStyle = '#285a46';
  ctx.fillRect(0, groundY, canvas.width, canvas.height - groundY);

  ctx.fillStyle = '#1b3c30';
  ctx.fillRect(0, groundY, canvas.width, 10);

  for (let x = -40; x < canvas.width + 40; x += 30) {
    ctx.fillStyle = '#d1fae5';
    ctx.fillRect(x, groundY + 18, 18, 6);
    ctx.fillStyle = '#86efac';
    ctx.fillRect(x + 6, groundY + 26, 10, 6);
  }
}

function drawPlayer() {
  const { x, y, width, height } = player;

  ctx.fillStyle = '#1e293b';
  ctx.fillRect(x + 10, y + 8, width - 18, height - 8);

  ctx.fillStyle = '#fbbf24';
  ctx.fillRect(x + 8, y + 12, width - 16, height - 16);

  ctx.fillStyle = '#0f172a';
  ctx.fillRect(x + 12, y + 18, 7, 7);
  ctx.fillRect(x + width - 19, y + 18, 7, 7);

  ctx.fillStyle = '#f8fafc';
  ctx.fillRect(x + 12, y + 18, 3, 3);
  ctx.fillRect(x + width - 19, y + 18, 3, 3);

  ctx.fillStyle = '#ef4444';
  ctx.fillRect(x + 14, y + 30, width - 28, 10);

  ctx.fillStyle = '#a78bfa';
  ctx.fillRect(x + 8, y + 36, width - 16, 7);

  ctx.fillStyle = '#f97316';
  ctx.fillRect(x + width / 2 - 5, y + 44, 10, 8);
}

function drawObstacle(obstacle) {
  const { x, y, width, height, color } = obstacle;

  if (obstacle.kind === 'cactus') {
    ctx.fillStyle = '#166534';
    ctx.fillRect(x + 8, y + height - 18, width - 16, 18);
    ctx.fillRect(x + 4, y + height - 32, 12, 32);
    ctx.fillRect(x + width - 16, y + height - 32, 12, 32);
    ctx.fillStyle = '#86efac';
    ctx.fillRect(x + 10, y + height - 24, width - 20, 5);
  } else {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(x + width / 2, y);
    ctx.lineTo(x + width, y + height);
    ctx.lineTo(x, y + height);
    ctx.closePath();
    ctx.fill();

    ctx.fillStyle = 'rgba(255,255,255,0.25)';
    ctx.fillRect(x + width * 0.25, y + 8, 8, 10);
  }
}

function drawParticles() {
  for (const particle of state.particles) {
    ctx.globalAlpha = Math.max(0, particle.life);
    ctx.fillStyle = particle.color;
    ctx.beginPath();
    ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalAlpha = 1;
}

function drawOverlay() {
  if (!state.running && !state.gameOver) {
    ctx.fillStyle = 'rgba(15, 23, 42, 0.18)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#0f172a';
    ctx.font = '800 52px Segoe UI';
    ctx.textAlign = 'center';
    ctx.fillText('제비루스 러너', canvas.width / 2, canvas.height / 2 - 20);

    ctx.font = '600 24px Segoe UI';
    ctx.fillText('스페이스 또는 클릭으로 시작', canvas.width / 2, canvas.height / 2 + 28);
  }

  if (state.gameOver) {
    ctx.fillStyle = 'rgba(15, 23, 42, 0.4)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#f8fafc';
    ctx.font = '800 52px Segoe UI';
    ctx.textAlign = 'center';
    ctx.fillText('게임 오버', canvas.width / 2, canvas.height / 2 - 18);

    ctx.font = '700 26px Segoe UI';
    ctx.fillText(`점수: ${Math.floor(state.score)}`, canvas.width / 2, canvas.height / 2 + 34);
    ctx.fillText('R 또는 버튼으로 다시 시작', canvas.width / 2, canvas.height / 2 + 72);
  }
}

function draw() {
  drawBackground();
  drawGround();

  for (const obstacle of state.obstacles) {
    drawObstacle(obstacle);
  }

  drawPlayer();
  drawParticles();

  if (state.flash > 0) {
    ctx.fillStyle = `rgba(248, 113, 113, ${state.flash * 0.35})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }

  drawOverlay();
}

function loop(timestamp) {
  const dt = Math.min((timestamp - state.lastTime) / 1000 || 0.016, 0.032);
  state.lastTime = timestamp;
  update(dt);
  draw();
  requestAnimationFrame(loop);
}

window.addEventListener('keydown', (event) => {
  const key = event.key.toLowerCase();

  if ([' ', 'arrowup', 'w'].includes(key) || event.key === 'ArrowUp') {
    event.preventDefault();
    jump();
    return;
  }

  if (key === 'r' && state.gameOver) {
    resetGame();
    startGame();
  }
});

canvas.addEventListener('pointerdown', () => {
  jump();
});

restartBtn.addEventListener('click', () => {
  resetGame();
  startGame();
});

createClouds();
resetGame();
refreshHud();
requestAnimationFrame(loop);
