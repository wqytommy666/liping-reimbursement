#!/usr/bin/env python3
"""Render an agent-reviewed task list and assemble A4 print copies; no policy inference."""
import argparse
import hashlib
import io
import json
import os
import sys
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

try:
    from PIL import Image, ImageOps
    from pypdf import PdfReader, PdfWriter, PageObject, Transformation
    from reportlab.lib import colors
except ModuleNotFoundError:
    _FALLBACK_PY = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
    if _FALLBACK_PY.is_file() and Path(sys.executable).resolve() != _FALLBACK_PY.resolve() and not os.environ.get('_AVC2_REEXEC'):
        os.environ['_AVC2_REEXEC'] = '1'
        os.execv(str(_FALLBACK_PY), [str(_FALLBACK_PY), *sys.argv])
    raise
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer

STATES = {
    'received': '已收到', 'generated': '已自动生成',
    'missing': '需要你补充', 'pending': '待确认', 'na': '不适用',
}
CATEGORIES = ['conference', 'transport', 'lodging', 'other', 'payment']
CATEGORY_LABELS = ['会议通知', '交通票据', '住宿票据', '其他票据', '支付记录']
PALETTE = {'received': '#16745C', 'generated': '#255FC2',
           'missing': '#B35813', 'pending': '#B35813', 'na': '#657185'}


def font_setup(explicit=None):
    candidates = [explicit] if explicit else [
        '/System/Library/Fonts/Supplemental/Songti.ttc',
        'C:/Windows/Fonts/simsun.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    ]
    for item in candidates:
        if item and Path(item).is_file():
            pdfmetrics.registerFont(TTFont('CJK', item, subfontIndex=0))
            return
    raise ValueError('需要可嵌入中文字体，请用 --font 指定支持中文的 TTF/TTC 文件。')


def validate(case, base):
    if not case.get('title') or not isinstance(case.get('tasks'), list):
        raise ValueError('manifest 需要 title 和 tasks 列表。')
    ids = set()
    for task in case['tasks']:
        if not task.get('id') or task['id'] in ids:
            raise ValueError('任务编号缺失或重复。')
        ids.add(task['id'])
        if task.get('status') not in STATES or not task.get('name'):
            raise ValueError(f'任务 {task["id"]} 状态或名称无效。')
        if task['status'] in ('missing', 'pending') and not task.get('action'):
            raise ValueError(f'任务 {task["id"]} 需要具体补充/确认动作。')
        if task['status'] == 'na' and not task.get('note'):
            raise ValueError('不适用项需要说明原因。')
        if task['status'] in ('received', 'generated') and not task.get('evidence'):
            raise ValueError(f'任务 {task["id"]} 需要证据/成果引用。')
    docids = set()
    for doc in case.get('documents', []):
        if not doc.get('id') or doc['id'] in docids:
            raise ValueError('入册材料编号缺失或重复。')
        docids.add(doc['id'])
        if doc.get('category') not in CATEGORIES:
            raise ValueError(f'材料 {doc["id"]} 分类无效。')
        path = (base / doc['path']).resolve()
        if not path.is_file():
            raise ValueError(f'材料不存在：{path}')
        if path.suffix.lower() not in ('.pdf', '.png', '.jpg', '.jpeg', '.webp'):
            raise ValueError(f'先将此格式转为PDF/图片再成册：{path.name}')
        if doc['category'] == 'payment' and not doc.get('label'):
            raise ValueError(f'支付材料 {doc["id"]} 需要 label 写明对应票据。')


def p(text, style):
    escaped = escape(str(text or '')).replace('²', '<super>2</super>').replace('\n', '<br/>')
    return Paragraph(escaped, style)


def render_list(case, output):
    style = ParagraphStyle('body', fontName='CJK', fontSize=10, leading=15,
                           textColor=colors.HexColor('#233249'), wordWrap='CJK')
    small = ParagraphStyle('small', parent=style, fontSize=9, leading=13)
    title = ParagraphStyle('title', parent=style, fontSize=21, leading=28, spaceAfter=9)
    muted = ParagraphStyle('muted', parent=small, textColor=colors.HexColor('#657185'))
    width = A4[0] - 84
    story = [p('LIPING REIMBURSEMENT · AVC² 团队助理丽萍姐', muted), Spacer(1, 8),
             p(case['title'], title)]
    if case.get('example'):
        story += [p('虚构示例 · 用于展示使用流程，不是实际报销材料', muted), Spacer(1, 12)]
    counts = Counter(t['status'] for t in case['tasks'])
    summary = Table([[
        p(f'{counts["received"]} 组材料已收到', style),
        p(f'{counts["generated"]} 项我已帮你生成', style),
        p(f'{counts["missing"] + counts["pending"]} 项还需要你提供', style),
    ]], colWidths=[width / 3] * 3)
    summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#E9F5EF')),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#EDF3FF')),
        ('BACKGROUND', (2, 0), (2, 0), colors.HexColor('#FFF1E4')),
        ('TOPPADDING', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
    ]))
    story += [summary, Spacer(1, 16)]
    if case.get('itinerary'):
        story += [p(case['itinerary'], style), Spacer(1, 8)]
    if case.get('note'):
        story += [p(case['note'], muted), Spacer(1, 12)]
    rows = [[p(x, small) for x in ('编号', '材料 / 整理成果', '状态', '说明与下一步')]]
    for task in case['tasks']:
        status_style = ParagraphStyle('state', parent=small,
                                     textColor=colors.HexColor(PALETTE[task['status']]))
        detail = task.get('action') or task.get('note') or task.get('evidence', '')
        rows.append([p(task['id'], small), p(task['name'], small),
                     p(STATES[task['status']], status_style), p(detail, small)])
    table = Table(rows, colWidths=[36, 113, 77, width - 226], repeatRows=1, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E8EDF3')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.HexColor('#CBD5E1')),
        ('LINEBELOW', (0, 1), (-1, -1), 0.3, colors.HexColor('#E3E8EF')),
    ]))
    story += [table, Spacer(1, 15), p(case.get('next_step') or
              '补充后更新表格、金额和材料册。原始材料与整理成果分开计数，材料数量随差旅情况变化。', muted)]

    def footer(c, doc):
        c.setStrokeColor(colors.HexColor('#DDE3EB'))
        c.line(42, 38, A4[0] - 42, 38)
        c.setFont('CJK', 8)
        c.setFillColor(colors.HexColor('#657185'))
        prefix = '丽萍姐报账 · AVC'
        c.drawString(42, 24, prefix)
        w_prefix = c.stringWidth(prefix, 'CJK', 8)
        c.setFont('CJK', 5.5)
        c.drawString(42 + w_prefix + 0.5, 27.5, '2')
        w_sup = c.stringWidth('2', 'CJK', 5.5)
        c.setFont('CJK', 8)
        c.drawString(42 + w_prefix + w_sup + 1, 24, ' 团队助理' + (' / 示例' if case.get('example') else ''))
        c.drawRightString(A4[0] - 42, 24, str(doc.page))

    SimpleDocTemplate(str(output), pagesize=A4, leftMargin=42, rightMargin=42,
                      topMargin=38, bottomMargin=52, title=case['title'],
                      author='丽萍姐报账 · AVC² 团队助理').build(
                          story, onFirstPage=footer, onLaterPages=footer)


