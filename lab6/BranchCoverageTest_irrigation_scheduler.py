import pytest
from irrigation_scheduler import should_irrigate, water_volume, schedule


# ---------- should_irrigate: every decision True and False, plus boundaries ----------
@pytest.mark.parametrize("moisture, rain, stage, expected", [
    # moisture >= 60
    (70, 0, "seedling", False),
    (60, 0, "seedling", False),      # boundary: exactly 60
    # rain_mm >= 10
    (50, 12, "seedling", False),
    (30, 10, "vegetative", False),   # boundary: exactly 10
    # seedling branch (moisture < 45)
    (44, 0, "seedling", True),
    (30, 0, "seedling", True),
    (45, 0, "seedling", False),      # boundary: exactly 45
    (50, 0, "seedling", False),
    # flowering branch (moisture < 55)
    (54, 0, "flowering", True),
    (55, 0, "flowering", False),     # boundary: exactly 55
    (58, 0, "flowering", False),
    # other stage: rain_mm >= 5
    (30, 6, "vegetative", False),
    (30, 5, "vegetative", False),    # boundary: exactly 5
    (30, 4, "vegetative", True),
    # other stage: moisture < 40
    (39, 0, "vegetative", True),
    (40, 0, "vegetative", False),    # boundary: exactly 40
])
def test_should_irrigate(moisture, rain, stage, expected):
    assert should_irrigate(moisture, rain, stage) is expected


# ---------- water_volume ----------
@pytest.mark.parametrize("area, stage, temp, expected", [
    (10, "seedling", 20, 20),
    (10, "flowering", 20, 50),
    (10, "vegetative", 20, 40),
    (10, "vegetative", 36, 60),      # temp > 35
    (10, "vegetative", 35, 40),      # boundary: exactly 35, no change
    (10, "vegetative", 9, 20),       # temp < 10
    (10, "vegetative", 10, 40),      # boundary: exactly 10, no change
])
def test_water_volume(area, stage, temp, expected):
    assert water_volume(area, stage, temp) == expected


@pytest.mark.parametrize("area", [0, -5])
def test_invalid_area_raises(area):
    with pytest.raises(ValueError, match="invalid area"):
        water_volume(area, "seedling", 20)


# ---------- schedule ----------
def test_schedule_empty_zones():
    assert schedule([], 100) == []


def test_schedule_all_zones_watered_loop_completes():
    zones = [
        ("A", 10, 30, 0, "seedling", 20),
        ("B", 10, 30, 0, "seedling", 20),
    ]
    assert schedule(zones, 100) == ["A", "B"]


def test_schedule_all_zones_skipped():
    zones = [("A", 10, 70, 0, "seedling", 20)]
    assert schedule(zones, 100) == []


def test_schedule_skips_dry_budget_runs_out():
    zones = [
        ("A", 10, 30, 0, "seedling", 20),
        ("B", 10, 70, 0, "seedling", 20),
        ("C", 10, 30, 0, "seedling", 20),
    ]
    assert schedule(zones, 30) == ["A"]


def test_schedule_need_exactly_equals_budget():
    zones = [("A", 10, 30, 0, "seedling", 20)]   # needs 20
    assert schedule(zones, 20) == ["A"]


def test_schedule_first_zone_exceeds_budget():
    zones = [("A", 10, 30, 0, "seedling", 20)]   # needs 20
    assert schedule(zones, 19) == []


def test_schedule_invalid_area_propagates_error():
    zones = [("A", 0, 30, 0, "seedling", 20)]
    with pytest.raises(ValueError):
        schedule(zones, 100)
