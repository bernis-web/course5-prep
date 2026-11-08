// 课题5 阶段汇报共用版式模块 —— 康复大学校模板（规格取自第一阶段汇报 PPT 原文件解包）
// 顶栏：蓝渐变 snip2DiagRect (0, 0.723, 9.556, 0.191) + 金条 (10.19, 0.723, 3.144, 0.191, FFC000)
// logo：10.63, 0.09, 1.92 × 0.59；标题：0.67, 1.05, 色 12365A；页脚：左标签 + 右页码，8.5pt，60758F
// 封面：校园底图 + 藏青带 (0, 2.14, 13.333, 1.99, 002060) + logo (0.84, 0.69, 4.14 × 1.28)
// 注意：顶栏斜切与渐变由 postprocess_bars.py 在生成后注入（objectName: bar-blue / bar-gold）
const pptxgen = require('pptxgenjs');

const W = 13.333, H = 7.5;
const C = { navy:'002060', title:'12365A', blue:'005BAC', blueLight:'EAF4FB', gold:'FFC000',
            goldLight:'FFF2CC', roseLight:'FCE4D6', greenLight:'E2EFDA', text:'1F2D3D',
            muted:'60758F', line:'B7C9D6', white:'FFFFFF' };
const F = '微软雅黑';
const LOGO = 'D:/projects/course5-prep/tmp/ppt-inspect/original_extract/ppt/media/image11.png';
const COVER_BG = 'D:/projects/course5-prep/results/report-02-metric-lineage-20261008/assets/cover-campus.jpg';
const FOOTER_LABEL = '课题5  阶段汇报';

function newDeck(meta) {
  meta = meta || {};
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_WIDE';
  pptx.author = '课题5';
  pptx.subject = meta.subject || '跨物种心脏单细胞整合方法学评估';
  pptx.title = meta.title || '';
  pptx.lang = 'zh-CN';
  pptx.theme = { headFontFace:F, bodyFontFace:F, lang:'zh-CN' };
  return pptx;
}

// 封面页
function cover(pptx, o) {
  const s = pptx.addSlide();
  s.background = { path: COVER_BG };
  s.addShape('rect', { x:0, y:2.14, w:W, h:1.99, fill:{color:C.navy}, line:{color:C.navy} });
  s.addImage({ path:LOGO, x:0.84, y:0.69, w:4.14, h:1.28 });
  s.addText(o.title, { x:0.90, y:2.31, w:11.46, h:0.75, fontFace:F, fontSize:o.titleSize||32, bold:true, color:C.white, margin:0, valign:'middle' });
  if (o.subtitle) s.addText(o.subtitle, { x:0.92, y:3.12, w:10.9, h:0.44, fontFace:F, fontSize:17, color:'D7E8F8', margin:0, fit:'shrink' });
  if (o.meta) s.addText(o.meta, { x:0.92, y:3.62, w:11.5, h:0.31, fontFace:F, fontSize:11.5, color:'DDEBFA', margin:0, fit:'shrink' });
  return s;
}

// 内容页页头/页脚
function chrome(slide, title, page) {
  slide.background = { color:C.white };
  slide.addShape('rect', { x:0, y:0.723, w:9.556, h:0.191, objectName:'bar-blue',
    fill:{color:'0063B9'}, line:{color:'0063B9', width:0} });
  slide.addShape('rect', { x:10.19, y:0.723, w:3.144, h:0.191, objectName:'bar-gold',
    fill:{color:C.gold}, line:{color:C.gold, width:0} });
  slide.addImage({ path:LOGO, x:10.63, y:0.09, w:1.92, h:0.59 });
  slide.addText(title, { x:0.67, y:1.05, w:11.25, h:0.62, fontFace:F, fontSize:24, bold:true, color:C.title, margin:0, valign:'middle' });
  slide.addText(FOOTER_LABEL, { x:0.67, y:7.06, w:4.0, h:0.23, fontFace:F, fontSize:8.5, color:C.muted, margin:0 });
  slide.addText(String(page).padStart(2,'0'), { x:11.6, y:7.06, w:1.06, h:0.23, fontFace:F, fontSize:8.5, color:C.muted, align:'right', margin:0 });
}

// 卡片
function box(slide, x,y,w,h, title, body, opts) {
  opts = opts || {};
  slide.addShape('roundRect', { x:x,y:y,w:w,h:h, rectRadius:0.06, fill:{color:opts.fill||C.blueLight}, line:{color:opts.line||C.line, width:1} });
  slide.addText(title, { x:x+0.16, y:y+0.1, w:w-0.32, h:0.3, fontFace:F, fontSize:opts.titleSize||14.5, bold:true, color:opts.titleColor||C.title, margin:0 });
  slide.addText(body, { x:x+0.16, y:y+0.46, w:w-0.32, h:h-0.56, fontFace:F, fontSize:opts.bodySize||11, color:opts.bodyColor||C.text, fit:'shrink', valign:'top', margin:0.02, paraSpaceAfterPt:4 });
}

// 底部结论条
function band(slide, text, y, fill, color) {
  slide.addShape('rect', { x:0, y:y, w:W, h:0.44, fill:{color:fill||C.goldLight}, line:{color:fill||C.goldLight} });
  slide.addText(text, { x:0.75, y:y+0.04, w:11.9, h:0.36, fontFace:F, fontSize:13, bold:true, color:color||'8A4B00', margin:0, fit:'shrink' });
}

// 表格（表头 005BAC 白字）
function table(slide, rows, x, y, w, colW, rowH, fontSize) {
  const styled = rows.map((r, ri) => r.map(c => ({ text: c, options: ri === 0
    ? { fill:{color:C.blue}, color:'FFFFFF', bold:true } : {} })));
  slide.addTable(styled, {
    x:x, y:y, w:w, colW:colW,
    border:{ type:'solid', color:'D6E0EA', pt:0.75 },
    fontFace:F, fontSize:fontSize||10.5, color:C.text, valign:'middle',
    rowH: rowH||0.38, margin:0.05,
    fill:{ color:C.white },
  });
}

function notes(slide, text) { try { slide.addNotes(text); } catch(e) {} }

module.exports = { newDeck, cover, chrome, box, band, table, notes, C, F, W, H, LOGO, COVER_BG };
