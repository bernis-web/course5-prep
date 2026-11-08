const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = '课题5';
pptx.company = '山东第二医科大学';
pptx.subject = '跨物种心脏单细胞整合方法学评估';
pptx.title = '课题5第一阶段成果汇报（老师批语修订版）';
pptx.lang = 'zh-CN';
pptx.theme = { headFontFace: '微软雅黑', bodyFontFace: '微软雅黑', lang: 'zh-CN' };

const W = 13.333, H = 7.5, M = 0.55;
const C = { navy:'002060', blue:'0B5EA8', blueLight:'EAF4FB', gold:'FFC000', goldLight:'FFF2CC', roseLight:'FCE4D6', green:'2E7D32', text:'1F2937', muted:'5B6573', line:'B7C9D6', white:'FFFFFF' };
const F = '微软雅黑';
const logo = 'D:/projects/course5-prep/tmp/ppt-inspect/original_extract/ppt/media/image11.png';
const out = 'D:/projects/course5-prep/results/phase1-revised/课题5第一阶段成果汇报_老师批语修订版.pptx';

function addHeader(slide, title, page, dark) {
  slide.background = { color: dark ? C.navy : C.white };
  if (!dark) slide.addShape(pptx.ShapeType.rect, { x:0, y:0, w:W, h:0.12, fill:{color:C.blue}, line:{color:C.blue} });
  slide.addText(title, { x:M, y:0.28, w:10.7, h:0.45, fontFace:F, fontSize:25, bold:true, color:dark?C.white:C.navy, margin:0 });
  if (!dark) slide.addImage({ path:logo, x:11.62, y:0.22, w:1.05, h:0.48, transparency:4 });
  slide.addText('课题5 第一阶段汇报  |  ' + String(page).padStart(2,'0'), { x:0.55, y:7.16, w:12.2, h:0.18, fontFace:F, fontSize:8.5, color:dark?'AFC8E5':C.muted, align:'right', margin:0 });
}
function box(slide, x,y,w,h, title, body, opts) {
  opts = opts || {};
  slide.addShape(pptx.ShapeType.roundRect, { x:x,y:y,w:w,h:h, rectRadius:0.06, fill:{color:opts.fill||C.blueLight}, line:{color:opts.line||C.line, width:1} });
  slide.addText(title, { x:x+0.16, y:y+0.12, w:w-0.32, h:0.3, fontFace:F, fontSize:opts.titleSize||15, bold:true, color:opts.titleColor||C.navy, margin:0 });
  slide.addText(body, { x:x+0.16, y:y+0.5, w:w-0.32, h:h-0.6, fontFace:F, fontSize:opts.bodySize||11.5, color:opts.bodyColor||C.text, fit:'shrink', valign:'top', margin:0.02, paraSpaceAfterPt:4 });
}
function notes(slide, text) { try { slide.addNotes(text); } catch(e) {} }

let s = pptx.addSlide();
s.background = { color:C.navy };
s.addShape(pptx.ShapeType.rect, { x:0,y:0,w:W,h:0.16,fill:{color:C.gold},line:{color:C.gold} });
s.addImage({ path:logo, x:5.55, y:0.58, w:2.23, h:1.04, transparency:3 });
s.addText('课题5 第一阶段成果汇报', { x:0.8,y:2.15,w:11.75,h:0.72,fontFace:F,fontSize:34,bold:true,color:C.white,align:'center',margin:0 });
s.addText('跨物种心脏单细胞整合：把“表格数字”变成可解释、可复核的证据', { x:1.1,y:3.07,w:11.1,h:0.55,fontFace:F,fontSize:19,color:'D7E8F8',align:'center',margin:0,fit:'shrink' });
s.addText('本次修订重点：数据来源 · 评分公式 · 方法适用边界 · 后续执行门', { x:1.0,y:4.03,w:11.3,h:0.45,fontFace:F,fontSize:15,color:'B7D4EE',align:'center',margin:0 });
s.addText('人 1,528  |  鼠 1,535  |  斑马鱼 1,543 细胞', { x:1.0,y:5.58,w:11.3,h:0.35,fontFace:F,fontSize:16,bold:true,color:C.gold,align:'center',margin:0 });
s.addText('2026年9月30日', { x:0.7,y:6.62,w:11.9,h:0.3,fontFace:F,fontSize:12,color:'AFC8E5',align:'center',margin:0 });
notes(s,'修订依据：老师录音转写“新录音 2.txt”、现有第一阶段 PPT、v74 证据文档和方法证据文档。');

