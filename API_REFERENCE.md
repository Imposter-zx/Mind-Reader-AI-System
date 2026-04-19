# 📚 Mind Reader AI - API Reference v2.0

## Base URL
```
http://localhost:5000/api
```

---

## Authentication

### Endpoint: POST /auth/login
**Description:** Authenticate user and get JWT token

**Request:**
```json
{
  "username": "user@example.com"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

**Error (401):**
```json
{
  "error": "Authentication failed"
}
```

---

## Health & Status

### Endpoint: GET /health
**Description:** Check system health status

**No authentication required**

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2026-04-19T10:30:00.000Z",
  "version": "2.0"
}
```

---

## Text Analysis

### Endpoint: POST /analyze/emotion
**Description:** Analyze emotions and sentiment from text

**Authentication:** Required (Bearer token)

**Request:**
```json
{
  "text": "I am very happy about this achievement!"
}
```

**Response (200):**
```json
{
  "status": "success",
  "emotion": {
    "primary_emotion": "joy",
    "confidence": 0.95,
    "sentiment": "positive",
    "sentiment_score": 0.87,
    "emotions": {
      "joy": 0.95,
      "trust": 0.45,
      "fear": 0.02,
      "surprise": 0.12,
      "sadness": 0.01,
      "disgust": 0.00,
      "anger": 0.00,
      "anticipation": 0.78
    },
    "emotional_intensity": "high"
  },
  "timestamp": "2026-04-19T10:30:00.000Z"
}
```

**Headers:**
- `Authorization: Bearer <token>`
- `Content-Type: application/json`

**Rate Limit:** 30 requests/minute

---

### Endpoint: POST /analyze/personality
**Description:** Analyze personality traits from text

**Authentication:** Required

**Request:**
```json
{
  "text": "I enjoy solving complex mathematical problems and working with data..."
}
```

**Response (200):**
```json
{
  "status": "success",
  "personality": {
    "big_five": {
      "openness": 0.78,
      "conscientiousness": 0.82,
      "extraversion": 0.45,
      "agreeableness": 0.65,
      "neuroticism": 0.32
    },
    "personality_type": "INTJ",
    "dominant_traits": [
      "analytical",
      "logical",
      "independent",
      "strategic"
    ],
    "archetype": "The Visionary",
    "motivation_style": "intrinsic",
    "communication_style": "direct",
    "confidence_score": 0.88
  },
  "timestamp": "2026-04-19T10:30:00.000Z"
}
```

**Rate Limit:** 20 requests/minute

---

### Endpoint: POST /analyze/deception
**Description:** Detect potential deception patterns

**Authentication:** Required

**Request:**
```json
{
  "text": "I absolutely did not steal the money. I wasn't even there..."
}
```

**Response (200):**
```json
{
  "status": "success",
  "deception_analysis": {
    "lie_probability": 0.72,
    "confidence": 0.84,
    "deception_indicators": [
      "excessive_denial",
      "defensive_language",
      "pronoun_avoidance",
      "over_explanation"
    ],
    "linguistic_markers": {
      "excessive_detail": true,
      "contradictions": 1,
      "pronoun_usage": "low",
      "emotional_words": 8,
      "certainty_modifiers": "high"
    },
    "risk_level": "high",
    "recommendation": "Further investigation recommended"
  },
  "timestamp": "2026-04-19T10:30:00.000Z"
}
```

**Rate Limit:** 20 requests/minute

---

### Endpoint: POST /analyze/dangerous
**Description:** Assess danger level and risk factors

**Authentication:** Required

**Request:**
```json
{
  "text": "I'm thinking about confronting them violently..."
}
```

**Response (200):**
```json
{
  "status": "success",
  "danger_assessment": {
    "risk_level": "HIGH",
    "danger_score": 0.85,
    "threat_indicators": [
      "violent_language",
      "intent_expression",
      "emotional_intensity"
    ],
    "factors": {
      "expression_of_intent": 0.90,
      "emotional_agitation": 0.78,
      "violence_language": 0.88,
      "self_harm_indicators": 0.15
    },
    "recommended_action": "ALERT",
    "follow_up_required": true
  },
  "timestamp": "2026-04-19T10:30:00.000Z"
}
```

**Rate Limit:** 20 requests/minute

---

### Endpoint: POST /analyze/comprehensive
**Description:** Multi-modal comprehensive analysis

**Authentication:** Required

**Request:**
```json
{
  "text": "Your input text here...",
  "metadata": {
    "source": "interview",
    "language": "en",
    "speaker_id": "user123"
  }
}
```

**Response (200):**
```json
{
  "status": "success",
  "analysis": {
    "emotion": { /* emotion analysis */ },
    "personality": { /* personality analysis */ },
    "deception": { /* deception analysis */ },
    "danger": { /* danger assessment */ },
    "future_behavior": {
      "predicted_actions": ["likely_cooperation", "potential_conflict"],
      "confidence": 0.76,
      "behavior_pattern": "unpredictable"
    },
    "anomalies": {
      "detected": true,
      "anomaly_types": ["linguistic_inconsistency"],
      "severity": "medium"
    }
  },
  "metadata": {
    "source": "interview",
    "language": "en",
    "speaker_id": "user123"
  },
  "timestamp": "2026-04-19T10:30:00.000Z"
}
```

