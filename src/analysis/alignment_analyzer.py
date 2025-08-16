"""
Political Alignment Analyzer
Uses NLP and machine learning to analyze political alignment
"""

import re
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter
import logging

# NLP imports
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.stem import WordNetLemmatizer
    from textblob import TextBlob
except ImportError:
    logging.warning("NLTK or TextBlob not available. Some features may not work.")

# ML imports
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
except ImportError:
    logging.warning("Scikit-learn not available. Some features may not work.")

from ..data.data_manager import DataManager
from ..api.congress_client import CongressClient
from ..utils.config import Config

logger = logging.getLogger(__name__)

class AlignmentAnalyzer:
    """Analyzes political alignment using various NLP and ML techniques"""
    
    def __init__(self):
        """Initialize the alignment analyzer"""
        self.data_manager = DataManager()
        self.client = CongressClient()
        
        # Initialize NLP components
        self._init_nlp()
        
        # Political ideology keywords (simplified)
        self.liberal_keywords = {
            'environmental', 'climate', 'renewable', 'green', 'sustainability',
            'healthcare', 'medicare', 'medicaid', 'universal', 'coverage',
            'education', 'student', 'loan', 'forgiveness', 'public',
            'immigration', 'refugee', 'asylum', 'pathway', 'citizenship',
            'gun', 'control', 'regulation', 'background', 'check',
            'abortion', 'reproductive', 'rights', 'choice', 'women',
            'lgbtq', 'gay', 'lesbian', 'transgender', 'equality',
            'minimum', 'wage', 'labor', 'union', 'worker', 'rights',
            'tax', 'increase', 'wealthy', 'billionaire', 'progressive'
        }
        
        self.conservative_keywords = {
            'tax', 'cut', 'reduction', 'deregulation', 'free', 'market',
            'business', 'corporation', 'entrepreneur', 'small', 'business',
            'defense', 'military', 'veteran', 'patriot', 'national', 'security',
            'border', 'wall', 'immigration', 'enforcement', 'deportation',
            'gun', 'rights', 'second', 'amendment', 'constitution',
            'abortion', 'pro-life', 'unborn', 'sanctity', 'life',
            'religious', 'freedom', 'christian', 'values', 'traditional',
            'fiscal', 'conservative', 'balanced', 'budget', 'deficit',
            'states', 'rights', 'federalism', 'local', 'control'
        }
    
    def _init_nlp(self):
        """Initialize NLP components"""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            self.stop_words = set(stopwords.words('english'))
            self.lemmatizer = WordNetLemmatizer()
            
        except Exception as e:
            logger.warning(f"Could not initialize NLTK: {e}")
            self.stop_words = set()
            self.lemmatizer = None
    
    def analyze_member(self, member_id: str, congress: int = 118) -> Dict[str, Any]:
        """Analyze political alignment for a specific member"""
        logger.info(f"Analyzing member {member_id} for Congress {congress}")
        
        # Get member data
        members = self.data_manager.get_members(congress)
        member = next((m for m in members if m.get('id') == member_id), None)
        
        if not member:
            logger.error(f"Member {member_id} not found")
            return {}
        
        # Get member's bills
        bills = self.data_manager.get_member_bills(member_id, congress)
        
        # Get member's votes
        votes = self.data_manager.get_member_votes(member_id)
        
        # Analyze text content
        text_analysis = self._analyze_text_content(bills)
        
        # Analyze voting patterns
        voting_analysis = self._analyze_voting_patterns(votes)
        
        # Calculate overall alignment score
        alignment_score = self._calculate_alignment_score(text_analysis, voting_analysis)
        
        # Topic modeling
        topic_scores = self._analyze_topics(bills)
        
        # Compile results
        analysis_result = {
            'member_id': member_id,
            'congress': congress,
            'member_info': member,
            'alignment_score': alignment_score,
            'ideology_score': self._calculate_ideology_score(alignment_score),
            'text_analysis': text_analysis,
            'voting_analysis': voting_analysis,
            'topic_scores': topic_scores,
            'bill_count': len(bills),
            'vote_count': len(votes),
            'analysis_timestamp': pd.Timestamp.now().isoformat()
        }
        
        # Save analysis results
        self.data_manager.save_alignment_analysis(member_id, congress, analysis_result)
        
        return analysis_result
    
    def _analyze_text_content(self, bills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze text content of bills for political indicators"""
        if not bills:
            return {'sentiment': 0, 'liberal_score': 0, 'conservative_score': 0}
        
        all_text = []
        bill_texts = []
        
        for bill in bills:
            # Get bill text if available
            bill_id = bill.get('id')
            if bill_id:
                text = self.data_manager.get_bill_text(bill_id)
                if text:
                    bill_texts.append(text)
                    all_text.append(text)
            
            # Use summary if available
            summary = bill.get('summary', '')
            if summary:
                all_text.append(summary)
        
        if not all_text:
            return {'sentiment': 0, 'liberal_score': 0, 'conservative_score': 0}
        
        # Combine all text
        combined_text = ' '.join(all_text)
        
        # Sentiment analysis
        sentiment_score = self._calculate_sentiment(combined_text)
        
        # Keyword analysis
        liberal_score = self._calculate_keyword_score(combined_text, self.liberal_keywords)
        conservative_score = self._calculate_keyword_score(combined_text, self.conservative_keywords)
        
        return {
            'sentiment': sentiment_score,
            'liberal_score': liberal_score,
            'conservative_score': conservative_score,
            'text_length': len(combined_text),
            'bill_count': len(bills)
        }
    
    def _analyze_voting_patterns(self, votes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze voting patterns for political indicators"""
        if not votes:
            return {'party_alignment': 0, 'vote_consistency': 0}
        
        # Count vote positions
        positions = [vote.get('position', '') for vote in votes]
        position_counts = Counter(positions)
        
        # Calculate party alignment (assuming party voting patterns)
        yes_votes = position_counts.get('Yes', 0)
        no_votes = position_counts.get('No', 0)
        total_votes = yes_votes + no_votes
        
        if total_votes > 0:
            party_alignment = (yes_votes - no_votes) / total_votes
        else:
            party_alignment = 0
        
        # Calculate vote consistency
        most_common_position = position_counts.most_common(1)[0][0] if position_counts else None
        if most_common_position:
            consistency = position_counts[most_common_position] / len(votes)
        else:
            consistency = 0
        
        return {
            'party_alignment': party_alignment,
            'vote_consistency': consistency,
            'total_votes': len(votes),
            'yes_votes': yes_votes,
            'no_votes': no_votes,
            'position_breakdown': dict(position_counts)
        }
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score using TextBlob"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return 0.0
    
    def _calculate_keyword_score(self, text: str, keywords: set) -> float:
        """Calculate keyword presence score"""
        if not text:
            return 0.0
        
        # Tokenize and clean text
        tokens = word_tokenize(text.lower())
        tokens = [token for token in tokens if token.isalpha() and token not in self.stop_words]
        
        if not tokens:
            return 0.0
        
        # Count keyword matches
        keyword_matches = sum(1 for token in tokens if token in keywords)
        
        # Return normalized score
        return keyword_matches / len(tokens)
    
    def _calculate_alignment_score(self, text_analysis: Dict, voting_analysis: Dict) -> float:
        """Calculate overall political alignment score"""
        # Weight different components
        text_weight = 0.6
        voting_weight = 0.4
        
        # Text-based score (liberal vs conservative)
        liberal_score = text_analysis.get('liberal_score', 0)
        conservative_score = text_analysis.get('conservative_score', 0)
        
        if liberal_score + conservative_score > 0:
            text_score = (liberal_score - conservative_score) / (liberal_score + conservative_score)
        else:
            text_score = 0
        
        # Voting-based score
        voting_score = voting_analysis.get('party_alignment', 0)
        
        # Combine scores
        alignment_score = (text_weight * text_score) + (voting_weight * voting_score)
        
        # Normalize to [-1, 1] range
        return np.clip(alignment_score, -1, 1)
    
    def _calculate_ideology_score(self, alignment_score: float) -> str:
        """Convert alignment score to ideology label"""
        if alignment_score > 0.3:
            return "Liberal"
        elif alignment_score < -0.3:
            return "Conservative"
        else:
            return "Moderate"
    
    def _analyze_topics(self, bills: List[Dict[str, Any]]) -> Dict[str, float]:
        """Perform topic modeling on bill content"""
        if not bills or len(bills) < 2:
            return {}
        
        try:
            # Extract text content
            texts = []
            for bill in bills:
                text = bill.get('summary', '')
                if text:
                    texts.append(text)
            
            if len(texts) < 2:
                return {}
            
            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                min_df=2,
                max_df=0.95
            )
            
            tfidf_matrix = vectorizer.fit_transform(texts)
            
            # Perform LDA topic modeling
            lda = LatentDirichletAllocation(
                n_components=min(5, len(texts)),
                random_state=42,
                max_iter=10
            )
            
            lda.fit(tfidf_matrix)
            
            # Get feature names and topic distributions
            feature_names = vectorizer.get_feature_names_out()
            topic_scores = {}
            
            for topic_idx, topic in enumerate(lda.components_):
                top_words = [feature_names[i] for i in topic.argsort()[-5:]]
                topic_name = f"Topic_{topic_idx + 1}"
                topic_scores[topic_name] = {
                    'words': top_words,
                    'weight': float(topic.sum())
                }
            
            return topic_scores
            
        except Exception as e:
            logger.warning(f"Topic modeling failed: {e}")
            return {}
    
    def compare_members(self, member_ids: List[str], congress: int = 118) -> Dict[str, Any]:
        """Compare political alignment between multiple members"""
        comparisons = {}
        
        for member_id in member_ids:
            analysis = self.analyze_member(member_id, congress)
            if analysis:
                comparisons[member_id] = analysis
        
        return comparisons
    
    def get_party_analysis(self, congress: int = 118) -> Dict[str, Any]:
        """Analyze political alignment by party"""
        members = self.data_manager.get_members(congress)
        
        party_analyses = {}
        
        for member in members:
            party = member.get('party', 'Unknown')
            member_id = member.get('id')
            
            if member_id:
                analysis = self.analyze_member(member_id, congress)
                if analysis:
                    if party not in party_analyses:
                        party_analyses[party] = []
                    party_analyses[party].append(analysis)
        
        # Calculate party averages
        party_summary = {}
        for party, analyses in party_analyses.items():
            if analyses:
                avg_alignment = np.mean([a.get('alignment_score', 0) for a in analyses])
                avg_ideology = np.mean([a.get('ideology_score', 0) for a in analyses])
                
                party_summary[party] = {
                    'member_count': len(analyses),
                    'avg_alignment_score': avg_alignment,
                    'avg_ideology_score': avg_ideology,
                    'members': analyses
                }
        
        return party_summary
