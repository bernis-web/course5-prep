// 课题5 第 3 次汇报（15 页）—— 校模板重排版 v2
// 内容真源：results/stage-reports-20261102/_content.json（由已交付 pptx 逐字抽出）+ _notes.txt
// 版式真源：results/stage-reports-20261009/lib/report-template.js（校模板生成器）+ postprocess_bars.py
// 硬约束：文字/数字/结论一字不改；配色/字体/母题全部取自校模板；不新增颜色。
const path = require('path');
const LIB = path.resolve(__dirname, '..', 'stage-reports-20261009', 'lib', 'report-template.js');
const { newDeck, band, C, F, W, H, LOGO, COVER_BG } = require(LIB);

const OUT = process.env.OUT_PPTX
  ? path.resolve(process.env.OUT_PPTX)
  : path.resolve(__dirname, '_candidate.pptx');

/* ───────────── 字号层级（锁定，全篇唯一一套） ─────────────
   封面主标题 32 Bold / 封面副标题 17 / 封面元信息 11.5
   页面标题   24 Bold 12365A
   导语       12.5     60758F
   正文       16       1F2D3D
   表格       11.5（表头 Bold 白字压 005BAC）
   结论条     13 Bold  8A4B00 on FFF2CC
   页脚/页码  8.5      60758F
   ──────────────────────────────────────────────────────── */
const S = {
  coverTitle: 32, coverSub: 17, coverMeta: 11.5,
  title: 24, lead: 12.5, body: 16,
  table: 11.5, band: 13, foot: 8.5,
};

/* 网格（取自校模板实测值） */
const L = 0.67;
const CW = 11.98;
const TITLE_Y = 1.02, TITLE_H = 0.62;
const LEAD_Y = 1.58, LEAD_H = 0.34;
const BAND_TOP = 2.00, BAND_BOT = 6.35;
const BAND_H = BAND_BOT - BAND_TOP;
const CONC_Y = 6.45;
const FOOT_Y = 7.06;
const LH = 1.40;
const MAX_TOP_PAD = 0.45;
const TGROW = 1.13;   // 实测：LibreOffice/PowerPoint 实际行高 ≈ 设定值 × 1.13
const FOOTER_TEXT = '课题5 · XenoTransfer v1.0 · 第 3 次汇报 · 2026-11-02';

/* ───────────── 度量 ───────────── */
function charW(s) {
  let w = 0;
  for (const ch of s) {
    const c = ch.codePointAt(0);
    if (c >= 0x2E80) w += 1.0;
    else if (ch === ' ') w += 0.30;
    else if (/[0-9]/.test(ch)) w += 0.56;
    else if (/[A-Z]/.test(ch)) w += 0.66;
    else if (/[a-z]/.test(ch)) w += 0.53;
    else if ('±×÷→←↔–—…·¥✓'.includes(ch)) w += 0.85;
    else w += 0.50;
  }
  return w;
}
const estLines = (t, wIn, pt) => Math.max(1, Math.ceil(charW(t) / ((wIn * 72) / pt)));
const paraH = (t, wIn, pt, lh) => (estLines(t, wIn, pt) * pt * lh) / 72 + 0.06;

/* ───────────── 段落 ───────────── */
function paras(s, items, o) {
  const { x, w, size: pt } = o, lh = o.lh || LH, gap = o.gap;
  let y = o.y, h = 0;
  items.forEach((t, i) => {
    const hh = paraH(t, w, pt, lh);
    s.addText(t, {
      x, y, w, h: hh, fontFace: F, fontSize: pt, color: o.color || C.text,
      bold: !!o.bold, margin: 0, valign: 'top', lineSpacingMultiple: lh,
    });
    y += hh; h += hh;
    if (i < items.length - 1) { const g = typeof gap === 'function' ? gap(i) : gap; y += g; h += g; }
  });
  return h;
}
function parasH(items, w, pt, lh, gap) {
  let h = 0;
  items.forEach((t, i) => {
    h += paraH(t, w, pt, lh);
    if (i < items.length - 1) h += typeof gap === 'function' ? gap(i) : gap;
  });
  return h;
}

