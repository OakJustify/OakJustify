/**
 * Runs the search off the main thread so the board stays clickable while the
 * engine thinks. The page falls back to an inline search if this worker cannot
 * be created (for example when the page is opened straight off the filesystem).
 */
import { Chess } from './chess.js';
import { bestMove } from './engine.js';

self.onmessage = ({ data }) => {
  const { id, fen, maxDepth, budgetMs } = data;
  const game = new Chess(fen);
  const r = bestMove(game, { maxDepth, budgetMs });
  self.postMessage({
    id,
    san: r.san,
    depth: r.depth,
    score: r.score,
    nodes: r.nodes,
    ms: r.ms,
  });
};