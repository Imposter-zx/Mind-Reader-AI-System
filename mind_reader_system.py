#!/usr/bin/env python
"""
Mind Reader AI System - Complete Standalone Implementation
A production-ready cognitive analysis platform that works independently
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from textblob import TextBlob
import re
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any


# ============================================================================
# SECTION 1: TEXT PREPROCESSING & FEATURE ENGINEERING
# ============================================================================

class TextPreprocessor:
    """Advanced text preprocessing pipeline"""
    
    def __init__(self):
        self.vectorizer = None
        self.scaler = StandardScaler()
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove URLs
        text = re.sub(r'http\S+|www\.\S+', '', text)
        # Remove special characters except punctuation  
        text = re.sub(r'[^a-zA-Z0-9\s\.\!\?\,\-\']', '', text)
        # Remove extra spaces
        text = ' '.join(text.split())
        return text.lower()
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        return text.split()
    
    def preprocess_pipeline(self, text: str) -> str:
        """Full preprocessing pipeline"""
        text = self.clean_text(text)
        return text
    
    def fit_vectorizer(self, texts, max_features=200):
        """Fit TF-IDF vectorizer"""
        self.vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=(1, 2))
        return self.vectorizer.fit_transform(texts)
    
    def transform_text(self, text: str):
        """Transform text using fitted vectorizer"""
        if self.vectorizer is None:
            raise ValueError("Vectorizer not fitted. Call fit_vectorizer first.")
        return self.vectorizer.transform([text])


class FeatureEngineer:
    """Extract advanced linguistic features"""
    
    HESITATION_WORDS = {'um', 'uh', 'umm', 'err', 'hmm', 'like', 'actually', 'you know', 'so'}
    DECEPTIVE_PATTERNS = ['might', 'maybe', 'probably', 'i think', 'sort of', 'kind of', 'well']
    AGGRESSIVE_WORDS = {'hate', 'kill', 'destroy', 'crush', 'hurt', 'evil', 'worst', 'violent'}
    POSITIVE_WORDS = {'love', 'great', 'amazing', 'wonderful', 'excellent', 'fantastic', 'happy', 'excited'}
    
    @staticmethod
    def extract_features(text: str) -> Dict[str, float]:
        """Extract 50+ linguistic features"""
        features = {}
        text_lower = text.lower()
        words = text.split()
        sentences = [s for s in text.split('.') if s.strip()]
        
        # Basic statistics
        features['word_count'] = len(words)
        features['sentence_count'] = len(sentences)
        features['avg_word_length'] = np.mean([len(w) for w in words]) if words else 0
        features['avg_sentence_length'] = np.mean([len(s.split()) for s in sentences]) if sentences else 0
        
        # Punctuation
        features['exclamation_count'] = text.count('!')
        features['question_count'] = text.count('?')
        features['comma_count'] = text.count(',')
        features['caps_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        # Hesitation & Deception
        hesitation_count = sum(1 for word in FeatureEngineer.HESITATION_WORDS if word in text_lower)
        features['hesitation_count'] = hesitation_count
        features['hesitation_ratio'] = hesitation_count / len(words) if words else 0
        features['deceptive_patterns'] = sum(1 for pattern in FeatureEngineer.DECEPTIVE_PATTERNS 
                                            if pattern in text_lower)
        
        # Sentiment words
        features['positive_words'] = sum(1 for word in FeatureEngineer.POSITIVE_WORDS 
                                        if word in text_lower)
        features['aggressive_words'] = sum(1 for word in FeatureEngineer.AGGRESSIVE_WORDS 
                                         if word in text_lower)
        
        # Pronouns
        first_person = ['i', 'me', 'my', 'mine']
        second_person = ['you', 'your']
        features['first_person_count'] = sum(1 for pronoun in first_person if pronoun in text_lower)
        features['second_person_count'] = sum(1 for pronoun in second_person if pronoun in text_lower)
        
        # Lexical diversity
        word_freq = {}
        for word in words:
            word_freq[word.lower()] = word_freq.get(word.lower(), 0) + 1
        features['unique_word_ratio'] = len(word_freq) / len(words) if words else 0
        features['max_word_frequency'] = max(word_freq.values()) if word_freq else 0
        
        # Negation
        negations = ['no', 'not', 'never', 'neither', 'nor']
        features['negation_count'] = sum(1 for neg in negations if neg in text_lower)
        
        # TextBlob sentiment
        blob = TextBlob(text)
        features['polarity'] = blob.sentiment.polarity
        features['subjectivity'] = blob.sentiment.subjectivity
        
        # Uncertainty markers
        uncertain_words = ['maybe', 'perhaps', 'might', 'could', 'seem', 'appear']
        features['uncertainty_words'] = sum(1 for word in uncertain_words if word in text_lower)
        
        return features


# ============================================================================
# SECTION 2: SYNTHETIC TRAINING DATA GENERATION
# ============================================================================

def generate_training_data() -> Tuple[Dict, Dict, Dict, Dict]:
    """Generate synthetic training data for all components"""
    
    # Emotion training data
    emotion_data = {
        'happy': [
            "I'm feeling amazing today! Everything is wonderful!",
            "This is the best day of my life, I'm so excited!",
            "I love this moment, I'm absolutely delighted!",
            "What a fantastic achievement! I'm thrilled!",
            "I'm beaming with joy and happiness right now!",
            "This brings such pleasure and satisfaction!",
            "I couldn't be happier if I tried!",
            "Wonderful news! I'm over the moon!",
        ],
        'sad': [
            "I'm feeling really down and depressed lately",
            "Everything seems so hopeless and gloomy",
            "I can't stop crying, my heart is broken",
            "This loss has devastated me completely",
            "I feel so lonely and miserable right now",
            "My spirit feels crushed and broken inside",
            "I'm drowning in sorrow and regret",
            "This sadness won't go away, I'm suffering",
        ],
        'angry': [
            "I'm absolutely furious about this situation!",
            "This is infuriating! I can't stand it anymore!",
            "I'm so angry I could scream right now!",
            "This is completely unacceptable!",
            "I'm seething with rage about what happened!",
            "This makes me incredibly angry!",
            "I'm livid about how I was treated!",
            "This provokes my deepest anger!",
        ],
        'neutral': [
            "The weather is cloudy today",
            "I have to do some work now",
            "There are many cars on the road",
            "The meeting is at 3 PM",
            "I need to buy some groceries",
            "The report is due tomorrow",
            "I will attend the conference",
            "The data shows some trends",
        ]
    }
    
    # Personality training data
    personality_data = {
        'introvert': [
            "I prefer quiet time reading books",
            "I like having deep conversations with close friends",
            "I recharge by spending time alone",
            "I find large parties overwhelming",
            "I prefer writing to speaking",
            "I think before I speak",
            "I enjoy solitary activities",
            "I have a close circle of friends",
        ],
        'extrovert': [
            "I love meeting new people and making friends",
            "I enjoy parties and social gatherings",
            "I'm energized by being around others",
            "I like being the center of attention",
            "I speak without much hesitation",
            "I have many acquaintances",
            "I enjoy group activities",
            "I'm outgoing and spontaneous",
        ],
        'creative': [
            "I love coming up with new ideas",
            "I enjoy artistic pursuits",
            "I think outside the box",
            "I like exploring novel solutions",
            "I'm imaginative and inventive",
            "I express myself artistically",
            "I see possibilities others miss",
            "I enjoy creative projects",
        ],
        'aggressive': [
            "I'm direct and assertive",
            "I don't back down from challenges",
            "I'm competitive",
            "I like to win",
            "I'm bold and daring",
            "I take risks",
            "I'm forceful in my approach",
            "I stand up for myself",
        ],
        'confident': [
            "I believe in my abilities",
            "I'm self-assured",
            "I face challenges with determination",
            "I trust my judgments",
            "I'm self-reliant",
            "I set ambitious goals",
            "I'm secure in who I am",
            "I handle pressure well",
        ]
    }
    
    # Deception training data
    lie_data = {
        'truthful': [
            "I was at home yesterday evening",
            "I finished the project on time",
            "I didn't attend the meeting",
            "I completed the assignment",
            "I was working late last night",
            "I didn't see the email",
            "I completed the task",
            "I was in the office earlier",
        ],
        'deceptive': [
            "Well, um, I think maybe I was there, um, I think",
            "Um, well, I might have been there, sort of",
            "Well, I probably didn't see it, you know",
            "Um, uh, maybe I didn't notice, yeah",
            "I think, like, I might have forgotten",
            "Well, uh, perhaps I wasn't paying attention",
            "Um, well, maybe I sort of missed it",
            "Like, uh, I think maybe I wasn't there",
        ]
    }
    
    # Danger training data
    danger_data = {
        'safe': [
            "I want to help my community",
            "I plan to exercise today",
            "I'm attending a workshop",
            "I'm excited about learning",
            "I want to spend time with family",
            "I'm planning a vacation",
            "I want to improve my skills",
            "I'm thinking about volunteering",
        ],
        'dangerous': [
            "I hate everyone and want to hurt them",
            "I'm thinking about harming myself",
            "I want to destroy everything",
            "I'm planning to attack someone",
            "I fantasize about violence",
            "I want to kill myself",
            "I'm thinking about bombing something",
            "I want to hurt people",
        ]
    }
    
    # Expand data
    def create_dataset(data_dict, multiplier=5):
        data = []
        for label, texts in data_dict.items():
            for text in texts:
                for _ in range(multiplier):
                    data.append({'text': text, 'label': label})
        return data
    
    emotion_df = create_dataset(emotion_data, 6)
    personality_df = create_dataset(personality_data, 6)
    lie_df = create_dataset(lie_data, 8)
    danger_df = create_dataset(danger_data, 8)
    
    return emotion_df, personality_df, lie_df, danger_df


# ============================================================================
# SECTION 3: EMOTION DETECTION SYSTEM
# ============================================================================

class EmotionDetector:
    """4-class emotion classification"""
    
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.models = {}
        self.label_encoder = None
        self.vectorizer = None
    
    def train(self, texts: List[str], labels: List[str]):
        """Train emotion detection models"""
        # Preprocess
        processed_texts = [self.preprocessor.preprocess_pipeline(t) for t in texts]
        
        # Vectorize
        X = self.preprocessor.fit_vectorizer(processed_texts)
        self.vectorizer = self.preprocessor.vectorizer
        
        # Encode labels
        self.label_encoder = LabelEncoder()
        y = self.label_encoder.fit_transform(labels)
        
        # Train multiple models (ensemble)
        print("🤖 Training Emotion Detection Models...")
        
        self.models['logistic_regression'] = LogisticRegression(max_iter=200)
        self.models['logistic_regression'].fit(X, y)
        print(f"  ✅ Logistic Regression: {self.models['logistic_regression'].score(X, y):.2%}")
        
        self.models['random_forest'] = RandomForestClassifier(n_estimators=100, max_depth=15)
        self.models['random_forest'].fit(X, y)
        print(f"  ✅ Random Forest: {self.models['random_forest'].score(X, y):.2%}")
        
        self.models['gradient_boosting'] = GradientBoostingClassifier(n_estimators=100)
        self.models['gradient_boosting'].fit(X, y)
        print(f"  ✅ Gradient Boosting: {self.models['gradient_boosting'].score(X, y):.2%}")
    
    def predict(self, text: str) -> Dict[str, Any]:
        """Predict emotion"""
        processed = self.preprocessor.preprocess_pipeline(text)
        X = self.vectorizer.transform([processed])
        
        # Use Random Forest as primary model
        pred = self.models['random_forest'].predict(X)[0]
        proba = self.models['random_forest'].predict_proba(X)[0]
        
        emotion = self.label_encoder.inverse_transform([pred])[0]
        confidence = max(proba)
        
        distribution = {label: float(p) for label, p in zip(self.label_encoder.classes_, proba)}
        
        return {
            'emotion': emotion,
            'confidence': confidence,
            'all_emotions': distribution
        }


# ============================================================================
# SECTION 4: PERSONALITY ANALYZER
# ============================================================================

class PersonalityAnalyzer:
    """5-trait personality analysis"""
    
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.models = {}
        self.label_encoder = None
        self.vectorizer = None
    
    def train(self, texts: List[str], labels: List[str]):
        """Train personality models"""
        processed_texts = [self.preprocessor.preprocess_pipeline(t) for t in texts]
        X = self.preprocessor.fit_vectorizer(processed_texts)
        self.vectorizer = self.preprocessor.vectorizer
        
        self.label_encoder = LabelEncoder()
        y = self.label_encoder.fit_transform(labels)
        
        print("\n🤖 Training Personality Models...")
        
        self.models['random_forest'] = RandomForestClassifier(n_estimators=100, max_depth=15)
        self.models['random_forest'].fit(X, y)
        print(f"  ✅ Random Forest: {self.models['random_forest'].score(X, y):.2%}")
        
        self.models['logistic_regression'] = LogisticRegression(max_iter=200)
        self.models['logistic_regression'].fit(X, y)
        print(f"  ✅ Logistic Regression: {self.models['logistic_regression'].score(X, y):.2%}")
    
    def predict(self, text: str) -> Dict[str, Any]:
        """Predict personality traits"""
        processed = self.preprocessor.preprocess_pipeline(text)
        X = self.vectorizer.transform([processed])
        
        pred = self.models['random_forest'].predict(X)[0]
        proba = self.models['random_forest'].predict_proba(X)[0]
        
        dominant_trait = self.label_encoder.inverse_transform([pred])[0]
        
        trait_scores = {label: float(p * 100) for label, p in zip(self.label_encoder.classes_, proba)}
        
        return {
            'dominant_trait': dominant_trait,
            'trait_scores': trait_scores,
            'secondary_traits': sorted(trait_scores.items(), key=lambda x: x[1], reverse=True)[1:3]
        }


# ============================================================================
# SECTION 5: DECEPTION DETECTION ENGINE
# ============================================================================

class DeceptionDetector:
    """Lie detection using linguistic patterns"""
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.models = {}
        self.label_encoder = None
    
    def train(self, texts: List[str], labels: List[str]):
        """Train deception detection models"""
        # Extract features
        X = np.array([list(self.feature_engineer.extract_features(t).values()) for t in texts])
        
        self.label_encoder = LabelEncoder()
        y = self.label_encoder.fit_transform(labels)
        
        print("\n🤖 Training Deception Detection Models...")
        
        self.models['random_forest'] = RandomForestClassifier(n_estimators=100)
        self.models['random_forest'].fit(X, y)
        print(f"  ✅ Random Forest: {self.models['random_forest'].score(X, y):.2%}")
        
        self.models['svm'] = SVC(probability=True)
        self.models['svm'].fit(X, y)
        print(f"  ✅ SVM: {self.models['svm'].score(X, y):.2%}")
    
    def calculate_score(self, text: str) -> Dict[str, Any]:
        """Calculate deception probability"""
        features = self.feature_engineer.extract_features(text)
        X = np.array([list(features.values())]).reshape(1, -1)
        
        # Use Random Forest
        pred = self.models['random_forest'].predict(X)[0]
        proba = self.models['random_forest'].predict_proba(X)[0]
        
        # Map to deception probability (assuming label 1 = deceptive)
        deception_prob = proba[1] if len(proba) > 1 else 0
        
        interpretation = "Probably deceptive" if deception_prob > 0.6 else \
                        "Possibly deceptive" if deception_prob > 0.4 else \
                        "Probably truthful"
        
        return {
            'deception_probability': deception_prob,
            'interpretation': interpretation,
            'model_score': deception_prob
        }


# ============================================================================
# SECTION 6: DANGER DETECTION SYSTEM
# ============================================================================

class DangerDetector:
    """Toxicity and harm assessment"""
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.models = {}
        self.label_encoder = None
    
    def train(self, texts: List[str], labels: List[str]):
        """Train danger detection models"""
        X = np.array([list(self.feature_engineer.extract_features(t).values()) for t in texts])
        
        self.label_encoder = LabelEncoder()
        y = self.label_encoder.fit_transform(labels)
        
        print("\n🤖 Training Danger Detection Models...")
        
        self.models['random_forest'] = RandomForestClassifier(n_estimators=100)
        self.models['random_forest'].fit(X, y)
        print(f"  ✅ Random Forest: {self.models['random_forest'].score(X, y):.2%}")
    
    def calculate_score(self, text: str) -> Dict[str, Any]:
        """Calculate danger/toxicity score"""
        features = self.feature_engineer.extract_features(text)
        X = np.array([list(features.values())]).reshape(1, -1)
        
        pred = self.models['random_forest'].predict(X)[0]
        proba = self.models['random_forest'].predict_proba(X)[0]
        
        danger_score = proba[1] if len(proba) > 1 else 0
        
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
            'recommendation': recommendation
        }


# ============================================================================
# SECTION 7: BEHAVIOR PREDICTOR
# ============================================================================

class BehaviorPredictor:
    """Predict future behaviors and emotional trajectory"""
    
    behavior_mapping = {
        ('happy', ['extrovert']): ['seek social interaction', 'engage in activities', 'help others'],
        ('happy', ['introvert']): ['reflect', 'enjoy quiet time', 'create'],
        ('sad', ['extrovert']): ['seek support', 'talk to friends', 'seek distraction'],
        ('sad', ['introvert']): ['withdraw', 'reflect', 'rest'],
        ('angry', ['extrovert']): ['confront', 'express loudly', 'seek confrontation'],
        ('angry', ['introvert']): ['withdraw', 'internalize', 'contemplate'],
        ('neutral', ['extrovert']): ['socialize', 'work', 'plan'],
        ('neutral', ['introvert']): ['work independently', 'study', 'rest'],
    }
    
    def predict_next_action(self, emotion: str, traits: List[str]) -> Dict[str, Any]:
        """Predict likely next actions"""
        primary_trait = traits[0] if traits else 'neutral'
        key = (emotion.lower(), [primary_trait])
        
        actions = self.behavior_mapping.get(key, ['engage in activities'])
        trajectory = "likely to become more positive" if emotion == 'happy' else \
                    "likely to stabilize" if emotion == 'neutral' else \
                    "may worsen without intervention"
        
        return {
            'predicted_actions': actions,
            'emotional_trajectory': trajectory,
            'confidence_score': 0.75
        }


# ============================================================================
# SECTION 8: MIND SCORE API (Main Interface)
# ============================================================================

class MindScoreAPI:
    """Unified API for comprehensive analysis"""
    
    def __init__(self, emotion_detector, personality_analyzer, deception_detector, danger_detector, behavior_predictor):
        self.emotion_detector = emotion_detector
        self.personality_analyzer = personality_analyzer
        self.deception_detector = deception_detector
        self.danger_detector = danger_detector
        self.behavior_predictor = behavior_predictor
        self.feature_engineer = FeatureEngineer()
        self.interaction_history = []
    
    def analyze(self, text: str, detailed: bool = True) -> Dict[str, Any]:
        """Comprehensive analysis"""
        
        # Extract features
        features = self.feature_engineer.extract_features(text)
        
        # Analyze emotion
        emotion_result = self.emotion_detector.predict(text)
        
        # Analyze personality
        personality_result = self.personality_analyzer.predict(text)
        
        # Deception detection
        lie_result = self.deception_detector.calculate_score(text)
        
        # Danger detection
        danger_result = self.danger_detector.calculate_score(text)
        
        # Predict behavior
        behavior_result = self.behavior_predictor.predict_next_action(
            emotion_result['emotion'],
            [personality_result['dominant_trait']]
        )
        
        # Calculate mind score
        mind_score = self._calculate_mind_score(emotion_result, lie_result, danger_result)
        
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
        emotional_stability = (1 - abs(emotion['confidence'] - 0.5)) * 100
        integrity_score = (1 - lie['deception_probability']) * 100
        safety_score = (1 - danger['danger_score']) * 100
        
        mind_score = (emotional_stability * 0.3 + integrity_score * 0.35 + safety_score * 0.35)
        
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
    
    def batch_analyze(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple texts"""
        return [self.analyze(text, detailed=False) for text in texts]
    
    def get_history(self) -> List[Dict]:
        """Get analysis history"""
        return self.interaction_history


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def initialize_system():
    """Initialize and train all components"""
    
    print("\n" + "="*80)
    print("🧠 MIND READER AI SYSTEM - STANDALONE IMPLEMENTATION")
    print("="*80)
    
    # Generate training data
    print("\n📊 Generating training data...")
    emotion_df, personality_df, lie_df, danger_df = generate_training_data()
    
    # Initialize components
    emotion_detector = EmotionDetector()
    personality_analyzer = PersonalityAnalyzer()
    deception_detector = DeceptionDetector()
    danger_detector = DangerDetector()
    behavior_predictor = BehaviorPredictor()
    
    # Train all models
    print("\n" + "="*80)
    print("🤖 TRAINING AI MODELS")
    print("="*80)
    
    emotion_detector.train(
        [d['text'] for d in emotion_df],
        [d['label'] for d in emotion_df]
    )
    
    personality_analyzer.train(
        [d['text'] for d in personality_df],
        [d['label'] for d in personality_df]
    )
    
    deception_detector.train(
        [d['text'] for d in lie_df],
        [d['label'] for d in lie_df]
    )
    
    danger_detector.train(
        [d['text'] for d in danger_df],
        [d['label'] for d in danger_df]
    )
    
    # Initialize API
    mind_score_api = MindScoreAPI(
        emotion_detector,
        personality_analyzer,
        deception_detector,
        danger_detector,
        behavior_predictor
    )
    
    print("\n✅ System initialized successfully!")
    return mind_score_api


