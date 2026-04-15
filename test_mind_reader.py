#!/usr/bin/env python3
"""
Mind Reader AI System - Unit Tests
Comprehensive test suite for all components
"""

import unittest
from mind_reader_lightweight import (
    FeatureEngineer, EmotionAnalyzer, PersonalityAnalyzer,
    DeceptionDetector, DangerDetector, BehaviorPredictor, MindScoreAPI
)


class TestFeatureEngineer(unittest.TestCase):
    """Test feature extraction"""
    
    def test_basic_features(self):
        """Test basic feature extraction"""
        text = "I'm so happy!"
        features = FeatureEngineer.extract_features(text)
        
        self.assertIn('word_count', features)
        self.assertIn('exclamation_count', features)
        self.assertEqual(features['exclamation_count'], 1)
        self.assertEqual(features['word_count'], 4)
    
    def test_sentiment_calculation(self):
        """Test sentiment calculation"""
        happy_text = "I love this amazing day"
        sad_text = "I hate this terrible day"
        
        happy_sentiment = FeatureEngineer.calculate_sentiment(happy_text)
        sad_sentiment = FeatureEngineer.calculate_sentiment(sad_text)
        
        self.assertGreater(happy_sentiment, sad_sentiment)
    
    def test_empty_text(self):
        """Test with empty text"""
        features = FeatureEngineer.extract_features("")
        
        self.assertEqual(features['word_count'], 0)
        self.assertEqual(features['sentence_count'], 1)
    
    def test_punctuation_count(self):
        """Test punctuation counting"""
        text = "Hello? Yes! Really?"
        features = FeatureEngineer.extract_features(text)
        
        self.assertEqual(features['question_count'], 2)
        self.assertEqual(features['exclamation_count'], 1)


class TestEmotionAnalyzer(unittest.TestCase):
    """Test emotion detection"""
    
    def setUp(self):
        self.analyzer = EmotionAnalyzer()
    
    def test_happy_emotion(self):
        """Test happy emotion detection"""
        result = self.analyzer.analyze("I'm so happy and excited!")
        
        self.assertEqual(result['emotion'], 'happy')
        self.assertGreater(result['confidence'], 0)
        self.assertIn('all_emotions', result)
    
    def test_sad_emotion(self):
        """Test sad emotion detection"""
        result = self.analyzer.analyze("I feel very sad and depressed")
        
        self.assertEqual(result['emotion'], 'sad')
        self.assertGreater(result['confidence'], 0)
    
    def test_angry_emotion(self):
        """Test angry emotion detection"""
        result = self.analyzer.analyze("I'm furious and infuriated!")
        
        self.assertEqual(result['emotion'], 'angry')
    
    def test_neutral_emotion(self):
        """Test neutral emotion detection"""
        result = self.analyzer.analyze("The meeting is at 3 PM")
        
        self.assertIn(result['emotion'], ['neutral', 'happy'])
    
    def test_confidence_range(self):
        """Test confidence is in valid range"""
        result = self.analyzer.analyze("I'm happy")
        
        self.assertGreaterEqual(result['confidence'], 0)
        self.assertLessEqual(result['confidence'], 1)


class TestPersonalityAnalyzer(unittest.TestCase):
    """Test personality analysis"""
    
    def setUp(self):
        self.analyzer = PersonalityAnalyzer()
    
    def test_introvert_trait(self):
        """Test introvert trait detection"""
        result = self.analyzer.analyze("I prefer quiet time and deep conversations")
        
        self.assertIn('dominant_trait', result)
        self.assertIn('trait_scores', result)
    
    def test_extrovert_trait(self):
        """Test extrovert trait detection"""
        result = self.analyzer.analyze("I love parties and meeting new people")
        
        self.assertIn(result['dominant_trait'], ['introvert', 'extrovert'])
    
    def test_trait_scores(self):
        """Test trait scores are valid"""
        result = self.analyzer.analyze("I'm creative and artistic")
        
        scores = result['trait_scores']
        
        # All scores should be percentages (0-100)
        for score in scores.values():
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)
    
    def test_secondary_traits(self):
        """Test secondary traits are returned"""
        result = self.analyzer.analyze("I'm confident and creative")
        
        self.assertIn('secondary_traits', result)
        self.assertIsInstance(result['secondary_traits'], list)