s = pptx.addSlide(); addHeader(s,'老师意见转化为三个必须回答的问题',2);
box(s,0.7,1.35,3.85,3.8,'1. 数字怎么来的？','从三物种原始 AnnData、冻结标签映射、表示层、邻域预测，到分母、coverage 和置换检验，必须能逐层追溯。',{fill:C.blueLight,bodySize:13});
box(s,4.75,1.35,3.85,3.8,'2. 为什么有含金量？','不是“跑出一个百分比”，而是在同一数据、同一方向、同一评分器下，同时给出 majority 基线、随机置换和逐细胞混淆矩阵。',{fill:C.goldLight,bodySize:13});
box(s,8.8,1.35,3.85,3.8,'3. 谁更好、为什么？','论文方法与本项目方法服务的问题不同。要比较信号来源、可解释性、算力代价和泛化协议，不能脱离协议直接排绝对名次。',{fill:C.roseLight,bodySize:13});
s.addText('因此，本次 PPT 不再只展示“结果表”，而是把每个数字放回完整的实验链条。', { x:0.85,y:5.7,w:11.7,h:0.55,fontFace:F,fontSize:18,bold:true,color:C.navy,align:'center',margin:0,fit:'shrink' });
notes(s,'老师批语的核心不是继续堆更多结果，而是解释比较逻辑、数据来源和方法学价值。');

s = pptx.addSlide(); addHeader(s,'数据与统一评估协议：三物种、六方向、一把尺子',3);
const species = [['人类','1,528','公开心脏单细胞数据'],['小鼠','1,535','公开心脏单细胞数据'],['斑马鱼','1,543','公开心脏单细胞数据']];
species.forEach((a,i)=>box(s,0.72+i*4.15,1.15,3.75,1.35,a[0],a[1]+' 细胞\n'+a[2],{fill:i===0?'E8F1FB':i===1?'EDF6EF':'FFF7E0',bodySize:13}));
box(s,0.72,2.92,5.8,2.35,'固定输入与标签','• 真实 ESM2 蛋白嵌入 / macrogenes 表示层\n• mapping v1：38 行 coarse/fine，SHA-256 已冻结\n• 74 个 unmapped 细胞在 v97g coarse/fine 中从训练与分母双向排除\n• 六个有向迁移：人↔鼠、人↔斑马鱼、鼠↔斑马鱼',{fill:C.blueLight,bodySize:12.2});
box(s,6.75,2.92,5.85,2.35,'固定评分器','• cosine 距离 + KNN15，倒距离加权\n• 逐细胞预测 → accuracy / coverage / confusion matrix\n• majority 常数预测作为强基线\n• 200 次置换检验；shuffle_p 作为“超出随机”的证据\n• 训练/评估角色和协议标签写入 manifest',{fill:C.goldLight,bodySize:12.2});
s.addText('主张边界：SATURN v97g 是 transductive / in-sample formal reassessment candidate，不是 held-out 或 inductive 泛化成绩。', { x:0.8,y:5.78,w:11.85,h:0.55,fontFace:F,fontSize:16,bold:true,color:'8A4B00',align:'center',margin:0,fit:'shrink' });
notes(s,'关键来源：docs/transductive-formal-v74-evidence-20260928.md；mapping SHA=BE9857354778535B76D1884D004C54691DC5FF2DAA7B098D71DC719DAF583165。');

