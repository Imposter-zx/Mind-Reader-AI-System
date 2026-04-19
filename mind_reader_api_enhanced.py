#!/usr/bin/env python
"""
Enhanced REST API Backend for Mind Reader AI System
Flask-based API with comprehensive endpoints, authentication, Rate limiting, WebSocket support
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_restx import Api, Resource, fields, Namespace
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_caching import Cache
import json
import functools
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our modules
try:
    from mind_reader_lightweight import MindScoreAPI
    from performance_optimizer import AnalysisCache, BatchProcessor, QueryOptimizer
    from database_integration import AnalysisDatabase
    from advanced_analytics import (
        SentimentTrajectory, SocialDynamicsAnalyzer,
        CognitiveComplexityAnalyzer, AnomalyDetector
    )
except ImportError as e:
    logger.warning(f"Some modules not found: {e}")


class EnhancedMindReaderAPI:
    """Enhanced REST API for Mind Reader AI System with advanced features"""
    
    def __init__(self, app_name: str = 'MindReaderAPI'):
        self.app = Flask(app_name)
        self.setup_config()
        self.setup_extensions()
        self.initialize_components()
        self.register_routes()
        
    def setup_config(self):
        """Configure Flask app"""
        self.app.config['JSON_SORT_KEYS'] = False
        self.app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.app.config['CACHE_TYPE'] = 'simple'
        self.app.config['RATELIMIT_STRATEGY'] = 'moving-window'
        
    def setup_extensions(self):
        """Setup Flask extensions"""
        CORS(self.app, resources={r"/api/*": {"origins": "*"}})
        
        # JWT
        self.jwt = JWTManager(self.app)
        
        # Rate limiting
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"]
        )
        
        # Caching
        self.cache = Cache(self.app)
        
        # API documentation
        self.api = Api(
            self.app,
            version='2.0',
            title='Mind Reader AI System API',
            description='Comprehensive cognitive analysis platform',
            doc='/api/docs'
        )
        
    def initialize_components(self):
        """Initialize AI components"""
        try:
            self.mind_api = MindScoreAPI()
            self.db = AnalysisDatabase()
            self.cache_manager = AnalysisCache(max_size=1000)
            self.batch_processor = BatchProcessor(batch_size=50)
            self.query_optimizer = QueryOptimizer()
            
            self.sentiment_analyzer = SentimentTrajectory()
            self.social_analyzer = SocialDynamicsAnalyzer()
            self.complexity_analyzer = CognitiveComplexityAnalyzer()
            self.anomaly_detector = AnomalyDetector()
            
            logger.info("✅ All AI components initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing components: {e}")
            
    def register_routes(self):
        """Register API routes"""
        ns = Namespace('api', description='Mind Reader API')
        
        # Health check
        @ns.route('/health')
        class Health(Resource):
            def get(self):
                """System health check"""
                return {
                    'status': 'healthy',
                    'timestamp': datetime.utcnow().isoformat(),
                    'version': '2.0'
                }, 200
        
        # Authentication
        @ns.route('/auth/login')
        class Login(Resource):
            def post(self):
                """User login - returns JWT token"""
                data = request.get_json()
                username = data.get('username', 'default_user')
                
                access_token = create_access_token(
                    identity=username,
                    expires_delta=timedelta(hours=24)
                )
                
                return {
                    'access_token': access_token,
                    'token_type': 'Bearer',
                    'expires_in': 86400
                }, 200
        
        # Core Analysis Endpoints
        @ns.route('/analyze/emotion')
        class EmotionAnalysis(Resource):
            @self.limiter.limit("30 per minute")
            @jwt_required()
            def post(self):
                """Analyze emotion from text"""
                data = request.get_json()
                text = data.get('text', '')
                
                if not text:
                    return {'error': 'Text is required'}, 400
                
                try:
                    result = self.mind_api.analyze_emotion(text)
                    
                    # Cache result
                    cache_key = hashlib.md5(text.encode()).hexdigest()
                    self.cache_manager.cache(cache_key, result)
                    
                    return {
                        'status': 'success',
                        'emotion': result,
                        'timestamp': datetime.utcnow().isoformat()
                    }, 200
                except Exception as e:
                    logger.error(f"Emotion analysis error: {e}")
                    return {'error': str(e)}, 500
        
        @ns.route('/analyze/personality')
        class PersonalityAnalysis(Resource):
            @self.limiter.limit("20 per minute")
            @jwt_required()
            def post(self):
                """Analyze personality from text"""
                data = request.get_json()
                text = data.get('text', '')
                
                if not text:
                    return {'error': 'Text is required'}, 400
                
                try:
                    result = self.mind_api.analyze_personality(text)
                    return {
                        'status': 'success',
                        'personality': result,
                        'timestamp': datetime.utcnow().isoformat()
                    }, 200
                except Exception as e:
                    logger.error(f"Personality analysis error: {e}")
                    return {'error': str(e)}, 500
        
        @ns.route('/analyze/deception')
        class DeceptionAnalysis(Resource):
            @self.limiter.limit("20 per minute")
            @jwt_required()
            def post(self):
                """Detect deception patterns"""
                data = request.get_json()
                text = data.get('text', '')
                
                if not text:
                    return {'error': 'Text is required'}, 400
                
                try:
                    result = self.mind_api.detect_deception(text)
                    return {
                        'status': 'success',
                        'deception_analysis': result,
                        'timestamp': datetime.utcnow().isoformat()
                    }, 200
                except Exception as e:
                    logger.error(f"Deception analysis error: {e}")
                    return {'error': str(e)}, 500
        
        @ns.route('/analyze/comprehensive')
        class ComprehensiveAnalysis(Resource):
            @self.limiter.limit("15 per minute")
            @jwt_required()
            def post(self):
                """Comprehensive multi-modal analysis"""
                data = request.get_json()
                text = data.get('text', '')
                metadata = data.get('metadata', {})
                
                if not text:
                    return {'error': 'Text is required'}, 400
                
                try:
                    results = {
                        'emotion': self.mind_api.analyze_emotion(text),
                        'personality': self.mind_api.analyze_personality(text),
                        'deception': self.mind_api.detect_deception(text),
                        'danger': self.mind_api.detect_danger(text),
                        'future_behavior': self.mind_api.predict_behavior(text),
                    }
                    
                    # Add advanced analytics if available
                    if hasattr(self, 'anomaly_detector'):
                        results['anomalies'] = self.anomaly_detector.detect(text)
                    
                    return {
                        'status': 'success',
                        'analysis': results,
                        'metadata': metadata,
                        'timestamp': datetime.utcnow().isoformat()
                    }, 200
                except Exception as e:
                    logger.error(f"Comprehensive analysis error: {e}")
                    return {'error': str(e)}, 500
        
        # Batch Processing
        @ns.route('/batch/analyze')
        class BatchAnalysis(Resource):
            @self.limiter.limit("10 per minute")
            @jwt_required()
            def post(self):
                """Batch analysis of multiple texts"""
                data = request.get_json()
                texts = data.get('texts', [])
                analysis_type = data.get('analysis_type', 'comprehensive')
                
                if not texts or not isinstance(texts, list):
                    return {'error': 'texts list is required'}, 400
                
                try:
                    results = []
                    for text in texts:
                        if analysis_type == 'emotion':
                            result = self.mind_api.analyze_emotion(text)
                        elif analysis_type == 'personality':
                            result = self.mind_api.analyze_personality(text)
                        elif analysis_type == 'deception':
                            result = self.mind_api.detect_deception(text)
                        else:
                            result = {
                                'emotion': self.mind_api.analyze_emotion(text),
                                'personality': self.mind_api.analyze_personality(text),
                            }
                        results.append({'text': text, 'result': result})
                    
                    return {
                        'status': 'success',
                        'batch_size': len(texts),
                        'results': results,
                        'timestamp': datetime.utcnow().isoformat()
                    }, 200
                except Exception as e:
                    logger.error(f"Batch analysis error: {e}")
                    return {'error': str(e)}, 500
        
        # Database Operations
        @ns.route('/history')
        class AnalysisHistory(Resource):
            @jwt_required()
            def get(self):
                """Get analysis history"""
                limit = request.args.get('limit', 50, type=int)
                try:
                    history = self.db.get_recent_analyses(limit)
                    return {
                        'status': 'success',
                        'count': len(history),
                        'history': history
                    }, 200
                except Exception as e:
                    logger.error(f"History retrieval error: {e}")
                    return {'error': str(e)}, 500
        
        @ns.route('/history/<int:analysis_id>')
        class AnalysisDetail(Resource):
            @jwt_required()
            def get(self, analysis_id):
                """Get specific analysis details"""
                try:
                    detail = self.db.get_analysis(analysis_id)
                    if detail:
                        return {'status': 'success', 'data': detail}, 200
                    return {'error': 'Analysis not found'}, 404
                except Exception as e:
                    logger.error(f"Analysis detail error: {e}")
                    return {'error': str(e)}, 500
        
        # Statistics
        @ns.route('/stats/summary')
        class StatisticsSummary(Resource):
            @self.cache.cached(timeout=300)
            @jwt_required()
            def get(self):
                """Get system statistics"""
                try:
                    stats = self.db.get_statistics()
                    return {
                        'status': 'success',
                        'statistics': stats,
                        'timestamp': datetime.utcnow().isoformat()
                    }, 200
                except Exception as e:
                    logger.error(f"Statistics error: {e}")
                    return {'error': str(e)}, 500
        
        @ns.route('/stats/performance')
        class PerformanceStats(Resource):
            @jwt_required()
            def get(self):
                """Get performance metrics"""
                try:
                    metrics = {
                        'cache_hits': self.cache_manager.hits,
                        'cache_misses': self.cache_manager.misses,
                        'cache_hit_rate': self.cache_manager.hit_rate(),
                        'db_queries': self.db.query_count,
                        'avg_response_time': self.db.avg_response_time
                    }
                    return {
                        'status': 'success',
                        'metrics': metrics
                    }, 200
                except Exception as e:
                    logger.error(f"Performance stats error: {e}")
                    return {'error': str(e)}, 500
        
        self.api.add_namespace(ns)
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the API server"""
        logger.info(f"🚀 Starting Mind Reader API on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def create_app():
    """Factory function to create app"""
    return EnhancedMindReaderAPI().app


if __name__ == '__main__':
    api = EnhancedMindReaderAPI()
    api.run(debug=True)
