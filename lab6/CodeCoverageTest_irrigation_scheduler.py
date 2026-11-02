import pytest
from irrigation_scheduler import should_irrigate, water_volume, schedule


# ---------- should_irrigate ----------
def test_wet_soil_no_irrigation():
    assert should_irrigate(70, 0, "seedling") is False


def test_heavy_rain_no_irrigation():
    assert should_irrigate(50, 12, "seedling") is False


def test_seedling_dry_irrigates():
    assert should_irrigate(30, 0, "seedling") is True


def test_seedling_moderate_moisture_no_irrigation():
    assert should_irrigate(50, 0, "seedling") is False


def test_flowering_dry_irrigates():
    assert should_irrigate(50, 0, "flowering") is True


def test_other_stage_light_rain_no_irrigation():
    assert should_irrigate(30, 6, "vegetative") is False


def test_other_stage_dry_irrigates():
    assert should_irrigate(30, 0, "vegetative") is True


# ---------- water_volume ----------
def test_seedling_volume():
    assert water_volume(10, "seedling", 20) == 20


def test_flowering_volume():
    assert water_volume(10, "flowering", 20) == 50


def test_other_stage_volume():
    assert water_volume(10, "vegetative", 20) == 40


def test_hot_weather_increases_volume():
    assert water_volume(10, "vegetative", 40) == 60


def test_cold_weather_decreases_volume():
    assert water_volume(10, "vegetative", 5) == 20


def test_invalid_area_raises():
    with pytest.raises(ValueError):
        water_volume(0, "seedling", 20)


# ---------- schedule ----------
def test_schedule_skips_dry_budget_runs_out():
    zones = [
        ("A", 10, 30, 0, "seedling", 20),  # needs 20 -> watered
        ("B", 10, 70, 0, "seedling", 20),  # too wet -> skipped
        ("C", 10, 30, 0, "seedling", 20),  # needs 20, only 10 left -> stop
    ]
    assert schedule(zones, 30) == ["A"]