/* ───────────── 列宽 ───────────── */
function fitCols(rows, total, exp, minW) {
  exp = exp === undefined ? 0.85 : exp;
  minW = minW === undefined ? 1.05 : minW;
  const n = rows[0].length, w = [];
  for (let c = 0; c < n; c++) {
    let mx = 0;
    for (const r of rows) mx = Math.max(mx, charW(String(r[c])));
    w.push(Math.pow(Math.max(mx, 3.2), exp));
  }
  const sum = w.reduce((a, b) => a + b, 0);
  let out = w.map(v => (total * v) / sum);
  for (let k = 0; k < 4; k++) {
    out = out.map(v => Math.max(v, minW));
    const s2 = out.reduce((a, b) => a + b, 0);
    out = out.map(v => (v * total) / s2);
  }
  out = out.map(v => Math.round(v * 100) / 100);
  const drift = Math.round((total - out.reduce((a, b) => a + b, 0)) * 100) / 100;
  out[out.length - 1] = Math.round((out[out.length - 1] + drift) * 100) / 100;
  return out;
}

/* ───────────── 表格 ─────────────
   列对齐规则：正文列（该列正文最长内容 > 12 em）左对齐，其余居中。
   理由：表格里居中长句会读成「散」，居中只适合短值与数字。 */
function tbl(s, rows, o) {
  const pt = o.size || S.table;
  const colW = o.colW || fitCols(rows, o.w);
  const prose = rows[0].map((_, c) => {
    let mx = 0;
    for (let r = 1; r < rows.length; r++) mx = Math.max(mx, charW(String(rows[r][c])));
    return mx > 12;
  });
  const data = rows.map((r, ri) =>
    r.map((cell, ci) => {
      const ov = (o.cell && o.cell(ri, ci, cell)) || {};
      const base = {
        fontFace: F, fontSize: pt,
        bold: ri === 0 || !!ov.bold,
        color: ri === 0 ? 'FFFFFF' : (ov.color || C.text),
        align: prose[ci] || ci === 0 ? 'left' : 'center',
        valign: 'middle',
        fill: { color: ri === 0 ? '005BAC' : (ov.fill || 'FFFFFF') },
      };
      return { text: cell, options: base };
    })
  );
  s.addTable(data, {
    x: o.x, y: o.y, w: o.w, colW, rowH: o.rowH,
    border: { type: 'solid', color: 'D6E0EA', pt: 0.75 },
    fontFace: F, fontSize: pt, color: C.text, valign: 'middle',
    margin: 0.07, fill: { color: 'FFFFFF' },
  });
  return colW;
}

/* ───────────── 垂直节奏 ─────────────
   块总高已知 → 块在内容带里居中，但顶部偏移封顶 0.45 in：
   表格类内容因此紧贴标题（读作「属于这页」），而不是浮在半空。 */
function layout(parts) {
  const total = parts.reduce((a, p) => a + p.h, 0);
  const nGap = parts.length - 1;
  let gap = nGap > 0 ? (BAND_H - total) / nGap : 0;
  gap = Math.min(gap, 0.55);
  if (gap < 0.14) gap = 0.14;
  const used = total + gap * nGap;
  const y0 = BAND_TOP + Math.max(0, Math.min(MAX_TOP_PAD, (BAND_H - used) / 2));
  let y = y0;
  parts.forEach(p => { p.draw(y); y += p.h + gap; });
  return { y0, gap, bottom: y0 + used };
}
/* 表格行高按剩余预算分配，保证块底不越过内容带 */
function rowFor(nRows, otherH) {
  const avail = BAND_H - (otherH || 0) - (otherH ? 0.22 : 0.10);
  return Math.max(0.30, avail / (nRows * TGROW));
}
const tH = (nRows, rowH) => nRows * rowH * TGROW;

