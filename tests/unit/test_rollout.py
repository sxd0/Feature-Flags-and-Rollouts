from libs.common.src.common.flags.rollout import is_in_rollout


def test_rollout_is_deterministic() -> None:
    a = is_in_rollout("f", "prod", "123", 5)
    b = is_in_rollout("f", "prod", "123", 5)
    assert a == b


def test_rollout_bounds() -> None:
    assert is_in_rollout("f", "prod", "u", 0) is False
    assert is_in_rollout("f", "prod", "u", 100) is True
