const COLS = 10;
const ROWS = 20;
const BLOCK = 30;
const LINES_PER_LEVEL = 10;

const COLORS = {
  I: '#38bdf8',
  O: '#facc15',
  T: '#c084fc',
  S: '#4ade80',
  Z: '#f87171',
  J: '#60a5fa',
  L: '#fb923c',
  G: '#1f2937'
};

const SHAPES = {
  I: [[1, 1, 1, 1]],
  O: [
    [1, 1],
    [1, 1]
  ],
  T: [
    [0, 1, 0],
    [1, 1, 1]
  ],
  S: [
    [0, 1, 1],
    [1, 1, 0]
  ],
  Z: [
    [1, 1, 0],
    [0, 1, 1]
  ],
  J: [
    [1, 0, 0],
    [1, 1, 1]
  ],
  L: [
    [0, 0, 1],
    [1, 1, 1]
  ]
};

const boardCanvas = document.getElementById('game');
const boardCtx = boardCanvas.getContext('2d');
const nextCanvas = document.getElementById('next');
const nextCtx = nextCanvas.getContext('2d');
const scoreEl = document.getElementById('score');
const linesEl = document.getElementById('lines');
const levelEl = document.getElementById('level');
const restartBtn = document.getElementById('restartBtn');

let board = [];
let currentPiece = null;
let nextPiece = null;
let score = 0;
let lines = 0;
let level = 1;
let droppedTime = 0;
let lastTime = 0;
let animationId = null;
let isGameOver = false;

function createBoard() {
  return Array.from({ length: ROWS }, () => Array(COLS).fill(null));
}

function cloneMatrix(matrix) {
  return matrix.map((row) => [...row]);
}

function randomPiece() {
  const keys = Object.keys(SHAPES);
  const type = keys[Math.floor(Math.random() * keys.length)];
  return {
    type,
    matrix: cloneMatrix(SHAPES[type]),
    x: Math.floor(COLS / 2) - Math.ceil(SHAPES[type][0].length / 2),
    y: 0,
    color: COLORS[type]
  };
}

function resetGame() {
  board = createBoard();
  score = 0;
  lines = 0;
  level = 1;
  scoreEl.textContent = '0';
  linesEl.textContent = '0';
  levelEl.textContent = '1';
  isGameOver = false;
  currentPiece = randomPiece();
  nextPiece = randomPiece();
  droppedTime = 0;
  lastTime = 0;
  cancelAnimationFrame(animationId);
  animationId = requestAnimationFrame(update);
}

function collide(boardState, piece) {
  for (let y = 0; y < piece.matrix.length; y += 1) {
    for (let x = 0; x < piece.matrix[y].length; x += 1) {
      if (!piece.matrix[y][x]) continue;

      const newX = piece.x + x;
      const newY = piece.y + y;

      if (newX < 0 || newX >= COLS || newY >= ROWS) {
        return true;
      }

      if (newY >= 0 && boardState[newY][newX]) {
        return true;
      }
    }
  }

  return false;
}

function mergePiece() {
  currentPiece.matrix.forEach((row, y) => {
    row.forEach((value, x) => {
      if (value) {
        const boardY = currentPiece.y + y;
        const boardX = currentPiece.x + x;
        if (boardY >= 0) {
          board[boardY][boardX] = currentPiece.type;
        }
      }
    });
  });
}

function rotateMatrix(matrix) {
  const rotated = matrix[0].map((_, index) =>
    matrix.map((row) => row[index]).reverse()
  );
  return rotated;
}

function rotatePiece() {
  if (isGameOver) return;

  const rotated = rotateMatrix(currentPiece.matrix);
  const testX = currentPiece.x;
  const testY = currentPiece.y;
  const kicks = [0, -1, 1, -2, 2];

  for (const offset of kicks) {
    currentPiece.x = testX + offset;
    currentPiece.matrix = rotated;
    if (!collide(board, currentPiece)) {
      return;
    }
  }

  currentPiece.x = testX;
  currentPiece.y = testY;
  currentPiece.matrix = currentPiece.matrix;
}

function removeCompleteLines() {
  let removed = 0;

  outer: for (let y = ROWS - 1; y >= 0; y -= 1) {
    while (board[y].every(Boolean)) {
      board.splice(y, 1);
      board.unshift(Array(COLS).fill(null));
      removed += 1;
      continue outer;
    }
  }

  if (removed > 0) {
    lines += removed;
    score += removed * 100 * level;
    level = Math.floor(lines / LINES_PER_LEVEL) + 1;
    scoreEl.textContent = String(score);
    linesEl.textContent = String(lines);
    levelEl.textContent = String(level);
  }
}