def markdown_list(case):
    def cell(s):
        return str(s or '').replace('|', '\\|').replace('\n', '<br>')
    counts = Counter(t['status'] for t in case['tasks'])
    lines = [f'# {case["title"]}', '']
    if case.get('example'):
        lines += ['虚构示例，不是实际报销材料。', '']
    lines += [case.get('itinerary', ''), '',
              f'已收到 {counts["received"]} 组，已自动生成 {counts["generated"]} 项，'
              f'需补充/确认 {counts["missing"] + counts["pending"]} 项。', '',
              '| 编号 | 项目 | 状态 | 依据/已有成果 | 下一步 |',
              '| --- | --- | --- | --- | --- |']
    for t in case['tasks']:
        lines.append('| ' + ' | '.join(cell(x) for x in [t['id'], t['name'],
                     STATES[t['status']], t.get('evidence') or t.get('note'),
                     t.get('action') or t.get('note')]) + ' |')
    lines += ['', case.get('note', ''), '', case.get('next_step', '')]
    return '\n'.join(lines) + '\n'


def annotation(label):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    text = p(label, ParagraphStyle('label', fontName='CJK', fontSize=8, leading=11))
    _, height = text.wrap(A4[0] - 48, 36)
    if height > 36:
        raise ValueError('支付页对应说明过长；用简短票据ID，详细关系写入明细表。')
    text.drawOn(c, 24, 12)
    c.save()
    return PdfReader(buffer).pages[0]


def a4_page(source, label=''):
    holder = PdfWriter()
    source = holder.add_page(source)
    source.transfer_rotation_to_content()
    box = source.cropbox
    sw, sh = float(box.width), float(box.height)
    if sw <= 0 or sh <= 0:
        raise ValueError('PDF页面尺寸异常。')
    bottom = 54 if label else 20
    available_w, available_h = A4[0] - 40, A4[1] - 20 - bottom
    scale = min(available_w / sw, available_h / sh)
    tx = 20 + (available_w - sw * scale) / 2 - float(box.left) * scale
    ty = bottom + (available_h - sh * scale) / 2 - float(box.bottom) * scale
    result = holder.add_blank_page(width=A4[0], height=A4[1])
    result.merge_transformed_page(source, Transformation((scale, 0, 0, scale, tx, ty)))
    if label:
        result.merge_page(annotation(label))
    return result


