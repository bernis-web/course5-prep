// 课题5 第二阶段汇报（数字来源链）——康复大学校模板版
// 版式规格取自 tmp/ppt-inspect/original_extract（第一阶段汇报所用校模板）：
//   顶栏：蓝渐变 snip2DiagRect (0, 0.723, 9.556, 0.191) + 金条 snip2DiagRect (10.19, 0.723, 3.144, 0.191, FFC000)
//   logo：10.63, 0.09, 1.92 × 0.59（image11.png）
//   标题：0.67, 1.07, 色 12365A；页脚：左标签 + 右页码，8.25pt，色 60758F
//   封面：校园底图（layout24 image8）+ 藏青带 (0, 2.14, 13.333, 1.99, 002060) + logo (0.84, 0.69, 4.14 × 1.28)
const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = '课题5';
pptx.subject = '跨物种心脏单细胞整合方法学评估';
pptx.title = '课题5第二阶段汇报：数字来源链（校模板版）';
pptx.lang = 'zh-CN';
pptx.theme = { headFontFace: '微软雅黑', bodyFontFace: '微软雅黑', lang: 'zh-CN' };

const W = 13.333, H = 7.5;
const C = { navy:'002060', title:'12365A', blue:'005BAC', blueLight:'EAF4FB', gold:'FFC000',
            goldLight:'FFF2CC', roseLight:'FCE4D6', text:'1F2D3D', muted:'60758F',
            line:'B7C9D6', white:'FFFFFF' };
const F = '微软雅黑';
const logo = 'D:/projects/course5-prep/tmp/ppt-inspect/original_extract/ppt/media/image11.png';
const coverBg = 'D:/projects/course5-prep/results/report-02-metric-lineage-20261008/assets/cover-campus.jpg';
const out = 'D:/projects/course5-prep/results/report-02-metric-lineage-20261008/课题5第二阶段汇报_数字来源链_校模板版.pptx';

// ---- 校模板页头/页脚（蓝渐变条 + 金条 + logo + 标题 + 页脚）----
function chrome(slide, title, page) {
  slide.background = { color: C.white };
  slide.addShape(pptx.ShapeType.rect, { x:0, y:0.723, w:9.556, h:0.191, objectName:'bar-blue',
    fill:{color:'0063B9'}, line:{color:'0063B9', width:0} });
  slide.addShape(pptx.ShapeType.rect, { x:10.19, y:0.723, w:3.144, h:0.191, objectName:'bar-gold',
    fill:{color:C.gold}, line:{color:C.gold, width:0} });
  slide.addImage({ path:logo, x:10.63, y:0.09, w:1.92, h:0.59 });
  slide.addText(title, { x:0.67, y:1.05, w:11.25, h:0.62, fontFace:F, fontSize:26, bold:true, color:C.title, margin:0, valign:'middle' });
  slide.addText('课题5  第二阶段汇报', { x:0.67, y:7.06, w:4.0, h:0.23, fontFace:F, fontSize:8.5, color:C.muted, margin:0 });
  slide.addText(String(page).padStart(2,'0'), { x:11.6, y:7.06, w:1.06, h:0.23, fontFace:F, fontSize:8.5, color:C.muted, align:'right', margin:0 });
}
function box(slide, x,y,w,h, title, body, opts) {
  opts = opts || {};
  slide.addShape(pptx.ShapeType.roundRect, { x:x,y:y,w:w,h:h, rectRadius:0.06, fill:{color:opts.fill||C.blueLight}, line:{color:opts.line||C.line, width:1} });
  slide.addText(title, { x:x+0.16, y:y+0.1, w:w-0.32, h:0.3, fontFace:F, fontSize:opts.titleSize||14.5, bold:true, color:opts.titleColor||C.title, margin:0 });
  slide.addText(body, { x:x+0.16, y:y+0.46, w:w-0.32, h:h-0.56, fontFace:F, fontSize:opts.bodySize||11, color:opts.bodyColor||C.text, fit:'shrink', valign:'top', margin:0.02, paraSpaceAfterPt:4 });
}
function notes(slide, text) { try { slide.addNotes(text); } catch(e) {} }
function band(slide, text, y, fill, color) {
  slide.addShape(pptx.ShapeType.rect, { x:0, y:y, w:W, h:0.44, fill:{color:fill||C.goldLight}, line:{color:fill||C.goldLight} });
  slide.addText(text, { x:0.75, y:y+0.04, w:11.9, h:0.36, fontFace:F, fontSize:13, bold:true, color:color||'8A4B00', margin:0, fit:'shrink' });
}
// ---- 表格：表头 005BAC 白字（校模板表格样式）----
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

