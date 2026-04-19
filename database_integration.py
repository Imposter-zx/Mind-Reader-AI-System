#!/usr/bin/env python
"""
Database Integration Module - Persistent Data Storage & Analysis History
Features:
  - SQLite database for analysis storage
  - Analysis history tracking
  - User profiles and statistics
  - Query interface
  - Data export/import
  - Analytics and reporting
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import os
from contextlib import contextmanager


class AnalysisDatabase:
    """SQLite database for Mind Reader AI System"""
    
    DB_PATH = 'mind_reader_data.db'
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or self.DB_PATH
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Analysis history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    text_hash TEXT UNIQUE,
                    emotion_score REAL,
                    emotion_label TEXT,
                    personality_traits TEXT,
                    deception_score REAL,
                    danger_score REAL,
                    overall_score REAL,
                    analysis_data JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User profiles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    name TEXT,
                    analysis_count INTEGER DEFAULT 0,
                    avg_emotion_score REAL,
                    avg_deception_score REAL,
                    personality_summary TEXT,
                    last_analysis_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    profile_data JSON
                )
            ''')
            
            # Batch operations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS batch_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT UNIQUE,
                    operation_type TEXT,
                    input_count INTEGER,
                    successful_count INTEGER,
                    failed_count INTEGER,
                    processing_time REAL,
                    status TEXT,
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')
            
            # Conversation data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT UNIQUE,
                    speakers TEXT,
                    participant_count INTEGER,
                    total_turns INTEGER,
                    conversation_data JSON,
                    analysis_results JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Statistics and insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_key TEXT UNIQUE,
                    stat_value REAL,
                    description TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def store_analysis(self, text: str, analysis_result: Dict[str, Any], user_id: str = None) -> int:
        """Store analysis result in database"""
        import hashlib
        
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT INTO analysis_history 
                    (text, text_hash, emotion_score, emotion_label, personality_traits,
                     deception_score, danger_score, overall_score, analysis_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    text,
                    text_hash,
                    analysis_result.get('emotion_score', 0),
                    analysis_result.get('emotion', 'unknown'),
                    json.dumps(analysis_result.get('personality_traits', {})),
                    analysis_result.get('deception_score', 0),
                    analysis_result.get('danger_score', 0),
                    analysis_result.get('overall_score', 0),
                    json.dumps(analysis_result)
                ))
                
                conn.commit()
                analysis_id = cursor.lastrowid
                
                # Update user profile if user_id provided
                if user_id:
                    self._update_user_profile(user_id, analysis_result)
                
                return analysis_id
            
            except sqlite3.IntegrityError:
                return -1  # Duplicate analysis
    
    def _update_user_profile(self, user_id: str, analysis_result: Dict):
        """Update or create user profile"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            
            if user:
                # Update existing profile
                new_count = user['analysis_count'] + 1
                avg_emotion = ((user['avg_emotion_score'] or 0) * user['analysis_count'] + 
                              analysis_result.get('emotion_score', 0)) / new_count
                avg_deception = ((user['avg_deception_score'] or 0) * user['analysis_count'] + 
                                analysis_result.get('deception_score', 0)) / new_count
                
                cursor.execute('''
                    UPDATE user_profiles 
                    SET analysis_count = ?, avg_emotion_score = ?, avg_deception_score = ?,
                        last_analysis_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (new_count, avg_emotion, avg_deception, user_id))
            else:
                # Create new profile
                cursor.execute('''
                    INSERT INTO user_profiles 
                    (user_id, analysis_count, avg_emotion_score, avg_deception_score)
                    VALUES (?, 1, ?, ?)
                ''', (user_id, analysis_result.get('emotion_score', 0), 
                      analysis_result.get('deception_score', 0)))
            
            conn.commit()
    
    def retrieve_analysis(self, analysis_id: int) -> Optional[Dict]:
        """Retrieve specific analysis"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM analysis_history WHERE id = ?', (analysis_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'text': row['text'],
                    'emotion_score': row['emotion_score'],
                    'emotion_label': row['emotion_label'],
                    'personality_traits': json.loads(row['personality_traits'] or '{}'),
                    'deception_score': row['deception_score'],
                    'danger_score': row['danger_score'],
                    'overall_score': row['overall_score'],
                    'analysis_data': json.loads(row['analysis_data'] or '{}'),
                    'created_at': row['created_at']
                }
            return None
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Retrieve user profile and statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                profile = {
                    'user_id': row['user_id'],
                    'name': row['name'],
                    'analysis_count': row['analysis_count'],
                    'avg_emotion_score': row['avg_emotion_score'],
                    'avg_deception_score': row['avg_deception_score'],
                    'last_analysis_at': row['last_analysis_at'],
                    'created_at': row['created_at']
                }
                
                # Get recent analyses for this user
                cursor.execute(
                    'SELECT id, emotion_label, overall_score, created_at FROM analysis_history '
                    'ORDER BY created_at DESC LIMIT 5'
                )
                profile['recent_analyses'] = [dict(r) for r in cursor.fetchall()]
                
                return profile
            return None
    
    def get_analysis_history(self, limit: int = 100, user_id: str = None) -> List[Dict]:
        """Retrieve analysis history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if user_id:
                # Future: implement user-specific filtering when user association is added
                pass
            
            cursor.execute('''
                SELECT id, text, emotion_label, overall_score, created_at 
                FROM analysis_history 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {
                'total_analyses': cursor.execute('SELECT COUNT(*) FROM analysis_history').fetchone()[0],
                'total_users': cursor.execute('SELECT COUNT(*) FROM user_profiles').fetchone()[0],
                'total_conversations': cursor.execute('SELECT COUNT(*) FROM conversations').fetchone()[0],
                'overall_avg_emotion': cursor.execute(
                    'SELECT AVG(emotion_score) FROM analysis_history').fetchone()[0],
                'overall_avg_deception': cursor.execute(
                    'SELECT AVG(deception_score) FROM analysis_history').fetchone()[0],
                'timestamp': datetime.now().isoformat()
            }
            
            return stats
    
    def store_conversation(self, conversation_id: str, speakers: List[str], 
                          conversation_data: List[Dict], analysis_results: Dict) -> int:
        """Store conversation analysis"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO conversations 
                (conversation_id, speakers, participant_count, total_turns, 
                 conversation_data, analysis_results)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                conversation_id,
                json.dumps(speakers),
                len(speakers),
                len(conversation_data),
                json.dumps(conversation_data),
                json.dumps(analysis_results)
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_top_emotions(self, limit: int = 10) -> Dict[str, int]:
        """Get most frequent emotions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT emotion_label, COUNT(*) as count 
                FROM analysis_history 
                GROUP BY emotion_label 
                ORDER BY count DESC 
                LIMIT ?
            ''', (limit,))
            
            return {row['emotion_label']: row['count'] for row in cursor.fetchall()}
    
    def export_data(self, output_file: str):
        """Export all data to JSON"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'analyses': [],
                'users': [],
                'conversations': [],
                'statistics': self.get_statistics()
            }
            
            # Export analyses
            cursor.execute('SELECT * FROM analysis_history')
            for row in cursor.fetchall():
                export_data['analyses'].append(dict(row))
            
            # Export users
            cursor.execute('SELECT * FROM user_profiles')
            for row in cursor.fetchall():
                export_data['users'].append(dict(row))
            
            # Export conversations
            cursor.execute('SELECT * FROM conversations')
            for row in cursor.fetchall():
                export_data['conversations'].append(dict(row))
            
            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
    
    def clear_old_data(self, days: int = 90):
        """Delete analyses older than specified days"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM analysis_history 
                WHERE created_at < datetime('now', '-' || ? || ' days')
            ''', (days,))
            conn.commit()
            return cursor.rowcount
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()


def get_database_instance(db_path: str = None) -> AnalysisDatabase:
    """Factory function to get database instance"""
    return AnalysisDatabase(db_path)


if __name__ == '__main__':
    print("💾 Database Integration Module Loaded\n")
    
    # Demo database operations
    db = AnalysisDatabase(':memory:')  # Use in-memory for demo
    
    # Store sample analysis
    sample_analysis = {
        'emotion_score': 0.85,
        'emotion': 'happy',
        'personality_traits': {'extrovert': 75, 'creative': 80},
        'deception_score': 0.15,
        'danger_score': 0.05,
        'overall_score': 0.82
    }
    
    analysis_id = db.store_analysis("This is a test text", sample_analysis, user_id="user_123")
    print(f"✅ Analysis stored with ID: {analysis_id}")
    
    # Retrieve analysis
    retrieved = db.retrieve_analysis(analysis_id)
    print(f"✅ Retrieved analysis: {retrieved['emotion_label']} (score: {retrieved['overall_score']})")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"\n📊 Database Statistics:")
    print(f"  Total analyses: {stats['total_analyses']}")
    print(f"  Avg emotion score: {stats['overall_avg_emotion']:.2f}")
    
    print(f"\n💾 Database Module Ready")