s = pptx.addSlide(); addHeader(s,'一个百分比是怎样得到的：从细胞到表格单元格',4);
const steps = [['① 输入','目标物种 query 细胞 + 参考物种 reference 细胞；先固定物种前缀条码'],['② 表示','读取指定表示层（SATURN 为 obsm["macrogenes"]；PCA 为 1:1 ortholog-PCA50）'],['③ 邻域','对每个 query 找 reference 的 KNN15，使用 cosine 与倒距离加权'],['④ 预测','按冻结 mapping v1 聚合邻域标签，得到逐细胞 coarse/fine 预测'],['⑤ 分母','只对 eligible query 计算；unmapped 排除数单列，coverage=eligible/原 query'],['⑥ 统计','accuracy=正确预测数/eligible 数；同时报告 majority、置换 p 和混淆矩阵']];
steps.forEach((a,i)=>{ const col=i%3,row=Math.floor(i/3); box(s,0.72+col*4.15,1.2+row*2.25,3.78,1.72,a[0],a[1],{fill:row===0?C.blueLight:C.goldLight,bodySize:11.3,titleSize:14}); });
s.addText('示例：人→鼠 SATURN coarse = 61.79% = 合规 eligible query 中预测正确的细胞数 ÷ eligible query 总数；coverage=0.9805。', { x:0.8,y:5.95,w:11.85,h:0.48,fontFace:F,fontSize:16,bold:true,color:C.navy,align:'center',margin:0,fit:'shrink' });
notes(s,'这页专门回应老师“表格里的数据怎么来的”。具体输入哈希、命令、逐细胞预测和混淆矩阵需要以本地回收验收后的 manifest 为最终依据。');

s = pptx.addSlide(); addHeader(s,'论文方法与本项目方法：比较“适用问题”，而不是绝对优劣',5);
const methodRows = [['SATURN','蛋白语言模型 → macrogenes → 联合训练','跨物种共享表示；测试蛋白同源信息是否带来增益','训练与评估协议敏感；容量、seed、留出设计影响大；当前 v97g 为 transductive'],['SAMap','同源基因图 + 联合流形','寻找跨物种细胞对应和局部对齐结构','内存和参数敏感；当前合规探索结果接近随机，v98 尚需修正复跑'],['ortholog-PCA','1:1 直系同源基因 + PCA50','回答“同源表达本身能做到什么”','不是整合模型；无法提供蛋白嵌入或非线性对齐能力']];
s.addShape(pptx.ShapeType.rect,{x:0.62,y:1.2,w:12.1,h:0.52,fill:{color:C.navy},line:{color:C.navy}});
['方法','核心信号','擅长回答','主要限制'].forEach((t,i)=>{const xs=[0.76,2.21,5.26,8.81]; const ws=[1.25,2.85,3.35,3.85]; s.addText(t,{x:xs[i],y:1.3,w:ws[i],h:0.22,fontFace:F,fontSize:11,bold:true,color:C.white,margin:0});});
s.addTable(methodRows,{x:0.62,y:1.72,w:12.1,h:4.03,border:{type:'solid',color:C.line,width:1},fill:C.white,color:C.text,fontFace:F,fontSize:11,margin:0.08,autoFit:false,rowH:[1.25,1.25,1.25],colW:[1.45,3.05,3.55,4.05],valign:'mid'});
s.addText('结论：正交基线提供可解释“下限/参照”；SATURN 测试蛋白同源信息；SAMap 测试图结构对齐。三者不能只用一个总分替代。', { x:0.8,y:6.1,w:11.85,h:0.42,fontFace:F,fontSize:14.5,bold:true,color:C.navy,align:'center',margin:0,fit:'shrink' });
notes(s,'论文方法证据见 docs/paper-method-evidence-20260924.md；方法到评估矩阵见 docs/method-to-evaluation-matrix-20260926.md。');