/* ───────────── 外壳（自己画，不复用模板 chrome —— 它会多画一条页脚） ───────────── */
function page(pptx, title, lead, num) {
  const s = pptx.addSlide();
  s.background = { color: C.white };
  s.addShape('rect', {
    x: 0, y: 0.723, w: 9.556, h: 0.191, objectName: 'bar-blue',
    fill: { color: '0063B9' }, line: { color: '0063B9', width: 0 },
  });
  s.addShape('rect', {
    x: 10.19, y: 0.723, w: 3.144, h: 0.191, objectName: 'bar-gold',
    fill: { color: C.gold }, line: { color: C.gold, width: 0 },
  });
  s.addImage({ path: LOGO, x: 10.63, y: 0.09, w: 1.92, h: 0.59 });
  s.addText(title, {
    x: L, y: TITLE_Y, w: 11.25, h: TITLE_H, fontFace: F, fontSize: S.title,
    bold: true, color: C.title, margin: 0, valign: 'middle',
  });
  if (lead) s.addText(lead, {
    x: L, y: LEAD_Y, w: CW, h: LEAD_H, fontFace: F, fontSize: S.lead,
    color: '60758F', margin: 0, valign: 'middle',
  });
  s.addText(FOOTER_TEXT, {
    x: L, y: FOOT_Y, w: 8.0, h: 0.23, fontFace: F, fontSize: S.foot, color: '60758F', margin: 0,
  });
  s.addText(String(num).padStart(2, '0'), {
    x: 11.6, y: FOOT_Y, w: 1.06, h: 0.23, fontFace: F, fontSize: S.foot,
    color: '60758F', align: 'right', margin: 0,
  });
  return s;
}

/* ═══════════════════════════ 建 deck ═══════════════════════════ */
const pptx = newDeck({ title: '课题5 第3次汇报：三场景结论与可复现闭环' });

/* ── 1 封面：校园底图 + 藏青带 + 校徽（校模板结构） ── */
{
  const s = pptx.addSlide();
  s.background = { path: COVER_BG };
  s.addShape('rect', { x: 0, y: 1.72, w: W, h: 3.62, fill: { color: C.navy }, line: { color: C.navy } });
  s.addImage({ path: LOGO, x: 0.84, y: 0.50, w: 3.60, h: 1.113 });
  s.addText('跨物种单细胞整合：三场景结论与可复现闭环', {
    x: 0.90, y: 1.92, w: 11.46, h: 0.62, fontFace: F, fontSize: S.coverTitle,
    bold: true, color: 'FFFFFF', margin: 0, valign: 'middle',
  });
  s.addText('课题5 第 3 次汇报（老师七条意见之后的重做）｜ XenoTransfer v1.0', {
    x: 0.92, y: 2.62, w: 11.2, h: 0.40, fontFace: F, fontSize: S.coverSub,
    color: 'D7E8F8', margin: 0, valign: 'middle',
  });
  paras(s, [
    '上次汇报后，老师提了 7 条意见 → 这一轮全部落地',
    '最重要的一件事：我们发现自己的 SATURN 分数被算高了 0.04–0.19，且鼠↔鱼结论因此翻转',
    '本讲三件事：① 三场景分开给结论　② 每个分数都带偏置　③ 可复现闭环已跑通',
  ], { x: 0.92, y: 3.22, w: 11.2, size: 13, color: 'D7E8F8', gap: 0.20, lh: 1.45 });
  s.addText(FOOTER_TEXT, {
    x: 0.92, y: 4.80, w: 11.2, h: 0.28, fontFace: F, fontSize: S.coverMeta,
    color: 'DDEBFA', margin: 0, valign: 'middle',
  });
  s.addShape('rect', { x: 0, y: 6.94, w: W, h: 0.56, fill: { color: C.goldLight }, line: { color: C.goldLight } });
  s.addText('这一轮不是加内容，是纠错。结论有改，而且改得更硬。', {
    x: 0.75, y: 6.94, w: 11.9, h: 0.56, fontFace: F, fontSize: S.band, bold: true,
    color: '8A4B00', margin: 0, valign: 'middle',
  });
  s.addNotes('开场就认错——先说我们发现了自己的口径问题，比等到被问出来强多了。');
}

/* ── 2 七条意见 → 落地 ── */
{
  const s = page(pptx, '一、老师七条意见 → 我们的落地', '每条都对应一个可复核的产物', 2);
  const rows = [
    ['老师意见', '我们做了什么', '产物'],
    ['①② 近缘/远缘/跨门分开说', '三场景各自给首选+配对检验', '§2–§4'],
    ['③ 百分数要考虑稳定性', '10 seed + 20 次数据扰动 + bootstrap CI', 'bootstrap.json'],
    ['④ 跟原文一样吗', '三篇原文逐条对比，不一致处给原因', 'report-08 §3'],
    ['⑤ 实际消耗', '四个任务 CPU 秒/费用台账 + 峰值内存', 'resource-ledger.json'],
    ['⑥ 流程要有名字', 'XenoTransfer v1.0', '交接文档'],
    ['⑦ 会不会发 GitHub/DCS', 'GitHub 仓库已在（本地领先 63 提交）；DCS 可发', '§6'],
  ];
  const rowH = rowFor(rows.length, 0);
  layout([{ h: tH(rows.length, rowH), draw: y => tbl(s, rows, { x: L, y, w: CW, rowH }) }]);
  band(s, '七条全部有落点，没有一条靠口头回答。', CONC_Y);
  s.addNotes('这一页是导航页，让老师知道每条都在哪儿。');
}

