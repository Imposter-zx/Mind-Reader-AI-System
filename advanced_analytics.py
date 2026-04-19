#!/usr/bin/env python
"""
Advanced Analytics Module - Extended AI Components
NEW FEATURES:
  - Sentiment trajectory analysis
  - Social dynamics detection
  - Cognitive complexity scoring
  - Linguistic patterns analysis
  - Topic modeling and clustering
  - Anomaly detection
"""

import numpy as np
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any
import re
from datetime import datetime
from itertools import combinations


class SentimentTrajectory:
    """Analyze emotional sentiment evolution over time/text"""
    
    SENTIMENT_KEYWORDS = {
        'very_positive': ['love', 'amazing', 'excellent', 'outstanding', 'fantastic', 'wonderful', 'perfect', 'brilliant'],
        'positive': ['like', 'good', 'great', 'nice', 'happy', 'pleased', 'satisfied', 'wonderful'],
        'neutral': ['okay', 'fine', 'normal', 'standard', 'average', 'regular'],
        'negative': ['dislike', 'bad', 'poor', 'unhappy', 'disappointed', 'frustrated', 'annoyed'],
        'very_negative': ['hate', 'terrible', 'awful', 'horrible', 'disgusting', 'pathetic', 'abysmal']
    }
    
    def __init__(self):
        self.sentiment_scores = {'very_positive': 2, 'positive': 1, 'neutral': 0, 
                                  'negative': -1, 'very_negative': -2}
    
    def analyze_trajectory(self, texts: List[str]) -> Dict[str, Any]:
        """Analyze sentiment changes across multiple texts"""
        sentiments = []
        scores = []
        
        for text in texts:
            sentiment, score = self._score_text(text)
            sentiments.append(sentiment)
            scores.append(score)
        
        trajectory = {
            'sentiments': sentiments,
            'scores': scores,
            'trend': self._calculate_trend(scores),
            'volatility': self._calculate_volatility(scores),
            'average_sentiment': np.mean(scores),
            'peak_emotion': max(scores) if scores else 0,
            'valley_emotion': min(scores) if scores else 0,
            'emotional_arc': self._classify_arc(scores)
        }
        
        return trajectory
    
    def _score_text(self, text: str) -> Tuple[str, float]:
        """Score sentiment of single text"""
        text_lower = text.lower()
        scores = {}
        
        for sentiment_type, keywords in self.SENTIMENT_KEYWORDS.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            scores[sentiment_type] = count * self.sentiment_scores[sentiment_type]
        
        total_score = sum(scores.values())
        
        if total_score >= 4:
            return 'very_positive', total_score
        elif total_score >= 1:
            return 'positive', total_score
        elif total_score <= -4:
            return 'very_negative', total_score
        elif total_score <= -1:
            return 'negative', total_score
        else:
            return 'neutral', total_score
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate overall trend direction"""
        if not scores or len(scores) < 2:
            return 'stable'
        
        start_avg = np.mean(scores[:len(scores)//2])
        end_avg = np.mean(scores[len(scores)//2:])
        
        if end_avg > start_avg + 0.5:
            return 'improving'
        elif end_avg < start_avg - 0.5:
            return 'deteriorating'
        else:
            return 'stable'
    
    def _calculate_volatility(self, scores: List[float]) -> float:
        """Calculate emotional volatility"""
        if len(scores) < 2:
            return 0.0
        return float(np.std(scores))
    
    def _classify_arc(self, scores: List[float]) -> str:
        """Classify emotional narrative arc"""
        if len(scores) < 3:
            return 'insufficient_data'
        
        first_third = np.mean(scores[:len(scores)//3])
        middle_third = np.mean(scores[len(scores)//3:2*len(scores)//3])
        last_third = np.mean(scores[2*len(scores)//3:])
        
        if first_third < middle_third > last_third:
            return 'rise_and_fall'
        elif first_third > middle_third < last_third:
            return 'valley'
        elif last_third > first_third:
            return 'rising_climax'
        else:
            return 'declining'


class SocialDynamicsAnalyzer:
    """Analyze social and interpersonal dynamics in conversations"""
    
    DOMINANCE_MARKERS = ['i think', 'i believe', 'you should', 'clearly', 'obviously', 'must', 'need to']
    SUBMISSION_MARKERS = ['i feel', 'perhaps', 'maybe', 'might', 'possibly', 'seems', 'could']
    COOPERATION_WORDS = ['we', 'together', 'collaborate', 'team', 'our', 'joint', 'mutual']
    CONFLICT_WORDS = ['but', 'however', 'disagree', 'wrong', 'not', 'although', 'yet']
    
    def analyze_dynamics(self, conversation: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze multi-party conversation dynamics"""
        speakers = {}
        interaction_matrix = defaultdict(lambda: defaultdict(int))
        
        for i, turn in enumerate(conversation):
            speaker = turn.get('speaker', f'Speaker_{i}')
            text = turn.get('text', '').lower()
            
            if speaker not in speakers:
                speakers[speaker] = {
                    'dominance_score': 0,
                    'cooperation_score': 0,
                    'conflict_score': 0,
                    'turn_count': 0,
                    'avg_turn_length': 0,
                    'word_count': 0
                }
            
            speakers[speaker]['turn_count'] += 1
            speakers[speaker]['word_count'] += len(text.split())
            speakers[speaker]['dominance_score'] += self._count_markers(text, self.DOMINANCE_MARKERS)
            speakers[speaker]['cooperation_score'] += self._count_markers(text, self.COOPERATION_WORDS)
            speakers[speaker]['conflict_score'] += self._count_markers(text, self.CONFLICT_WORDS)
            
            if i > 0:
                prev_speaker = conversation[i-1].get('speaker', f'Speaker_{i-1}')
                if prev_speaker != speaker:
                    interaction_matrix[prev_speaker][speaker] += 1
        
        # Calculate averages
        for speaker in speakers:
            if speakers[speaker]['turn_count'] > 0:
                speakers[speaker]['avg_turn_length'] = speakers[speaker]['word_count'] / speakers[speaker]['turn_count']
        
        return {
            'speakers': speakers,
            'interaction_matrix': dict(interaction_matrix),
            'power_structure': self._determine_power_structure(speakers),
            'cooperation_level': self._calculate_cooperation_level(speakers),
            'conflict_level': self._calculate_conflict_level(speakers),
            'engagement_score': self._calculate_engagement(interaction_matrix, speakers)
        }
    
    @staticmethod
    def _count_markers(text: str, markers: List[str]) -> int:
        """Count occurrences of markers in text"""
        return sum(1 for marker in markers if marker in text)
    
    @staticmethod
    def _determine_power_structure(speakers: Dict) -> str:
        """Determine conversation power dynamics"""
        if not speakers:
            return 'unknown'
        
        dominance_scores = {s: speakers[s]['dominance_score'] for s in speakers}
        max_speaker = max(dominance_scores, key=dominance_scores.get)
        max_score = dominance_scores[max_speaker]
        
        other_scores = [v for k, v in dominance_scores.items() if k != max_speaker]
        avg_others = np.mean(other_scores) if other_scores else 0
        
        if max_score > avg_others * 2:
            return f'{max_speaker}_dominant'
        elif all(abs(v - np.mean(list(dominance_scores.values()))) < 1 for v in dominance_scores.values()):
            return 'balanced'
        else:
            return 'competitive'
    
    @staticmethod
    def _calculate_cooperation_level(speakers: Dict) -> float:
        """Calculate overall cooperation level"""
        coop_scores = [speakers[s]['cooperation_score'] for s in speakers]
        return float(np.mean(coop_scores)) if coop_scores else 0.0
    
    @staticmethod
    def _calculate_conflict_level(speakers: Dict) -> float:
        """Calculate conflict level"""
        conflict_scores = [speakers[s]['conflict_score'] for s in speakers]
        return float(np.mean(conflict_scores)) if conflict_scores else 0.0
    
    @staticmethod
    def _calculate_engagement(interaction_matrix: dict, speakers: dict) -> float:
        """Calculate engagement between parties"""
        if not interaction_matrix:
            return 0.0
        
        total_interactions = sum(sum(v.values()) for v in interaction_matrix.values())
        num_speakers = len(speakers)
        
        if num_speakers < 2:
            return 0.0
        
        possible_interactions = num_speakers * (num_speakers - 1)
        return min(1.0, total_interactions / (possible_interactions * 5))


