# SkillsMP API Reference

## Base URL

```
https://skillsmp.com/api/v1
```

## Authentication

All API requests require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <SKILLSMP_API_KEY>
```

To obtain an API key, visit https://skillsmp.com/docs/api and click "Generate API Key".

## Endpoints

### Keyword Search

**GET** `/skills/search`

Search for skills using keyword matching.

**Query Parameters:**

| Parameter | Type   | Required | Default | Description                          |
|-----------|--------|----------|---------|--------------------------------------|
| q         | string | Yes      | -       | Search query term                    |
| page      | int    | No       | 1       | Page number for pagination           |
| limit     | int    | No       | 20      | Results per page (max: 100)          |
| sort      | string | No       | stars   | Sort order: `stars` or `recent`      |

**Response:**

```json
{
  "success": true,
  "total": 42,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "id": "skill-abc123",
      "name": "Web Scraper Pro",
      "description": "Advanced web scraping skill with support for dynamic pages",
      "stars": 128,
      "url": "https://skillsmp.com/skills/web-scraper-pro",
      "author": "username",
      "created_at": "2025-10-15T08:30:00Z",
      "updated_at": "2026-01-20T14:22:00Z"
    }
  ]
}
```

### AI Semantic Search

**GET** `/skills/ai-search`

Search for skills using AI-powered semantic matching.

**Query Parameters:**

| Parameter | Type   | Required | Description                              |
|-----------|--------|----------|------------------------------------------|
| q         | string | Yes      | Natural language query or description     |

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "id": "skill-abc123",
      "name": "Web Scraper Pro",
      "description": "Advanced web scraping skill with support for dynamic pages",
      "stars": 128,
      "url": "https://skillsmp.com/skills/web-scraper-pro",
      "relevance_score": 0.95,
      "author": "username"
    }
  ]
}
```

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": {
    "status": 401,
    "message": "Invalid or missing API key"
  }
}
```

### Common Error Codes

| Status | Description                                      |
|--------|--------------------------------------------------|
| 400    | Bad Request - Invalid parameters                 |
| 401    | Unauthorized - Invalid or missing API key        |
| 403    | Forbidden - Insufficient permissions             |
| 404    | Not Found - Endpoint or resource not found       |
| 429    | Too Many Requests - Rate limit exceeded          |
| 500    | Internal Server Error                            |

## Rate Limits

- Standard rate limiting applies to all endpoints
- Exceeding the rate limit returns a 429 status code
- Include a `Retry-After` header indicating wait time in seconds
