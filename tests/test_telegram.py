"""Tests for the telegram delivery module."""

from unittest.mock import patch, MagicMock
import pytest
from telegram.error import TelegramError
from delivery.telegram import send


class TestTelegramSend:
    """Test cases for the send function in telegram module."""

    def test_send_success(self):
        """Test successful message sending."""
        with patch.dict('os.environ', {
            'TELEGRAM_BOT_TOKEN': 'test_bot_token',
            'TELEGRAM_CHANNEL': 'test_channel_id',
            'TELEGRAM_PARSE_MODE': 'HTML'
        }):
            with patch('delivery.telegram.Bot') as mock_bot_class:
                mock_bot = MagicMock()
                mock_bot_class.return_value = mock_bot
                mock_message = MagicMock()
                mock_message.message_id = 12345
                mock_bot.send_message.return_value = mock_message
                
                result = send("<b>Test Post</b>")
                
                assert result == 12345
                mock_bot_class.assert_called_once_with(token='test_bot_token')
                mock_bot.send_message.assert_called_once_with(
                    chat_id='test_channel_id',
                    text="<b>Test Post</b>",
                    parse_mode='HTML'
                )

    def test_send_missing_credentials(self):
        """Test that ValueError is raised when credentials are missing."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match=".*credentials.*"):
                send("Test message")

    def test_send_telegram_error(self):
        """Test that TelegramError is properly handled and re-raised."""
        with patch.dict('os.environ', {
            'TELEGRAM_BOT_TOKEN': 'test_bot_token',
            'TELEGRAM_CHANNEL': 'test_channel_id',
            'TELEGRAM_PARSE_MODE': 'HTML'
        }):
            with patch('delivery.telegram.Bot') as mock_bot_class:
                mock_bot = MagicMock()
                mock_bot_class.return_value = mock_bot
                mock_bot.send_message.side_effect = TelegramError("Bot was blocked")
                
                with pytest.raises(TelegramError, match="Bot was blocked"):
                    send("Test message")