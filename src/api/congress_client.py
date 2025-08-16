"""
Congress.gov API Client
Handles all interactions with the Congress.gov API v3
"""

import requests
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
import logging

from ..utils.config import Config

logger = logging.getLogger(__name__)

class CongressClient:
    """Client for interacting with Congress.gov API"""
    
    def __init__(self):
        """Initialize the Congress API client"""
        Config.validate_config()
        self.base_url = Config.CONGRESS_API_BASE_URL
        self.headers = Config.get_api_headers()
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = 0
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the Congress.gov API with rate limiting"""
        
        # Rate limiting check
        current_time = time.time()
        if current_time - self.last_request_time < 1:  # 1 second between requests
            time.sleep(1)
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            self.request_count += 1
            self.last_request_time = time.time()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_members(self, congress: int = 118, chamber: str = "both") -> List[Dict[str, Any]]:
        """Get members of Congress"""
        members = []
        
        if chamber in ["house", "both"]:
            house_members = self._get_chamber_members(congress, "house")
            members.extend(house_members)
        
        if chamber in ["senate", "both"]:
            senate_members = self._get_chamber_members(congress, "senate")
            members.extend(senate_members)
        
        return members
    
    def _get_chamber_members(self, congress: int, chamber: str) -> List[Dict[str, Any]]:
        """Get members for a specific chamber"""
        endpoint = f"member"
        params = {
            'congress': congress,
            'chamber': chamber,
            'limit': 250
        }
        
        all_members = []
        offset = 0
        
        while True:
            params['offset'] = offset
            response = self._make_request(endpoint, params)
            
            if 'members' not in response:
                break
                
            members = response['members']
            all_members.extend(members)
            
            # Check if there are more results
            if len(members) < 250:
                break
                
            offset += 250
        
        return all_members
    
    def get_bills(self, congress: int = 118, limit: int = 100) -> List[Dict[str, Any]]:
        """Get bills from Congress"""
        endpoint = f"bill"
        params = {
            'congress': congress,
            'limit': min(limit, Config.MAX_BILLS_PER_REQUEST)
        }
        
        response = self._make_request(endpoint, params)
        
        if 'bills' not in response:
            return []
        
        return response['bills']
    
    def get_bill_details(self, congress: int, bill_type: str, bill_number: int) -> Dict[str, Any]:
        """Get detailed information about a specific bill"""
        endpoint = f"bill/{congress}/{bill_type}/{bill_number}"
        
        response = self._make_request(endpoint)
        return response
    
    def get_bill_text(self, congress: int, bill_type: str, bill_number: int) -> str:
        """Get the text content of a bill"""
        endpoint = f"bill/{congress}/{bill_type}/{bill_number}/text"
        
        response = self._make_request(endpoint)
        
        # Extract text from response
        if 'textVersions' in response and response['textVersions']:
            text_version = response['textVersions'][0]
            if 'formats' in text_version and text_version['formats']:
                # Get the first available format (usually PDF or HTML)
                format_info = text_version['formats'][0]
                if 'url' in format_info:
                    # For now, return the URL. In a full implementation,
                    # you might want to download and parse the actual text
                    return format_info['url']
        
        return ""
    
    def get_member_bills(self, member_id: str, congress: int = 118) -> List[Dict[str, Any]]:
        """Get bills sponsored by a specific member"""
        endpoint = f"member/{member_id}/bills"
        params = {
            'congress': congress,
            'limit': 250
        }
        
        response = self._make_request(endpoint, params)
        
        if 'bills' not in response:
            return []
        
        return response['bills']
    
    def get_congressional_record(self, congress: int = 118, limit: int = 100) -> List[Dict[str, Any]]:
        """Get Congressional Record entries"""
        endpoint = f"congressional-record"
        params = {
            'congress': congress,
            'limit': limit
        }
        
        response = self._make_request(endpoint, params)
        
        if 'results' not in response:
            return []
        
        return response['results']
    
    def get_votes(self, congress: int = 118, limit: int = 100) -> List[Dict[str, Any]]:
        """Get voting records"""
        endpoint = f"vote"
        params = {
            'congress': congress,
            'limit': limit
        }
        
        response = self._make_request(endpoint, params)
        
        if 'votes' not in response:
            return []
        
        return response['votes']
    
    def search_bills(self, query: str, congress: int = 118, limit: int = 100) -> List[Dict[str, Any]]:
        """Search for bills by keyword"""
        endpoint = f"bill"
        params = {
            'congress': congress,
            'limit': limit,
            'query': query
        }
        
        response = self._make_request(endpoint, params)
        
        if 'bills' not in response:
            return []
        
        return response['bills']
    
    def get_member_votes(self, member_id: str, congress: int = 118) -> List[Dict[str, Any]]:
        """Get voting record for a specific member"""
        endpoint = f"member/{member_id}/votes"
        params = {
            'congress': congress,
            'limit': 250
        }
        
        response = self._make_request(endpoint, params)
        
        if 'votes' not in response:
            return []
        
        return response['votes']