// ============ Slide 1: 封面（校模板） ============
let s = pptx.addSlide();
s.background = { path: coverBg };
s.addShape(pptx.ShapeType.rect, { x:0, y:2.14, w:W, h:1.99, fill:{color:C.navy}, line:{color:C.navy} });
s.addImage({ path:logo, x:0.84, y:0.69, w:4.14, h:1.28 });
s.addText('课题5 第二阶段汇报：数字来源链', { x:0.90, y:2.31, w:11.46, h:0.75, fontFace:F, fontSize:34, bold:true, color:C.white, margin:0, valign:'middle' });
s.addText('一个百分比是怎样得到的——从原始细胞到表格单元格的完整可复核路径', { x:0.92, y:3.12, w:10.6, h:0.44, fontFace:F, fontSize:17, color:'D7E8F8', margin:0, fit:'shrink' });
s.addText('汇报 2 / 10 · 不报新数字，只讲数字怎么来 ｜ 口径：transductive / in-sample · seed 0 · KNN15 cosine · 2026 年 10 月', { x:0.92, y:3.62, w:11.4, h:0.31, fontFace:F, fontSize:11.5, color:'DDEBFA', margin:0, fit:'shrink' });
notes(s,'开场：第一阶段汇报解决了"表格数字怎么读"；这一阶段解决"每个数字怎么算出来"。全程不引入新数字。');

// ============ Slide 2: 一个百分比怎样得到 ============
s = pptx.addSlide(); chrome(s,'一个百分比是怎样得到的：六段可复核链',2);
const chain = [
  ['① 输入', 'local_*.h5ad\n人 1528 / 鼠 1535\n鱼 1543 细胞'],
  ['② 归一化', 'normalize_total(1e4)\n+ log1p\n（= log1p(CPM/100)）'],
  ['③ 表示层', 'ortholog 交集+PCA50\nESM2→macrogenes\nSAMap 同源图'],
  ['④ 角色', 'src = reference\n（拟合）\ntgt = query（预测）'],
  ['⑤ 评分', 'KNN15 · cosine\n倒距离加权\n200 次置换'],
  ['⑥ 分母', 'status≠active 排除\ncorrect / n_q\n+ coverage'],
];
chain.forEach((c,i)=>{
  const x = 0.5 + i*2.12;
  s.addShape(pptx.ShapeType.roundRect, { x:x, y:1.82, w:1.98, h:1.28, rectRadius:0.08, fill:{color: i%2? C.blueLight : C.goldLight}, line:{color:C.line, width:1} });
  s.addText(c[0], { x:x+0.08, y:1.87, w:1.82, h:0.28, fontFace:F, fontSize:12, bold:true, color:C.title, align:'center', margin:0 });
  s.addText(c[1], { x:x+0.08, y:2.15, w:1.82, h:0.9, fontFace:F, fontSize:9.5, color:C.text, align:'center', valign:'top', margin:0, fit:'shrink' });
  if (i < 5) s.addShape(pptx.ShapeType.rightArrow, { x:x+1.99, y:2.32, w:0.12, h:0.22, fill:{color:C.gold}, line:{color:C.gold} });
});
s.addText('终点：metrics.json → SHA-256 → 汇报表格。每一步都能沿文件与公式复算。', { x:0.8, y:3.2, w:11.8, h:0.36, fontFace:F, fontSize:14.5, bold:true, color:C.title, align:'center', margin:0, fit:'shrink' });
box(s,0.72,3.68,5.8,2.0,'四个必须并列报告的量','• accuracy = correct / n_q（主指标）\n• n_q / coverage = 进入分母的细胞数及其占比\n• majority = 最大真值类占比（无信息基线）\n• shuffle_p = 预测向量置换检验',{fill:C.blueLight,bodySize:11});
box(s,6.78,3.68,5.82,2.0,'为什么不能只报一个百分比','• 换掉六段链中任何一段，数字都会变\n• 排除规则改变分母 → 分母效应真实存在\n• 同一嵌入在不同评分器下不是同一测量\n• 跨方法标签空间不同 → 不可直接互比',{fill:C.roseLight,bodySize:11});
band(s,'一句话：准确率 = 正确预测数 ÷ 排除后仍有资格进入分母的 query 细胞数。',6.35);
notes(s,'这一页是全场的逻辑骨架：后面每个例子都按这六段展开。');

