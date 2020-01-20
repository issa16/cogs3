from io import BytesIO

from django.test import TestCase
from docx import Document

from funding.generate_docx import create_funding_document


class create_funding_documentTest(TestCase):

    def setUp(self):
        self.fixture = {
            'funding_body': 'FUNDINGBODY',
            'title': '"TITLE"',
            'pi_fullname': 'PINAME',
            'pi_department': 'PIDEPARTMENT',
            'institution_name': 'INSTITUTION',
            'receiver': 'RECEIVER',
        }
        templates = ['Swansea.docx', 'Aberystwyth.docx']
        self.texts = dict()
        for template in templates:
            content = create_funding_document(
                funding_body=self.fixture['funding_body'],
                title=self.fixture['title'],
                pi_fullname=self.fixture['pi_fullname'],
                pi_department=self.fixture['pi_department'],
                receiver=self.fixture['receiver'],
                institution_name=self.fixture['institution_name'],
                template=template
            )
            # reconstructing the document
            docx = Document(BytesIO(content))
            self.texts[template] = '\n'.join([p.text for p in docx.paragraphs])

    def test_argument_in_text(self):
        for text in self.texts.values():
            for key in self.fixture.keys():
                with self.subTest():
                    assert self.fixture[key
                                       ] in text, '{}=({}) Not present'.format(
                                           key, self.fixture[key]
                                       )