class TestDeceptionDetector(unittest.TestCase):
    """Test deception detection"""
    
    def setUp(self):
        self.detector = DeceptionDetector()
    
    def test_deceptive_text(self):
        """Test detection of deceptive language"""
        deceptive_text = "Well, um, I think maybe I wasn't there, um..."
        result = self.detector.calculate_score(deceptive_text)
        
        self.assertGreater(result['deception_probability'], 0)
        self.assertIn('interpretation', result)
    
    def test_truthful_text(self):
        """Test detection of truthful language"""
        truthful_text = "I was at home yesterday"
        result = self.detector.calculate_score(truthful_text)
        
        self.assertGreaterEqual(result['deception_probability'], 0)
        self.assertLess(result['deception_probability'], 1)
    
    def test_probability_range(self):
        """Test probability is in valid range (0-1)"""
        result = self.detector.calculate_score("Any text")
        
        self.assertGreaterEqual(result['deception_probability'], 0)
        self.assertLessEqual(result['deception_probability'], 1)
    
    def test_interpretation(self):
        """Test interpretations are provided"""
        result = self.detector.calculate_score("I think maybe")
        
        self.assertIn(result['interpretation'], 
                     ['Probably deceptive', 'Possibly deceptive', 'Probably truthful'])


class TestDangerDetector(unittest.TestCase):
    """Test danger detection"""
    
    def setUp(self):
        self.detector = DangerDetector()
    
    def test_safe_text(self):
        """Test safe text detection"""
        result = self.detector.calculate_score("I'm going to help my community")
        
        self.assertLess(result['danger_score'], 0.5)
        self.assertIn("Safe", result['risk_level'])
    
    def test_danger_keywords(self):
        """Test danger keyword detection"""
        result = self.detector.calculate_score("I hate everything")
        
        self.assertGreater(result['danger_score'], 0)
        self.assertIn('risk_level', result)
    
    def test_risk_levels(self):
        """Test risk level classification"""
        safe_result = self.detector.calculate_score("Good day")
        
        self.assertIn(safe_result['risk_level'], 
                     ['🟢 Very Low Risk', '🟡 Low Risk', '🟠 Medium Risk', '🔴 High Risk'])
    
    def test_recommendation_provided(self):
        """Test recommendation is always provided"""
        result = self.detector.calculate_score("Any text")
        
        self.assertIn('recommendation', result)
        self.assertGreater(len(result['recommendation']), 0)


class TestBehaviorPredictor(unittest.TestCase):
    """Test behavior prediction"""
    
    def setUp(self):
        self.predictor = BehaviorPredictor()
    
    def test_happy_prediction(self):
        """Test happy emotion behavior prediction"""
        result = self.predictor.predict('happy', ['introvert'])
        
        self.assertIn('predicted_actions', result)
        self.assertIsInstance(result['predicted_actions'], list)
        self.assertGreater(len(result['predicted_actions']), 0)
    
    def test_sad_prediction(self):
        """Test sad emotion behavior prediction"""
        result = self.predictor.predict('sad', ['extrovert'])
        
        self.assertIn('emotional_trajectory', result)
        self.assertIn('confidence_score', result)
    
    def test_all_emotions(self):
        """Test predictions for all emotions"""
        emotions = ['happy', 'sad', 'angry', 'neutral']
        traits = ['introvert']
        
        for emotion in emotions:
            result = self.predictor.predict(emotion, traits)
            
            self.assertIn('predicted_actions', result)
            self.assertIn('emotional_trajectory', result)
    
    def test_confidence_in_range(self):
        """Test confidence score is valid"""
        result = self.predictor.predict('happy', ['introvert'])
        
        confidence = result['confidence_score']
        self.assertGreaterEqual(confidence, 0)
        self.assertLessEqual(confidence, 1)


