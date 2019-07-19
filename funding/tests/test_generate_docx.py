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
            'template': 'Swansea.docx'
        }
        content = create_funding_document(**self.fixture)

        # reconstructing the document
        docx = Document(BytesIO(content))
        self.text = '\n'.join([p.text for p in docx.paragraphs])

    def test_argument_in_text(self):
        for key in self.fixture.keys() - ['template']:
            assert self.fixture[key] in self.text, f'{key} Not present'
