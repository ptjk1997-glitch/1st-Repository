const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const livesEl = document.getElementById('lives');
const levelEl = document.getElementById('level');
const restartBtn = document.getElementById('restartBtn');

const state = {
  score: 0,
  lives: 3,
  level: 1,
  over: false,
  lastTime: 0,
  spawnTimer: 0.7,
  flash: 0,
  bullets: [],
  enemies: [],
  enemyBullets: [],
};

const input = {
  left: false,
  right: false,
  up: false,
  down: false,
  fire: false,
};

const player = {
  x: canvas.width / 2,
  y: canvas.height - 62,
  width: 38,
  height: 46,
  speed: 420,
  cooldown: 0,
  invuln: 0,
};

function updateHud() {
  scoreEl.textContent = String(state.score);
  livesEl.textContent = String(state.lives);
  levelEl.textContent = String(state.level);
}

function resetGame() {
  state.score = 0;
  state.lives = 3;
  state.level = 1;
  state.over = false;
  state.spawnTimer = 0.7;
  state.flash = 0;
  state.bullets = [];
  state.enemies = [];
  state.enemyBullets = [];
  player.x = canvas.width / 2;
  player.y = canvas.height - 62;
  player.cooldown = 0;
  player.invuln = 0;
  updateHud();
}

function fireBullet() {
  if (player.cooldown > 0 || state.over) {
    return;
  }

  player.cooldown = 0.18;

  const spread = state.level >= 3 ? [-8, 0, 8] : [0];
  for (const angleOffset of spread) {
    state.bullets.push({
      x: player.x + angleOffset * 0.35,
      y: player.y - 18,
      radius: 4,
      vy: -680,
      color: '#7dd3fc',
      dx: angleOffset,
    });
  }
}

function fireEnemyBullet(enemy) {
  const dx = player.x - enemy.x;
  const dy = player.y - enemy.y;
  const distance = Math.max(30, Math.hypot(dx, dy));
  const speed = 250 + state.level * 16;

  state.enemyBullets.push({
    x: enemy.x,
    y: enemy.y,
    radius: 5,
    vx: (dx / distance) * speed,
    vy: (dy / distance) * speed,
    color: '#fca5a5',
  });
}

function spawnEnemy() {
  const roll = Math.random();
  const levelFactor = 1 + (state.level - 1) * 0.12;

  let radius = 18 + Math.random() * 12;
  let speed = 120 + Math.random() * 40 + state.level * 8;
  let scoreValue = 10;
  let color = '#f87171';

  if (roll > 0.8) {
    radius = 22 + Math.random() * 12;
    speed = 70 + Math.random() * 25 + state.level * 9;
    scoreValue = 20;
    color = '#fbbf24';
  } else if (roll > 0.45) {
    radius = 16 + Math.random() * 10;
    speed = 140 + Math.random() * 40 + state.level * 14;
    scoreValue = 15;
    color = '#c084fc';
  }

  state.enemies.push({
    x: 30 + Math.random() * (canvas.width - 60),
    y: -radius - 10,
    radius,
    speed: speed * levelFactor,
    phase: Math.random() * Math.PI * 2,
    drift: 30 + Math.random() * 40,
    color,
    scoreValue,
    fireCooldown: 0.8 + Math.random() * 1.2,
  });
}

function hitPlayer() {
  if (player.invuln > 0 || state.over) {
    return;
  }

  state.lives -= 1;
  player.invuln = 1.5;
  state.flash = 1;

  if (state.lives <= 0) {
    state.lives = 0;
    state.over = true;
  }

  updateHud();
}

function intersectsCircleRect(circle, rect) {
  const closestX = Math.max(rect.x, Math.min(circle.x, rect.x + rect.width));
  const closestY = Math.max(rect.y, Math.min(circle.y, rect.y + rect.height));
  const dx = circle.x - closestX;
  const dy = circle.y - closestY;
  return dx * dx + dy * dy <= circle.radius * circle.radius;
}

