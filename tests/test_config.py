import pytest
import yaml
from pathlib import Path
from utils.config import load_config, get_database_file, get_sources_config


class TestConfig:
    """Essential tests for config functions."""

    def test_load_config_valid_file(self, tmp_path):
        """Test loading a valid YAML configuration file."""
        config_data = {"database": {"file": "test.db"}}
        
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))
        
        result = load_config(str(config_file))
        assert result == config_data

    def test_load_config_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is raised when config file doesn't exist."""
        non_existent_file = tmp_path / "nonexistent.yaml"
        
        with pytest.raises(FileNotFoundError):
            load_config(str(non_existent_file))

    def test_get_database_file_valid(self, tmp_path):
        """Test getting database file from valid configuration."""
        config_data = {"database": {"file": "my_database.db"}}
        
        config_file = tmp_path / "db_config.yaml"
        config_file.write_text(yaml.dump(config_data))
        
        result = get_database_file(str(config_file))
        assert result == "my_database.db"

    def test_get_database_file_missing_key(self, tmp_path):
        """Test that ValueError is raised when 'database' key is missing."""
        config_data = {"other": "value"}
        
        config_file = tmp_path / "missing_db_config.yaml"
        config_file.write_text(yaml.dump(config_data))
        
        with pytest.raises(ValueError):
            get_database_file(str(config_file))

    def test_get_sources_config_valid(self, tmp_path):
        """Test getting sources configuration with valid data."""
        config_data = {
            "sources": [
                {"name": "TechCrunch", "enabled": True}
            ]
        }
        
        config_file = tmp_path / "sources_config.yaml"
        config_file.write_text(yaml.dump(config_data))
        
        result = get_sources_config(str(config_file))
        assert result == config_data

    def test_get_sources_config_no_enabled_sources(self, tmp_path):
        """Test that ValueError is raised when no sources are enabled."""
        config_data = {
            "sources": [
                {"name": "Source1", "enabled": False}
            ]
        }
        
        config_file = tmp_path / "no_enabled_sources.yaml"
        config_file.write_text(yaml.dump(config_data))
        
        with pytest.raises(ValueError):
            get_sources_config(str(config_file))
