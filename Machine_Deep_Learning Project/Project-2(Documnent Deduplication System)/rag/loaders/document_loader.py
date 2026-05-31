from pathlib import Path


class DocumentLoader:

    @staticmethod
    def load_document(
        file_path
    ):

        suffix = (
            Path(file_path)
            .suffix
            .lower()
        )

        if suffix == ".txt":

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                return file.read()

        return ""