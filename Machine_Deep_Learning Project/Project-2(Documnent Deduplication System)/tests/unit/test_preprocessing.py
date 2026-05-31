from ai_engine.preprocessing.text_cleaner import TextCleaner


def test_text_cleaning():

    text = "Hello!!! AI World 123"

    cleaned = TextCleaner.clean(text)

    assert cleaned == "hello ai world 123"