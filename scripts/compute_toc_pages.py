#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
两遍排版里的第二遍：算出每个标题落在 PDF 第几页，写 _toc_pages.json。
跳过封面和目录页（目录页含点线引导符 ......，正文页不会有）。
"""
import os, re, json, subprocess, sys
from docx import Document

BASE = r"D:\projects\course5-prep"
DOCX = os.path.join(BASE, "deliverables", "课题5-组员入门手册-20261104.docx")
SRC  = os.path.join(BASE, "docs", "team-handbook")
CACHE = os.path.join(SRC, "_toc_pages.json")
TMP  = os.path.join(BASE, "deliverables", "_hbcheck")

def norm(s):
    return re.sub(r'\s+', '', s or '')

def key_of(title):
    """剥掉「第 N 章」「Q8」「5.3」这类编号前缀，只留标题文字。
    PDF 提取时编号常被排到别处，整串匹配会失败。"""
    t = re.sub(r'^第\s*\d+\s*章[　\s]*', '', title)
    t = re.sub(r'^Q\s*\d+[　\s]*', '', t)
    t = re.sub(r'^\d+\.\d+[　\s]*', '', t)
    t = re.sub(r'^第\s*\d+\s*片[　\s]*', '', t)
    return norm(t)

def main():
    doc = Document(DOCX)
    heads = []
    for p in doc.paragraphs:
        sn = p.style.name if p.style is not None else ''
        if sn in ('Heading 1', 'Heading 2'):
            t = p.text.strip()
            if t: heads.append((sn, t))
    print('标题数:', len(heads))

    os.makedirs(TMP, exist_ok=True)
    so = r"C:\Program Files\LibreOffice\program\soffice.exe"
    profile = 'file:///' + os.path.join(os.environ['TEMP'], 'lo_toc').replace('\\', '/')
    subprocess.run([so, '--headless', '-env:UserInstallation=' + profile,
                    '--convert-to', 'pdf', '--outdir', TMP, DOCX],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    pdfs = [f for f in os.listdir(TMP) if f.lower().endswith('.pdf')]
    if not pdfs:
        print('PDF 没生成'); sys.exit(1)
    pdf = os.path.join(TMP, pdfs[0])

    info = subprocess.run(['pdfinfo', pdf], capture_output=True, timeout=60)
    m = re.search(rb'Pages:\s+(\d+)', info.stdout)
    total = int(m.group(1)) if m else 0
    print('PDF 页数:', total)

    pages = {}
    for pno in range(1, total + 1):
        r = subprocess.run(['pdftotext', '-f', str(pno), '-l', str(pno), pdf, '-'],
                           capture_output=True, timeout=60)
        txt = r.stdout.decode('utf-8', 'ignore')
        if pno == 1 or '......' in txt:   # 封面 / 目录页，跳过
            continue
        pages[pno] = norm(txt)

    result = {}
    last = 0
    for style, title in heads:
        k = key_of(title)
        if not k:
            continue
        hit = None
        # 标题在文档里是顺序出现的 → 页码必须单调不减。
        # 这样「这章记住三句话」这种重名标题不会匹配到前面那一章。
        for probe in (k, k[:14], k[:10]):
            if len(probe) < 4:
                continue
            for pno in sorted(p for p in pages if p >= last):
                if probe in pages[pno]:
                    hit = pno; break
            if hit: break
        if hit:
            result[title] = hit
            last = hit

    with open(CACHE, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)

    miss = [t for _, t in heads if t not in result]
    print('已定位 %d / %d' % (len(result), len(heads)))
    if miss:
        print('没定位到:')
        for t in miss[:10]: print('  -', t)

if __name__ == '__main__':
    main()
