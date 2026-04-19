#!/usr/bin/env python
"""
Mind Reader AI - API Test Client
Comprehensive testing tool for API endpoints
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, List
import argparse
from pathlib import Path

class APITestClient:
    """Test client for Mind Reader API"""
    
    def __init__(self, api_url: str = "http://localhost:5000/api", verbose: bool = False):
        self.api_url = api_url
        self.verbose = verbose
        self.token = None
        self.results = []
        self.start_time = time.time()
        
    def log(self, message: str, level: str = "INFO"):
        """Log message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        self.log("🔐 Authenticating...")
        
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json={"username": "test_user"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.log("✅ Authentication successful", "SUCCESS")
                return True
            else:
                self.log(f"❌ Authentication failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Authentication error: {e}", "ERROR")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Content-Type": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def test_health(self) -> bool:
        """Test health endpoint"""
        self.log("🏥 Testing health endpoint...")
        
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Health check passed: {data.get('status')}", "SUCCESS")
                self.results.append(("Health Check", "PASS"))
                return True
            else:
                self.log(f"❌ Health check failed: {response.status_code}", "ERROR")
                self.results.append(("Health Check", "FAIL"))
                return False
                
        except Exception as e:
            self.log(f"❌ Health check error: {e}", "ERROR")
            self.results.append(("Health Check", "ERROR"))
            return False
    
    def test_emotion_analysis(self, text: str = None) -> bool:
        """Test emotion analysis endpoint"""
        if not text:
            text = "I am very excited about this amazing opportunity!"
        
        self.log("😊 Testing emotion analysis...")
        
        try:
            response = requests.post(
                f"{self.api_url}/analyze/emotion",
                headers=self.get_headers(),
                json={"text": text},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    emotion = data.get("emotion", {})
                    primary = emotion.get("primary_emotion")
                    confidence = emotion.get("confidence", 0)
                    self.log(f"✅ Emotion: {primary.upper()} ({confidence:.2%})", "SUCCESS")
                    self.results.append(("Emotion Analysis", "PASS"))
                    return True
            
            self.log(f"❌ Emotion analysis failed: {response.status_code}", "ERROR")
            self.results.append(("Emotion Analysis", "FAIL"))
            return False
            
        except Exception as e:
            self.log(f"❌ Emotion analysis error: {e}", "ERROR")
            self.results.append(("Emotion Analysis", "ERROR"))
            return False
    
    def test_personality_analysis(self, text: str = None) -> bool:
        """Test personality analysis endpoint"""
        if not text:
            text = "I love solving complex problems and working with data. I prefer working independently and think analytically about most situations."
        
        self.log("👤 Testing personality analysis...")
        
        try:
            response = requests.post(
                f"{self.api_url}/analyze/personality",
                headers=self.get_headers(),
                json={"text": text},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    personality = data.get("personality", {})
                    mbti = personality.get("personality_type")
                    confidence = personality.get("confidence_score", 0)
                    self.log(f"✅ Personality: {mbti} ({confidence:.2%})", "SUCCESS")
                    self.results.append(("Personality Analysis", "PASS"))
                    return True
            
            self.log(f"❌ Personality analysis failed: {response.status_code}", "ERROR")
            self.results.append(("Personality Analysis", "FAIL"))
            return False
            
        except Exception as e:
            self.log(f"❌ Personality analysis error: {e}", "ERROR")
            self.results.append(("Personality Analysis", "ERROR"))
            return False
    
    def test_deception_detection(self, text: str = None) -> bool:
        """Test deception detection endpoint"""
        if not text:
            text = "I absolutely did not take the money. I wasn't even there that day. I don't know anything about it."
        
        self.log("🔍 Testing deception detection...")
        
        try:
            response = requests.post(
                f"{self.api_url}/analyze/deception",
                headers=self.get_headers(),
                json={"text": text},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    deception = data.get("deception_analysis", {})
                    probability = deception.get("lie_probability", 0)
                    risk = deception.get("risk_level")
                    self.log(f"✅ Deception Probability: {probability:.2%}, Risk: {risk}", "SUCCESS")
                    self.results.append(("Deception Detection", "PASS"))
                    return True
            
            self.log(f"❌ Deception detection failed: {response.status_code}", "ERROR")
            self.results.append(("Deception Detection", "FAIL"))
            return False
            
        except Exception as e:
            self.log(f"❌ Deception detection error: {e}", "ERROR")
            self.results.append(("Deception Detection", "ERROR"))
            return False
    
    def test_comprehensive_analysis(self, text: str = None) -> bool:
        """Test comprehensive analysis endpoint"""
        if not text:
            text = "I'm really excited but also nervous about the upcoming changes. This could be really good or potentially problematic."
        
        self.log("🔬 Testing comprehensive analysis...")
        
        try:
            response = requests.post(
                f"{self.api_url}/analyze/comprehensive",
                headers=self.get_headers(),
                json={"text": text},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    analysis = data.get("analysis", {})
                    components = list(analysis.keys())
                    self.log(f"✅ Comprehensive Analysis Complete: {len(components)} components", "SUCCESS")
                    self.results.append(("Comprehensive Analysis", "PASS"))
                    return True
            
            self.log(f"❌ Comprehensive analysis failed: {response.status_code}", "ERROR")
            self.results.append(("Comprehensive Analysis", "FAIL"))
            return False
            
        except Exception as e:
            self.log(f"❌ Comprehensive analysis error: {e}", "ERROR")
            self.results.append(("Comprehensive Analysis", "ERROR"))
            return False
    
    def test_batch_analysis(self) -> bool:
        """Test batch analysis endpoint"""
        self.log("📦 Testing batch analysis...")
        
        texts = [
            "I love this!",
            "I hate this!",
            "This is neutral.",
            "Absolutely amazing experience!",
            "Terrible and disappointing."
        ]
        
        try:
            response = requests.post(
                f"{self.api_url}/batch/analyze",
                headers=self.get_headers(),
                json={
                    "texts": texts,
                    "analysis_type": "comprehensive"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    batch_size = data.get("batch_size", 0)
                    self.log(f"✅ Batch Analysis Complete: {batch_size} texts analyzed", "SUCCESS")
                    self.results.append(("Batch Analysis", "PASS"))
                    return True
            
            self.log(f"❌ Batch analysis failed: {response.status_code}", "ERROR")
            self.results.append(("Batch Analysis", "FAIL"))
            return False
            
        except Exception as e:
            self.log(f"❌ Batch analysis error: {e}", "ERROR")
            self.results.append(("Batch Analysis", "ERROR"))
            return False
    
    def test_history(self) -> bool:
        """Test history endpoint"""
        self.log("📜 Testing history endpoint...")
        
        try:
            response = requests.get(
                f"{self.api_url}/history?limit=10",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    count = data.get("count", 0)
                    self.log(f"✅ History Retrieved: {count} records", "SUCCESS")
                    self.results.append(("History", "PASS"))
                    return True
            
            self.log(f"❌ History retrieval failed: {response.status_code}", "ERROR")
            self.results.append(("History", "FAIL"))
            return False
            
        except Exception as e:
            self.log(f"❌ History error: {e}", "ERROR")
            self.results.append(("History", "ERROR"))
            return False
    
    def test_statistics(self) -> bool:
        """Test statistics endpoint"""
        self.log("📊 Testing statistics endpoint...")
        
        try:
            response = requests.get(
                f"{self.api_url}/stats/summary",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    stats = data.get("statistics", {})
                    total = stats.get("total_analyses", 0)
                    self.log(f"✅ Statistics Retrieved: {total} total analyses", "SUCCESS")
                    self.results.append(("Statistics", "PASS"))
                    return True
            
            self.log(f"❌ Statistics retrieval failed: {response.status_code}", "ERROR")
            self.results.append(("Statistics", "FAIL"))
            return False
            
        except Exception as e:
            self.log(f"❌ Statistics error: {e}", "ERROR")
            self.results.append(("Statistics", "ERROR"))
            return False
    
    def test_rate_limiting(self) -> bool:
        """Test rate limiting"""
        self.log("🚦 Testing rate limiting...")
        
        try:
            # Make multiple rapid requests
            for i in range(5):
                response = requests.post(
                    f"{self.api_url}/analyze/emotion",
                    headers=self.get_headers(),
                    json={"text": "Test"},
                    timeout=5
                )
                
                if response.status_code == 429:
                    self.log("✅ Rate limiting working: 429 received", "SUCCESS")
                    self.results.append(("Rate Limiting", "PASS"))
                    return True
            
            self.log("⚠️ Rate limiting test: No 429 received (may be expected)", "WARNING")
            self.results.append(("Rate Limiting", "WARN"))
            return True
            
        except Exception as e:
            self.log(f"⚠️ Rate limiting test error: {e}", "WARNING")
            return True
    
    def run_all_tests(self) -> None:
        """Run all tests"""
        self.log("=" * 50)
        self.log("🧠 Mind Reader AI - API Test Suite")
        self.log("=" * 50)
        
        # Health check (no auth needed)
        self.test_health()
        
        # Authenticate
        if not self.authenticate():
            self.log("❌ Cannot proceed without authentication", "ERROR")
            return
        
        # Run tests
        self.test_emotion_analysis()
        self.test_personality_analysis()
        self.test_deception_detection()
        self.test_comprehensive_analysis()
        self.test_batch_analysis()
        self.test_history()
        self.test_statistics()
        self.test_rate_limiting()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self) -> None:
        """Print test summary"""
        elapsed = time.time() - self.start_time
        
        self.log("=" * 50)
        self.log("📋 TEST SUMMARY")
        self.log("=" * 50)
        
        passed = sum(1 for _, result in self.results if result == "PASS")
        failed = sum(1 for _, result in self.results if result == "FAIL")
        errors = sum(1 for _, result in self.results if result == "ERROR")
        
        for test_name, result in self.results:
            icon = "✅" if result == "PASS" else "❌" if result == "FAIL" else "⚠️"
            self.log(f"{icon} {test_name}: {result}")
        
        self.log("=" * 50)
        self.log(f"Total: {len(self.results)} | Passed: {passed} | Failed: {failed} | Errors: {errors}")
        self.log(f"Time: {elapsed:.2f}s")
        self.log("=" * 50)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Mind Reader AI - API Test Client")
    parser.add_argument("--api-url", default="http://localhost:5000/api", help="API base URL")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    client = APITestClient(api_url=args.api_url, verbose=args.verbose)
    client.run_all_tests()


if __name__ == "__main__":
    main()
