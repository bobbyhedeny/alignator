"""
Data Manager for Alignator
Handles data storage and retrieval using SQLite
"""

import sqlite3
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..utils.config import Config

logger = logging.getLogger(__name__)

class DataManager:
    """Manages data storage and retrieval"""
    
    def __init__(self):
        """Initialize the data manager"""
        self.db_path = Config.DATABASE_PATH
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with required tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create members table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS members (
                    id TEXT PRIMARY KEY,
                    congress INTEGER,
                    chamber TEXT,
                    name TEXT,
                    party TEXT,
                    state TEXT,
                    district TEXT,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create bills table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bills (
                    id TEXT PRIMARY KEY,
                    congress INTEGER,
                    bill_type TEXT,
                    bill_number INTEGER,
                    title TEXT,
                    sponsor_id TEXT,
                    summary TEXT,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create bill_texts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bill_texts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id TEXT,
                    text_content TEXT,
                    text_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (bill_id) REFERENCES bills (id)
                )
            ''')
            
            # Create votes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS votes (
                    id TEXT PRIMARY KEY,
                    congress INTEGER,
                    chamber TEXT,
                    vote_type TEXT,
                    question TEXT,
                    result TEXT,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create member_votes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS member_votes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id TEXT,
                    vote_id TEXT,
                    position TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (member_id) REFERENCES members (id),
                    FOREIGN KEY (vote_id) REFERENCES votes (id)
                )
            ''')
            
            # Create alignment_analysis table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alignment_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    member_id TEXT,
                    congress INTEGER,
                    alignment_score REAL,
                    ideology_score REAL,
                    topic_scores TEXT,
                    analysis_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (member_id) REFERENCES members (id)
                )
            ''')
            
            conn.commit()
    
    def save_members(self, members: List[Dict[str, Any]]):
        """Save members to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for member in members:
                cursor.execute('''
                    INSERT OR REPLACE INTO members 
                    (id, congress, chamber, name, party, state, district, data, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    member.get('id'),
                    member.get('congress'),
                    member.get('chamber'),
                    member.get('name'),
                    member.get('party'),
                    member.get('state'),
                    member.get('district'),
                    json.dumps(member),
                    datetime.now()
                ))
            
            conn.commit()
    
    def save_bills(self, bills: List[Dict[str, Any]]):
        """Save bills to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for bill in bills:
                cursor.execute('''
                    INSERT OR REPLACE INTO bills 
                    (id, congress, bill_type, bill_number, title, sponsor_id, summary, data, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    bill.get('id'),
                    bill.get('congress'),
                    bill.get('billType'),
                    bill.get('billNumber'),
                    bill.get('title'),
                    bill.get('sponsorId'),
                    bill.get('summary'),
                    json.dumps(bill),
                    datetime.now()
                ))
            
            conn.commit()
    
    def save_bill_text(self, bill_id: str, text_content: str, text_type: str = "introduced"):
        """Save bill text to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO bill_texts (bill_id, text_content, text_type)
                VALUES (?, ?, ?)
            ''', (bill_id, text_content, text_type))
            
            conn.commit()
    
    def save_votes(self, votes: List[Dict[str, Any]]):
        """Save votes to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for vote in votes:
                cursor.execute('''
                    INSERT OR REPLACE INTO votes 
                    (id, congress, chamber, vote_type, question, result, data, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    vote.get('id'),
                    vote.get('congress'),
                    vote.get('chamber'),
                    vote.get('voteType'),
                    vote.get('question'),
                    vote.get('result'),
                    json.dumps(vote),
                    datetime.now()
                ))
            
            conn.commit()
    
    def save_member_votes(self, member_id: str, votes: List[Dict[str, Any]]):
        """Save member voting records"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for vote in votes:
                cursor.execute('''
                    INSERT OR REPLACE INTO member_votes (member_id, vote_id, position)
                    VALUES (?, ?, ?)
                ''', (
                    member_id,
                    vote.get('voteId'),
                    vote.get('position')
                ))
            
            conn.commit()
    
    def save_alignment_analysis(self, member_id: str, congress: int, analysis_data: Dict[str, Any]):
        """Save alignment analysis results"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alignment_analysis 
                (member_id, congress, alignment_score, ideology_score, topic_scores, analysis_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                member_id,
                congress,
                analysis_data.get('alignment_score'),
                analysis_data.get('ideology_score'),
                json.dumps(analysis_data.get('topic_scores', {})),
                json.dumps(analysis_data)
            ))
            
            conn.commit()
    
    def get_members(self, congress: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get members from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if congress:
                cursor.execute('SELECT data FROM members WHERE congress = ?', (congress,))
            else:
                cursor.execute('SELECT data FROM members')
            
            results = cursor.fetchall()
            return [json.loads(row[0]) for row in results]
    
    def get_bills(self, congress: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get bills from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if congress:
                cursor.execute('SELECT data FROM bills WHERE congress = ?', (congress,))
            else:
                cursor.execute('SELECT data FROM bills')
            
            results = cursor.fetchall()
            return [json.loads(row[0]) for row in results]
    
    def get_bill_text(self, bill_id: str) -> Optional[str]:
        """Get bill text from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT text_content FROM bill_texts WHERE bill_id = ? ORDER BY created_at DESC LIMIT 1', (bill_id,))
            result = cursor.fetchone()
            
            return result[0] if result else None
    
    def get_member_bills(self, member_id: str, congress: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get bills sponsored by a specific member"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if congress:
                cursor.execute('SELECT data FROM bills WHERE sponsor_id = ? AND congress = ?', (member_id, congress))
            else:
                cursor.execute('SELECT data FROM bills WHERE sponsor_id = ?', (member_id,))
            
            results = cursor.fetchall()
            return [json.loads(row[0]) for row in results]
    
    def get_member_votes(self, member_id: str) -> List[Dict[str, Any]]:
        """Get voting record for a specific member"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT v.data, mv.position 
                FROM votes v 
                JOIN member_votes mv ON v.id = mv.vote_id 
                WHERE mv.member_id = ?
            ''', (member_id,))
            
            results = cursor.fetchall()
            votes = []
            for row in results:
                vote_data = json.loads(row[0])
                vote_data['position'] = row[1]
                votes.append(vote_data)
            
            return votes
    
    def get_alignment_analysis(self, member_id: str, congress: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get alignment analysis for a member"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if congress:
                cursor.execute('''
                    SELECT analysis_data FROM alignment_analysis 
                    WHERE member_id = ? AND congress = ? 
                    ORDER BY created_at DESC LIMIT 1
                ''', (member_id, congress))
            else:
                cursor.execute('''
                    SELECT analysis_data FROM alignment_analysis 
                    WHERE member_id = ? 
                    ORDER BY created_at DESC LIMIT 1
                ''', (member_id,))
            
            result = cursor.fetchone()
            return json.loads(result[0]) if result else None