/* ── 3 SATURN 被抬高：三段语义带（事实 / 规则 / 损伤） ── */
{
  const s = page(pptx, '二、最重要的发现：SATURN 分数被口径抬高了', '映射不到 coarse 的预测被丢弃 = 按预测结果筛样本', 3);
  const items = [
    'oPCA/scVI 的预测只可能是训练用的 8–9 个 coarse 类，永远不可能「预测到类外」；SATURN 输出原始细胞类型，会预测出 Orthers、Ventricular Cardiomyocyte 这类映射不到的标签',
    '旧口径：这些预测连同细胞一起丢掉 → 分母只留「预测恰好可映射」的细胞',
    '后果：鼠↔鱼两向被抬高 0.19 左右，结论直接从「SATURN 大胜」翻成「scVI 显著更好」',
  ];
  const tints = ['EAF4FB', 'FFF2CC', 'FCE4D6'];
  const padX = 0.30, padY = 0.34;
  const hs = items.map(t => paraH(t, CW - padX * 2, S.body, LH) + padY * 2);
  const gap = Math.min(0.28, Math.max(0.18, (BAND_H - hs.reduce((a, b) => a + b, 0)) / 2));
  const totalH = hs.reduce((a, b) => a + b, 0) + gap * 2;
  let y = BAND_TOP + Math.max(0, Math.min(MAX_TOP_PAD, (BAND_H - totalH) / 2));
  items.forEach((t, i) => {
    s.addShape('rect', { x: L, y, w: CW, h: hs[i], fill: { color: tints[i] }, line: { color: tints[i] } });
    s.addText(t, {
      x: L + padX, y: y + padY, w: CW - padX * 2, h: hs[i] - padY * 2,
      fontFace: F, fontSize: S.body, color: C.text, margin: 0, valign: 'middle', lineSpacingMultiple: LH,
    });
    y += hs[i] + gap;
  });
  band(s, '这不是小修，是结论翻转。所以我们同时报两个口径，对外用公平口径。', CONC_Y);
  s.addNotes('这页是整个汇报的重点，讲慢一点。强调「按预测结果筛样本」这句话。');
}

/* ── 4 口径偏差量化（「被抬高」列整体压红 = 缺陷列） ── */
{
  const s = page(pptx, '三、口径偏差的量化', '同一批预测，两种口径差多少', 4);
  const rows = [
    ['方向', '现口径', '公平口径', '被抬高', '被丢掉的细胞'],
    ['人→鼠', '0.4147', '0.3402', '+0.0745', '89'],
    ['鼠→人', '0.4010', '0.3118', '+0.0892', '135'],
    ['人→斑马鱼', '0.2479', '0.2051', '+0.0428', '15'],
    ['斑马鱼→人', '0.4021', '0.2139', '+0.1882', '736'],
    ['鼠→斑马鱼', '0.6500', '0.4560', '+0.1940', '529'],
    ['斑马鱼→鼠', '0.6510', '0.4588', '+0.1922', '456'],
  ];
  const rowH = Math.min(0.60, rowFor(rows.length, 0));
  layout([{
    h: tH(rows.length, rowH),
    draw: y => tbl(s, rows, {
      x: L, y, w: CW, rowH,
      cell: (ri, ci) => (ri > 0 && ci === 3 ? { color: 'C00000', bold: true } : null),
    }),
  }]);
  band(s, '抬高幅度 0.043–0.194，前四向温和、后两向致命。', CONC_Y);
  s.addNotes('鼠→斑马鱼、斑马鱼→鼠这两行是重点，抬高接近 0.19。');
}

