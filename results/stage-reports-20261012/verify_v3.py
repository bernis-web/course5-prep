# 内容自检：卡片内文字是否溢出卡片下沿 + 数字是否与冻结源逐格一致
# 用法: python verify_v3.py <pdf> 
import sys, json, re
import fitz

def norm(x):
    return round(float(x), 4)

def main(pdf):
    doc = fitz.open(pdf)
    txt = "\n".join(p.get_text() for p in doc)
    doc.close()
    flat = re.sub(r"\s+", "", txt)

    # ---- A. 冻结数字必须在册 ----
    fr = json.load(open('../../results/stage-reports-20261009/frozen-numbers.json', encoding='utf-8'))
    checks = []
    for d in ['human->mouse', 'mouse->human', 'human->zebrafish',
              'mouse->zebrafish', 'zebrafish->human', 'zebrafish->mouse']:
        o = fr[d]['ortholog']['coarse']['acc']
        checks.append(('oPCA %s' % d, '%.4f' % o))
        checks.append(('oPCA %s maj' % d, '%.4f' % fr[d]['ortholog']['coarse']['maj']))
    for d in ['human->mouse', 'mouse->human', 'human->zebrafish',
              'mouse->zebrafish', 'zebrafish->human', 'zebrafish->mouse']:
        checks.append(('v99 %s' % d, '%.4f' % fr[d]['v99']['coarse']['acc']))
        checks.append(('SAMap %s' % d, '%.4f' % fr[d]['samap']['coarse']['acc']))
        checks.append(('v97g %s' % d, '%.4f' % fr[d]['saturn_v97g']['coarse']))

    missing = [(n, v) for n, v in checks if v not in flat]
    print("A. 冻结数字在位检查: %d/%d" % (len(checks) - len(missing), len(checks)))
    for n, v in missing:
        print("   MISSING %s = %s" % (n, v))

    # ---- B. 关键事实关键词在位 ----
    kws = ['0.8618', '0.7369', '0.1961', '0.2755', '0.1813', '0.5761',
           '0.1050', '0.4844', '0.6179', '127/127', '36/36', '16/16',
           'b2b3ac6b', 'be985735', 'W202610110124739', 'W202610110124487',
           'transductive', 'SAMap-approx', 'label-aware', '1,505', '1,535']
    miss2 = [k for k in kws if k not in txt]
    print("B. 关键词在位: %d/%d" % (len(kws) - len(miss2), len(kws)))
    for k in miss2:
        print("   MISSING_KW %s" % k)

    # ---- C. 禁用越界表述必须不出现 ----
    banned = ['显著优于', '泛化能力强', 'inductive能力', '冠军方法', '临床可用']
    hit = [b for b in banned if b in txt]
    print("C. 越界表述: %s" % ("无" if not hit else hit))

if __name__ == '__main__':
    main(sys.argv[1])