function spawnPiece() {
  currentPiece = nextPiece;
  currentPiece.x = Math.floor(COLS / 2) - Math.ceil(currentPiece.matrix[0].length / 2);
  currentPiece.y = 0;
  nextPiece = randomPiece();

  if (collide(board, currentPiece)) {
    isGameOver = true;
  }
}

function dropPiece() {
  if (isGameOver) return;

  currentPiece.y += 1;
  if (collide(board, currentPiece)) {
    currentPiece.y -= 1;
    mergePiece();
    removeCompleteLines();
    spawnPiece();
  }
}

function movePiece(dx) {
  if (isGameOver) return;

  currentPiece.x += dx;
  if (collide(board, currentPiece)) {
    currentPiece.x -= dx;
  }
}

function hardDrop() {
  if (isGameOver) return;

  while (!collide(board, currentPiece)) {
    currentPiece.y += 1;
  }
  currentPiece.y -= 1;
  mergePiece();
  removeCompleteLines();
  spawnPiece();
}

function getDropInterval() {
  return Math.max(120, 700 - (level - 1) * 70);
}

function handleKeydown(event) {
  if (isGameOver && event.key !== 'r' && event.key !== 'R') return;

  switch (event.key) {
    case 'ArrowLeft':
      movePiece(-1);
      break;
    case 'ArrowRight':
      movePiece(1);
      break;
    case 'ArrowDown':
      dropPiece();
      break;
    case 'ArrowUp':
    case 'x':
    case 'X':
      rotatePiece();
      break;
    case ' ':
      event.preventDefault();
      hardDrop();
      break;
    case 'r':
    case 'R':
      resetGame();
      break;
    default:
      break;
  }
}

function drawCell(ctx, x, y, color, size = BLOCK) {
  ctx.fillStyle = color;
  ctx.fillRect(x * size, y * size, size, size);
  ctx.strokeStyle = 'rgba(255,255,255,0.15)';
  ctx.strokeRect(x * size + 0.5, y * size + 0.5, size - 1, size - 1);
}

function drawBoard() {
  boardCtx.clearRect(0, 0, boardCanvas.width, boardCanvas.height);

  for (let y = 0; y < ROWS; y += 1) {
    for (let x = 0; x < COLS; x += 1) {
      const cell = board[y][x];
      if (cell) {
        drawCell(boardCtx, x, y, COLORS[cell]);
      } else {
        boardCtx.strokeStyle = 'rgba(148,163,184,0.12)';
        boardCtx.strokeRect(x * BLOCK + 0.5, y * BLOCK + 0.5, BLOCK - 1, BLOCK - 1);
      }
    }
  }

  if (currentPiece) {
    currentPiece.matrix.forEach((row, y) => {
      row.forEach((value, x) => {
        if (value) {
          drawCell(boardCtx, currentPiece.x + x, currentPiece.y + y, currentPiece.color);
        }
      });
    });
  }

  if (isGameOver) {
    boardCtx.fillStyle = 'rgba(15,23,42,0.72)';
    boardCtx.fillRect(0, 0, boardCanvas.width, boardCanvas.height);
    boardCtx.fillStyle = '#f8fafc';
    boardCtx.font = 'bold 30px sans-serif';
    boardCtx.textAlign = 'center';
    boardCtx.fillText('Game Over', boardCanvas.width / 2, boardCanvas.height / 2);
    boardCtx.font = '18px sans-serif';
    boardCtx.fillText('Press R to restart', boardCanvas.width / 2, boardCanvas.height / 2 + 34);
  }
}

function drawNextPiece() {
  nextCtx.clearRect(0, 0, nextCanvas.width, nextCanvas.height);

  const matrix = nextPiece.matrix;
  const offsetX = Math.floor((nextCanvas.width - matrix[0].length * 24) / 2);
  const offsetY = Math.floor((nextCanvas.height - matrix.length * 24) / 2);

  matrix.forEach((row, y) => {
    row.forEach((value, x) => {
      if (value) {
        nextCtx.fillStyle = nextPiece.color;
        nextCtx.fillRect(offsetX + x * 24, offsetY + y * 24, 24, 24);
        nextCtx.strokeStyle = 'rgba(255,255,255,0.15)';
        nextCtx.strokeRect(offsetX + x * 24 + 0.5, offsetY + y * 24 + 0.5, 23, 23);
      }
    });
  });
}

function update() {
  const delta = lastTime ? performance.now() - lastTime : 0;
  lastTime = performance.now();

  if (!isGameOver) {
    droppedTime += delta;
    if (droppedTime >= getDropInterval()) {
      dropPiece();
      droppedTime = 0;
    }
  }

  drawBoard();
  drawNextPiece();
  requestAnimationFrame(update);
}

restartBtn.addEventListener('click', resetGame);
document.addEventListener('keydown', handleKeydown);

resetGame();