/* ── 5 近缘 ── */
{
  const s = page(pptx, '四、近缘场景：oPCA 与 scVI 打平', '人↔鼠｜macro-F1 ± bootstrap SE', 5);
  const rows = [
    ['方法', '人→鼠', '鼠→人', '两向均值'],
    ['oPCA', '0.6435±0.0186', '0.6729±0.0215', '0.6582'],
    ['scVI', '0.6683±0.0206', '0.5895±0.0140', '0.6289'],
    ['SATURN', '0.4147±0.0152', '0.4010±0.0210', '0.4079'],
    ['SAMap', '0.1127±0.0141', '0.0401±0.0051', '0.0764'],
  ];
  const rowH = Math.min(0.64, rowFor(rows.length, 0));
  layout([{ h: tH(rows.length, rowH), draw: y => tbl(s, rows, { x: L, y, w: CW, rowH }) }]);
  band(s, '人→鼠差 −0.0247（不显著）；鼠→人 oPCA 显著更高 +0.0833。打平 → 选 oPCA（27 秒、1.31 GB、无 GPU）。', CONC_Y);
  s.addNotes('打平是关键：既然打平，就该选代价小的那个。');
}

/* ── 6 远缘：SATURN 两口径并排（现口径浅橙 / 公平口径浅绿，让差自己说话） ── */
{
  const s = page(pptx, '五、远缘场景：统一选 scVI', '鱼参与的四方向｜注意两个口径的 SATURN 都列出来', 6);
  const rows = [
    ['方向', 'oPCA', 'scVI', 'SATURN 现', 'SATURN 公平'],
    ['人→斑马鱼', '0.1654±0.0152', '0.4014±0.0117', '0.2479', '0.2051'],
    ['斑马鱼→人', '0.1512±0.0070', '0.4290±0.0119', '0.4021', '0.2139'],
    ['鼠→斑马鱼', '0.2177±0.0135', '0.4248±0.0155', '0.6500', '0.4560'],
    ['斑马鱼→鼠', '0.4405±0.0144', '0.4786±0.0114', '0.6510', '0.4588'],
  ];
  const rowH = Math.min(0.64, rowFor(rows.length, 0));
  layout([{
    h: tH(rows.length, rowH),
    draw: y => tbl(s, rows, {
      x: L, y, w: CW, rowH,
      cell: (ri, ci) => (ri > 0 && ci === 3 ? { fill: 'FCE4D6' } : ri > 0 && ci === 4 ? { fill: 'E2EFDA' } : null),
    }),
  }]);
  band(s, '同细胞配对检验：鼠→鱼 SATURN−scVI = −0.1713、鱼→鼠 = −0.0709，两个方向 scVI 都显著更好。', CONC_Y);
  s.addNotes('强调「同一批细胞上比」才算公平，跨方法比绝对值会被分母骗。');
}

/* ── 7 跨门（负结果） ── */
{
  const s = page(pptx, '六、跨门场景：这一族方法都做不了', '七鳃鳗↔小鼠｜13 类交集｜55,694 细胞', 7);
  const rows = [
    ['方向', '方法', 'accuracy', 'macro-F1', '多数类基线'],
    ['Lamprey→Mouse', 'oPCA', '0.0575±0.0020', '0.0235', '0.2168'],
    ['Lamprey→Mouse', 'scVI', '0.0582±0.0020', '0.0241', '0.2168'],
    ['Mouse→Lamprey', 'oPCA', '0.0516±0.0011', '0.0257', '0.3059'],
    ['Mouse→Lamprey', 'scVI', '0.0457±0.0011', '0.0267', '0.3059'],
  ];
  const rowH = Math.min(0.66, rowFor(rows.length, 0));
  layout([{ h: tH(rows.length, rowH), draw: y => tbl(s, rows, { x: L, y, w: CW, rowH }) }]);
  band(s, 'accuracy 4.6–5.8%，低于 13 类随机猜的 7.69%；macro-F1 甚至低于多数类基线。这是硬负结果。', CONC_Y);
  s.addNotes('负结果要讲得理直气壮：它证明的不是「我们没做好」，是「这条路在跨门断掉了」。');
}

