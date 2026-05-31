from pathlib import Path
import fitz
import docx


class TextExtractor:

    @staticmethod
    def extract(file_path):

        suffix = Path(file_path).suffix.lower()

        if suffix == ".pdf":
            return TextExtractor.extract_pdf(file_path)

        elif suffix == ".docx":
            return TextExtractor.extract_docx(file_path)

        elif suffix == ".txt":
            return TextExtractor.extract_txt(file_path)

        return ""

    @staticmethod
    def extract_pdf(file_path):

        text = ""

        pdf = fitz.open(file_path)

        for page in pdf:
            text += page.get_text()

        return text

    @staticmethod
    def extract_docx(file_path):

        doc = docx.Document(file_path)

        return "\n".join(
            paragraph.text
            for paragraph in doc.paragraphs
        )

    @staticmethod
    def extract_txt(file_path):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:
            return file.read()