// 通用校模板 PPT 渲染器：读 JSON 规格 -> 生成 8 页左右汇报
// 用法: node build_deck.js <spec.json>
const path = require('path');
const fs = require('fs');
const T = require(path.resolve(__dirname, '..', 'stage-reports-20261009', 'lib', 'report-template.js'));
const { newDeck, cover, chrome, box, band, table, C, F, W, H } = T;

const specPath = process.argv[2];
if (!specPath) { console.error('usage: node build_deck.js <spec.json>'); process.exit(2); }
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));

const pptx = newDeck({ title: spec.title });

// 封面
cover(pptx, { title: spec.coverTitle, subtitle: spec.coverSubtitle, meta: spec.coverMeta });

const FILLS = { blue: C.blueLight, gold: C.goldLight, rose: C.roseLight, green: C.greenLight };

spec.pages.forEach((p, idx) => {
  const s = pptx.addSlide();
  chrome(s, p.title, idx + 2);
  let y = 1.62;

  (p.blocks || []).forEach(b => {
    if (b.kicker) {
      s.addText(b.kicker, { x: 0.67, y: y, w: 11.98, h: 0.32, fontFace: F, fontSize: 12.5, bold: true, color: C.blue, margin: 0 });
      y += 0.4;
    }
    if (b.text) {
      s.addText(b.text, { x: 0.67, y: y, w: 11.98, h: b.h || 0.42, fontFace: F, fontSize: b.size || 12.5,
        color: b.red ? 'C00000' : C.text, bold: !!b.bold, margin: 0, fit: 'shrink' });
      y += (b.h || 0.42) + (b.gap !== undefined ? b.gap : 0.18);
    }
    if (b.bullets) {
      const n = b.bullets.length;
      s.addText(b.bullets.map(t => '· ' + t).join('\n'), {
        x: 0.67, y: y, w: 11.98, h: Math.min(0.42 * n + 0.2, 2.4),
        fontFace: F, fontSize: 11.5, color: C.text, margin: 0, fit: 'shrink',
        lineSpacingMultiple: 1.3,
      });
      y += Math.min(0.42 * n + 0.2, 2.4) + 0.15;
    }
    if (b.table) {
      const t = b.table;
      const rowH = t.rowH || 0.44;
      table(s, [t.headers].concat(t.rows), 0.67, y, 11.98, t.widths, rowH, t.fs || 11);
      y += rowH * (t.rows.length + 1) + (t.gap !== undefined ? t.gap : 0.16);
    }
    if (b.boxes) {
      const n = b.boxes.length;
      const gap = 0.13;
      const bw = (11.98 - gap * (n - 1)) / n;
      const bh = b.h || 1.3;
      b.boxes.forEach((bx, i) => {
        box(s, 0.67 + i * (bw + gap), y, bw, bh, bx.title, bx.body,
          { fill: FILLS[bx.fill || 'blue'], bodySize: bx.size || 11 });
      });
      y += bh + 0.2;
    }
  });

  if (p.band) band(s, p.band, 6.45);
});

const out = spec.out;
pptx.writeFile({ fileName: out }).then(f => console.log('WROTE', f, 'pages=', spec.pages.length + 1));