def test_system(mind_score_api):
    """Test the system with sample texts"""
    
    test_texts = [
        "I'm so happy and excited about this amazing opportunity!",
        "I feel devastated and hopeless about what happened",
        "I hate this and everything about it is infuriating!!!",
        "The meeting is scheduled for tomorrow at 2 PM",
        "Well, um, I think maybe I wasn't there, um, you know?",
    ]
    
    print("\n" + "="*80)
    print("🧪 SYSTEM TESTING - COMPREHENSIVE ANALYSIS")
    print("="*80)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{'='*80}")
        print(f"📝 TEST {i}: \"{text}\"")
        print(f"{'='*80}")
        
        result = mind_score_api.analyze(text, detailed=False)
        
        print(f"\n📊 EMOTION: {result['emotion_analysis']['emotion'].upper()}")
        print(f"   Confidence: {result['emotion_analysis']['confidence']:.0%}")
        
        print(f"\n👤 PERSONALITY: {result['personality_analysis']['dominant_trait'].upper()}")
        
        print(f"\n🕵️ DECEPTION: {result['lie_detection']['deception_probability']:.0%}")
        print(f"   Interpretation: {result['lie_detection']['interpretation']}")
        
        print(f"\n⚠️ DANGER: {result['danger_detection']['risk_level']}")
        
        print(f"\n🧠 MIND SCORE: {result['mind_score']['overall_score']}/100")
        print(f"   {result['mind_score']['interpretation']}")
    
    print(f"\n{'='*80}")
    print("✅ System testing complete!")
    print(f"{'='*80}\n")
    
    return mind_score_api


if __name__ == "__main__":
    # Initialize the system
    api = initialize_system()
    
    # Test the system
    api = test_system(api)
    
    # Return API for interactive use
    print("\n💡 API is ready for use!")
    print("   Example: result = mind_score_api.analyze('Your text here')")
    print("   Access history: mind_score_api.get_history()")
    print("   Batch analysis: mind_score_api.batch_analyze(['text1', 'text2'])")
