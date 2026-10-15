// Engine checks for docs/chess/engine.js: evaluation symmetry, tactics, the
// time budget and legal-move integrity over a self-play game.
//
//   node tests/engine.test.mjs
import { Chess } from '../docs/chess/chess.js';
import { evaluate, bestMove } from '../docs/chess/engine.js';

let pass = 0, fail = 0;
const ok = (n, c, e = '') => { if (c) { pass++; console.log(`  PASS  ${n}`); } else { fail++; console.log(`  FAIL  ${n} ${e}`); } };

const FILES = 'abcdefgh';
const rot = sq => FILES[7 - FILES.indexOf(sq[0])] + (9 - +sq[1]);
function rot180AndSwap(fen) {
  const src = new Chess(fen), out = new Chess();
  for (let r = 8; r >= 1; r--) for (const f of FILES) out.remove(f + r);
  for (const s of src.board().flat()) if (s) out.put({ type: s.type, color: s.color === 'w' ? 'b' : 'w' }, rot(s.square));
  return out;
}
const mateInOne = fen => {
  const g = new Chess(fen);
  return g.moves({ verbose: true }).find(m => { g.move(m); const w = g.isCheckmate(); g.undo(); return w; });
};

console.log('\n1. evaluation');
{
  ok('start position balanced', Math.abs(evaluate(new Chess())) < 5, evaluate(new Chess()));
  const g = new Chess('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1');
  g.move('e4');
  ok('1.e4 near neutral', Math.abs(evaluate(g)) < 120, evaluate(g));
  ok('rook is worth ~500', Math.abs(evaluate(new Chess('4k3/8/8/8/8/8/8/4K2R w K - 0 1')) - 500) < 60);
  ok('queen beats two rooks', evaluate(new Chess('4k3/8/8/8/8/8/8/3QK2R w K - 0 1'))
     > evaluate(new Chess('4k3/8/8/8/8/8/8/R3K2R w K - 0 1')));
}

console.log('\n2. colour symmetry');
{
  let worst = 0, detail = '';
  for (const fen of [
    'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 0 3',
    'r2q1rk1/pp2bppp/2n1pn2/3p4/3P4/2N1PN2/PP2BPPP/R2Q1RK1 w - - 0 9',
    '8/2k5/8/8/8/5p2/6P1/4K2R b K - 0 1',
    '4k3/8/8/2p5/8/1P6/8/4K3 w - - 0 1',
    'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1',
    '8/8/8/3k4/8/8/PPPPPPPP/RNBQKBNR w KQ - 0 1',
  ]) {
    const a = evaluate(new Chess(fen)), b = evaluate(rot180AndSwap(fen));
    const d = Math.abs(a + b);
    if (d > worst) { worst = d; detail = `${fen} -> ${a} vs ${b}`; }
  }
  ok('rotate 180 + swap colours negates the score', worst === 0, `off by ${worst} (${detail})`);
}

console.log('\n3. finds forced mate in one');
for (const fen of ['6k1/5ppp/8/8/8/8/8/R3K2R w KQ - 0 1', 'r5k1/5ppp/8/7Q/8/8/6PP/R5K1 w - - 0 1']) {
  const mate = mateInOne(fen);
  const g = new Chess(fen);
  const r = bestMove(g, { maxDepth: 8, budgetMs: 900 });
  ok(`plays ${mate.san}`, r.san === mate.san, `chose ${r.san}`);
}

console.log('\n4. takes free material');
for (const fen of [
  '4k3/8/8/4q3/8/5N2/8/4K3 w - - 0 1',
  '4k3/8/8/8/3q4/4R3/8/4K3 w - - 0 1',
  '4k3/8/8/8/8/8/4r3/4K3 w - - 0 1',
]) {
  const r = bestMove(new Chess(fen), { maxDepth: 8, budgetMs: 900 });
  ok(`captures in ${fen.slice(0, 22)}…`, r.san && r.san.includes('x'), `chose ${r.san}`);
}

console.log('\n5. the time budget is respected');
{
  const fen = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1';
  for (const [level, budget] of [[1, 200], [2, 900], [3, 2500]]) {
    const g = new Chess(fen);
    const t0 = Date.now();
    const r = bestMove(g, { maxDepth: level === 1 ? 4 : level === 2 ? 8 : 12, budgetMs: budget });
    const ms = Date.now() - t0;
    ok(`level ${level} returns within budget + slack`, ms <= budget + 1200, `${ms}ms for a ${budget}ms budget`);
    console.log(`        level ${level}: ${ms}ms, reached depth ${r.depth}, ${r.nodes.toLocaleString()} nodes, ${r.san}`);
  }
}

console.log('\n6. deeper levels actually play stronger');
{
  const fens = ['r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4'];
  for (const fen of fens) {
    const moves = [1, 2, 3].map(l => bestMove(new Chess(fen), {
      maxDepth: l === 1 ? 4 : l === 2 ? 8 : 12, budgetMs: l === 1 ? 200 : l === 2 ? 900 : 2500,
    }));
    console.log(`        L1 ${moves[0].san} (d${moves[0].depth})  L2 ${moves[1].san} (d${moves[1].depth})  L3 ${moves[2].san} (d${moves[2].depth})`);
    ok('L1 reached depth 1', moves[0].depth === 1);
    ok('L2 searched deeper than L1', moves[1].depth > moves[0].depth);
    ok('L3 searched at least as deep as L2', moves[2].depth >= moves[1].depth);
  }
}

console.log('\n7. self-play stays legal');
{
  const g = new Chess();
  let ply = 0, illegal = 0;
  while (!g.isGameOver() && ply < 200) {
    const r = bestMove(g, { maxDepth: 3, budgetMs: 200 });
    if (!r.san) break;
    if (!g.moves().some(s => s === r.san)) illegal++;
    g.move(r.san);
    ply++;
  }
  ok('every move legal', illegal === 0, `${illegal} illegal`);
  console.log(`        ${ply} plies, ${g.isCheckmate() ? 'checkmate' : g.isStalemate() ? 'stalemate' : g.isDraw() ? 'draw' : 'ply cap'}`);
}

console.log('\n8. edge cases');
{
  const cases = [
    ['8/8/8/8/8/5k2/6q1/7K w - - 0 1', 'white is mated'],
    ['4k3/8/8/8/8/8/8/K7 w - - 0 1', 'bare kings, dead'],
    ['4k3/8/8/8/8/8/8/K6R w - - 0 1', 'rook endgame'],
    ['8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1', 'perft 3'],
  ];
  let good = true;
  for (const [fen, note] of cases) {
    const g = new Chess(fen);
    const over = g.isGameOver();
    const r = bestMove(g, { maxDepth: 4, budgetMs: 600 });
    const sane = over ? r.san === null
      : !!r.san && g.moves().some(s => s === r.san);
    if (!sane) { good = false; console.log(`        ${note}: ${r.move && r.san}`); }
    else console.log(`        ${note}: ${over ? 'no move (game over)' : r.san}`);
  }
  ok('edge cases behaved', good);
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);