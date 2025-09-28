import pytest
from delivery import telegram
from models.article import Article

class TestTelegramDelivery:
    """Tests for Telegram delivery mechanism.
    
    These tests verify:
    1. Environment configuration handling
    2. Input validation
    3. Basic message delivery functionality
    """

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test data that will be used by all tests."""
        self.valid_item = Article(
            guid="test",
            source="test",
            title="Test News",
            link="https://example.com",
            summary="Test Content"
        )
        self.valid_credentials = {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_CHAT_ID": "test_chat_id"
        }

    def test_missing_token(self, monkeypatch):
        """Should raise ValueError when TELEGRAM_BOT_TOKEN is missing."""
        def mock_getenv(key):
            return "test_chat_id" if key == "TELEGRAM_CHAT_ID" else None
        monkeypatch.setattr('os.getenv', mock_getenv)
        
        with pytest.raises(ValueError, match=".*credentials.*"):
            telegram.send([self.valid_item])

    def test_missing_chat_id(self, monkeypatch):
        """Should raise ValueError when TELEGRAM_CHAT_ID is missing."""
        def mock_getenv(key):
            return "test_token" if key == "TELEGRAM_BOT_TOKEN" else None
        monkeypatch.setattr('os.getenv', mock_getenv)
        
        with pytest.raises(ValueError, match=".*credentials.*"):
            telegram.send([self.valid_item])

    def test_missing_all_credentials(self, monkeypatch):
        """Should raise ValueError when all credentials are missing."""
        monkeypatch.setattr('os.getenv', lambda x: None)
        
        with pytest.raises(ValueError, match=".*credentials.*"):
            telegram.send([self.valid_item])

    def test_valid_credentials(self, monkeypatch):
        """Should process messages when credentials are valid."""
        def mock_getenv(key):
            return self.valid_credentials.get(key)
        monkeypatch.setattr('os.getenv', mock_getenv)
        
        telegram.send([self.valid_item])  # Should not raise any exception

    def test_empty_message_list(self, monkeypatch):
        """Should handle empty message list gracefully."""
        def mock_getenv(key):
            return self.valid_credentials.get(key)
        monkeypatch.setattr('os.getenv', mock_getenv)
        
        telegram.send([])  # Should not raise any exception
