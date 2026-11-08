# 在既有索引中登记"实质内容版"交付（就地替换汇报 1 两行，不覆盖历史稿）
import io, os

p = os.path.join('results', 'stage-reports-20261009', 'index.md')
s = io.open(p, encoding='utf-8').read()
lines = s.split('\n')
old15, old16 = lines[14], lines[15]
assert old15.startswith('- 汇报 1 最新交付'), old15
assert old16.startswith('- 汇报 1 内容稿'), old16

new = '\n'.join([
    '- 汇报 1 最新交付（**实质内容版，当前推荐**）：`results/stage-reports-20261012/课题5第01次汇报_实做进度与关键问题_实质版.pptx`（11 页），SHA-256 见 `results/stage-reports-20261012/SHA256SUMS-v3.txt`',
    '- 汇报 1 内容稿（实质内容版）：`docs/reports/report-01-substantive-v3-20261012.md`',
    '- 汇报 1 历史交付（保留，不覆盖）：`results/stage-reports-20261012/课题5第01次汇报_现状与问题定稿_修订版.pptx`（7 页）与 `results/stage-reports-20261009/课题5第01次汇报_现状与问题定稿.pptx`；原内容稿 `docs/reports/report-01-evidence-status-freeze-20261012.md`',
    '- 说明：实质内容版以"我们解决了什么问题"为主线重做，数字仍逐格取自冻结 metrics（30/30 在位校验通过）；本轮未作 Claude 复审',
])
s = s.replace(old15 + '\n' + old16, new)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('INDEX_UPDATED')