s = pptx.addSlide(); addHeader(s,'核心数字：六方向 × 三方法（coarse，证据等级已标注）',6);
const rows=[['人→鼠','80.9%*','61.79%','1.95%†','48.17%'],['鼠→人','38.3%*','25.39%','19.11%†','31.15%'],['人→斑马鱼','40.5%*','18.35%','0%†','39.76%'],['鼠→斑马鱼','22.4%*','30.09%','38.56%†','39.76%'],['斑马鱼→人','11.9%*','24.74%','1.96%†','31.15%'],['斑马鱼→鼠','79.5%*','46.51%','1.95%†','48.17%']];
s.addShape(pptx.ShapeType.rect,{x:0.75,y:1.15,w:11.85,h:0.62,fill:{color:C.navy},line:{color:C.navy}});
['迁移方向','ortholog-PCA\n阶段草表','SATURN v97g\ntransductive candidate','SAMap\n探索性候选','majority'].forEach((t,i)=>{const xs=[0.87,2.97,5.22,7.87,10.47]; const ws=[1.85,2.05,2.35,2.25,1.95]; s.addText(t,{x:xs[i],y:1.28,w:ws[i],h:0.3,fontFace:F,fontSize:11,bold:true,color:C.white,align:'center',valign:'mid',margin:0,fit:'shrink'});});
s.addTable(rows,{x:0.75,y:1.77,w:11.85,h:3.73,border:{type:'solid',color:C.line,width:1},fill:C.white,color:C.text,fontFace:F,fontSize:13,margin:0.09,autoFit:false,rowH:[0.62,0.62,0.62,0.62,0.62,0.62],colW:[2.1,2.25,2.65,2.6,2.25],valign:'mid',align:'center'});
s.addText('* ortholog-PCA 数字来自早期阶段草表，统一评分器复算后再冻结；† SAMap 为合规探索性对照，不进入正式 benchmark 排名。SATURN 数字为 v97g coarse，coverage：0.9805/1/0.9715/0.9715/1/0.9805。', { x:0.82,y:5.78,w:11.75,h:0.6,fontFace:F,fontSize:11.5,color:C.muted,margin:0,fit:'shrink' });
notes(s,'PPT 明确区分正式候选、阶段草表和探索性候选，避免把不同证据等级混成一个排名。');

s = pptx.addSlide(); addHeader(s,'为什么这张表有含金量：数字背后有五道“防误读门”',7);
const gates=[['同一把尺子','六个方向都用同一评分器、同一 mapping、同一分母规则，避免方法各报各的指标。'],['方向性','人→鼠与鼠→人分开报告；不能用一个平均数掩盖物种方向不对称。'],['强基线','majority 告诉我们模型是否真的超过“全猜多数类”；ortholog-PCA 告诉我们同源表达本身能做到什么。'],['随机对照','200 次置换检验和 shuffle_p 把“看起来有信号”与“超出随机”分开。'],['可追溯','逐细胞预测、混淆矩阵、哈希、命令和环境文件让别人能复核，而不是只看一张截图。']];
gates.forEach((a,i)=>{const y=1.18+i*1.04; s.addShape(pptx.ShapeType.roundRect,{x:0.82,y:y,w:1.25,h:0.68,rectRadius:0.04,fill:{color:i<3?C.navy:C.blue},line:{color:i<3?C.navy:C.blue}}); s.addText(String(i+1),{x:0.82,y:y,w:1.25,h:0.68,fontFace:F,fontSize:22,bold:true,color:C.white,align:'center',valign:'mid',margin:0}); s.addText(a[0],{x:2.35,y:y+0.04,w:2.1,h:0.28,fontFace:F,fontSize:16,bold:true,color:C.navy,margin:0}); s.addText(a[1],{x:4.25,y:y+0.01,w:8.15,h:0.52,fontFace:F,fontSize:12.8,color:C.text,fit:'shrink',margin:0});});
s.addText('即使结果不理想，也能判断“是模型没学到，还是协议/标签/算力限制了结果”。这就是方法学价值。', { x:0.82,y:6.42,w:11.7,h:0.35,fontFace:F,fontSize:15,bold:true,color:'8A4B00',align:'center',margin:0,fit:'shrink' });
notes(s,'这页用来回应老师所说的“表格含金量高但没有体现”。重点是把可审计性、基线和失败信息说清楚。');