/* ── 8 稳定性 ── */
{
  const s = page(pptx, '七、稳定性：十个 seed 不会给出十个结果', '老师问的「一个方法测十次」，我们拆成三种不确定性分别测', 8);
  const rows = [
    ['方向', '10 seed SD', '换10%细胞 SD', '换10%基因 SD'],
    ['人→鼠', '0.0017', '0.0238', '0.0121'],
    ['鼠→人', '0.0025', '0.0214', '0.0133'],
    ['人→斑马鱼', '0.0032', '0.0111', '0.0240'],
    ['斑马鱼→人', '0.0030', '0.0059', '0.0084'],
    ['鼠→斑马鱼', '0.0021', '0.0056', '0.0210'],
    ['斑马鱼→鼠', '0.0059', '0.0282', '0.0341'],
  ];
  const rowH = Math.min(0.58, rowFor(rows.length, 0));
  layout([{ h: tH(rows.length, rowH), draw: y => tbl(s, rows, { x: L, y, w: CW, rowH }) }]);
  band(s, '换种子 SD 只有 0.0017–0.0059；换 10% 细胞能到 0.028、换 10% 基因能到 0.034。不确定性来自数据，不来自种子。', CONC_Y);
  s.addNotes('这一页直接回答老师第③条，而且结论反直觉：换种子几乎没用。');
}

/* ── 9 每个分数带偏置 ── */
{
  const s = page(pptx, '八、每个分数都带偏置', '四方法 × 六方向全部配 bootstrap SE 与 95% CI', 9);
  const rows = [
    ['方向', 'oPCA', 'scVI', 'SATURN', 'SAMap'],
    ['人→鼠', '0.6435±0.0186', '0.6683±0.0206', '0.4147±0.0152', '0.1127±0.0141'],
    ['鼠→人', '0.6729±0.0215', '0.5895±0.0140', '0.4010±0.0210', '0.0401±0.0051'],
    ['人→斑马鱼', '0.1654±0.0152', '0.4014±0.0117', '0.2479±0.0137', '0.0477±0.0042'],
    ['斑马鱼→人', '0.1512±0.0070', '0.4290±0.0119', '0.4021±0.0178', '—'],
    ['鼠→斑马鱼', '0.2177±0.0135', '0.4248±0.0155', '0.6500±0.0259', '—'],
    ['斑马鱼→鼠', '0.4405±0.0144', '0.4786±0.0114', '0.6510±0.0260', '—'],
  ];
  const rowH = Math.min(0.58, rowFor(rows.length, 0));
  layout([{ h: tH(rows.length, rowH), draw: y => tbl(s, rows, { x: L, y, w: CW, rowH }) }]);
  band(s, '22 格全部通过「与冻结值逐格对齐」校验（0 mismatch），所以这些 CI 是挂在已验证数字上的。', CONC_Y);
  s.addNotes('可以现场点开 bootstrap.json 给老师看 matches_frozen 全是 true。');
}

/* ── 10 实际消耗 ── */
{
  const s = page(pptx, '九、实际消耗', '平台任务台账 + 本地白盒测内存', 10);
  const rows = [
    ['方法', '任务号', '实际计算', '资源档', '费用'],
    ['oPCA (FIXKEY)', 'W202610150090794', '866 s', '2c8g', '¥0.19'],
    ['scVI 门内', 'W202610190042919', '916 s', '2c8g', '¥0.20'],
    ['scVI 跨门', 'W202610220063725', '9,773 s', '2c8g', '¥2.06'],
    ['SAMap', 'W202610260103163', '354 s', '1c4g', '¥0.02'],
    ['合计', '4 个任务', '11,909 s (3h18m)', '—', '¥2.47'],
  ];
  const bl = [
    'oPCA 本地白盒测量：墙钟 26.68 s（25.52–26.92），峰值工作集 1307.9 MB',
    '跨门那次占总额 84%（¥2.06/¥2.47），细胞数 12 倍、耗时 10.7 倍——近似线性，不是平方',
  ];
  const bh = parasH(bl, CW, S.body, LH, 0.16);
  const rowH = Math.min(0.46, rowFor(rows.length, bh));
  layout([
    { h: tH(rows.length, rowH), draw: y => tbl(s, rows, { x: L, y, w: CW, rowH }) },
    { h: bh, draw: y => paras(s, bl, { x: L, y, w: CW, size: S.body, gap: 0.16 }) },
  ]);
  band(s, '四个任务合计 11,909 CPU 秒 / ¥2.47。SATURN 是 GPU 任务，平台不记 CPU/内存，如实标为缺口。', CONC_Y);
  s.addNotes('诚实标缺口：SATURN 没有资源数据，不编。');
}

