from app.services.pause_service import PauseService


def test_pause_is_bounded():
    pause = PauseService.calculate_pause("This is a short sentence.")
    assert 2 <= pause <= 6
