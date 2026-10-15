/**
 * Contribution Chess engine.
 *
 * Kept free of any DOM access so the same code can run inside a Web Worker
 * (preferred, keeps the page responsive) or straight on the main thread as a
 * fallback when Workers are unavailable.
 *
 * Scoring is material + piece-square tables with a separate king table once
 * the pawns are gone. Search is negamax with alpha-beta pruning, move ordering
 * that tries captures first, and iterative deepening under a wall-clock budget
 * so "how hard" is expressed in time rather than in depth.
 */

export const VALUE = { p: 100, n: 320, b: 330, r: 500, q: 900, k: 20000 };
const MATE = 1000000;

// tables are written a8 -> h1, so index 0 is a8
const PST = {
  p: [  0,  0,  0,  0,  0,  0,  0,  0,
      50, 50, 50, 50, 50, 50, 50, 50,
      10, 10, 20, 30, 30, 20, 10, 10,
       5,  5, 10, 25, 25, 10,  5,  5,
       0,  0,  0, 20, 20,  0,  0,  0,
       5, -5,-10,  0,  0,-10, -5,  5,
       5, 10, 10,-20,-20, 10, 10,  5,
       0,  0,  0,  0,  0,  0,  0,  0],
  n: [-50,-40,-30,-30,-30,-30,-40,-50,
      -40,-20,  0,  0,  0,  0,-20,-40,
      -30,  0, 10, 15, 15, 10,  0,-30,
      -30,  5, 15, 20, 20, 15,  5,-30,
      -30,  0, 15, 20, 20, 15,  0,-30,
      -30,  5, 10, 15, 15, 10,  5,-30,
      -40,-20,  0,  5,  5,  0,-20,-40,
      -50,-40,-30,-30,-30,-30,-40,-50],
  b: [-20,-10,-10,-10,-10,-10,-10,-20,
      -10,  0,  0,  0,  0,  0,  0,-10,
      -10,  0,  5, 10, 10,  5,  0,-10,
      -10,  5,  5, 10, 10,  5,  5,-10,
      -10,  0, 10, 10, 10, 10,  0,-10,
      -10, 10, 10, 10, 10, 10, 10,-10,
      -10,  5,  0,  0,  0,  0,  5,-10,
      -20,-10,-10,-10,-10,-10,-10,-20],
  r: [  0,  0,  0,  0,  0,  0,  0,  0,
       5, 10, 10, 10, 10, 10, 10,  5,
      -5,  0,  0,  0,  0,  0,  0, -5,
      -5,  0,  0,  0,  0,  0,  0, -5,
      -5,  0,  0,  0,  0,  0,  0, -5,
      -5,  0,  0,  0,  0,  0,  0, -5,
      -5,  0,  0,  0,  0,  0,  0, -5,
       0,  0,  5,  5,  0,  0,  0,  0],
  q: [-20,-10,-10, -5, -5,-10,-10,-20,
      -10,  0,  0,  0,  0,  0,  0,-10,
      -10,  0,  5,  5,  5,  5,  0,-10,
       -5,  0,  5,  5,  5,  5,  0, -5,
        0,  0,  5,  5,  5,  5,  0, -5,
      -10,  5,  5,  5,  5,  5,  0,-10,
      -10,  0,  5,  0,  0,  0,  0,-10,
      -20,-10,-10, -5, -5,-10,-10,-20],
  k: [-30,-40,-40,-50,-50,-40,-40,-30,
      -30,-40,-40,-50,-50,-40,-40,-30,
      -30,-40,-40,-50,-50,-40,-40,-30,
      -30,-40,-40,-50,-50,-40,-40,-30,
      -20,-30,-30,-40,-40,-30,-30,-20,
      -10,-20,-20,-20,-20,-20,-20,-10,
       20, 20,  0,  0,  0,  0, 20, 20,
       20, 30, 10,  0,  0, 10, 30, 20],
};

// king walks towards the middle once the board is bare
const PST_END = {
  k: [-50,-40,-30,-20,-20,-30,-40,-50,
      -30,-20,-10,  0,  0,-10,-20,-30,
      -30,-10, 20, 30, 30, 20,-10,-30,
      -30,-10, 30, 40, 40, 30,-10,-30,
      -30,-10, 30, 40, 40, 30,-10,-30,
      -30,-10, 20, 30, 30, 20,-10,-30,
      -30,-30,  0,  0,  0,  0,-30,-30,
      -50,-30,-30,-30,-30,-30,-30,-50],
};

export const mirror = i => (7 - ((i / 8) | 0)) * 8 + (i % 8);

/**
 * Score a position from white's point of view.
 * Black is read on the mirrored square before the whole term is negated,
 * which is what makes the evaluation colour-symmetric.
 */
