# Hardcoded Values Audit

## Environment-Specific Values That Should Be Externalized

### 1. API Configuration
| Variable | Current Value | Environment Impact | Should Externalize |
|----------|--------------|-------------------|-------------------|
| `API_BASE_URL` | `https://dataiku-api-devqa.lower.internal.sephora.com` | ✅ **YES** - Different URLs for DEV/QA/PROD | **HIGH PRIORITY** |
| `API_ENDPOINT` | `/public/api/v1/mltr/v3/run` | ⚠️ MAYBE - Might change between versions | MEDIUM PRIORITY |

**Impact**: Currently hardcoded to DEV/QA environment. Production uses different base URL.

---

### 2. File Paths
| Variable | Current Value | Environment Impact | Should Externalize |
|----------|--------------|-------------------|-------------------|
| `EMPLOYEES_FILE` | `input/employees.csv` | ⚠️ MAYBE - Different test datasets | MEDIUM PRIORITY |
| `OUTPUT_DIR` | `generated_files` | ⚠️ MAYBE - Different output locations | LOW PRIORITY |
| `SFTP_LOCAL_DIR` | `downloaded_files` | ⚠️ MAYBE - Different download locations | LOW PRIORITY |
| Template path | `docs/sample_files/UserCompletion_v2_YYYY_m_d_1_000001.csv` | ⚠️ MAYBE - Different templates per env | LOW PRIORITY |

**Impact**: Paths might vary between local development, testing, and production environments.

---

### 3. Databricks Configuration
| Variable | Current Status | Should Externalize |
|----------|---------------|-------------------|
| `DATABRICKS_HOST` | ✅ Already externalized via `.env` | ✓ DONE |
| `DATABRICKS_HTTP_PATH` | ✅ Already externalized via `.env` | ✓ DONE |
| `DATABRICKS_TOKEN` | ✅ Already externalized via `.env` | ✓ DONE |
| `DATABRICKS_CATALOG` | ⚠️ Has default, but in `.env` | ✓ DONE |
| `DATABRICKS_SCHEMA` | ⚠️ Has default, but in `.env` | ✓ DONE |

**Status**: Databricks configuration is already properly externalized.

---

### 4. SFTP Configuration
| Variable | Current Status | Should Externalize |
|----------|---------------|-------------------|
| `SFTP_INBOUND_HOST` | ✅ Already externalized via `.env` | ✓ DONE |
| `SFTP_INBOUND_USER` | ✅ Already externalized via `.env` | ✓ DONE |
| `SFTP_INBOUND_PASSWORD` | ✅ Already externalized via `.env` | ✓ DONE |
| `SFTP_INBOUND_REMOTE_PATH` | ✅ Already externalized via `.env` | ✓ DONE |

**Status**: SFTP configuration is already properly externalized.

---

### 5. Other Constants (Probably Don't Need Externalization)
| Variable | Current Value | Should Externalize |
|----------|--------------|-------------------|
| `PT` (timezone) | `America/Los_Angeles` | ❌ NO - Business requirement, not environment-specific |
| SSL verification | `verify=False` | ❌ NO - Internal APIs don't use valid certs |
| API timeout | `30` seconds | ⚠️ MAYBE - Could make configurable |

---

## Recommended Priority

### HIGH PRIORITY - Must Externalize
1. **API_BASE_URL** - Different per environment (DEV/QA/PROD)

### MEDIUM PRIORITY - Should Externalize
2. **API_ENDPOINT** - Might change between API versions
3. **EMPLOYEES_FILE** - Different test datasets per environment
4. **API_TIMEOUT** - Different performance characteristics per environment

### LOW PRIORITY - Optional Externalization
5. **OUTPUT_DIR** - Rarely changes
6. **SFTP_LOCAL_DIR** - Rarely changes
7. **Template file path** - Rarely changes

---

## Production vs. Non-Production URLs

### ML Training Recommender API
- **DEV/QA**: `https://dataiku-api-devqa.lower.internal.sephora.com`
- **Production**: `https://dataiku-api-prod.prod.internal.sephora.com/public`

Note: Production URL includes `/public` in the base URL while DEV/QA does not.

---

## Recommendations

### Immediate Actions
1. ✅ Externalize `API_BASE_URL` to environment variable
2. ✅ Externalize `API_ENDPOINT` (for flexibility)
3. ✅ Externalize `EMPLOYEES_FILE` path
4. ✅ Add `API_TIMEOUT` configuration
5. ✅ Add `USER_COMPLETION_TEMPLATE_FILE` path

### Configuration Strategy
- Use environment variables with sensible defaults
- Document which values must be changed per environment
- Provide environment-specific `.env.dev`, `.env.qa`, `.env.prod` examples
