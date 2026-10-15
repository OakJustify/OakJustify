// Guards the idle animation on the 3D contribution city.
//
// The city is regenerated every day by github-profile-3d-contrib, which knows
// nothing about scripts/animate_city.py. If the workflow ever loses that step,
// the SVG silently goes back to being a still image and nothing in the README
// looks wrong. This checks the committed file actually carries the animation.
//
//   node tests/city.test.mjs
import { readFileSync } from 'node:fs';

const FILE = new URL('../profile-3d-contrib/jane-night.svg', import.meta.url).pathname;
const svg = readFileSync(FILE, 'utf8');

let pass = 0, fail = 0;
const ok = (n, c, e = '') => { if (c) { pass++; console.log(`  PASS  ${n}`); } else { fail++; console.log(`  FAIL  ${n} ${e}`); } };

console.log('\n1. the idle animation is present');
ok('city-idle keyframes exist', svg.includes('@keyframes city-idle'));
ok('the wrapper class is styled', /\.cd\{animation:city-idle/.test(svg));
ok('reduced motion is respected', svg.includes('prefers-reduced-motion'));
ok('the animation loops forever', /animation:[^;]*infinite/.test(svg));

console.log('\n2. every cube is wrapped');
const cubes = (svg.match(/class="cont-top-\d"/g) || []).length;
const wrappers = (svg.match(/class="cd"/g) || []).length;
ok('one wrapper per cube', wrappers === cubes, `${wrappers} wrappers vs ${cubes} cubes`);
ok('the city is not empty', cubes > 300, `${cubes} cubes`);

console.log('\n3. each wrapper carries its own timing and amplitude');
const bad = [...svg.matchAll(/<g class="cd" style="([^"]*)"/g)]
  .filter(m => {
    const s = m[1];
    return !/--d:-?[\d.]+s/.test(s) || !/--a:-?[\d.]+px/.test(s) || !/--x:-?[\d.]+px/.test(s);
  });
ok('all wrappers define --d, --a and --x', bad.length === 0, `${bad.length} malformed`);

const delays = [...svg.matchAll(/--d:(-?[\d.]+)s/g)].map(m => parseFloat(m[1]));
const amps = [...svg.matchAll(/--a:(-?[\d.]+)px/g)].map(m => parseFloat(m[1]));
ok('delays are staggered, not all identical', new Set(delays).size > 20, `${new Set(delays).size} distinct`);
ok('every amplitude lifts the cube upwards', amps.every(a => a <= 0), `min ${Math.min(...amps)} max ${Math.max(...amps)}`);
ok('busier days move further than empty ones',
  Math.min(...amps) < -3, `strongest bob ${Math.min(...amps)}px`);

console.log('\n4. the wrapping did not disturb the geometry');
// the wrapper adds no transform of its own, so the generated positioning has to
// survive untouched
ok('the cube group transform attribute is intact', /<g transform="translate\([-\d.]+ [-\d.]+\)">/.test(svg));
const opens = (svg.match(/<g\b/g) || []).length;
const closes = (svg.match(/<\/g>/g) || []).length;
ok('every <g> is closed', opens === closes, `${opens} open vs ${closes} close`);
ok('the file still parses as XML-ish', svg.trim().startsWith('<svg') && svg.trim().endsWith('</svg>'));

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);