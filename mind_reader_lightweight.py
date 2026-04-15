#!/usr/bin/env python3
"""
Mind Reader AI System - Lightweight Standalone Implementation
Works with minimal dependencies - no heavy ML frameworks required
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any
from collections import Counter


# ============================================================================
# SECTION 1: FEATURE ENGINEER (Lightweight)
# ============================================================================

class FeatureEngineer:
    """Extract linguistic features without heavy dependencies"""
    
    EMOTION_MARKERS = {
        'happy': ['happy', 'joy', 'love', 'amazing', 'wonderful', 'excellent', 'fantastic', 'excited', 'delighted', 'thrilled'],
        'sad': ['sad', 'depressed', 'miserable', 'lonely', 'down', 'devastated', 'broken', 'suffering', 'hopeless'],
        'angry': ['angry', 'furious', 'hate', 'infuriating', 'rage', 'seething', 'livid', 'enraged'],
        'neutral': ['the', 'a', 'is', 'was', 'report', 'meeting', 'work', 'do', 'schedule']
    }
    
    PERSONALITY_MARKERS = {
        'introvert': ['prefer', 'quiet', 'alone', 'friend', 'deep', 'small', 'think', 'alone', 'solitary'],
        'extrovert': ['love', 'party', 'people', 'social', 'outgoing', 'spontaneous', 'meet', 'fun'],
        'creative': ['idea', 'art', 'create', 'imagine', 'novel', 'invent', 'design'],
        'aggressive': ['direct', 'assertive', 'competitive', 'win', 'bold', 'dare'],
        'confident': ['believe', 'sure', 'trust', 'able', 'secure', 'strong']
    }
    
    DECEPTIVE_WORDS = {'um', 'uh', 'umm', 'err', 'hmm', 'like', 'maybe', 'might', 'perhaps', 'sort of', 'kind of'}
    DANGER_WORDS = {'hate', 'kill', 'destroy', 'hurt', 'violent', 'harm', 'attack'}
    
    @staticmethod
    def extract_features(text: str) -> Dict[str, any]:
        """Extract features from text"""
        text_lower = text.lower()
        words = text_lower.split()
        
        return {
            'word_count': len(words),
            'sentence_count': len(text.split('.')),
            'exclamation_count': text.count('!'),
            'question_count': text.count('?'),
            'caps_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            'unique_words': len(set(words)),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'hesitation_count': sum(1 for w in FeatureEngineer.DECEPTIVE_WORDS if w in text_lower),
            'danger_words_count': sum(1 for w in FeatureEngineer.DANGER_WORDS if w in text_lower),
            'polarity_score': FeatureEngineer.calculate_sentiment(text_lower)
        }
    
    @staticmethod
    def calculate_sentiment(text: str) -> float:
        """Simple sentiment score (-1 to 1)"""
        positive_words = set(['love', 'happy', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic'])
        negative_words = set(['hate', 'sad', 'bad', 'terrible', 'awful', 'horrible', 'disgusting'])
        
        words = set(text.lower().split())
        pos_count = len(words & positive_words)
        neg_count = len(words & negative_words)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        
        return (pos_count - neg_count) / total


# ============================================================================
# SECTION 2: LIGHTWEIGHT ANALYZERS
# ============================================================================

class EmotionAnalyzer:
    """Lightweight emotion detection based on keyword matching"""
    
    def __init__(self):
        self.emotion_keywords = FeatureEngineer.EMOTION_MARKERS
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze emotion"""
        text_lower = text.lower()
        
        scores = {}
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[emotion] = score
        
        # Normalize scores
        total = sum(scores.values())
        if total == 0:
            normalized = {e: 0.25 for e in scores}
        else:
            normalized = {e: s / total for e, s in scores.items()}
        
        dominant_emotion = max(normalized, key=normalized.get)
        confidence = normalized[dominant_emotion]
        
        return {
            'emotion': dominant_emotion,
            'confidence': confidence,
            'all_emotions': normalized
        }