def image_reader(path):
    with Image.open(path) as img:
        if getattr(img, 'n_frames', 1) > 1:
            raise ValueError('多帧图片请先逐帧转PDF，避免漏页。')
        img = ImageOps.exif_transpose(img).convert('RGB')
        data = io.BytesIO()
        c = canvas.Canvas(data, pagesize=img.size)
        from reportlab.lib.utils import ImageReader
        c.drawImage(ImageReader(img), 0, 0, width=img.width, height=img.height)
        c.save()
    return PdfReader(data)


def assemble(case, base, output):
    writer = PdfWriter()
    indexes, used_pages = [], set()
    documents = sorted(case.get('documents', []), key=lambda d: CATEGORIES.index(d['category']))
    for doc in documents:
        path = (base / doc['path']).resolve()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if path.suffix.lower() == '.pdf':
            reader = PdfReader(path)
            if reader.is_encrypted:
                raise ValueError(f'加密PDF须由用户提供可读取版本：{path.name}')
            if reader.get_fields():
                raise ValueError(f'交互表单先导出可视打印副本，保留原件：{path.name}')
        else:
            reader = image_reader(path)
        pages = doc.get('pages', list(range(1, len(reader.pages) + 1)))
        if not pages:
            raise ValueError(f'材料 {doc["id"]} 未选择页面。')
        start = len(writer.pages) + 1
        for number in pages:
            if type(number) is not int or number < 1 or number > len(reader.pages):
                raise ValueError(f'材料 {doc["id"]} 页码超范围。')
            key = (digest, number)
            if key in used_pages:
                raise ValueError(f'同一内容页重复入册：{doc["id"]} 第{number}页。请去重或将支付页标注全部对应票据。')
            used_pages.add(key)
            label = doc.get('label', '') if doc['category'] == 'payment' else ''
            writer.add_page(a4_page(reader.pages[number - 1], label))
        writer.add_outline_item(doc.get('title', doc['id']), start - 1)
        indexes.append({'id': doc['id'], 'category': doc['category'], 'file': path.name,
                        'sha256': digest, 'source_pages': pages,
                        'packet_start': start, 'packet_end': len(writer.pages)})
    if writer.pages:
        writer.add_metadata({'/Title': case['title'], '/Author': 'AVC2 Reimbursement Assistant'})
        with output.open('wb') as f:
            writer.write(f)
        actual = len(PdfReader(output).pages)
        if actual != sum(len(row['source_pages']) for row in indexes):
            raise ValueError('输出页数核对失败。')
    return indexes


def build(manifest, output, font=None):
    manifest, output = Path(manifest).resolve(), Path(output).resolve()
    case = json.loads(manifest.read_text(encoding='utf-8'))
    validate(case, manifest.parent)
    if output.exists() and any(output.iterdir()):
        raise ValueError('输出目录非空，请使用新的版本目录以保留原件与旧结果。')
    font_setup(font)
    output.mkdir(parents=True, exist_ok=True)
    unresolved = any(t['status'] in ('missing', 'pending') for t in case['tasks'])
    # This flag records the agent's review; it does not establish financial approval.
    draft = unresolved or not case.get('review_completed') or case.get('example', False)
    packet = output / ('报销材料册-待补草稿.pdf' if draft else '报销材料册-待助理初审.pdf')
    indexes = assemble(case, manifest.parent, packet)
    render_list(case, output / '材料核对清单.pdf')
    (output / '材料核对清单.md').write_text(markdown_list(case), encoding='utf-8')
    (output / '材料索引.json').write_text(json.dumps(indexes, ensure_ascii=False, indent=2), encoding='utf-8')
    return {'output': str(output), 'list_pdf': str(output / '材料核对清单.pdf'),
            'packet_pdf': str(packet) if indexes else None,
            'packet_pages': sum(len(x['source_pages']) for x in indexes), 'draft': draft}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', help='JSON manifest prepared after reading actual materials')
    parser.add_argument('--output', required=True, help='New or empty version directory')
    parser.add_argument('--font', help='Embeddable CJK TTF/TTC font')
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.manifest, args.output, args.font), ensure_ascii=False))
    except (ValueError, KeyError, OSError) as exc:
        print(f'无法成册：{exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
