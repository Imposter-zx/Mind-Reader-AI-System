#!/usr/bin/env python
"""
Comprehensive Test Suite for Mind Reader AI System
Tests all major components and edge cases
"""

import unittest
import sys
import json
from datetime import datetime
from performance_optimizer import AnalysisCache, PerformanceProfiler, BatchProcessor, QueryOptimizer
from database_integration import AnalysisDatabase
from advanced_analytics import (
    SentimentTrajectory, SocialDynamicsAnalyzer, 
    CognitiveComplexityAnalyzer, AnomalyDetector
)


class TestPerformanceOptimizations(unittest.TestCase):
    """Test performance optimization modules"""
    
    def test_cache_basic_operations(self):
        """Test cache put and get operations"""
        cache = AnalysisCache(max_size=10)
        
        test_text = "This is a test"
        test_result = {'score': 0.85}
        
        cache.put(test_text, test_result)
        found, result = cache.get(test_text)
        
        self.assertTrue(found)
        self.assertEqual(result, test_result)
    
    def test_cache_miss(self):
        """Test cache miss returns False"""
        cache = AnalysisCache()
        found, result = cache.get("nonexistent text")
        
        self.assertFalse(found)
        self.assertIsNone(result)
    
    def test_cache_statistics(self):
        """Test cache statistics tracking"""
        cache = AnalysisCache()
        
        cache.put("text1", {'score': 1})
        cache.get("text1")
        cache.get("nonexistent")
        
        stats = cache.get_stats()
        
        self.assertEqual(stats['hits'], 1)
        self.assertEqual(stats['misses'], 1)
        self.assertEqual(stats['hit_rate'], 50.0)
    
    def test_cache_eviction(self):
        """Test LRU eviction when max_size exceeded"""
        cache = AnalysisCache(max_size=3)
        
        cache.put("text1", {'score': 1})
        cache.put("text2", {'score': 2})
        cache.put("text3", {'score': 3})
        cache.put("text4", {'score': 4})  # Should evict text1
        
        found, _ = cache.get("text1")
        self.assertFalse(found)
        
        found, _ = cache.get("text4")
        self.assertTrue(found)
    
    def test_batch_processor(self):
        """Test batch processing"""
        processor = BatchProcessor(batch_size=10)
        items = [f"item_{i}" for i in range(25)]
        
        results = processor.process_batch(items, len)
        
        self.assertEqual(len(results), 25)
        self.assertEqual(processor.items_processed, 25)
    
    def test_query_optimizer_patterns(self):
        """Test query optimization patterns"""
        components = QueryOptimizer.optimize_for_speed('emotion_only')
        self.assertEqual(components, ['emotion_analysis'])
        
        components = QueryOptimizer.optimize_for_speed('full_analysis')
        self.assertEqual(len(components), 5)
    
    def test_performance_profiler(self):
        """Test performance profiling"""
        profiler = PerformanceProfiler()
        
        @profiler.measure_time
        def test_function():
            return sum(range(1000))
        
        result = test_function()
        report = profiler.get_performance_report()
        
        self.assertIn('test_function', report)
        self.assertGreater(report['test_function']['calls'], 0)


class TestDatabase(unittest.TestCase):
    """Test database integration"""
    
    def setUp(self):
        """Create in-memory database for testing"""
        self.db = AnalysisDatabase(':memory:')
    
    def test_store_and_retrieve_analysis(self):
        """Test storing and retrieving analysis"""
        analysis = {
            'emotion_score': 0.8,
            'emotion': 'happy',
            'personality_traits': {'extrovert': 70},
            'deception_score': 0.2,
            'danger_score': 0.1,
            'overall_score': 0.75
        }
        
        analysis_id = self.db.store_analysis("Test text", analysis)
        self.assertGreater(analysis_id, 0)
        
        retrieved = self.db.retrieve_analysis(analysis_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['emotion_label'], 'happy')
        self.assertEqual(retrieved['overall_score'], 0.75)
    
    def test_duplicate_analysis_handling(self):
        """Test handling of duplicate analyses"""
        analysis = {'emotion_score': 0.8, 'emotion': 'happy', 'overall_score': 0.75}
        
        id1 = self.db.store_analysis("Same text", analysis)
        id2 = self.db.store_analysis("Same text", analysis)
        
        self.assertGreater(id1, 0)
        self.assertEqual(id2, -1)  # Duplicate should return -1
    
    def test_user_profile_creation(self):
        """Test user profile creation and updates"""
        analysis = {'emotion_score': 0.8, 'emotion': 'happy', 'deception_score': 0.2, 'overall_score': 0.75}
        
        self.db.store_analysis("Text 1", analysis, user_id="user_123")
        profile = self.db.get_user_profile("user_123")
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile['user_id'], "user_123")
        self.assertEqual(profile['analysis_count'], 1)
    
    def test_conversation_storage(self):
        """Test conversation storage"""
        conversation = [
            {'speaker': 'Alice', 'text': 'Hello'},
            {'speaker': 'Bob', 'text': 'Hi there'}
        ]
        
        analysis_results = {'dynamics': 'balanced'}
        
        conv_id = self.db.store_conversation("conv_1", ['Alice', 'Bob'], conversation, analysis_results)
        self.assertGreater(conv_id, 0)
    
    def test_database_statistics(self):
        """Test statistics retrieval"""
        analysis = {'emotion_score': 0.8, 'emotion': 'happy', 'deception_score': 0.2, 'overall_score': 0.75}
        
        self.db.store_analysis("Text 1", analysis)
        self.db.store_analysis("Text 2", analysis)
        
        stats = self.db.get_statistics()
        
        self.assertEqual(stats['total_analyses'], 2)
        self.assertAlmostEqual(stats['overall_avg_emotion'], 0.8, places=1)


