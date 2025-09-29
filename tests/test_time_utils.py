from datetime import datetime, timezone
from unittest.mock import patch
from utils.time_utils import is_search_time_reached, was_search_run_today, should_run_delivery


class TestTimeUtils:
    """Tests for time utility functions."""

    def test_is_search_time_reached_valid_time_before(self):
        """Test is search time reached when current time is before search time."""
        with patch('utils.time_utils.datetime') as mock_datetime:
            # Mock current time to 10:30 UTC
            mock_now = datetime(2024, 1, 1, 10, 30, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Search time is 12:00 UTC
            result = is_search_time_reached("12:00")
            assert result is False

    def test_is_search_time_reached_valid_time_after(self):
        """Test is search time reached when current time is after search time."""
        with patch('utils.time_utils.datetime') as mock_datetime:
            # Mock current time to 14:30 UTC
            mock_now = datetime(2024, 1, 1, 14, 30, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Search time is 12:00 UTC
            result = is_search_time_reached("12:00")
            assert result is True

    def test_is_search_time_reached_invalid_format(self):
        """Test is search time reached with invalid time format."""
        result = is_search_time_reached("invalid_time")
        assert result is False

    def test_is_search_time_reached_malformed_time(self):
        """Test is search time reached with malformed time string."""
        result = is_search_time_reached("25:70")
        assert result is False

    def test_was_search_run_today_with_today_datetime(self):
        """Test was search run today when last_datetime is from today."""
        with patch('utils.time_utils.datetime') as mock_datetime:
            # Mock current date to 2024-01-01
            mock_now = datetime(2024, 1, 1, 10, 30, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Last run was today at 08:00 UTC
            last_run = datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
            result = was_search_run_today(last_run)
            assert result is True

    def test_was_search_run_today_with_yesterday_datetime(self):
        """Test was search run today when last_datetime is from yesterday."""
        with patch('utils.time_utils.datetime') as mock_datetime:
            # Mock current date to 2024-01-02
            mock_now = datetime(2024, 1, 2, 10, 30, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Last run was yesterday
            last_run = datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
            result = was_search_run_today(last_run)
            assert result is False

    def test_should_run_delivery_conditions_met(self):
        """Test should run delivery when all conditions are met."""
        with patch('utils.time_utils.datetime') as mock_datetime, \
             patch('utils.time_utils.logging') as mock_logging:
            # Mock current time to 14:30 UTC on 2024-01-01
            mock_now = datetime(2024, 1, 1, 14, 30, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Last run was yesterday, delivery time is 12:00 UTC
            last_run = datetime(2023, 12, 31, 8, 0, 0, tzinfo=timezone.utc)  # Yesterday
            result = should_run_delivery(last_run, "12:00")
            assert result is True

    def test_should_run_delivery_already_run_today(self):
        """Test should run delivery when delivery was already run today."""
        with patch('utils.time_utils.datetime') as mock_datetime, \
             patch('utils.time_utils.logging') as mock_logging:
            # Mock current time to 14:30 UTC on 2024-01-01
            mock_now = datetime(2024, 1, 1, 14, 30, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Last run was today at 08:00 UTC
            last_run = datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc)  # Today
            result = should_run_delivery(last_run, "12:00")
            assert result is False

    def test_should_run_delivery_time_not_reached(self):
        """Test should run delivery when current time is before delivery time."""
        with patch('utils.time_utils.datetime') as mock_datetime, \
             patch('utils.time_utils.logging') as mock_logging:
            # Mock current time to 10:30 UTC on 2024-01-01
            mock_now = datetime(2024, 1, 1, 10, 30, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Last run was yesterday, delivery time is 12:00 UTC
            last_run = datetime(2023, 12, 31, 8, 0, 0, tzinfo=timezone.utc)  # Yesterday
            result = should_run_delivery(last_run, "12:00")
            assert result is False

    def test_should_run_delivery_no_previous_run(self):
        """Test should run delivery when there was no previous run."""
        with patch('utils.time_utils.datetime') as mock_datetime, \
             patch('utils.time_utils.logging') as mock_logging:
            # Mock current time to 14:30 UTC on 2024-01-01
            mock_now = datetime(2024, 1, 1, 14, 30, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # No previous run
            result = should_run_delivery(None, "12:00")
            assert result is True
