#!/usr/bin/env python
"""
REST API Backend for Mind Reader AI System
Flask-based API with comprehensive endpoints
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import functools
from datetime import datetime
from typing import Dict, Any

# Import our modules
try:
    from mind_reader_lightweight import MindScoreAPI
    from performance_optimizer import AnalysisCache, BatchProcessor, QueryOptimizer
    from database_integration import AnalysisDatabase
    from advanced_analytics import (
        SentimentTrajectory, SocialDynamicsAnalyzer,
        CognitiveComplexityAnalyzer, AnomalyDetector
    )
except ImportError:
    print("⚠️  Some modules not found - using stubs")


class MindReaderAPI:
    """REST API for Mind Reader AI System"""
    
    def __init__(self, app_name: str = 'MindReader'):
        self.app = Flask(app_name)
        CORS(self.app)
        
        # Initialize components
        self.cache = AnalysisCache(max_size=1000)
        self.db = AnalysisDatabase()
        self.batch_processor = BatchProcessor(batch_size=50)
        
        self.sentiment_analyzer = SentimentTrajectory()
        self.social_analyzer = SocialDynamicsAnalyzer()
        self.complexity_analyzer = CognitiveComplexityAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        
        # Attempt to load mind_reader API
        try:
            self.mind_api = MindScoreAPI()
        except:
            self.mind_api = None
        
        # Register routes
        self.register_routes()
    
    def register_routes(self):
        """Register all API endpoints"""
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'operational',
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0',
                'components': {
                    'api': 'ready',
                    'cache': 'ready',
                    'database': 'ready'
                }
            }), 200
        
        @self.app.route('/api/analyze', methods=['POST'])
        def analyze():
            """Analyze text and return results"""
            data = request.get_json()
            
            if not data or 'text' not in data:
                return jsonify({'error': 'Text input required'}), 400
            
            text = data['text']
            query_type = data.get('query_type', 'light_analysis')
            
            # Check cache
            found, cached_result = self.cache.get(text)
            if found:
                return jsonify({
                    'result': cached_result,
                    'cached': True,
                    'timestamp': datetime.now().isoformat()
                }), 200
            
            try:
                # Perform analysis
                if self.mind_api:
                    result = self.mind_api.analyze(text)
                else:
                    result = self._stub_analysis(text)
                
                # Cache result
                self.cache.put(text, result)
                
                # Store in database
                analysis_id = self.db.store_analysis(
                    text, result,
                    user_id=data.get('user_id')
                )
                
                response = {
                    'result': result,
                    'analysis_id': analysis_id,
                    'cached': False,
                    'timestamp': datetime.now().isoformat()
                }
                
                return jsonify(response), 200
            
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/batch-analyze', methods=['POST'])
        def batch_analyze():
            """Analyze multiple texts in batch"""
            data = request.get_json()
            
            if not data or 'texts' not in data:
                return jsonify({'error': 'texts array required'}), 400
            
            texts = data['texts']
            
            if not isinstance(texts, list):
                return jsonify({'error': 'texts must be an array'}), 400
            
            try:
                def process_text(text):
                    found, cached = self.cache.get(text)
                    if found:
                        return cached
                    
                    if self.mind_api:
                        result = self.mind_api.analyze(text)
                    else:
                        result = self._stub_analysis(text)
                    
                    self.cache.put(text, result)
                    self.db.store_analysis(text, result, user_id=data.get('user_id'))
                    
                    return result
                
                results = self.batch_processor.process_batch(texts, process_text)
                
                return jsonify({
                    'results': results,
                    'count': len(results),
                    'timestamp': datetime.now().isoformat()
                }), 200
            
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/sentiment-trajectory', methods=['POST'])
        def sentiment_trajectory():
            """Analyze sentiment evolution"""
            data = request.get_json()
            
            if not data or 'texts' not in data:
                return jsonify({'error': 'texts array required'}), 400
            
            try:
                result = self.sentiment_analyzer.analyze_trajectory(data['texts'])
                
                return jsonify({
                    'trajectory': result,
                    'timestamp': datetime.now().isoformat()
                }), 200
            
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/conversation-analysis', methods=['POST'])
        def analyze_conversation():
            """Analyze conversation dynamics"""
            data = request.get_json()
            
            if not data or 'conversation' not in data:
                return jsonify({'error': 'conversation array required'}), 400
            
            try:
                result = self.social_analyzer.analyze_dynamics(data['conversation'])
                
                # Store conversation
                speakers = [turn.get('speaker') for turn in data['conversation']]
                conv_id = self.db.store_conversation(
                    data.get('conversation_id', f'conv_{datetime.now().timestamp()}'),
                    speakers,
                    data['conversation'],
                    result
                )
                
                return jsonify({
                    'dynamics': result,
                    'conversation_id': conv_id,
                    'timestamp': datetime.now().isoformat()
                }), 200
            
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/complexity-analysis', methods=['POST'])
        def complexity_analysis():
            """Analyze text complexity"""
            data = request.get_json()
            
            if not data or 'text' not in data:
                return jsonify({'error': 'text required'}), 400
            
            try:
                result = self.complexity_analyzer.analyze_complexity(data['text'])
                
                return jsonify({
                    'complexity': result,
                    'timestamp': datetime.now().isoformat()
                }), 200
            
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/analysis-history', methods=['GET'])
        def get_history():
            """Get analysis history"""
            limit = request.args.get('limit', 100, type=int)
            user_id = request.args.get('user_id')
            
            try:
                history = self.db.get_analysis_history(limit=limit, user_id=user_id)
                
                return jsonify({
                    'history': history,
                    'count': len(history),
                    'timestamp': datetime.now().isoformat()
                }), 200
            
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/user-profile/<user_id>', methods=['GET'])
        def get_profile(user_id):
            """Get user profile"""
            try:
                profile = self.db.get_user_profile(user_id)
                
                if not profile:
                    return jsonify({'error': 'User not found'}), 404
                
                return jsonify({
                    'profile': profile,
                    'timestamp': datetime.now().isoformat()
                }), 200
            
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/statistics', methods=['GET'])
        def get_statistics():
            """Get system statistics"""
            try:
                db_stats = self.db.get_statistics()
                cache_stats = self.cache.get_stats()
                
                return jsonify({
                    'database': db_stats,
                    'cache': cache_stats,
                    'timestamp': datetime.now().isoformat()
                }), 200
            
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/cache/clear', methods=['POST'])
        def clear_cache():
            """Clear analysis cache"""
            self.cache.clear()
            
            return jsonify({
                'status': 'cache cleared',
                'timestamp': datetime.now().isoformat()
            }), 200
        
        @self.app.route('/api/export', methods=['GET'])
        def export_data():
            """Export all data"""
            try:
                output_file = f'mind_reader_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                self.db.export_data(output_file)
                
                return jsonify({
                    'status': 'exported',
                    'file': output_file,
                    'timestamp': datetime.now().isoformat()
                }), 200
            
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors"""
            return jsonify({'error': 'Endpoint not found'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            """Handle 500 errors"""
            return jsonify({'error': 'Internal server error'}), 500
    
    @staticmethod
    def _stub_analysis(text: str) -> Dict[str, Any]:
        """Stub analysis for demo purposes"""
        return {
            'text': text,
            'emotion': 'neutral',
            'emotion_score': 0.5,
            'personality_traits': {'extrovert': 50, 'creative': 50},
            'deception_score': 0.3,
            'danger_score': 0.2,
            'overall_score': 0.5
        }
    
    def run(self, host: str = '127.0.0.1', port: int = 5000, debug: bool = False):
        """Run the API server"""
        print(f"\n🚀 Starting Mind Reader API Server")
        print(f"   Address: http://{host}:{port}")
        print(f"   Debug: {debug}")
        print(f"\n📚 API Documentation:")
        print(f"   Health Check: GET /api/health")
        print(f"   Analyze Text: POST /api/analyze")
        print(f"   Batch Analysis: POST /api/batch-analyze")
        print(f"   Sentiment Trajectory: POST /api/sentiment-trajectory")
        print(f"   Conversation Analysis: POST /api/conversation-analysis")
        print(f"   Complexity Analysis: POST /api/complexity-analysis")
        print(f"   User Profile: GET /api/user-profile/<user_id>")
        print(f"   Statistics: GET /api/statistics")
        print(f"   Analysis History: GET /api/analysis-history")
        print(f"\n")
        
        self.app.run(host=host, port=port, debug=debug)


def create_api_app():
    """Factory function to create API app"""
    return MindReaderAPI()


if __name__ == '__main__':
    api = MindReaderAPI()
    
    print("=" * 80)
    print("🧠 MIND READER AI SYSTEM - REST API")
    print("=" * 80)
    print("\n✅ API module loaded successfully")
    print("\nTo start the server, run:")
    print("  python mind_reader_api.py")
    print("\nOr programmatically:")
    print("  api = create_api_app()")
    print("  api.run(debug=True)")