s = pptx.addSlide(); addHeader(s,'SATURN：有真实信号，但当前结果不能被解释成泛化性能',8);
box(s,0.72,1.15,5.8,4.65,'目前能支持的判断','• ESM2 / macrogene 表示层可携带跨物种同源信息\n• 人→鼠 coarse v97g = 61.79%，高于 majority 48.17%\n• 16→1,000 macrogenes 的容量效应与消融结果说明容量是关键变量\n• seed、物种距离和标签协议会明显改变结果\n• 因此：方法有信号，但信号依赖协议与容量',{fill:C.blueLight,bodySize:13});
box(s,6.75,1.15,5.85,4.65,'目前不能支持的判断','• 不能称为 held-out benchmark\n• 不能把 67.4% v72-era 数字当正式主结果\n• 不能用单一方向最高分代表普遍跨物种泛化\n• 不能把 v99 远程产物在本地未回收前写成 provenance complete\n• inductive 留出重训仍是后续独立门',{fill:C.roseLight,bodySize:13});
s.addText('推荐措辞：transductive / in-sample formal reassessment candidate（管线验证与方法学探索）', { x:0.85,y:6.22,w:11.65,h:0.36,fontFace:F,fontSize:15,bold:true,color:C.navy,align:'center',margin:0,fit:'shrink' });
notes(s,'transductive 边界来自 v71/v72 训练与评估使用同一 4,606 细胞集合，且目标标签参与训练路径。');

s = pptx.addSlide(); addHeader(s,'SAMap 与 ortholog-PCA：一个测对齐，一个测信号下限',9);
box(s,0.72,1.15,5.8,4.55,'SAMap 当前定位','• 目标：同源图联合嵌入是否形成跨物种细胞对齐\n• 18 格合规探索性结果均≤随机或等于 majority，shuffle_p≥0.98\n• 这不是“工具无效”的普遍结论，而是本数据规模、标签协议和当前运行设置下未观察到稳定信号\n• v98 仍需 umap=False、ncpus=1、前缀冲突修复后复跑',{fill:C.goldLight,bodySize:12.8});
box(s,6.75,1.15,5.85,4.55,'ortholog-PCA 当前定位','• 目标：不做整合时，1:1 直系同源表达本身有多强\n• 参数少、可解释、算力低，是必要强基线\n• 早期六方向数字有启发性，但统一评分器复算前只称“阶段草表”\n• 若 PCA 已很强，复杂模型的增益必须相对它解释，而不是只和 majority 比',{fill:C.blueLight,bodySize:12.8});
s.addText('因此比较问题是：复杂方法是否在相同协议下，稳定、可复现地超过“同源信号基线”？', { x:0.85,y:6.18,w:11.65,h:0.42,fontFace:F,fontSize:15,bold:true,color:C.navy,align:'center',margin:0,fit:'shrink' });
notes(s,'SAMap 证据见 docs/transductive-formal-v74-evidence-20260928.md 和 docs/local-samap3-readonly-audit-20260927.md。');

s = pptx.addSlide(); addHeader(s,'阶段一结束时，我们能回答什么、还不能回答什么',10);
box(s,0.72,1.15,5.8,4.7,'能回答','✓ 已把三种方法放进同一套可审计协议\n✓ 已识别标签、容量、seed、物种距离和算力是关键变量\n✓ 已看到同源表达基线在部分方向很强\n✓ 已确认 SATURN 有真实但不稳定的信号\n✓ 已形成可交给 Flash 执行的验收门和证据链',{fill:'EDF6EF',line:'A9D3AF',titleColor:C.green,bodySize:13});
box(s,6.75,1.15,5.85,4.7,'还不能回答','? 哪个方法在严格 inductive 留出下普遍最好\n? SAMap v98 修复后是否改变当前探索性结论\n? reviewer 是否确认 4 个低置信映射\n? v99 远程 provenance 是否已完整回收到本地并独立验收\n? 单核数据、更多物种和空间信息是否改变结论',{fill:C.roseLight,bodySize:13});
s.addText('阶段一的成果不是“最终冠军”，而是把后续比较变成有协议、有证据等级、有停止条件的实验。', { x:0.85,y:6.25,w:11.65,h:0.4,fontFace:F,fontSize:15,bold:true,color:C.navy,align:'center',margin:0,fit:'shrink' });
notes(s,'把未完成项显式列出，避免汇报时把候选证据包装成正式结论。');