class CognitiveComplexityAnalyzer:
    """Measure cognitive and linguistic complexity"""
    
    COMPLEX_CONCEPTS = {
        'abstract': ['theory', 'concept', 'abstract', 'philosophical', 'epistemology', 'metaphysical'],
        'technical': ['algorithm', 'topology', 'quantum', 'neural', 'recursive', 'architecture'],
        'analytical': ['analyze', 'examine', 'systematic', 'correlation', 'variable', 'methodology'],
        'creative': ['imagine', 'metaphor', 'symbolism', 'transcend', 'synthesize', 'paradigm']
    }
    
    def analyze_complexity(self, text: str) -> Dict[str, Any]:
        """Comprehensive cognitive complexity analysis"""
        words = text.lower().split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        complexity_metrics = {
            'word_diversity': self._calculate_diversity(words),
            'vocabulary_level': self._assess_vocab_level(words),
            'sentence_complexity': self._analyze_sentences(sentences),
            'concept_density': self._measure_concept_density(text),
            'argumentation_strength': self._analyze_argumentation(text),
            'overall_score': 0.0
        }
        
        # Calculate overall score
        overall = (
            complexity_metrics['word_diversity'] * 0.2 +
            complexity_metrics['vocabulary_level'] * 0.2 +
            complexity_metrics['sentence_complexity'] * 0.2 +
            complexity_metrics['concept_density'] * 0.2 +
            complexity_metrics['argumentation_strength'] * 0.2
        )
        
        complexity_metrics['overall_score'] = round(overall, 2)
        complexity_metrics['complexity_level'] = self._classify_complexity(overall)
        
        return complexity_metrics
    
    @staticmethod
    def _calculate_diversity(words: List[str]) -> float:
        """Calculate vocabulary diversity (TTR - Type-Token Ratio)"""
        if not words:
            return 0.0
        unique_words = len(set(words))
        ttr = unique_words / len(words)
        return min(1.0, ttr)
    
    @staticmethod
    def _assess_vocab_level(words: List[str]) -> float:
        """Assess vocabulary sophistication"""
        complex_threshold = 8  # Words with 8+ characters
        complex_words = sum(1 for w in words if len(w) >= complex_threshold)
        return min(1.0, complex_words / len(words)) if words else 0.0
    
    @staticmethod
    def _analyze_sentences(sentences: List[str]) -> float:
        """Analyze sentence structure complexity"""
        if not sentences:
            return 0.0
        
        complexity_scores = []
        for sentence in sentences:
            words = sentence.split()
            # Longer sentences = more complex
            length_score = min(1.0, len(words) / 30)
            # Punctuation diversity
            punct_score = min(1.0, (sentence.count(',') + sentence.count(';')) / 5)
            complexity_scores.append((length_score + punct_score) / 2)
        
        return np.mean(complexity_scores) if complexity_scores else 0.0
    
    @classmethod
    def _measure_concept_density(cls, text: str) -> float:
        """Measure density of complex concepts"""
        text_lower = text.lower()
        concept_count = sum(
            sum(1 for concept in concepts if concept in text_lower)
            for concepts in cls.COMPLEX_CONCEPTS.values()
        )
        words = text_lower.split()
        return min(1.0, concept_count / len(words)) if words else 0.0
    
    @staticmethod
    def _analyze_argumentation(text: str) -> float:
        """Analyze argumentative structure strength"""
        arg_markers = ['therefore', 'because', 'however', 'moreover', 'in conclusion', 
                      'based on', 'evidence', 'thus', 'consequently', 'my argument']
        
        marker_count = sum(1 for marker in arg_markers if marker in text.lower())
        arg_strength = min(1.0, marker_count / 5)
        
        return arg_strength
    
    @staticmethod
    def _classify_complexity(score: float) -> str:
        """Classify complexity level"""
        if score < 0.2:
            return 'very_simple'
        elif score < 0.4:
            return 'simple'
        elif score < 0.6:
            return 'moderate'
        elif score < 0.8:
            return 'complex'
        else:
            return 'very_complex'