class TestMindScoreAPI(unittest.TestCase):
    """Test the unified Mind Score API"""
    
    def setUp(self):
        self.api = MindScoreAPI()
    
    def test_single_analysis(self):
        """Test single text analysis"""
        result = self.api.analyze("I'm happy")
        
        self.assertIn('emotion_analysis', result)
        self.assertIn('personality_analysis', result)
        self.assertIn('lie_detection', result)
        self.assertIn('danger_detection', result)
        self.assertIn('behavior_prediction', result)
        self.assertIn('mind_score', result)
    
    def test_mind_score_range(self):
        """Test mind score is in valid range"""
        result = self.api.analyze("Test text")
        
        score = result['mind_score']['overall_score']
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_mind_score_interpretation(self):
        """Test mind score has interpretation"""
        result = self.api.analyze("Test")
        
        mind_score = result['mind_score']
        self.assertIn('interpretation', mind_score)
        self.assertGreater(len(mind_score['interpretation']), 0)
    
    def test_batch_analysis(self):
        """Test batch analysis"""
        texts = ["I'm happy", "I'm sad", "I'm angry"]
        results = self.api.batch_analyze(texts)
        
        self.assertEqual(len(results), 3)
        
        for result in results:
            self.assertIn('emotion_analysis', result)
            self.assertIn('mind_score', result)
    
    def test_history_storage(self):
        """Test analysis history is stored"""
        initial_count = len(self.api.get_history())
        
        self.api.analyze("First analysis")
        self.api.analyze("Second analysis")
        
        final_count = len(self.api.get_history())
        
        self.assertEqual(final_count, initial_count + 2)
    
    def test_statistics(self):
        """Test statistics generation"""
        self.api.analyze("I'm happy")
        self.api.analyze("I'm sad")
        
        stats = self.api.get_statistics()
        
        self.assertGreaterEqual(stats['total_analyses'], 2)
        self.assertIn('emotion_distribution', stats)
        self.assertIn('average_mind_score', stats)
    
    def test_detailed_output(self):
        """Test detailed analysis output"""
        result = self.api.analyze("Test", detailed=True)
        
        self.assertIn('extracted_features', result)
        self.assertIsNotNone(result['extracted_features'])
    
    def test_simple_output(self):
        """Test simple analysis output (without features)"""
        result = self.api.analyze("Test", detailed=False)
        
        if result['extracted_features'] is None:
            self.assertIsNone(result['extracted_features'])
    
    def test_timestamp_included(self):
        """Test timestamp is included in results"""
        result = self.api.analyze("Test")
        
        self.assertIn('timestamp', result)
        self.assertGreater(len(result['timestamp']), 0)
    
    def test_input_summary(self):
        """Test input summary is provided"""
        result = self.api.analyze("Test text")
        
        summary = result['input_summary']
        self.assertIn('text_length', summary)
        self.assertIn('word_count', summary)
        
        self.assertEqual(summary['text_length'], 9)
        self.assertEqual(summary['word_count'], 2)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        self.api = MindScoreAPI()
    
    def test_full_workflow(self):
        """Test complete workflow"""
        # Analyze multiple texts
        texts = [
            "I'm excited about this opportunity!",
            "I feel sad today",
            "This is infuriating!",
            "The report is due tomorrow"
        ]
        
        results = self.api.batch_analyze(texts)
        
        # Verify results
        self.assertEqual(len(results), 4)
        
        # Check statistics
        stats = self.api.get_statistics()
        self.assertEqual(stats['total_analyses'], 4)
        
        # Verify emotions detected
        emotions = stats['emotion_distribution']
        self.assertGreater(len(emotions), 0)
    
    def test_api_consistency(self):
        """Test API returns consistent results"""
        text = "I'm happy"
        
        result1 = self.api.analyze(text)
        result2 = self.api.analyze(text)
        
        # Both should have same emotion
        self.assertEqual(
            result1['emotion_analysis']['emotion'],
            result2['emotion_analysis']['emotion']
        )
    
    def test_component_interaction(self):
        """Test all components work together"""
        result = self.api.analyze("I'm happy about this amazing opportunity!")
        
        # Verify all components provided output
        self.assertIsNotNone(result['emotion_analysis']['emotion'])
        self.assertIsNotNone(result['personality_analysis']['dominant_trait'])
        self.assertIsNotNone(result['lie_detection']['deception_probability'])
        self.assertIsNotNone(result['danger_detection']['danger_score'])
        self.assertIsNotNone(result['behavior_prediction']['predicted_actions'])


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFeatureEngineer))
    suite.addTests(loader.loadTestsFromTestCase(TestEmotionAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestPersonalityAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestDeceptionDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestDangerDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestBehaviorPredictor))
    suite.addTests(loader.loadTestsFromTestCase(TestMindScoreAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
