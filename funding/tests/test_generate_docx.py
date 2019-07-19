from django.test import TestCase
from funding.generate_docx import create_funding_document
from io import BytesIO
from docx import Document


class create_funding_documentTest(TestCase):

    def setUp(self):
        self.fixture = {
            'funding_body': 'FUNDINGBODY',
            'title': '"TITLE"',
            'pi_firstname': 'PINAME',
            'pi_lastname': 'PILASTNAME',
            'pi_department': 'PIDEPARTMENT',
            'receiver': 'RECEIVER',
        }
        templates = ['Swansea.docx', 'Aberystwyth.docx']
        self.texts = dict()
        for template in templates:
            content = create_funding_document(**self.fixture, template=template)
            # reconstructing the document
            docx = Document(BytesIO(content))
            self.texts[template] = '\n'.join([p.text for p in docx.paragraphs])

    def test_argument_in_text(self):
        for text in self.texts.values():
            for key in self.fixture.keys():
                with self.subTest():
                    assert self.fixture[
                        key
                    ] in text, f'{key}=({self.fixture[key]}) Not present'