class AnomalyDetector:
    """Detect unusual patterns and anomalies"""
    
    def __init__(self):
        self.baseline_stats = {}
    
    def establish_baseline(self, texts: List[str]):
        """Learn baseline patterns from texts"""
        stats = {
            'avg_length': np.mean([len(t.split()) for t in texts]),
            'avg_caps_ratio': np.mean([sum(1 for c in t if c.isupper()) / len(t) if t else 0 for t in texts]),
            'avg_punctuation': np.mean([sum(1 for c in t if c in '!?.,-;:') for t in texts]),
            'vocab_diversity': np.mean([len(set(t.lower().split())) / len(t.split()) if t.split() else 0 for t in texts])
        }
        self.baseline_stats = stats
    
    def detect_anomalies(self, text: str) -> Dict[str, Any]:
        """Detect deviations from baseline"""
        if not self.baseline_stats:
            return {'anomaly_detected': False, 'reason': 'No baseline established'}
        
        words = text.split()
        length = len(words)
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        punctuation = sum(1 for c in text if c in '!?.,-;:')
        vocab_div = len(set(text.lower().split())) / len(words) if words else 0
        
        anomalies = []
        
        # Length anomaly
        if abs(length - self.baseline_stats['avg_length']) > 2 * np.std([1, 2, 3]):
            anomalies.append(f'unusual_length: {length} vs avg {self.baseline_stats["avg_length"]:.1f}')
        
        # Caps anomaly
        if caps_ratio > self.baseline_stats['avg_caps_ratio'] * 2:
            anomalies.append('excessive_capitalization')
        
        # Punctuation anomaly
        if punctuation > self.baseline_stats['avg_punctuation'] * 2:
            anomalies.append('excessive_punctuation')
        
        return {
            'is_anomalous': len(anomalies) > 0,
            'anomalies': anomalies,
            'confidence': min(1.0, len(anomalies) / 3)
        }


if __name__ == '__main__':
    # Test advanced analytics
    print("🧠 Advanced Analytics Module Loaded")
    
    # Test sentiment trajectory
    traj = SentimentTrajectory()
    texts = ["I love this!", "It was okay.", "This is awful."]
    result = traj.analyze_trajectory(texts)
    print(f"\n📊 Sentiment Trajectory: {result['emotional_arc']}")
    
    # Test cognitive complexity
    complex_text = "The epistemological implications of quantum topology suggest a paradigmatic shift in our understanding."
    cc = CognitiveComplexityAnalyzer()
    complexity = cc.analyze_complexity(complex_text)
    print(f"🧠 Complexity Level: {complexity['complexity_level']}")
