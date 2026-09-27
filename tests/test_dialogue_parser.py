from app.services.dialogue_parser import DialogueParser


def test_single_speaker_line():
    items, warnings = DialogueParser().parse("Hello there. [2]")
    assert not warnings
    assert items[0].text == "Hello there."
    assert items[0].pause == 2.0


def test_multi_speaker_line():
    items, warnings = DialogueParser().parse("[speaker2] Hello there. [1.5]")
    assert not warnings
    assert items[0].speaker == "speaker2"
    assert items[0].pause == 1.5


def test_missing_pause_defaults_to_zero():
    items, warnings = DialogueParser().parse("Hello there.")
    assert not warnings
    assert len(items) == 1
    assert items[0].text == "Hello there."
    assert items[0].pause == 0.0
