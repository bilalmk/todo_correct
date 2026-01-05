"""Unit tests for validation functions."""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from backend.src.core.validators import validate_hex_color
from backend.src.schemas.task import TaskCreate
from backend.src.schemas.tag import TagCreate


class TestHexColorValidator:
    """Test suite for hex color validation and normalization."""

    def test_valid_rgb_shorthand_lowercase(self):
        """Test #RGB shorthand format (lowercase) normalizes to #RRGGBB uppercase."""
        assert validate_hex_color("#f5a") == "#FF55AA"
        assert validate_hex_color("#abc") == "#AABBCC"
        assert validate_hex_color("#123") == "#112233"

    def test_valid_rgb_shorthand_uppercase(self):
        """Test #RGB shorthand format (uppercase) normalizes to #RRGGBB."""
        assert validate_hex_color("#F5A") == "#FF55AA"
        assert validate_hex_color("#ABC") == "#AABBCC"

    def test_valid_rgb_shorthand_mixed_case(self):
        """Test #RGB shorthand format (mixed case) normalizes to #RRGGBB uppercase."""
        assert validate_hex_color("#f5A") == "#FF55AA"
        assert validate_hex_color("#AbC") == "#AABBCC"

    def test_valid_rrggbb_lowercase(self):
        """Test #RRGGBB full format (lowercase) normalizes to uppercase."""
        assert validate_hex_color("#ff5733") == "#FF5733"
        assert validate_hex_color("#abcdef") == "#ABCDEF"
        assert validate_hex_color("#123456") == "#123456"

    def test_valid_rrggbb_uppercase(self):
        """Test #RRGGBB full format (uppercase) remains uppercase."""
        assert validate_hex_color("#FF5733") == "#FF5733"
        assert validate_hex_color("#ABCDEF") == "#ABCDEF"

    def test_valid_rrggbb_mixed_case(self):
        """Test #RRGGBB full format (mixed case) normalizes to uppercase."""
        assert validate_hex_color("#Ff5733") == "#FF5733"
        assert validate_hex_color("#aBcDeF") == "#ABCDEF"

    def test_none_returns_none(self):
        """Test that None input returns None."""
        assert validate_hex_color(None) is None

    def test_missing_hash_raises_error(self):
        """Test that missing # prefix raises ValueError."""
        with pytest.raises(ValueError, match="Invalid hex color format"):
            validate_hex_color("FF5733")
        with pytest.raises(ValueError, match="Invalid hex color format"):
            validate_hex_color("F5A")

    def test_wrong_length_raises_error(self):
        """Test that wrong length (not 3 or 6 hex digits) raises ValueError."""
        with pytest.raises(ValueError, match="Invalid hex color format"):
            validate_hex_color("#FF")  # Too short
        with pytest.raises(ValueError, match="Invalid hex color format"):
            validate_hex_color("#FFFF")  # Too long for shorthand, too short for full
        with pytest.raises(ValueError, match="Invalid hex color format"):
            validate_hex_color("#FF573")  # 5 digits (invalid)
        with pytest.raises(ValueError, match="Invalid hex color format"):
            validate_hex_color("#FF57333")  # 7 digits (too long)

    def test_non_hex_characters_raises_error(self):
        """Test that non-hex characters raise ValueError."""
        with pytest.raises(ValueError, match="Invalid hex color format"):
            validate_hex_color("#GGG")  # G is not a hex digit
        with pytest.raises(ValueError, match="Invalid hex color format"):
            validate_hex_color("#GGGGGG")
        with pytest.raises(ValueError, match="Invalid hex color format"):
            validate_hex_color("#FF57ZZ")  # Z is not a hex digit
        with pytest.raises(ValueError, match="Invalid hex color format"):
            validate_hex_color("#12345G")

    def test_whitespace_trimmed(self):
        """Test that leading/trailing whitespace is trimmed before validation."""
        assert validate_hex_color("  #FF5733  ") == "#FF5733"
        assert validate_hex_color("\t#F5A\n") == "#FF55AA"
        assert validate_hex_color(" #abc ") == "#AABBCC"

    def test_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Invalid hex color format"):
            validate_hex_color("")
        with pytest.raises(ValueError, match="Invalid hex color format"):
            validate_hex_color("   ")  # Whitespace-only

    def test_special_characters_raise_error(self):
        """Test that special characters raise ValueError."""
        with pytest.raises(ValueError, match="Invalid hex color format"):
            validate_hex_color("#FF57@3")
        with pytest.raises(ValueError, match="Invalid hex color format"):
            validate_hex_color("#AB CD EF")  # Spaces inside