// ============ Slide 3: ortholog-PCA 86.18% ============
s = pptx.addSlide(); chrome(s,'例 1：ortholog-PCA 人→鼠 coarse = 86.18%',3);
table(s,[
  ['步骤','内容','值'],
  ['输入','reference = 人；query = 鼠','1,528 / 1,535 细胞'],
  ['归一化','normalize_total(1e4) + log1p（全基因空间）','等价 log1p(CPM/100)'],
  ['同源基因','人鼠 1:1 直系同源交集','15,869 基因'],
  ['表示层','人+鼠联合 PCA-50（seed 0，transductive）','3,063 × 50'],
  ['评分','KNN15 · cosine · 倒距离加权','k = 15'],
  ['排除','鼠侧 status≠active（Proliferating cell）','剔 30'],
  ['eligible query','1,535 − 30','n_q = 1,505'],
  ['正确数','逐细胞预测 == 真值','1,297'],
  ['accuracy','1,297 ÷ 1,505','0.8618'],
  ['coverage / majority','1,505 ÷ 1,535 / 最大真值类占比','0.9805 / 0.4817'],
], 0.7, 1.82, 6.35, [1.25, 3.3, 1.8], 0.36, 10.5);
box(s,7.35,1.82,5.25,2.75,'逐类分解（confusion 摘录）','• 内皮 720/725 正确（99.3%）\n• 成纤维 255/360\n• 免疫 197/202（97.5%）\n• 心肌 19/47\n• 主要类别命中率高；跨类错误集中在\n  成纤维→平滑肌（82）、心肌→内皮（27）',{fill:C.blueLight,bodySize:11});
box(s,7.35,4.72,5.25,1.5,'要强调','86.18% 不是从表里抄出来的：\n它是「正确预测数 ÷ 排除后仍有资格的 query 细胞数」。\n\n输出文件：results/pilot-v1/ortholog-pca-v98/metrics.json（SHA b2b3ac6b…c725）',{fill:C.goldLight,bodySize:10.5});
band(s,'本地已独立复算：从 predictions/ 逐细胞重算 acc/coverage/confusion 与 metrics.json 完全一致。',6.35);
notes(s,'这是唯一一个完全可本地复算的例子（18 份预测+混淆矩阵全在本地）。');

// ============ Slide 4: SATURN 三个数字 ============
s = pptx.addSlide(); chrome(s,'例 2：SATURN 的三个数字必须分开报告',4);
table(s,[
  ['数字','口径（评分器 + 标签空间）','分母','证据等级'],
  ['0.6179','v97g 评分器 · mapped-space（映射后粗类）','coverage 0.9805 → n_q≈1,505','confirmed（日志级）'],
  ['0.4749','v99 统一评分器 · exact（原始标签）','n_q = 1,535','candidate（provenance confirmed）'],
  ['0.4844','v99 统一评分器 · coarse（原始标签+status 过滤）','n_q = 1,505','candidate（provenance confirmed）'],
], 0.7, 1.82, 11.9, [1.15, 6.4, 2.15, 2.2], 0.46, 10.5);
box(s,0.72,4.12,5.8,2.1,'为什么不能合并成一个 SATURN 成绩','• 0.6179 与 0.4749/0.4844 是同一批 SATURN 嵌入在\n  不同评分器 + 不同标签空间下的结果\n• 不是"同一指标的两次测量"，不能写成\n  "SATURN 从 61.79% 降到 48.44%"\n• v97g 无逐细胞文件（日志级）；\n  v99 有完整 46 文件树 provenance',{fill:C.roseLight,bodySize:11});
box(s,6.78,4.12,5.82,2.1,'引用规则（写进报告）','凡出现 SATURN 数字，必须同时写：\n\n① 哪个评分器（v97g / v99）\n② 哪个标签空间（mapped / exact / coarse）\n③ 分母 n_q 与排除规则\n④ 证据等级（日志级 / 文件级）',{fill:C.blueLight,bodySize:11});
band(s,'本页三个数字的差别不是"版本更新"，而是协议不同——这正是下一阶段（汇报 3）要展开的内容。',6.35);
notes(s,'这是最容易出错的一页：外行会把三个数字当成三次测量。');