function update(dt) {
  if (state.over) {
    return;
  }

  state.level = 1 + Math.floor(state.score / 250);
  state.flash = Math.max(0, state.flash - dt * 1.8);
  player.cooldown = Math.max(0, player.cooldown - dt);
  player.invuln = Math.max(0, player.invuln - dt);

  if (input.left) player.x -= player.speed * dt;
  if (input.right) player.x += player.speed * dt;
  if (input.up) player.y -= player.speed * dt;
  if (input.down) player.y += player.speed * dt;
  if (input.fire) fireBullet();

  player.x = Math.max(player.width / 2 + 8, Math.min(canvas.width - player.width / 2 - 8, player.x));
  player.y = Math.max(40, Math.min(canvas.height - player.height / 2 - 8, player.y));

  state.spawnTimer -= dt;
  if (state.spawnTimer <= 0) {
    spawnEnemy();
    const minDelay = 0.35;
    const maxDelay = 1.4;
    state.spawnTimer = minDelay + Math.random() * (maxDelay - minDelay) / (1 + state.level * 0.15);
  }

  for (const bullet of state.bullets) {
    bullet.y += bullet.vy * dt;
    bullet.x += bullet.dx * dt * 60;
  }

  for (const enemyBullet of state.enemyBullets) {
    enemyBullet.x += enemyBullet.vx * dt;
    enemyBullet.y += enemyBullet.vy * dt;
  }

  state.bullets = state.bullets.filter((bullet) => bullet.y > -20);
  state.enemyBullets = state.enemyBullets.filter((bullet) =>
    bullet.x > -20 && bullet.x < canvas.width + 20 && bullet.y > -20 && bullet.y < canvas.height + 20
  );

  for (const enemy of state.enemies) {
    enemy.y += enemy.speed * dt;
    enemy.x += Math.sin((enemy.y + enemy.phase) * 0.06) * enemy.drift * dt;
    enemy.fireCooldown -= dt;

    if (enemy.fireCooldown <= 0) {
      fireEnemyBullet(enemy);
      enemy.fireCooldown = Math.max(0.7, 1.5 - state.level * 0.08) + Math.random() * 0.8;
    }
  }

  for (let i = state.enemies.length - 1; i >= 0; i -= 1) {
    const enemy = state.enemies[i];

    const rect = {
      x: player.x - player.width / 2,
      y: player.y - player.height / 2,
      width: player.width,
      height: player.height,
    };

    if (intersectsCircleRect({ x: enemy.x, y: enemy.y, radius: enemy.radius }, rect)) {
      state.enemies.splice(i, 1);
      hitPlayer();
      continue;
    }

    for (let j = state.bullets.length - 1; j >= 0; j -= 1) {
      const bullet = state.bullets[j];
      const distance = Math.hypot(enemy.x - bullet.x, enemy.y - bullet.y);
      if (distance < enemy.radius + bullet.radius) {
        state.bullets.splice(j, 1);
        state.enemies.splice(i, 1);
        state.score += enemy.scoreValue;
        updateHud();
        break;
      }
    }

    if (enemy.y - enemy.radius > canvas.height + 30) {
      state.enemies.splice(i, 1);
      hitPlayer();
    }
  }

  for (let i = state.enemyBullets.length - 1; i >= 0; i -= 1) {
    const bullet = state.enemyBullets[i];
    const rect = {
      x: player.x - player.width / 2,
      y: player.y - player.height / 2,
      width: player.width,
      height: player.height,
    };

    if (Math.hypot(player.x - bullet.x, player.y - bullet.y) < 18 + player.width * 0.5) {
      state.enemyBullets.splice(i, 1);
      hitPlayer();
      continue;
    }

    if (
      bullet.x > rect.x - bullet.radius &&
      bullet.x < rect.x + rect.width + bullet.radius &&
      bullet.y > rect.y - bullet.radius &&
      bullet.y < rect.y + rect.height + bullet.radius
    ) {
      state.enemyBullets.splice(i, 1);
      hitPlayer();
    }
  }

  updateHud();
}

function drawBackground() {
  const sky = ctx.createLinearGradient(0, 0, 0, canvas.height);
  sky.addColorStop(0, '#030b14');
  sky.addColorStop(0.4, '#0d1e35');
  sky.addColorStop(1, '#06111d');
  ctx.fillStyle = sky;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.strokeStyle = 'rgba(148, 163, 184, 0.12)';
  ctx.lineWidth = 1;
  for (let y = 0; y < canvas.height; y += 40) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
    ctx.stroke();
  }
}