s = pptx.addSlide(); addHeader(s,'交给 Flash 的后续执行顺序：先验收，再补跑，最后冻结',11);
const plan=[['Wave 0','只读核对证据：confirmed / candidate / blocked 矩阵；不提交任务'],['Wave 1','回收 v99：manifest、command、environment、sha256、18 组预测/混淆矩阵，做本地 hash 与抽样复核'],['Wave 2','SAMap v98：修正前缀、ncpus=1、umap=False；只允许一次任务，失败即停并反馈'],['Wave 3','ortholog-PCA：用统一评分器复算六方向，锁定表示层和分母'],['Wave 4','mapping reviewer 签认；无签名不得升级正式排名'],['Wave 5','用户批准后做最小 inductive 留出：留一物种/分层留出，预算和停止条件先写入 manifest'],['Wave 6','统一比较矩阵冻结，生成 Word 报告与最终图表']];
plan.forEach((a,i)=>{const y=1.02+i*0.78; s.addShape(pptx.ShapeType.roundRect,{x:0.72,y:y,w:1.22,h:0.5,rectRadius:0.04,fill:{color:i<2?C.navy:C.blue},line:{color:i<2?C.navy:C.blue}}); s.addText(a[0],{x:0.72,y:y,w:1.22,h:0.5,fontFace:F,fontSize:12.5,bold:true,color:C.white,align:'center',valign:'mid',margin:0}); s.addText(a[1],{x:2.15,y:y+0.04,w:10.35,h:0.38,fontFace:F,fontSize:12.3,color:C.text,fit:'shrink',margin:0});});
s.addText('执行纪律：一次性检查，不对已结束任务死循环轮询；每波按“做了什么—证据—测试—未完成—下一步请求”停止反馈。', { x:0.8,y:6.63,w:11.75,h:0.3,fontFace:F,fontSize:12.5,bold:true,color:'8A4B00',align:'center',margin:0,fit:'shrink' });
notes(s,'Flash 第一条可直接复制的指令见配套计划文档。DCS/GPU 只在对应波次、用户批准后执行。');

s = pptx.addSlide();
s.background = { color:C.navy };
s.addShape(pptx.ShapeType.rect,{x:0,y:0,w:W,h:0.16,fill:{color:C.gold},line:{color:C.gold}});
s.addText('阶段一结论', { x:0.8,y:1.18,w:11.75,h:0.5,fontFace:F,fontSize:22,color:'B7D4EE',align:'center',margin:0 });
s.addText('我们已经把“跨物种整合谁更好”\n改造成了一个可审计、可复算、可继续推进的问题。', { x:1.1,y:2.15,w:11.1,h:1.45,fontFace:F,fontSize:28,bold:true,color:C.white,align:'center',valign:'mid',margin:0,fit:'shrink' });
s.addText('当前最重要的不是再堆一个高分，而是：\n把 provenance、SAMap 修复、PCA 复算和 inductive 留出按门推进。', { x:1.2,y:4.15,w:10.9,h:0.95,fontFace:F,fontSize:18,color:'D7E8F8',align:'center',margin:0,fit:'shrink' });
s.addText('谢谢', { x:0.8,y:6.25,w:11.75,h:0.38,fontFace:F,fontSize:18,bold:true,color:C.gold,align:'center',margin:0 });
notes(s,'收尾时强调：阶段一完成的是可信比较框架和候选结果，不是无条件的最终排名。');

pptx.writeFile({ fileName: out }).then(function(){ console.log('PPTX_DONE ' + out); }).catch(function(err){ console.error(err); process.exitCode=1; });