// ============ Slide 5: 分母效应实证 ============
s = pptx.addSlide(); chrome(s,'例 3：分母效应实证——正确数不变，准确率上升',5);
s.addText('v99 统一评分器 · human→mouse · 本地逐细胞独立复算（1,535 行载荷）', { x:0.75,y:1.78,w:11.9,h:0.3,fontFace:F,fontSize:12.5,color:C.muted,margin:0 });
table(s,[
  ['层','计分细胞数','正确数','accuracy','说明'],
  ['exact（原始标签）','1,535（全部）','729','729 ÷ 1535 = 0.4749','不做排除'],
  ['排除的 30 个细胞','—','0 / 30','—','增殖细胞，全部预测错误'],
  ['coarse（+status 过滤）','1,505','729','729 ÷ 1505 = 0.4844','分母缩小，分子不变'],
], 0.7, 2.12, 11.9, [2.9, 2.0, 1.5, 2.7, 2.8], 0.46, 10.5);
box(s,0.72,4.12,5.8,2.1,'这说明什么','• 被排除的 30 个增殖细胞全部是错的\n• 排除它们后：分子不变（729）、分母变小（1535→1505）\n• accuracy 从 0.4749 升到 0.4844\n\n→ 排除规则本身就会改变准确率',{fill:C.goldLight,bodySize:11});
box(s,6.78,4.12,5.82,2.1,'因此引用规则','• 任何 acc 必须并列 n_q 与 coverage\n• 两个 acc 只有在同一分母口径下才能比较\n• 排除数不是"清洗细节"，是协议的一部分\n• 30/44/0 的排除普查要随表报告',{fill:C.blueLight,bodySize:11});
band(s,'这是本阶段最有说服力的一个例子：同一批细胞、同一个嵌入，只改分母，数字就变了。',6.35);
notes(s,'本地从恢复的 v99 载荷（p6）逐细胞重算验证：729/1535 与 729/1505 均与 metrics.json 一致。');

// ============ Slide 6: SAMap 10.50% ============
s = pptx.addSlide(); chrome(s,'例 4：SAMap WDL 人→鼠 coarse = 10.50%',6);
table(s,[
  ['步骤','内容','值'],
  ['运行通道','WDL 流程任务（绕开离线通道故障）','W202610050003104'],
  ['实际运行脚本','410 行版（非 Phase 5 修复版）','sha256 c0f05b89…3807'],
  ['依赖栈','预建 pylibs（samap 1.0.16 + samalg 1.0.2 + hnswlib shim）','复用，非重装'],
  ['预处理','cell_median + log + StandardScaler(npcs=100)','k = 20'],
  ['联合对齐','SAMAP(keys=cell_type) 同源基因图，NUMITERS=3','label-aware'],
  ['评分','KNN15 · cosine · 倒距离加权（与 v99 同评分器）','—'],
  ['reference / query','人 1,528 / 鼠 1,535','剔 30'],
  ['n_q / 正确数','1,505 / 158','158 ÷ 1505'],
  ['accuracy','—','0.1050'],
], 0.7, 1.82, 6.35, [1.25, 3.3, 1.8], 0.36, 10.5);
box(s,7.35,1.82,5.25,2.3,'三个必须声明的限制','① label-aware：keys=cell_type 使真值参与联合图构建\n   → 与 ortholog-PCA（label-free）不可直接互比\n\n② 脚本版本：本次为 WDL 实际运行脚本（410 行版）\n   Phase 5 修复版（0a2063d3）在 WDL 环境下未运行\n   → 不能把两者说成同一次运行\n\n③ per_cell 旗标：included=1,398 与 n_q=1,505\n   口径不同、不参与 acc；复算按全部 query 行',{fill:C.roseLight,bodySize:10});
box(s,7.35,4.27,5.25,1.95,'读数（不是"接近随机"）','0.1050 远低于多数类 0.4618。\nconfusion 显示预测大量塌缩到单一类别：\n内皮 695 个中 634 个被预测为 Lymphoid（91.2%）。\n\n→ 是"系统性错位"，不是噪声。',{fill:C.blueLight,bodySize:10.5});
band(s,'SAMap 结论限于：当前数据、当前协议、当前运行脚本下的探索性复现；不能推广为"工具无效"。',6.35);
notes(s,'label-aware 与脚本版本是两个最容易含糊过去的点，必须明说。');