export function evaluate(game) {
  // chess.js hands back 8 rows, so flatten to a8..h1 (index 0 = a8)
  const board = game.board().flat();
  let score = 0, minors = 0;
  for (let i = 0; i < 64; i++) {
    const sq = board[i];
    if (sq && sq.type === 'p') minors++;
  }
  const endgame = minors <= 2;
  for (let i = 0; i < 64; i++) {
    const sq = board[i];
    if (!sq) continue;
    const table = (sq.type === 'k' && endgame) ? PST_END.k : PST[sq.type];
    const v = VALUE[sq.type] + (sq.color === 'w' ? table[i] : table[mirror(i)]);
    score += sq.color === 'w' ? v : -v;
  }
  return score;
}

/**
 * Move ordering on plain SAN strings.
 *
 * chess.js's verbose move objects carry a `before` and `after` FEN, which
 * means it re-serialises the whole board for every candidate move: measured at
 * roughly 160 calls per second here, versus 2700 for the plain SAN list. Since
 * we only need captures and castling promoted to the front, the information is
 * already encoded in the SAN text, so the plain list is the one to use.
 */
function rank(san) {
  let s = 0;
  if (san.indexOf('x') !== -1) s += 1000;      // capture
  if (san.indexOf('=') !== -1) s += 900;       // promotion
  if (san.charCodeAt(0) === 79 /* O */) s += 800; // castling
  return s;
}

function order(moves) {
  if (moves.length < 2) return moves;
  const scored = new Array(moves.length);
  for (let i = 0; i < moves.length; i++) scored[i] = [moves[i], rank(moves[i])];
  scored.sort((a, b) => b[1] - a[1]);
  for (let i = 0; i < scored.length; i++) scored[i] = scored[i][0];
  return scored;
}

/**
 * Negamax with alpha-beta pruning.
 *
 * Mate and stalemate fall out of the move list we build anyway; chess.js's own
 * isCheckmate() calls isStalemate(), which generates and replays every legal
 * move, so calling it per node is far too slow. isDraw() is likewise only
 * consulted near the leaves.
 *
 * `deadline` is an absolute Date.now() value; the search gives up on going
 * deeper once it has passed, which is what keeps the engine inside its budget.
 */
export function search(game, depth, alpha, beta, ply, deadline, stats) {
  if (depth <= 0) {
    if (game.inCheck() && !game.moves().length) return -MATE + ply;
    const s = evaluate(game);
    return game.turn() === 'w' ? s : -s;   // negamax scores from the side to move
  }

  const moves = order(game.moves());
  if (!moves.length) return game.inCheck() ? -MATE + ply : 0;  // mate or stalemate
  if (depth <= 2 && game.isDraw()) return 0;

  let best = -Infinity;
  for (const m of moves) {
    game.move(m);
    const v = -search(game, depth - 1, -beta, -alpha, ply + 1, deadline, stats);
    game.undo();
    if (stats && ++stats.nodes % 2048 === 0 && Date.now() > deadline) return best;
    if (v > best) best = v;
    if (best > alpha) alpha = best;
    if (alpha >= beta) break;
  }
  return best;
}

/**
 * Pick a move with iterative deepening, so a partially finished deeper pass
 * still leaves us with the best move from the last completed one.
 *
 * @param {import('./chess.js').Chess} game
 * @param {{maxDepth?:number, budgetMs?:number, onInfo?:Function}} opts
 */
export function bestMove(game, opts = {}) {
  const maxDepth = opts.maxDepth ?? 4;
  const budgetMs = opts.budgetMs ?? 1000;
  const onInfo = opts.onInfo;

  if (game.isGameOver()) return { san: null, depth: 0, score: 0, nodes: 0, ms: 0 };

  const root = order(game.moves());
  if (!root.length) return { san: null, depth: 0, score: 0, nodes: 0, ms: 0 };

  const started = Date.now();
  const deadline = started + budgetMs;
  const stats = { nodes: 0 };

  let best = root[0], bestScore = -Infinity, completed = 0;

  for (let d = 1; d <= maxDepth; d++) {
    let localBest = null, localScore = -Infinity, alpha = -Infinity;
    let finished = true;
    for (const m of root) {
      game.move(m);
      // the root is a maximising node with beta = +Infinity, so the child is
      // searched over (alpha, +Infinity) and the sign flipped
      const v = -search(game, d - 1, alpha, Infinity, 1, deadline, stats);
      game.undo();
      if (Date.now() > deadline) { finished = false; break; }
      if (v > localScore) { localScore = v; localBest = m; }
      if (v > alpha) alpha = v;
    }
    if (!finished || !localBest) break;
    best = localBest; bestScore = localScore; completed = d;
    onInfo?.({ depth: completed, score: localScore, nodes: stats.nodes, ms: Date.now() - started });
    if (Math.abs(bestScore) > MATE - 100) break; // mate found, no need to go deeper
    if (Date.now() > deadline) break;
  }

  return { san: best, depth: completed, score: bestScore, nodes: stats.nodes, ms: Date.now() - started };
}