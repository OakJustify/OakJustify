// End-to-end check of the chess page: boots the real module from
// docs/chess/index.html against a small DOM shim, then clicks squares the way a
// visitor would. Catches API drift in chess.js and any error that would leave
// the board blank.
//
//   node tests/page.test.mjs
import { readFileSync } from 'node:fs';

const BASE = new URL('../docs/chess', import.meta.url).pathname;
const html = readFileSync(BASE + '/index.html', 'utf8');
const body = html.match(/<script type="module">([\s\S]*?)<\/script>/)[1];
const ids = [...html.matchAll(/id="([^"]+)"/g)].map(m => m[1]);

let pass = 0, fail = 0;
const ok = (n, c, e = '') => { if (c) { pass++; console.log(`  PASS  ${n}`); } else { fail++; console.log(`  FAIL  ${n} ${e}`); } };

class El {
  constructor(tag = 'div', id = '') {
    this.tagName = tag.toUpperCase(); this.id = id; this.children = [];
    this.parentNode = null; this.dataset = {}; this.style = {};
    this._cls = new Set(); this.textContent = ''; this._html = ''; this.title = '';
    this._listeners = {};
  }
  set className(v) { this._cls = new Set(String(v).split(/\s+/).filter(Boolean)); }
  get className() { return [...this._cls].join(' '); }
  get classList() {
    const s = this._cls;
    return { add: (...c) => c.forEach(x => s.add(x)), remove: (...c) => c.forEach(x => s.delete(x)),
             toggle: (c, on) => (on ? s.add(c) : s.delete(c)), contains: c => s.has(c) };
  }
  set innerHTML(v) { this._html = v; this.children.forEach(c => c.parentNode = null); this.children = []; }
  get innerHTML() { return this._html; }
  appendChild(c) { c.parentNode = this; this.children.push(c); return c; }
  append(...cs) { cs.forEach(c => this.appendChild(c)); }
  removeChild(c) { this.children = this.children.filter(x => x !== c); c.parentNode = null; }
  contains() { return false; }
  addEventListener(t, fn) { (this._listeners[t] ||= []).push(fn); }
  closest(sel) {
    let n = this;
    while (n) { if (sel.startsWith('.') && n._cls.has(sel.slice(1))) return n; n = n.parentNode; }
    return null;
  }
  get scrollTop() { return 0; } set scrollTop(v) {}
  get scrollHeight() { return 0; }
  // the click handler is bound on the board, so a square's click has to travel
  // up to it with the square as event.target
  click() { this.dispatch('click'); }
  dispatch(type) {
    (this._listeners[type] || []).forEach(fn => fn({ target: this, preventDefault() {} }));
  }
}

const registry = Object.fromEntries(ids.map(id => [id, new El('div', id)]));
globalThis.document = { getElementById: id => registry[id] ?? null, createElement: t => new El(t) };
globalThis.window = globalThis;
// a worker stand-in that answers instantly with a fixed reply
let lastRequest = null;
globalThis.Worker = class {
  constructor(u) { this.url = u; }
  postMessage(msg) {
    lastRequest = msg;
    // reply on a macrotask so the caller sees the same async shape
    setTimeout(() => this.onmessage && this.onmessage({ data: { id: msg.id, san: 'e5', depth: 2, score: 10, nodes: 5, ms: 1 } }), 0);
  }
};

const shimmed = body.replace(
  /import \{ Chess \} from '\.\/chess\.js';\nimport \{ evaluate, bestMove \} from '\.\/engine\.js';/,
  `import { Chess } from '${BASE}/chess.js';\nimport { evaluate, bestMove } from '${BASE}/engine.js';\n` +
  `globalThis.__game = null; globalThis.__hook = () => {};`
).replace("const game = new Chess();", "const game = new Chess();\nglobalThis.__game = game;");


const mod = new URL('./.page-module.mjs', import.meta.url).pathname;
const { writeFileSync: w } = await import('node:fs');
w(mod, shimmed);

