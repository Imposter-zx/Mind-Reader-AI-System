# 🧪 Testing Guide - Mind Reader AI System

## Table of Contents
1. [Quick Test](#quick-test)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [API Testing](#api-testing)
5. [Performance Testing](#performance-testing)
6. [Security Testing](#security-testing)

---

## Quick Test

### 1. Start the API
```bash
# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Start API
python mind_reader_api_enhanced.py
```

### 2. Run Built-in Test Client
```bash
# In another terminal
python test_api_client.py

# With verbose output
python test_api_client.py --verbose

# Custom API URL
python test_api_client.py --api-url http://localhost:8000/api
```

### Expected Output
```
[2026-04-19 10:30:00] [INFO] ==================================================
[2026-04-19 10:30:00] [INFO] 🧠 Mind Reader AI - API Test Suite
[2026-04-19 10:30:00] [INFO] ==================================================
[2026-04-19 10:30:00] [INFO] 🏥 Testing health endpoint...
[2026-04-19 10:30:00] [SUCCESS] ✅ Health check passed: healthy
...
[2026-04-19 10:30:15] [INFO] ==================================================
[2026-04-19 10:30:15] [INFO] 📋 TEST SUMMARY
[2026-04-19 10:30:15] [INFO] ==================================================
✅ Health Check: PASS
✅ Emotion Analysis: PASS
✅ Personality Analysis: PASS
✅ Deception Detection: PASS
✅ Comprehensive Analysis: PASS
✅ Batch Analysis: PASS
✅ History: PASS
✅ Statistics: PASS
✅ Rate Limiting: PASS
[2026-04-19 10:30:15] [INFO] Total: 9 | Passed: 9 | Failed: 0 | Errors: 0
[2026-04-19 10:30:15] [INFO] Time: 2.34s
```

---

## Unit Testing

### Run Unit Tests
```bash
# Run all tests
pytest test_comprehensive_suite.py -v

# Run specific test class
pytest test_comprehensive_suite.py::TestEmotionDetection -v

# Run with coverage
pytest test_comprehensive_suite.py --cov=. --cov-report=html

# Run specific test
pytest test_comprehensive_suite.py::TestEmotionDetection::test_basic_emotion -v
```

### Run Mind Reader Tests
```bash
# Test core functionality
pytest test_mind_reader.py -v

# Test with output
pytest test_mind_reader.py -v -s
```

### Sample Test Output
```
test_comprehensive_suite.py::TestEmotionDetection::test_basic_emotion PASSED [ 10%]
test_comprehensive_suite.py::TestEmotionDetection::test_negative_emotion PASSED [ 20%]
test_comprehensive_suite.py::TestPersonalityAnalysis::test_mbti_analysis PASSED [ 30%]
...
======================== 45 passed in 2.34s ========================
```

---

## Integration Testing

### Test Multiple Components Together
```python
# integration_test.py
import pytest
from mind_reader_lightweight import MindScoreAPI
from database_integration import AnalysisDatabase
from performance_optimizer import AnalysisCache

class TestIntegration:
    @pytest.fixture
    def setup(self):
        """Setup test fixtures"""
        self.api = MindScoreAPI()
        self.db = AnalysisDatabase()
        self.cache = AnalysisCache()
        yield
        # Cleanup
        self.db.clear()
    
    def test_end_to_end_analysis(self, setup):
        """Test complete analysis pipeline"""
        text = "I am very happy about this!"
        
        # Analyze
        result = self.api.analyze_emotion(text)
        
        # Store in database
        analysis_id = self.db.store_analysis(text, "emotion", result)
        
        # Retrieve from database
        retrieved = self.db.get_analysis(analysis_id)
        
        # Verify
        assert retrieved is not None
        assert retrieved['result'] == result
```

### Run Integration Tests
```bash
pytest integration_test.py -v
```

---

## API Testing

### Using test_api_client.py

Comprehensive automated API testing:
```bash
python test_api_client.py --verbose
```

### Manual API Testing with cURL

#### 1. Authentication
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user"}'

# Save token for other requests
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test_user"}' | jq -r '.access_token')
```

#### 2. Test Emotion Analysis
```bash
curl -X POST http://localhost:5000/api/analyze/emotion \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"I am very happy!"}'

# Response
{
  "status": "success",
  "emotion": {
    "primary_emotion": "joy",
    "confidence": 0.95,
    "sentiment": "positive",
    "sentiment_score": 0.87
  }
}
```

#### 3. Test Personality Analysis
```bash
curl -X POST http://localhost:5000/api/analyze/personality \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"I love solving complex problems..."}'
```

#### 4. Test Comprehensive Analysis
```bash
curl -X POST http://localhost:5000/api/analyze/comprehensive \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text":"Your text here",
    "metadata":{"source":"testing"}
  }'
```

#### 5. Test Batch Processing
```bash
curl -X POST http://localhost:5000/api/batch/analyze \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "texts":["Text 1", "Text 2", "Text 3"],
    "analysis_type":"comprehensive"
  }'
```

### Using Python Requests
```python
import requests

BASE_URL = "http://localhost:5000/api"

# Authenticate
response = requests.post(f"{BASE_URL}/auth/login",
                        json={"username": "test_user"})
token = response.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Test emotion analysis
response = requests.post(
    f"{BASE_URL}/analyze/emotion",
    headers=headers,
    json={"text": "I am very happy!"}
)

print(response.json())
```

### Using Postman

1. **Import Collection:**
   - Download `mind_reader_api.postman_collection.json`
   - Open Postman → Import → Select file

2. **Setup Environment:**
   - Create new environment
   - Add variable: `api_url` = `http://localhost:5000/api`
   - Add variable: `token` = (auto-populated from login)

3. **Run Tests:**
   - Select collection
   - Click "Run" button
   - Monitor test results

---

## Performance Testing

### Load Testing with Apache AB
```bash
# Single request performance
ab -n 100 -c 10 http://localhost:5000/api/health

# Response analysis
ab -n 1000 -c 50 -p request.json \
   -T "application/json" \
   http://localhost:5000/api/analyze/emotion
```

### Stress Testing with Apache AB
```bash
# Increase load gradually
for concurrent in 10 50 100 200; do
  echo "Testing with $concurrent concurrent connections..."
  ab -n 500 -c $concurrent http://localhost:5000/api/health
done
```

### Using Python - locust
```bash
# Install
pip install locust

# Create locustfile.py
cat > locustfile.py << 'EOF'
from locust import HttpUser, task

class APIUser(HttpUser):
    @task
    def emotion_analysis(self):
        self.client.post(
            "/api/analyze/emotion",
            json={"text": "I am happy"},
            headers={"Authorization": "Bearer token"}
        )
    
    @task
    def health_check(self):
        self.client.get("/api/health")
EOF

# Run
locust -f locustfile.py --host=http://localhost:5000
```

Then open: `http://localhost:8089`

### Memory Profiling
```bash
# Install
pip install memory-profiler

# Profile function
python -m memory_profiler script.py

# Or in code
from memory_profiler import profile

@profile
def analyze_text(text):
    # Your code
    pass
```

### Response Time Benchmarks
```python
import time
import requests

def benchmark_api():
    BASE_URL = "http://localhost:5000/api"
    headers = {"Authorization": f"Bearer {token}"}
    
    timestamps = []
    
    for i in range(100):
        start = time.time()
        requests.post(
            f"{BASE_URL}/analyze/emotion",
            headers=headers,
            json={"text": f"Test {i}"}
        )
        elapsed = time.time() - start
        timestamps.append(elapsed)
    
    print(f"Avg: {sum(timestamps)/len(timestamps):.3f}s")
    print(f"Min: {min(timestamps):.3f}s")
    print(f"Max: {max(timestamps):.3f}s")
    print(f"P95: {sorted(timestamps)[int(len(timestamps)*0.95)]:.3f}s")
```

---

## Security Testing

### 1. SQL Injection Testing
```bash
# Should safely handle special characters
curl -X POST http://localhost:5000/api/analyze/emotion \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"test\"; DROP TABLE analyses; --"}'
```

### 2. XSS Testing
```bash
# Should sanitize output
curl -X POST http://localhost:5000/api/analyze/emotion \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"<script>alert(1)</script>"}'
```

### 3. Authentication Testing
```bash
# Should reject without token
curl -X GET http://localhost:5000/api/history
# Expected: 401 Unauthorized

# Should reject with invalid token
curl -X GET http://localhost:5000/api/history \
  -H "Authorization: Bearer invalid_token"
# Expected: 403 Forbidden
```

### 4. Rate Limiting
```bash
# Make rapid requests
for i in {1..100}; do
  curl -X POST http://localhost:5000/api/analyze/emotion \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"text":"test"}'
done

# Should eventually get 429 Too Many Requests
```

### 5. CORS Testing
```bash
# Should respect CORS headers
curl -X OPTIONS http://localhost:5000/api/analyze/emotion \
  -H "Origin: http://untrusted.com" \
  -H "Access-Control-Request-Method: POST"

# Should reject from untrusted origin
# Check response headers
```

---

## Continuous Integration

### GitHub Actions Example
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest test_comprehensive_suite.py --cov
    
    - name: Start API
      run: python mind_reader_api_enhanced.py &
      
    - name: Run API tests
      run: python test_api_client.py
```

---

## Test Coverage

### Generate Coverage Report
```bash
# Run tests with coverage
pytest test_comprehensive_suite.py --cov=. --cov-report=html

# Open report
open htmlcov/index.html
```

### Coverage Thresholds
- Target: >80% code coverage
- Critical paths: >95%
- Minimum acceptable: >70%

---

## Troubleshooting Tests

### Issue: Tests Fail with "Connection Refused"
```bash
# Make sure API is running
curl http://localhost:5000/api/health

# If not, start it
python mind_reader_api_enhanced.py
```

### Issue: "Token Expired" Errors
```bash
# Re-authenticate in test client
python test_api_client.py --verbose
```

### Issue: Database Lock
```bash
# Clear database
rm mind_reader.db

# Or for PostgreSQL
dropdb mindreader_test
createdb mindreader_test
```

### Issue: Rate Limit Errors
```bash
# Wait before retrying
time.sleep(2)

# Or disable rate limiting in tests
RATELIMIT_ENABLED=False pytest test_api_client.py
```

---

## Best Practices

1. **Isolate Tests:**
   - Use fixtures for setup/teardown
   - Create separate test databases
   - Clean up after each test

2. **Mock External Services:**
   - Mock API calls to third-party services
   - Use fixtures for consistent test data

3. **Test Edge Cases:**
   - Empty strings
   - Very long strings
   - Special characters
   - Unicode/emojis

4. **Performance Tests:**
   - Run regularly
   - Track trends
   - Alert on regressions

5. **Security Tests:**
   - Test authentication
   - Test authorization
   - Verify rate limiting

---

**Last Updated:** April 19, 2026  
**Version:** 2.0