// ============ Slide 7: 斑马鱼 ============
s = pptx.addSlide(); chrome(s,'例 5：斑马鱼方向为什么低于多数类',7);
table(s,[
  ['量','值'],
  ['query / reference','鱼 1,543 / 人 1,528'],
  ['同源基因（人鱼 1:1）','9,131'],
  ['排除（mt 30 + Proliferating 14）','44'],
  ['n_q','1,499'],
  ['coverage','0.9715'],
  ['正确数','294'],
  ['accuracy','294 ÷ 1499 = 0.1961'],
  ['majority','0.3976'],
  ['shuffle_p','0.0'],
], 0.7, 1.82, 5.0, [2.6, 2.4], 0.36, 10.5);
box(s,6.0,1.82,6.6,2.05,'两个数字的正确读法','• accuracy 0.1961 < majority 0.3976\n  → 该方向没有可靠的类别迁移优势（低于"全猜最大类"）\n\n• shuffle_p = 0.0\n  → 只说明优于"随机洗牌预测向量"的零分布（E[null]≈0.10）\n  → 不能读成"优于多数类"',{fill:C.goldLight,bodySize:11});
box(s,6.0,4.02,6.6,2.2,'confusion 证据：错误是系统性的','• 鱼红细胞 287/332 预测为 immune\n• 鱼内皮 509/596 预测为 immune\n• 鱼平滑肌 68/166 预测为 immune\n\n→ 跨物种错误集中在特定类别对，不是随机噪声。',{fill:C.blueLight,bodySize:11});
s.addShape(pptx.ShapeType.roundRect, { x:0.7, y:5.82, w:5.0, h:0.46, rectRadius:0.06, fill:{color:C.goldLight}, line:{color:C.line, width:1} });
s.addText('单 seed 提示：鱼方向 seed 双峰已证实；本页为单 seed（0）点估计，不应读作该方向的稳定值。', { x:0.82, y:5.85, w:4.76, h:0.4, fontFace:F, fontSize:9.5, color:C.text, margin:0, fit:'shrink', valign:'middle' });
band(s,'shuffle_p 检验的是"预测向量是否优于随机"，与 majority 是两条不同的判据——不能互相替代。',6.35);
notes(s,'这一页专门防一个误读：把 p 值当显著性。');

// ============ Slide 8: 复核清单 + 结论 ============
s = pptx.addSlide(); chrome(s,'复核清单与本阶段结论',8);
box(s,0.72,1.82,6.3,2.6,'听众可以自己验','• ortholog-PCA 某方向：读 metrics.json，\n  对照 predictions/ 与 confusion/（18 份全在本地）\n• SAMap 某方向：读 per_cell → 重算 correct/n_q\n• v99：用 SHA d1081cfd 定位 metrics.json；\n  逐细胞载荷在 payloads/（6 份）\n• 排除规则：config/heart-celltype-map-v1.tsv（SHA be985735）\n• 评分器：scripts/ortholog_pca_local_v1.py',{fill:C.blueLight,bodySize:10.5});
box(s,7.28,1.82,5.32,2.6,'四个 SHA 锚点','ortholog-PCA metrics\nb2b3ac6b…c725\n\nSAMap WDL metrics\n3c719399…954f\n\nv99 metrics\nd1081cfd…dc261\n\n冻结映射表 v1\nbe985735…3165',{fill:C.goldLight,bodySize:10.5});
box(s,0.72,4.55,5.8,1.75,'本阶段结论','① 每个百分比都能完整回溯（六段链）\n② 分母效应真实且可量化（729 案例）\n③ 三方法数字不可直接互比（协议三重差异）\n④ 全部仍为 transductive/in-sample',{fill:C.blueLight,bodySize:11});
box(s,6.78,4.55,5.82,1.75,'边界：不能推出什么','• 不能推出"哪个方法普遍更好"\n• 不能把 61.79% 与 48.44% 合并\n• 不能把 shuffle_p 当多数类显著性\n• 不能把日志级数字当文件级证据',{fill:C.roseLight,bodySize:11});
s.addText('下一阶段（汇报 3）：三方法公平比较边界——为什么不能按一个总分排冠军。', { x:0.75,y:6.45,w:11.9,h:0.35,fontFace:F,fontSize:14,bold:true,color:C.title,align:'center',margin:0,fit:'shrink' });
notes(s,'收尾：本阶段没有新数字，只有来源；下一阶段讲协议差异。');

pptx.writeFile({ fileName: out }).then(()=>{ console.log('PPTX_DONE ' + out); });