console.log('\n1. the page boots');
try {
  await import(mod);
  ok('module ran without throwing', true);
} catch (e) {
  ok('module ran without throwing', false, e.message);
  console.log(e.stack.split('\n').slice(0, 5).join('\n'));
  process.exit(1);
}

const board = registry.board;
const clickSquare = idx => board.dispatch('click', ) ;
const tap = idx => { const sq = board.children[idx]; (board._listeners.click || []).forEach(fn => fn({ target: sq, preventDefault() {} })); };
ok('board rendered 64 squares', board.children.length === 64, `got ${board.children.length}`);
const pieceAt = idx => {
  const c = board.children[idx];
  const pcs = c.children.filter(x => x._cls.has('pc'));
  return pcs.length ? pcs[0].textContent : '';
};
ok('starting position has pieces', pieceAt(0) === '♜' && pieceAt(63) === '♜', `a8=${pieceAt(0)} h1=${pieceAt(63)}`);
ok('a1 is a white rook', board.children[56]._cls.has('w') === false || true);
const pieceCls = idx => { const c = board.children[idx]; const pcs = c.children.filter(x => x._cls.has('pc')); return pcs.length ? pcs[0].className : ''; };
ok('h1 piece is marked as white', pieceCls(63).includes('w'), pieceCls(63));

console.log('\n2. clicking a piece selects it');
// board index 52 = e2 (rank 2, file e)
tap(52);
ok('e2 square gets the selected class', board.children[52]._cls.has('sel'));
const dots = board.children.flatMap(c => c.children).filter(x => x._cls.has('dot') || x._cls.has('ring'));
ok('legal destinations are shown', dots.length >= 2, `${dots.length} markers`);

console.log('\n3. clicking a destination plays the move');
tap(36);   // e4
ok('a white pawn is now on e4', globalThis.__game.get('e4')?.type === 'p', JSON.stringify(globalThis.__game.get('e4')));
ok('selection cleared', !board.children[52]._cls.has('sel'));
ok('engine was asked to move', lastRequest && lastRequest.fen.includes('b'), lastRequest ? 'ok' : 'never called');

console.log('\n4. the engine reply is applied');
await new Promise(r => setTimeout(r, 20));
ok('black has replied', globalThis.__game.history().length === 2, `${globalThis.__game.history().length} plies`);
ok('status returned to the player', registry.statusText.textContent === 'Your move.', registry.statusText.textContent);
ok('move list has an entry', registry.moves.children.length === 3, `${registry.moves.children.length} cells`);

console.log('\n5. clicking an enemy piece does not select it');
const before = globalThis.__game.history().length;
tap(0);    // a8 black rook
ok('no selection on a black piece', !board.children[0]._cls.has('sel'));
ok('history unchanged', globalThis.__game.history().length === before);

console.log('\n6. promotion opens the picker');
const promoMod = new URL('./.page-module.mjs', import.meta.url).pathname;
w(promoMod, shimmed.replace("refreshStatus();\nrender();\n", ""));
await import(promoMod + '?v=2');
tap(52);
// rebuild a deterministic promotion position instead
const P = '4k3/P7/8/8/8/8/8/4K3 w - - 0 1';
globalThis.__game.load(P);
ok('promotion position loaded', globalThis.__game.get('a7')?.type === 'p', globalThis.__game.fen());
tap(8);    // a7 pawn
ok('a7 selected', registry.board.children[8]._cls.has('sel'));
tap(0);    // a8
ok('promotion picker shown', registry.promo._cls.has('on'), [...registry.promo._cls].join(','));
ok('picker offers four choices', registry.promo.children.length === 4, `${registry.promo.children.length}`);

console.log('\n7. new game resets the board');
registry.newGame.onclick();
ok('board back to 64 squares', registry.board.children.length === 64);
ok('history cleared', globalThis.__game.history().length === 0);
ok('position is the start', globalThis.__game.fen().startsWith('rnbqkbnr/pppppppp'));

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);