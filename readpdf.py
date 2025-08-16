import PyPDF2
from PyPDF2 import PdfFileReader

class Extractpdf:

    def __init__(self, file, pgno):
        
        self.file = file
        self.pgno = pgno


    def read_content(self):
        # creating a pdf reader object
        reader = PyPDF2.PdfReader(self.file)
        text = reader.pages[int(self.pgno)-1].extract_text()
        return text