function drawPlayer() {
  const x = player.x;
  const y = player.y;
  const w = player.width;
  const h = player.height;

  if (player.invuln > 0 && Math.floor(player.invuln * 10) % 2 === 0) {
    return;
  }

  ctx.save();
  ctx.translate(x, y);

  ctx.fillStyle = '#e0f2fe';
  ctx.beginPath();
  ctx.moveTo(0, -h / 2);
  ctx.lineTo(w / 2, h / 2);
  ctx.lineTo(0, h / 4);
  ctx.lineTo(-w / 2, h / 2);
  ctx.closePath();
  ctx.fill();

  ctx.fillStyle = '#7dd3fc';
  ctx.fillRect(-5, 6, 10, 18);
  ctx.fillStyle = '#a78bfa';
  ctx.fillRect(-12, -4, 24, 10);

  ctx.restore();
}

function drawEnemy(enemy) {
  ctx.save();
  ctx.translate(enemy.x, enemy.y);
  ctx.fillStyle = enemy.color;
  ctx.beginPath();
  for (let i = 0; i < 6; i += 1) {
    const angle = (Math.PI * 2 / 6) * i;
    const radius = enemy.radius * (i % 2 === 0 ? 1 : 0.6);
    const px = Math.cos(angle) * radius;
    const py = Math.sin(angle) * radius;
    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }
  ctx.closePath();
  ctx.fill();

  ctx.fillStyle = 'rgba(255,255,255,0.7)';
  ctx.beginPath();
  ctx.arc(-enemy.radius * 0.18, -enemy.radius * 0.18, 3, 0, Math.PI * 2);
  ctx.arc(enemy.radius * 0.18, -enemy.radius * 0.18, 3, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawBullets() {
  for (const bullet of state.bullets) {
    ctx.fillStyle = '#7dd3fc';
    ctx.beginPath();
    ctx.arc(bullet.x, bullet.y, bullet.radius, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawEnemyBullets() {
  for (const bullet of state.enemyBullets) {
    ctx.fillStyle = '#fca5a5';
    ctx.beginPath();
    ctx.arc(bullet.x, bullet.y, bullet.radius, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawGameOver() {
  ctx.fillStyle = 'rgba(2, 6, 23, 0.45)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.textAlign = 'center';
  ctx.fillStyle = '#f8fafc';
  ctx.font = '800 48px Segoe UI';
  ctx.fillText('게임 오버', canvas.width / 2, canvas.height / 2 - 20);

  ctx.font = '600 20px Segoe UI';
  ctx.fillStyle = '#cbd5e1';
  ctx.fillText(`최종 점수: ${state.score}`, canvas.width / 2, canvas.height / 2 + 30);
}

function loop(timestamp) {
  const dt = Math.min(0.033, (timestamp - state.lastTime) / 1000 || 0.016);
  state.lastTime = timestamp;

  update(dt);
  drawBackground();
  drawEnemyBullets();
  drawBullets();
  for (const enemy of state.enemies) drawEnemy(enemy);
  drawPlayer();

  if (state.flash > 0) {
    ctx.fillStyle = `rgba(248, 113, 113, ${state.flash * 0.28})`;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }

  if (state.over) {
    drawGameOver();
  }

  requestAnimationFrame(loop);
}

function handleKeyChange(event, pressed) {
  const key = event.key.toLowerCase();
  if (key === 'arrowleft' || key === 'a') input.left = pressed;
  if (key === 'arrowright' || key === 'd') input.right = pressed;
  if (key === 'arrowup' || key === 'w') input.up = pressed;
  if (key === 'arrowdown' || key === 's') input.down = pressed;
  if (key === ' ' || event.code === 'Space') {
    input.fire = pressed;
  }
  if (pressed && (key === ' ' || event.code === 'Space')) {
    fireBullet();
  }
}

window.addEventListener('keydown', (event) => {
  if (['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', ' '].includes(event.key)) {
    event.preventDefault();
  }
  handleKeyChange(event, true);
});

window.addEventListener('keyup', (event) => handleKeyChange(event, false));

canvas.addEventListener('pointerdown', () => {
  if (!state.over) {
    input.fire = true;
    fireBullet();
  }
});

window.addEventListener('pointerup', () => {
  input.fire = false;
});

restartBtn.addEventListener('click', () => {
  resetGame();
});

updateHud();
requestAnimationFrame(loop);
