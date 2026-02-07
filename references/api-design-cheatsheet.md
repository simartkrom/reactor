# API Design Cheatsheet

> Best practices for designing clean, scalable APIs

---

## 1. Naming

| 원칙 | 올바른 예 | 잘못된 예 |
|------|-----------|-----------|
| Use Nouns | `/users` | `/getUsers` |
| Plural Resources | `/orders` | `/order` |
| Nested Relations | `/users/123/orders` | - |
| Kebab-case | `/user-profiles` | `/userProfiles` |

---

## 2. Methods

| Method | 역할 | 멱등성 |
|--------|------|--------|
| **GET** | Retrieve (조회) | Idempotent |
| **POST** | Create (생성) | Not idempotent |
| **PUT** | Replace entire resource (전체 교체) | Idempotent |
| **PATCH** | Partial update (부분 수정) | Not idempotent |
| **DELETE** | Remove resource (제거) | Idempotent |

---

## 3. Response

- **Consistent Format** - 항상 `{data, error, meta}` 구조 유지
- **Proper Status Codes** - `200`, `201`, `400`, `404`, `500`
- **Error Messages** - Clear, actionable errors
- **Envelope Pattern** - Wrap response in `{data: ...}`

```json
{
  "data": { ... },
  "error": null,
  "meta": { "page": 1, "total": 100 }
}
```

---

## 4. Filtering

| 기능 | 쿼리 파라미터 예시 |
|------|---------------------|
| Query Params | `?status=active&type=admin` |
| Pagination | `?page=2&limit=20` |
| Sorting | `?sort=created_at:desc` |
| Field Selection | `?fields=id,name,email` |

---

## 5. Security

- **Always HTTPS** - Never expose plain HTTP
- **Auth Token** - JWT in Authorization header
- **Rate Limiting** - `X-RateLimit-*` headers
- **Input Validation** - Sanitize all inputs

---

## 6. Versioning

| 방식 | 예시 |
|------|------|
| URL Versioning | `/api/v1/users` |
| Header Versioning | `Accept-Version: v1` |
| Deprecation | `Sunset` header + docs |
| Changelog | Document breaking changes |

---

> 잘 설계된 API는 코드보다 오래 살아남는 제품 인터페이스다.

*Source: @theskilledcoder*