**Rate Limit:** 15 requests/minute

---

## Batch Processing

### Endpoint: POST /batch/analyze
**Description:** Analyze multiple texts in one request

**Authentication:** Required

**Request:**
```json
{
  "texts": [
    "Text one to analyze",
    "Another text sample",
    "Third text example"
  ],
  "analysis_type": "comprehensive"
}
```

**Response (200):**
```json
{
  "status": "success",
  "batch_size": 3,
  "results": [
    {
      "text": "Text one to analyze",
      "result": { /* analysis results */ }
    },
    {
      "text": "Another text sample",
      "result": { /* analysis results */ }
    }
  ],
  "timestamp": "2026-04-19T10:30:00.000Z"
}
```

**Analysis Types:**
- `comprehensive` - All features
- `emotion` - Emotion analysis only
- `personality` - Personality analysis only
- `deception` - Deception detection only

**Rate Limit:** 10 requests/minute

---

## History & Database

### Endpoint: GET /history
**Description:** Retrieve analysis history

**Authentication:** Required

**Query Parameters:**
- `limit` (int, optional, default=50): Number of records
- `offset` (int, optional, default=0): Pagination offset
- `filter` (string, optional): Filter by type (emotion, personality, etc.)

**Request:**
```
GET /history?limit=25&offset=0
```

**Response (200):**
```json
{
  "status": "success",
  "count": 25,
  "history": [
    {
      "id": 1,
      "timestamp": "2026-04-19T10:30:00.000Z",
      "text": "Analysis text...",
      "type": "comprehensive",
      "results": { /* analysis results */ }
    }
  ]
}
```

---

### Endpoint: GET /history/{id}
**Description:** Get specific analysis details

**Authentication:** Required

**Response (200):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "timestamp": "2026-04-19T10:30:00.000Z",
    "text": "Full analysis text...",
    "type": "comprehensive",
    "results": { /* full results */ }
  }
}
```

**Error (404):**
```json
{
  "error": "Analysis not found"
}
```

---

## Statistics

### Endpoint: GET /stats/summary
**Description:** Get system statistics summary

**Authentication:** Required

**Response (200):**
```json
{
  "status": "success",
  "statistics": {
    "total_analyses": 1547,
    "analyses_today": 145,
    "average_confidence": 0.867,
    "most_common_emotion": "neutral",
    "most_common_personality_type": "INTJ",
    "system_uptime_hours": 720
  },
  "timestamp": "2026-04-19T10:30:00.000Z"
}
```

**Cache:** 5 minutes

---

### Endpoint: GET /stats/performance
**Description:** Get API performance metrics

**Authentication:** Required

**Response (200):**
```json
{
  "status": "success",
  "metrics": {
    "cache_hits": 3245,
    "cache_misses": 1256,
    "cache_hit_rate": 0.7211,
    "db_queries": 4501,
    "avg_response_time": 245.3,
    "max_response_time": 1200,
    "min_response_time": 45,
    "requests_per_minute": 18.5
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Text is required",
  "status": "error"
}
```

### 401 Unauthorized
```json
{
  "error": "Missing Authorization Header"
}
```

### 403 Forbidden
```json
{
  "error": "Token has expired"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded: 30 per minute"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "timestamp": "2026-04-19T10:30:00.000Z"
}
```

---

## Rate Limiting

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/analyze/emotion` | 30 | per minute |
| `/analyze/personality` | 20 | per minute |
| `/analyze/deception` | 20 | per minute |
| `/analyze/dangerous` | 20 | per minute |
| `/analyze/comprehensive` | 15 | per minute |
| `/batch/analyze` | 10 | per minute |
| Global default | 200 | per day |

---

## Pagination

For endpoints returning lists, use pagination:

```
GET /history?limit=50&offset=0    # First 50 items
GET /history?limit=50&offset=50   # Next 50 items
```

---

## Caching

Some responses are cached for performance:

- `/stats/summary` - 5 minutes
- `/health` - 1 minute
- Analysis results - 1 hour (by content hash)

To bypass cache, add header:
```
X-Cache-Control: no-cache
```

---

## SDK Examples

### Python
```python
import requests

token = requests.post('http://localhost:5000/api/auth/login',
                     json={'username': 'user@example.com'}).json()['access_token']

headers = {'Authorization': f'Bearer {token}'}

result = requests.post('http://localhost:5000/api/analyze/emotion',
                      headers=headers,
                      json={'text': 'I am happy!'}).json()
```

### JavaScript
```javascript
const token = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  body: JSON.stringify({username: 'user@example.com'})
}).then(r => r.json()).then(d => d.access_token);

const result = await fetch('http://localhost:5000/api/analyze/emotion', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({text: 'I am happy!'})
}).then(r => r.json());
```

### cURL
```bash
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com"}' | jq -r '.access_token')

curl -X POST http://localhost:5000/api/analyze/emotion \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"I am happy!"}'
```

---

**API Version:** 2.0  
**Last Updated:** April 19, 2026  
**Status:** ✅ Production Ready