class TestAdvancedAnalytics(unittest.TestCase):
    """Test advanced analytics modules"""
    
    def test_sentiment_trajectory(self):
        """Test sentiment trajectory analysis"""
        traj = SentimentTrajectory()
        texts = ["I love this!", "It's okay", "This is terrible"]
        
        result = traj.analyze_trajectory(texts)
        
        self.assertEqual(len(result['sentiments']), 3)
        self.assertEqual(len(result['scores']), 3)
        self.assertIn('trend', result)
        self.assertIn('emotional_arc', result)
    
    def test_sentiment_trend_detection(self):
        """Test trend detection"""
        traj = SentimentTrajectory()
        improving_texts = ["Bad start", "Getting better", "Excellent result"]
        
        result = traj.analyze_trajectory(improving_texts)
        
        self.assertEqual(result['trend'], 'improving')
    
    def test_social_dynamics_analyzer(self):
        """Test social dynamics analysis"""
        analyzer = SocialDynamicsAnalyzer()
        
        conversation = [
            {'speaker': 'Alice', 'text': 'I think this approach is clearly wrong'},
            {'speaker': 'Bob', 'text': 'Well, maybe we could consider another way'},
            {'speaker': 'Alice', 'text': 'You should follow my recommendation'}
        ]
        
        result = analyzer.analyze_dynamics(conversation)
        
        self.assertIn('speakers', result)
        self.assertIn('power_structure', result)
        self.assertEqual(len(result['speakers']), 2)
    
    def test_cognitive_complexity(self):
        """Test cognitive complexity analysis"""
        analyzer = CognitiveComplexityAnalyzer()
        
        simple_text = "This is simple"
        complex_text = "The epistemological implications of quantum topology suggest paradigmatic shifts"
        
        simple_result = analyzer.analyze_complexity(simple_text)
        complex_result = analyzer.analyze_complexity(complex_text)
        
        self.assertLess(simple_result['overall_score'], complex_result['overall_score'])
        self.assertEqual(simple_result['complexity_level'], 'very_simple')
    
    def test_anomaly_detector_baseline(self):
        """Test anomaly detection with baseline"""
        detector = AnomalyDetector()
        
        baseline_texts = ["Hello world", "This is normal", "Standard message"]
        detector.establish_baseline(baseline_texts)
        
        result = detector.detect_anomalies("Normal text here")
        
        self.assertIn('is_anomalous', result)
        self.assertIn('anomalies', result)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    def test_end_to_end_analysis_workflow(self):
        """Test complete analysis workflow"""
        db = AnalysisDatabase(':memory:')
        cache = AnalysisCache()
        profiler = PerformanceProfiler()
        
        test_text = "This is an amazing result!"
        
        # Simulate analysis
        analysis_result = {
            'emotion_score': 0.9,
            'emotion': 'happy',
            'personality_traits': {'extrovert': 80},
            'deception_score': 0.1,
            'danger_score': 0.05,
            'overall_score': 0.88
        }
        
        # Store in cache
        cache.put(test_text, analysis_result)
        
        # Retrieve from cache
        found, cached_result = cache.get(test_text)
        self.assertTrue(found)
        
        # Store in database
        analysis_id = db.store_analysis(test_text, analysis_result, user_id="test_user")
        self.assertGreater(analysis_id, 0)
        
        # Verify database storage
        retrieved = db.retrieve_analysis(analysis_id)
        self.assertEqual(retrieved['emotion_label'], 'happy')
        
        # Check cache stats
        stats = cache.get_stats()
        self.assertEqual(stats['hits'], 1)
    
    def test_batch_analysis_workflow(self):
        """Test batch processing workflow"""
        db = AnalysisDatabase(':memory:')
        processor = BatchProcessor(batch_size=5)
        
        sample_texts = [f"Sample text {i}" for i in range(12)]
        
        def mock_analysis(text):
            return {'emotion': 'neutral', 'score': 0.5}
        
        results = processor.process_batch(sample_texts, mock_analysis)
        
        self.assertEqual(len(results), 12)
        
        stats = processor.get_stats()
        self.assertEqual(stats['items_processed'], 12)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def test_empty_text_handling(self):
        """Test handling of empty text"""
        analyzer = CognitiveComplexityAnalyzer()
        result = analyzer.analyze_complexity("")
        
        self.assertEqual(result['word_diversity'], 0.0)
    
    def test_empty_conversation(self):
        """Test handling of empty conversation"""
        analyzer = SocialDynamicsAnalyzer()
        result = analyzer.analyze_dynamics([])
        
        self.assertEqual(len(result['speakers']), 0)
    
    def test_cache_with_none_values(self):
        """Test cache handling of None values"""
        cache = AnalysisCache()
        cache.put("text", None)
        
        found, result = cache.get("text")
        self.assertTrue(found)
        self.assertIsNone(result)
    
    def test_database_nonexistent_analysis(self):
        """Test retrieving nonexistent analysis"""
        db = AnalysisDatabase(':memory:')
        result = db.retrieve_analysis(9999)
        
        self.assertIsNone(result)


def run_all_tests():
    """Run all tests with detailed reporting"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceOptimizations))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestAdvancedAnalytics))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("🧪 Running Comprehensive Test Suite\n")
    print("=" * 80)
    
    result = run_all_tests()
    
    print("\n" + "=" * 80)
    print("\n📊 TEST SUMMARY:")
    print(f"  Tests Run: {result.testsRun}")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    sys.exit(0 if result.wasSuccessful() else 1)
