from database.models.point import Point
from database.models.clue import Clue


def test_get_clues_up_to_filters_by_max_order(clue_repo, point, make_clue):
    for order in range(1, 6):
        make_clue(order)

    result = clue_repo.get_clues_up_to(point.id, 3)

    orders = [c.order for c in result]
    assert orders == [1, 2, 3]
    

def test_get_clues_up_to_returns_clues_sorted_by_order(clue_repo, point, make_clue):
    for order in range(5, 0, -1):
        make_clue(order)

    clues = clue_repo.get_clues_up_to(point.id, 3)

    order = [clue.order for clue in clues]
    assert order == [1, 2, 3]


def test_get_clues_up_to_does_not_return_clues_for_other_points(clue_repo, make_point):
    p1 = make_point("P1")
    Clue.create(point=p1, order=1, text="C1")
    p2 = make_point("P2")
    Clue.create(point=p2, order=1, text="C2")

    result = clue_repo.get_clues_up_to(p1.id, 3)

    assert result.count() == 1
    assert result.first().point == p1


def test_get_clues_up_to_returns_empty_when_no_clues_for_point(clue_repo, point):
    assert clue_repo.get_clues_up_to(point.id, 3).exists() is False