class PersonalityAnalyzer:
    """Lightweight personality detection"""
    
    def __init__(self):
        self.trait_keywords = FeatureEngineer.PERSONALITY_MARKERS
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze personality"""
        text_lower = text.lower()
        
        scores = {}
        for trait, keywords in self.trait_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[trait] = score
        
        # Normalize
        total = sum(scores.values()) if scores else 1
        if total == 0:
            total = 1
        normalized = {t: s / total for t, s in scores.items()}
        
        dominant_trait = max(normalized, key=normalized.get)
        
        return {
            'dominant_trait': dominant_trait,
            'trait_scores': {t: int(s * 100) for t, s in normalized.items()},
            'secondary_traits': sorted(normalized.items(), key=lambda x: x[1], reverse=True)[1:3]
        }


class DeceptionDetector:
    """Detect deception using linguistic markers"""
    
    def calculate_score(self, text: str) -> Dict[str, Any]:
        """Calculate deception probability"""
        text_lower = text.lower()
        
        deceptive_indicators = {
            'hesitation_words': sum(1 for w in ['um', 'uh', 'umm', 'err', 'hmm'] if w in text_lower),
            'uncertain_words': sum(1 for w in ['maybe', 'perhaps', 'might', 'could'] if w in text_lower),
            'vague_language': sum(1 for w in ['sort of', 'kind of', 'i think', 'apparently'] if w in text_lower),
            'self_reference_count': text_lower.count('i ') + text_lower.count('me '),
            'sentence_length': len(text.split('.'))
        }
        
        # Calculate score
        deception_score = (
            (deceptive_indicators['hesitation_words'] * 0.15 +
             deceptive_indicators['uncertain_words'] * 0.20 +
             deceptive_indicators['vague_language'] * 0.25) / max(1, len(text.split()))
        )
        
        deception_probability = min(1.0, deception_score * 2)
        
        if deception_probability > 0.6:
            interpretation = "Probably deceptive"
        elif deception_probability > 0.4:
            interpretation = "Possibly deceptive"
        else:
            interpretation = "Probably truthful"
        
        return {
            'deception_probability': deception_probability,
            'interpretation': interpretation,
            'model_score': deception_probability
        }


class DangerDetector:
    """Detect danger/toxicity"""
    
    def calculate_score(self, text: str) -> Dict[str, Any]:
        """Calculate danger score"""
        text_lower = text.lower()
        
        danger_keywords = {
            'violence': ['kill', 'hurt', 'destroy', 'violent', 'attack', 'harm', 'assault', 'murder'],
            'self_harm': ['suicide', 'kill myself', 'harm myself', 'hurt myself'],
            'toxicity': ['hate', 'evil', 'worst', 'disgusting', 'horrible'],
            'aggression': ['fight', 'punch', 'hit', 'attack', 'kick']
        }
        
        danger_score = 0
        triggers_found = []
        
        for category, keywords in danger_keywords.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            if count > 0:
                danger_score += count * 0.15
                triggers_found.append(f"{category}({count})")
        
        danger_score = min(1.0, danger_score)
        
        if danger_score > 0.7:
            risk_level = "🔴 High Risk"
            recommendation = "Requires immediate attention"
        elif danger_score > 0.5:
            risk_level = "🟠 Medium Risk"
            recommendation = "Monitor closely"
        elif danger_score > 0.3:
            risk_level = "🟡 Low Risk"
            recommendation = "Low risk detected"
        else:
            risk_level = "🟢 Very Low Risk"
            recommendation = "Safe"
        
        return {
            'danger_score': danger_score,
            'risk_level': risk_level,
            'recommendation': recommendation,
            'triggers': triggers_found
        }


class BehaviorPredictor:
    """Predict future behaviors"""
    
    def predict(self, emotion: str, personality_traits: List[str]) -> Dict[str, Any]:
        """Predict behavior"""
        
        behavior_map = {
            'happy': ['engage in activities', 'help others', 'seek social interaction'],
            'sad': ['seek support', 'reflect', 'may withdraw'],
            'angry': ['express strongly', 'confront issues', 'seek resolution'],
            'neutral': ['continue routines', 'work', 'plan']
        }
        
        trajectory_map = {
            'happy': 'likely to remain positive',
            'sad': 'may improve with support',
            'angry': 'likely to build towards resolution',
            'neutral': 'likely to stabilize'
        }
        
        predicted_actions = behavior_map.get(emotion.lower(), ['continue current activities'])
        trajectory = trajectory_map.get(emotion.lower(), 'likely to stabilize')
        
        return {
            'predicted_actions': predicted_actions,
            'emotional_trajectory': trajectory,
            'confidence_score': 0.75
        }


# ============================================================================
# SECTION 3: MIND SCORE API (Main Interface)
# ============================================================================

class MindScoreAPI:
    """Unified API for comprehensive analysis"""
    
    def __init__(self):
        self.emotion_analyzer = EmotionAnalyzer()
        self.personality_analyzer = PersonalityAnalyzer()
        self.deception_detector = DeceptionDetector()
        self.danger_detector = DangerDetector()
        self.behavior_predictor = BehaviorPredictor()
        self.feature_engineer = FeatureEngineer()
        self.interaction_history = []
    
    def analyze(self, text: str, detailed: bool = True) -> Dict[str, Any]:
        """Comprehensive analysis of the input text"""
        
        # Extract features
        features = self.feature_engineer.extract_features(text)
        
        # Analyze everything
        emotion_result = self.emotion_analyzer.analyze(text)
        personality_result = self.personality_analyzer.analyze(text)
        lie_result = self.deception_detector.calculate_score(text)
        danger_result = self.danger_detector.calculate_score(text)
        behavior_result = self.behavior_predictor.predict(
            emotion_result['emotion'],
            [personality_result['dominant_trait']]
        )
        
        # Calculate mind score
        mind_score = self._calculate_mind_score(emotion_result, lie_result, danger_result)
        
        # Compile results
        result = {
            'timestamp': datetime.now().isoformat(),
            'input_summary': {
                'text_length': len(text),
                'word_count': len(text.split())
            },
            'emotion_analysis': emotion_result,
            'personality_analysis': personality_result,
            'lie_detection': {
                'deception_probability': lie_result['deception_probability'],
                'interpretation': lie_result['interpretation']
            },
            'danger_detection': danger_result,
            'behavior_prediction': behavior_result,
            'mind_score': mind_score,
            'extracted_features': features if detailed else None
        }
        
        self.interaction_history.append(result)
        return result
    
    def _calculate_mind_score(self, emotion, lie, danger) -> Dict[str, Any]:
        """Calculate overall mind score (0-100)"""
        
        # Component scores
        emotional_stability = (1 - abs(emotion['confidence'] - 1)) * 100
        integrity_score = (1 - lie['deception_probability']) * 100
        safety_score = (1 - danger['danger_score']) * 100
        
        # Weighted average
        mind_score = (
            emotional_stability * 0.30 +
            integrity_score * 0.35 + 
            safety_score * 0.35
        )
        
        # Interpretation
        if mind_score >= 85:
            interpretation = "Exceptional clarity and authenticity"
        elif mind_score >= 70:
            interpretation = "Good psychological coherence"
        elif mind_score >= 55:
            interpretation = "Moderate coherence with some tensions"
        elif mind_score >= 40:
            interpretation = "Significant psychological tensions"
        else:
            interpretation = "Critical coherence issues"
        
        return {
            'overall_score': round(mind_score, 2),
            'interpretation': interpretation,
            'score_range': '0-100'
        }
    
    def batch_analyze(self, texts: List[str]) -> List[Dict]:
        """Analyze multiple texts"""
        return [self.analyze(text, detailed=False) for text in texts]
    
    def get_history(self) -> List[Dict]:
        """Get analysis history"""
        return self.interaction_history
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from history"""
        if not self.interaction_history:
            return {'total_analyses': 0}
        
        emotions = [r['emotion_analysis']['emotion'] for r in self.interaction_history]
        scores = [r['mind_score']['overall_score'] for r in self.interaction_history]
        
        emotions_count = Counter(emotions)
        
        return {
            'total_analyses': len(self.interaction_history),
            'emotion_distribution': dict(emotions_count),
            'average_mind_score': sum(scores) / len(scores) if scores else 0,
            'min_score': min(scores) if scores else 0,
            'max_score': max(scores) if scores else 100
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    print("\n" + "="*80)
    print("🧠 MIND READER AI SYSTEM - LIGHTWEIGHT STANDALONE")
    print("="*80 + "\n")
    
    # Initialize API
    mind_score_api = MindScoreAPI()
    
    # Test cases
    test_texts = [
        "I'm so happy and excited about this amazing opportunity!",
        "I feel devastated and hopeless about what happened",
        "I hate this and everything about it is infuriating!!!",
        "The meeting is scheduled for tomorrow at 2 PM",
        "Well, um, I think maybe I wasn't there, um, you know?",
    ]
    
    print("🧪 RUNNING COMPREHENSIVE ANALYSIS TESTS:\n")
    
    for i, text in enumerate(test_texts, 1):
        print(f"{'─'*80}")
        print(f"TEST {i}: \"{text}\"")
        print(f"{'─'*80}")
        
        result = mind_score_api.analyze(text, detailed=False)
        
        # Display results
        print(f"📊 EMOTION: {result['emotion_analysis']['emotion'].upper()}")
        print(f"   Confidence: {result['emotion_analysis']['confidence']:.0%}")
        
        print(f"\n👤 PERSONALITY: {result['personality_analysis']['dominant_trait'].upper()}")
        trait_scores = result['personality_analysis']['trait_scores']
        for trait, score in sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"   {trait.capitalize()}: {score}%")
        
        print(f"\n🕵️  DECEPTION: {result['lie_detection']['deception_probability']:.0%}")
        print(f"   Interpretation: {result['lie_detection']['interpretation']}")
        
        print(f"\n⚠️  DANGER: {result['danger_detection']['risk_level']}")
        print(f"   {result['danger_detection']['recommendation']}")
        
        print(f"\n🧠 MIND SCORE: {result['mind_score']['overall_score']}/100")
        print(f"   {result['mind_score']['interpretation']}")
        print()
    
    # Statistics
    print("\n" + "="*80)
    print("📊 SYSTEM STATISTICS")
    print("="*80 + "\n")
    
    stats = mind_score_api.get_statistics()
    print(f"Total Analyses Performed: {stats['total_analyses']}")
    print(f"Average Mind Score: {stats['average_mind_score']:.1f}/100")
    print(f"Score Range: {stats['min_score']:.1f} - {stats['max_score']:.1f}")
    print(f"\nEmotion Distribution:")
    for emotion, count in stats['emotion_distribution'].items():
        print(f"  {emotion.capitalize()}: {count} analyses")
    
    print("\n" + "="*80)
    print("✅ SYSTEM READY FOR USE")
    print("="*80 + "\n")
    
    print("💡 USAGE EXAMPLES:")
    print("   result = mind_score_api.analyze('Your text here')")
    print("   history = mind_score_api.get_history()")
    print("   stats = mind_score_api.get_statistics()")
    print("   results = mind_score_api.batch_analyze(['text1', 'text2'])\n")
    
    return mind_score_api


if __name__ == "__main__":
    api = main()