/* ── 11 可复现闭环（✓ 列压绿） ── */
{
  const s = page(pptx, '十、可复现闭环：镜像建好，6 个值在里面逐位复现', 'g5-opca-container（基于 SATURN--22，7 个 pip 精确版本）', 11);
  const rows = [
    ['方向', '冻结值', '镜像内实测', '一致'],
    ['人→鼠', '0.8618', '0.8618', '✓'],
    ['鼠→人', '0.7369', '0.7369', '✓'],
    ['人→斑马鱼', '0.1795', '0.1795', '✓'],
    ['斑马鱼→人', '0.1734', '0.1734', '✓'],
    ['鼠→斑马鱼', '0.2675', '0.2675', '✓'],
    ['斑马鱼→鼠', '0.5814', '0.5814', '✓'],
  ];
  const bl = [
    '镜像构建成功 → 离线任务实测可选中 → 在镜像内跑完整评估，6/6 逐位一致',
    '7 个包版本全部命中：numpy 1.23.5 / scipy 1.10.1 / pandas 1.5.3 / sklearn 1.6.1 / anndata 0.10.8 / scanpy 1.9.3 / h5py 3.8.0',
  ];
  const bh = parasH(bl, CW, S.body, LH, 0.16);
  const rowH = Math.min(0.42, rowFor(rows.length, bh));
  layout([
    {
      h: tH(rows.length, rowH),
      draw: y => tbl(s, rows, {
        x: L, y, w: CW, rowH,
        cell: (ri, ci) => (ri > 0 && ci === 3 ? { color: '1F7A4D', bold: true } : null),
      }),
    },
    { h: bh, draw: y => paras(s, bl, { x: L, y, w: CW, size: S.body, gap: 0.16 }) },
  ]);
  band(s, '从「配方看起来完整」到「真的跑出同样数字」，这一步此前从未做到过。', CONC_Y);
  s.addNotes('这是本轮最硬的一块证据，可以给老师看日志里的 header 和 DONE。');
}

/* ── 12 两件事都是坑（三段事实带） ── */
{
  const s = page(pptx, '十一、一路上查清的两件事（都是坑）', '同名 ≠ 同文件', 12);
  const items = [
    '平台 ortholog_pca_dcs_v3_fixkey.txt（17,382 B / 421 行 / json.loads 在 167 行 / sha 514d9314…）与本地 scripts/*.py（16,463 B / 383 行 / csv.DictReader 在 123 行 / sha f9683cf9…）不是同一文件，同名函数有两种实现',
    '平台版要的映射是 /Files/wheelhouse/v99_mapping_embedded.json（38 条 dict），不是 heart-celltype-map-v1.tsv',
    '平台把任务标成「失败」那次，其实计算成功了——只是脚本最后 cat 了错误的输出目录变量名',
  ];
  const padX = 0.30, padY = 0.30;
  const hs = items.map(t => paraH(t, CW - padX * 2, S.body, LH) + padY * 2);
  const gap = Math.min(0.28, Math.max(0.18, (BAND_H - hs.reduce((a, b) => a + b, 0)) / 2));
  const totalH = hs.reduce((a, b) => a + b, 0) + gap * 2;
  let y = BAND_TOP + Math.max(0, Math.min(MAX_TOP_PAD, (BAND_H - totalH) / 2));
  items.forEach((t, i) => {
    s.addShape('rect', { x: L, y, w: CW, h: hs[i], fill: { color: 'EAF4FB' }, line: { color: 'B7C9D6', width: 0.75 } });
    s.addText(t, {
      x: L + padX, y: y + padY, w: CW - padX * 2, h: hs[i] - padY * 2,
      fontFace: F, fontSize: S.body, color: C.text, margin: 0, valign: 'middle', lineSpacingMultiple: LH,
    });
    y += hs[i] + gap;
  });
  band(s, '教训：先比 wc -c / wc -l / sha256sum，再决定用哪个文件；平台标「失败」要看它退出在哪一步。', CONC_Y);
  s.addNotes('这一页体现工程严谨，老师会认这个。');
}