class TestTaskCreateSchemaValidation:
    """Test suite for TaskCreate schema validation (T019)."""

    def test_title_required(self):
        """Test that title is required."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate()

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("title",) for error in errors)

    def test_title_max_length_255(self):
        """Test that title cannot exceed 255 characters."""
        long_title = "a" * 256
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title=long_title)

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("title",) and "at most 255 characters" in str(error)
            for error in errors
        )

    def test_title_not_whitespace_only(self):
        """Test that title cannot be whitespace-only."""
        with pytest.raises(ValidationError, match="cannot be empty or whitespace-only"):
            TaskCreate(title="   ")

    def test_description_max_length_10000(self):
        """Test that description cannot exceed 10,000 characters."""
        long_description = "a" * 10001
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Test", description=long_description)

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("description",) and "at most 10000 characters" in str(error)
            for error in errors
        )

    def test_reminder_at_must_be_before_due_date(self):
        """Test that reminder_at must be before due_date."""
        due_date = datetime.now()
        reminder_at = due_date + timedelta(hours=1)  # After due_date

        with pytest.raises(
            ValidationError, match="reminder_at must be before due_date"
        ):
            TaskCreate(
                title="Test Task", due_date=due_date, reminder_at=reminder_at
            )

    def test_reminder_at_equal_to_due_date_raises_error(self):
        """Test that reminder_at cannot equal due_date."""
        same_time = datetime.now()

        with pytest.raises(
            ValidationError, match="reminder_at must be before due_date"
        ):
            TaskCreate(
                title="Test Task", due_date=same_time, reminder_at=same_time
            )

    def test_reminder_at_before_due_date_valid(self):
        """Test that reminder_at before due_date is valid."""
        due_date = datetime.now()
        reminder_at = due_date - timedelta(hours=1)  # Before due_date

        task = TaskCreate(
            title="Test Task", due_date=due_date, reminder_at=reminder_at
        )

        assert task.reminder_at < task.due_date

    def test_completed_defaults_to_false(self):
        """Test that completed defaults to False."""
        task = TaskCreate(title="Test Task")
        assert task.completed is False

    def test_valid_task_with_all_fields(self):
        """Test creating a valid task with all fields."""
        due_date = datetime.now() + timedelta(days=1)
        reminder_at = datetime.now() + timedelta(hours=12)

        task = TaskCreate(
            title="Buy groceries",
            description="Milk, eggs, bread",
            completed=False,
            priority="high",
            due_date=due_date,
            reminder_at=reminder_at,
            recurrence_pattern="weekly",
            recurrence_config={"rrule": "FREQ=WEEKLY;BYDAY=MO,FR"},
        )

        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.completed is False
        assert task.priority == "high"
        assert task.due_date == due_date
        assert task.reminder_at == reminder_at
        assert task.recurrence_pattern == "weekly"
        assert task.recurrence_config == {"rrule": "FREQ=WEEKLY;BYDAY=MO,FR"}


class TestTagCreateSchemaValidation:
    """Test suite for TagCreate schema validation with hex color normalization (T043)."""

    def test_hex_color_normalization_rgb_to_rrggbb(self):
        """Test TagCreate schema normalizes #RGB shorthand to #RRGGBB uppercase."""
        tag = TagCreate(name="work", color="#f5a")
        assert tag.color == "#FF55AA"

    def test_hex_color_normalization_lowercase_to_uppercase(self):
        """Test TagCreate schema normalizes lowercase #RRGGBB to uppercase."""
        tag = TagCreate(name="work", color="#ff5733")
        assert tag.color == "#FF5733"

    def test_hex_color_normalization_mixed_case(self):
        """Test TagCreate schema normalizes mixed case to uppercase."""
        tag = TagCreate(name="work", color="#Ff57Aa")
        assert tag.color == "#FF57AA"

    def test_hex_color_validation_invalid_format(self):
        """Test TagCreate schema rejects invalid hex color format."""
        with pytest.raises(ValidationError, match="Invalid hex color format"):
            TagCreate(name="work", color="FF5733")  # Missing #

    def test_hex_color_validation_wrong_length(self):
        """Test TagCreate schema rejects wrong color length."""
        with pytest.raises(ValidationError, match="Invalid hex color format"):
            TagCreate(name="work", color="#FF")  # Too short

    def test_hex_color_validation_non_hex_characters(self):
        """Test TagCreate schema rejects non-hex characters."""
        with pytest.raises(ValidationError, match="Invalid hex color format"):
            TagCreate(name="work", color="#GGGGGG")  # G is not hex

    def test_hex_color_optional_none(self):
        """Test TagCreate schema accepts None for optional color field."""
        tag = TagCreate(name="work", color=None)
        assert tag.color is None

    def test_hex_color_optional_omitted(self):
        """Test TagCreate schema works without color field."""
        tag = TagCreate(name="work")
        assert tag.color is None

    def test_name_required(self):
        """Test that tag name is required."""
        with pytest.raises(ValidationError) as exc_info:
            TagCreate()

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_name_max_length_50(self):
        """Test that tag name cannot exceed 50 characters."""
        long_name = "a" * 51
        with pytest.raises(ValidationError) as exc_info:
            TagCreate(name=long_name)

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("name",) and "at most 50 characters" in str(error)
            for error in errors
        )
