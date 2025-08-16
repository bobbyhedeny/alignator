"""
Basic tests for Alignator
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.utils.config import Config
from src.data.data_manager import DataManager

class TestConfig(unittest.TestCase):
    """Test configuration management"""
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test without API key
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                Config.validate_config()
    
    def test_api_headers(self):
        """Test API headers generation"""
        with patch.dict(os.environ, {'CONGRESS_API_KEY': 'test_key'}):
            headers = Config.get_api_headers()
            self.assertIn('X-API-Key', headers)
            self.assertEqual(headers['X-API-Key'], 'test_key')

class TestDataManager(unittest.TestCase):
    """Test data management"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db_path = "test_alignator.db"
        with patch.object(Config, 'DATABASE_PATH', self.test_db_path):
            self.data_manager = DataManager()
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_save_and_get_members(self):
        """Test saving and retrieving members"""
        test_members = [
            {
                'id': 'test1',
                'name': 'Test Member 1',
                'party': 'D',
                'state': 'CA',
                'congress': 118
            },
            {
                'id': 'test2',
                'name': 'Test Member 2',
                'party': 'R',
                'state': 'TX',
                'congress': 118
            }
        ]
        
        # Save members
        self.data_manager.save_members(test_members)
        
        # Retrieve members
        retrieved_members = self.data_manager.get_members(118)
        
        # Verify
        self.assertEqual(len(retrieved_members), 2)
        self.assertEqual(retrieved_members[0]['name'], 'Test Member 1')
        self.assertEqual(retrieved_members[1]['name'], 'Test Member 2')

if __name__ == '__main__':
    unittest.main()