/* ── 13 跟原文一致吗 ── */
{
  const s = page(pptx, '十二、跟原文一致吗', '三篇原文逐条对比', 13);
  const rows = [
    ['原文', '作者主张', '我们复现到哪'],
    ['SATURN (Nat Methods 2024)', '蛙↔鱼 85.8% 中位准确率，比 SAMap 高 119%', '方向一致（SATURN>SAMap），但输给 scVI'],
    ['SAMap (eLife 2021)', '同门内全同源图可跨远缘映射', '我们只喂 1:1 同源、规模差 300 倍，几乎无信号'],
    ['HEART (Science 2026)', '27 物种心脏图谱，SATURN 整合 16 物种', '仅用其小子集，未复现原规模'],
  ];
  const bl = ['不一致的三个原因：①原文 scVI 是纯无监督整合，我们加了 KNN 标签迁移层　②我们的口径偏差（已修）　③SAMap 靠全同源图，我们只给 1:1'];
  const bh = parasH(bl, CW, S.body, LH, 0.16);
  const rowH = Math.min(0.72, rowFor(rows.length, bh));
  layout([
    { h: tH(rows.length, rowH), draw: y => tbl(s, rows, { x: L, y, w: CW, rowH, colW: fitCols(rows, CW, 0.72, 2.2) }) },
    { h: bh, draw: y => paras(s, bl, { x: L, y, w: CW, size: S.body, gap: 0.16 }) },
  ]);
  band(s, '「SAMap 不行」不能说，只能说「在本项目 1,500 细胞 + 1:1 同源约束下无信号」。', CONC_Y);
  s.addNotes('这一页回答老师第④条，重点是把「我们和别人不一样」说成可解释的差异，而不是掩饰。');
}

/* ── 14 还剩什么（组内 0.16 / 组间 0.40，靠留白分组，不加字） ── */
{
  const s = page(pptx, '十三、还剩什么', '三条边界，两条待人做', 14);
  const items = [
    '待人做 ①：mapping 表 38 行 reviewer 仍是 pending，需导师/生物学同学签字——而且签之前建议先改 3 行（Orthers→neural 最该改）',
    '待人做 ②：GitHub 推送（本地领先 63 提交，当时代理端口无监听）',
    '明确不做：SATURN 批次指标（重训会产出不同表示，造成假对照）',
    '明确不做：排总分冠军（分母/特征空间/训练方式/统计强度都不同）',
    '明确不做：held-out / inductive 重跑（需新协议与预算，现有结论只声称 transductive）',
  ];
  const gap = i => (i === 1 ? 0.40 : 0.16);
  const h = parasH(items, CW, S.body, LH, gap);
  layout([{ h, draw: y => paras(s, items, { x: L, y, w: CW, size: S.body, gap }) }]);
  band(s, '12 项课程要求：11 项完成、1 项部分（批次混合，SATURN 缺席有硬理由）。', CONC_Y);
  s.addNotes('收口页，把「还剩什么」说成清单，不是辩解。');
}

/* ── 15 如果只记三句（三条语义带，填满内容带；同 p3/p12 母题） ── */
{
  const s = page(pptx, '如果只记三句', '课后能复述的三句', 15);
  const items = [
    '1. 没有全面赢家 → 不排总分，只做「场景 → 方法」',
    '2. 我们自己发现并修正了一个抬高 0.04–0.19 的口径偏差，鼠↔鱼结论因此翻转',
    '3. 所有结论限定在 transductive / in-sample、4,606 细胞、且 macro-F1 必须带「union 口径 + 分母」一起说',
  ];
  const padX = 0.34, padY = 0.30;
  const hs = items.map(t => paraH(t, CW - padX * 2, S.body, LH) + padY * 2);
  const gap = Math.min(0.30, Math.max(0.18, (BAND_H - hs.reduce((a, b) => a + b, 0)) / 2));
  const totalH = hs.reduce((a, b) => a + b, 0) + gap * 2;
  let y = BAND_TOP + Math.max(0, Math.min(MAX_TOP_PAD, (BAND_H - totalH) / 2));
  items.forEach((t, i) => {
    s.addShape('rect', { x: L, y, w: CW, h: hs[i], fill: { color: 'EAF4FB' }, line: { color: 'EAF4FB' } });
    s.addText(t, {
      x: L + padX, y: y + padY, w: CW - padX * 2, h: hs[i] - padY * 2,
      fontFace: F, fontSize: S.body, color: C.title, margin: 0, valign: 'middle', lineSpacingMultiple: LH,
    });
    y += hs[i] + gap;
  });
  band(s, '算得对是底线，分得对要人签字。', CONC_Y);
  s.addNotes('结束页，停在这里提问。');
}

pptx.writeFile({ fileName: OUT }).then(f => console.log('saved', f));
