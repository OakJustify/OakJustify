// Checks every link that ships in docs/ : relative ones must exist in the
// repo, and absolute ones must answer 200. Run it after touching a page.
//
//   node tests/links.test.mjs
import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';

const DOCS = new URL('../docs', import.meta.url).pathname;
const SITE = 'https://oakjustify.github.io/OakJustify';

let pass = 0, fail = 0;
const ok = (n, c, e = '') => { if (c) { pass++; console.log(`  PASS  ${n}`); } else { fail++; console.log(`  FAIL  ${n} ${e}`); } };

function htmlFiles(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap(e => {
    const p = resolve(dir, e.name);
    return e.isDirectory() ? htmlFiles(p) : (e.name.endsWith('.html') ? [p] : []);
  });
}

console.log('\n1. relative links resolve against the published site, not just on disk');
// Resolving a relative href against the local directory is not enough: docs/
// is not the site root, so "../../" happens to land on a directory that exists
// on disk while being a 404 once published. Resolve against the real URL.
for (const file of htmlFiles(DOCS)) {
  const rel = file.slice(DOCS.length);
  const pageUrl = (SITE + (rel.endsWith('/index.html')
    ? rel.slice(0, -'index.html'.length)
    : rel)).replace(/\/{2,}/g, '/');
  const src = readFileSync(file, 'utf8');
  for (const m of src.matchAll(/href="([^"]+)"/g)) {
    const href = m[1];
    if (/^(https?:|mailto:|#)/.test(href)) continue;

    const url = new URL(href, pageUrl).href;
    // a link that climbs above the Pages site can never be served
    const escaped = !url.startsWith(SITE + '/') && url !== SITE;
    let status = 0;
    try { status = (await fetch(url, { redirect: 'follow' })).status; } catch { status = 0; }
    ok(`${rel} -> ${href}  =>  ${url}`,
      !escaped && status === 200, escaped ? 'escapes the Pages site root' : `status ${status}`);
  }
}

console.log('\n2. absolute links answer 200');
const externals = [...new Set(htmlFiles(DOCS).flatMap(f =>
  [...readFileSync(f, 'utf8').matchAll(/href="(https?:[^"]+)"/g)].map(m => m[1])))];
for (const href of externals) {
  let status = 0;
  try {
    const r = await fetch(href, { redirect: 'follow', headers: { 'user-agent': 'Mozilla/5.0' } });
    status = r.status;
  } catch { status = 0; }
  ok(`${href}`, status === 200, `status ${status}`);
}

console.log('\n3. the Pages site itself is reachable');
for (const p of ['/', '/chess/', '/chess/engine.js', '/chess/worker.js', '/chess/chess.js']) {
  let status = 0;
  try { status = (await fetch(SITE + p, { redirect: 'follow' })).status; } catch { status = 0; }
  ok(`${SITE}${p}`, status === 200, `status ${status}`);
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);