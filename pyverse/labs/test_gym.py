import pytest

from pyverse.labs.gym import PACKAGES, verify
from pyverse.labs.gym_seed import SEED


def _need(ex):
    for p in PACKAGES[ex["library"]]:
        pytest.importorskip(p)


@pytest.mark.parametrize("ex", SEED, ids=lambda e: e["slug"])
def test_solution_passes_check(ex):
    _need(ex)
    ok, msg = verify(ex["setup_code"], ex["solution_code"], ex["check_code"])
    assert ok, msg


@pytest.mark.parametrize("ex", SEED, ids=lambda e: e["slug"])
def test_starter_fails_check(ex):
    _need(ex)
    ok, _ = verify(ex["setup_code"], ex["starter_code"], ex["check_code"])
    assert not ok


def test_slugs_unique():
    assert len({e["slug"] for e in SEED}) == len(SEED)
