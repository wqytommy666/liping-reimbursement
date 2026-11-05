"""Tests use synthetic pages only; they do not certify policy compliance."""
import copy
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from PIL import Image
except ModuleNotFoundError:
    _FALLBACK_PY = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
    if _FALLBACK_PY.is_file() and Path(sys.executable).resolve() != _FALLBACK_PY.resolve() and not os.environ.get('_AVC2_REEXEC'):
        os.environ['_AVC2_REEXEC'] = '1'
        os.execv(str(_FALLBACK_PY), [str(_FALLBACK_PY), *sys.argv])
    raise

from build_packet import build, validate


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='avc2-test-')
        self.root = Path(self.tmp.name)
        for name in ['CONFERENCE', 'TRANSPORT', 'LODGING', 'OTHER', 'PAYMENT']:
            c = canvas.Canvas(str(self.root / f'{name}.pdf'), pagesize=(600, 400))
            c.drawString(30, 320, name + ' SYNTHETIC TEST PAGE')
            c.save()
        writer = PdfWriter()
        writer.add_page(PdfReader(self.root / 'OTHER.pdf').pages[0]).rotate(90)
        with (self.root / 'ROTATED.pdf').open('wb') as f:
            writer.write(f)
        self.case = {
            'title': '测试材料清单', 'review_completed': True,
            'tasks': [{'id': '01', 'name': '住宿详情', 'status': 'missing',
                       'action': '提供入住和退房日期'}],
            'documents': [
                {'id': 'P01', 'category': 'payment', 'path': 'PAYMENT.pdf', 'label': 'P01 对应 T01'},
                {'id': 'H01', 'category': 'lodging', 'path': 'LODGING.pdf'},
                {'id': 'C01', 'category': 'conference', 'path': 'CONFERENCE.pdf'},
                {'id': 'O01', 'category': 'other', 'path': 'ROTATED.pdf'},
                {'id': 'T01', 'category': 'transport', 'path': 'TRANSPORT.pdf'},
            ],
        }

    def tearDown(self):
        self.tmp.cleanup()

    def run_build(self, case=None, name='output'):
        manifest = self.root / 'case.json'
        manifest.write_text(json.dumps(case or self.case), encoding='utf-8')
        return build(manifest, self.root / name)

    def test_order_pages_a4_annotations_and_source_preservation(self):
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.glob('*.pdf')}
        result = self.run_build()
        reader = PdfReader(result['packet_pdf'])
        self.assertEqual(len(reader.pages), 5)
        for page, marker in zip(reader.pages, ['CONFERENCE', 'TRANSPORT', 'LODGING', 'OTHER', 'PAYMENT']):
            self.assertIn(marker, page.extract_text())
            self.assertAlmostEqual(float(page.mediabox.width), 595.2756, places=2)
            self.assertAlmostEqual(float(page.mediabox.height), 841.8898, places=2)
        self.assertIn('P01 对应 T01', reader.pages[-1].extract_text())
        self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in self.root.glob('*.pdf')})
        index = json.loads((self.root / 'output' / '材料索引.json').read_text())
        self.assertEqual([r['packet_start'] for r in index], [1, 2, 3, 4, 5])

    def test_pending_forces_draft_even_when_review_flag_true(self):
        result = self.run_build()
        self.assertTrue(result['draft'])
        self.assertIn('待补草稿', result['packet_pdf'])

    def test_review_flag_defaults_to_draft(self):
        case = copy.deepcopy(self.case)
        case['tasks'] = [{'id': '01', 'name': '材料', 'status': 'received', 'evidence': 'C01'}]
        case.pop('review_completed')
        self.assertTrue(self.run_build(case)['draft'])

    def test_reviewed_complete_label_does_not_claim_finance_approval(self):
        case = copy.deepcopy(self.case)
        case['tasks'] = [{'id': '01', 'name': '材料', 'status': 'received', 'evidence': 'C01'}]
        result = self.run_build(case)
        self.assertFalse(result['draft'])
        self.assertIn('待助理初审', result['packet_pdf'])

    def test_duplicate_content_page_rejected(self):
        case = copy.deepcopy(self.case)
        (self.root / 'COPY.pdf').write_bytes((self.root / 'TRANSPORT.pdf').read_bytes())
        case['documents'].append({'id': 'T02', 'category': 'transport', 'path': 'COPY.pdf'})
        with self.assertRaisesRegex(ValueError, '重复入册'):
            self.run_build(case)

    def test_invalid_page_rejected(self):
        case = copy.deepcopy(self.case)
        case['documents'][0]['pages'] = [2]
        with self.assertRaisesRegex(ValueError, '页码超范围'):
            self.run_build(case)

    def test_empty_documents_produces_list_but_no_empty_packet(self):
        case = copy.deepcopy(self.case)
        case['documents'] = []
        result = self.run_build(case)
        self.assertIsNone(result['packet_pdf'])
        self.assertEqual(result['packet_pages'], 0)
        self.assertGreater(len(PdfReader(result['list_pdf']).pages), 0)

    def test_payment_needs_invoice_mapping(self):
        self.case['documents'][0].pop('label')
        with self.assertRaisesRegex(ValueError, '对应票据'):
            validate(self.case, self.root)

    def test_unknown_status_and_missing_action_rejected(self):
        self.case['tasks'][0]['status'] = 'done'
        with self.assertRaisesRegex(ValueError, '状态'):
            validate(self.case, self.root)
        self.case['tasks'][0]['status'] = 'pending'
        self.case['tasks'][0].pop('action')
        with self.assertRaisesRegex(ValueError, '具体补充'):
            validate(self.case, self.root)

    def test_existing_output_not_overwritten(self):
        self.run_build()
        with self.assertRaisesRegex(ValueError, '非空'):
            self.run_build()

    def test_image_payment_is_embedded_and_annotated(self):
        Image.new('RGB', (200, 500), (230, 245, 235)).save(self.root / 'pay.png')
        case = copy.deepcopy(self.case)
        case['documents'] = [{'id': 'P01', 'category': 'payment', 'path': 'pay.png',
                              'label': 'P01 对应 T01、H01'}]
        result = self.run_build(case)
        page = PdfReader(result['packet_pdf']).pages[0]
        self.assertIn('P01 对应 T01、H01', page.extract_text())
        self.assertEqual(len(page.images), 1)

    def test_selected_pages_keep_order(self):
        c = canvas.Canvas(str(self.root / 'multi.pdf'))
        for i in range(1, 4):
            c.drawString(30, 500, f'PAGE NUMBER {i}')
            c.showPage()
        c.save()
        case = copy.deepcopy(self.case)
        case['documents'] = [{'id': 'T01', 'category': 'transport', 'path': 'multi.pdf', 'pages': [3, 1]}]
        result = self.run_build(case)
        pages = PdfReader(result['packet_pdf']).pages
        self.assertEqual(len(pages), 2)
        self.assertIn('PAGE NUMBER 3', pages[0].extract_text())
        self.assertIn('PAGE NUMBER 1', pages[1].extract_text())


if __name__ == '__main__':
    unittest.main()
