# Environment Configuration Guide

This document describes all configurable environment variables for the BTC Fake training completion simulator.

## Quick Start

1. Copy the appropriate environment template:
   ```bash
   # For DEV
   cp .env.dev.example .env

   # For QA
   cp .env.qa.example .env

   # For PROD
   cp .env.prod.example .env
   ```

2. Fill in the required credentials (marked with `your_*_here`)

3. Run the notebook

---

## Configuration Sections

### 1. ML Training Recommender API

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_BASE_URL` | **YES** | DEV/QA URL | API base URL (**varies by environment**) |
| `API_ENDPOINT` | No | `/public/api/v1/mltr/v3/run` | API endpoint path |
| `API_TIMEOUT` | No | `30` | API request timeout in seconds |

#### Environment-Specific Values

| Environment | API_BASE_URL |
|-------------|--------------|
| **DEV/QA** | `https://dataiku-api-devqa.lower.internal.sephora.com` |
| **PROD** | `https://dataiku-api-prod.prod.internal.sephora.com/public` |

⚠️ **IMPORTANT**: Production URL includes `/public` in the base URL!

---

### 2. File Paths

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMPLOYEES_FILE` | No | `input/employees.csv` | Path to employees input file |
| `OUTPUT_DIR` | No | `generated_files` | Output directory for generated files |
| `SFTP_LOCAL_DIR` | No | `downloaded_files` | Local directory for downloaded files |
| `USER_COMPLETION_TEMPLATE_FILE` | No | `docs/sample_files/UserCompletion_v2_YYYY_m_d_1_000001.csv` | Template file path |

💡 **TIP**: Use different employee files for different test scenarios

---

### 3. Databricks Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABRICKS_TOKEN` | **YES** | *(none)* | Personal access token |
| `DATABRICKS_HOST` | **YES** | *(none)* | Workspace hostname |
| `DATABRICKS_HTTP_PATH` | **YES** | *(none)* | SQL warehouse HTTP path |
| `DATABRICKS_CATALOG` | No | `retail_systems_dev` | Catalog name (**varies by environment**) |
| `DATABRICKS_SCHEMA` | No | `store_enablement` | Schema name |

#### Environment-Specific Values

| Environment | DATABRICKS_CATALOG |
|-------------|--------------------|
| **DEV** | `retail_systems_dev` |
| **QA** | `retail_systems_qa` |
| **PROD** | `retail_systems_prod` |

#### How to Get Databricks Credentials

1. **Token**: Databricks Workspace → User Settings → Access Tokens → Generate New Token
2. **Host**: Your workspace URL (e.g., `adb-1234567890123456.7.azuredatabricks.net`)
3. **HTTP Path**: Compute → SQL Warehouses → [Your Warehouse] → Connection Details → HTTP Path

---

### 4. SFTP Inbound Server

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SFTP_INBOUND_HOST` | No | `sftp.sephora.com` | SFTP server hostname |
| `SFTP_INBOUND_USER` | No | `SephoraMSL` | SFTP username |
| `SFTP_INBOUND_PASSWORD` | **YES** | *(none)* | SFTP password |
| `SFTP_INBOUND_REMOTE_PATH` | No | `/inbound/BTC/retailData/prod/...` | Remote directory path (**varies by environment**) |

#### Environment-Specific Values

| Environment | SFTP_INBOUND_REMOTE_PATH |
|-------------|--------------------------|
| **DEV** | `/inbound/BTC/retailData/dev/vendor/mySephoraLearning-archive` |
| **QA** | `/inbound/BTC/retailData/qa/vendor/mySephoraLearning-archive` |
| **PROD** | `/inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive` |

---

### 5. SFTP Outbound Server (Publishing)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SFTP_OUTBOUND_HOST` | No | `internal-sftp.sephoraus.com` | SFTP outbound server hostname |
| `SFTP_OUTBOUND_USER` | No | `SephoraRDIInternal` | SFTP outbound username |
| `SFTP_OUTBOUND_PASSWORD` | **YES** | *(none)* | SFTP outbound password |
| `SFTP_OUTBOUND_REMOTE_PATH` | No | `/inbound/BTC/retailData/prod/...` | Remote directory path (**varies by environment**) |
| `SFTP_PUBLISH_ENABLED` | No | `true` | Enable/disable file publishing |

#### Environment-Specific Values

| Environment | SFTP_OUTBOUND_REMOTE_PATH |
|-------------|---------------------------|
| **DEV** | `/inbound/BTC/retailData/dev/vendor/mySephoraLearningV2` |
| **QA** | `/inbound/BTC/retailData/qa/vendor/mySephoraLearningV2` |
| **PROD** | `/inbound/BTC/retailData/prod/vendor/mySephoraLearningV2` |

#### Publishing Control

To **enable** publishing (upload files after generation):
```bash
SFTP_PUBLISH_ENABLED=true
```

To **disable** publishing (skip upload, only generate files locally):
```bash
SFTP_PUBLISH_ENABLED=false
```

---

## Environment Comparison Matrix

### Required Changes Per Environment

| Variable | DEV | QA | PROD | Notes |
|----------|-----|-----|------|-------|
| `API_BASE_URL` | devqa URL | devqa URL | **prod URL** | ⚠️ **Different in PROD** |
| `DATABRICKS_CATALOG` | `_dev` | `_qa` | `_prod` | Suffix changes |
| `SFTP_INBOUND_REMOTE_PATH` | `/dev/` | `/qa/` | `/prod/` | Path segment changes |
| `SFTP_OUTBOUND_REMOTE_PATH` | `/dev/` | `/qa/` | `/prod/` | Path segment changes |
| Databricks credentials | DEV workspace | QA workspace | PROD workspace | All different |
| SFTP inbound password | DEV password | QA password | PROD password | All different |
| SFTP outbound password | DEV password | QA password | PROD password | All different |

---

## Validation Checklist

Before running the notebook in a new environment, verify:

### ✅ API Configuration
- [ ] `API_BASE_URL` points to correct environment
- [ ] For PROD: Verify `/public` is in base URL
- [ ] API is accessible from your network

### ✅ Databricks Configuration
- [ ] Token is valid and not expired
- [ ] Hostname matches the workspace
- [ ] HTTP path matches the warehouse
- [ ] Catalog name matches environment (dev/qa/prod)
- [ ] You have SELECT permission on `content_assignments` table

### ✅ SFTP Inbound Configuration
- [ ] Password is correct for the environment
- [ ] Remote path exists on SFTP server
- [ ] Network access to SFTP server (port 22)

### ✅ SFTP Outbound Configuration (Publishing)
- [ ] Outbound password is correct for the environment
- [ ] Remote path exists on SFTP outbound server
- [ ] Network access to SFTP outbound server (port 22)
- [ ] `SFTP_PUBLISH_ENABLED` is set to desired value (true/false)

### ✅ File Paths
- [ ] `EMPLOYEES_FILE` exists and contains valid data
- [ ] Output directories exist (or will be created)
- [ ] Template file exists

---

## Troubleshooting

### API Connection Errors

**Problem**: `Connection refused` or `Timeout`
- **Check**: Is `API_BASE_URL` correct for your environment?
- **Check**: Are you on the VPN or corporate network?
- **Check**: Is the API service running?

### Databricks Query Fails

**Problem**: `Table or view not found`
- **Check**: Is `DATABRICKS_CATALOG` correct for your environment?
- **Check**: Does the table exist: `{CATALOG}.{SCHEMA}.content_assignments`?
- **Check**: Do you have SELECT permission?

**Problem**: `Invalid access token`
- **Check**: Has the token expired? Generate a new one
- **Check**: Is the token for the correct workspace?

### SFTP Download Fails

**Problem**: `Authentication failed`
- **Check**: Is `SFTP_INBOUND_PASSWORD` correct?
- **Check**: Is the username correct for this environment?

**Problem**: `Directory not found`
- **Check**: Does `SFTP_INBOUND_REMOTE_PATH` exist?
- **Check**: Is the path correct for your environment (dev/qa/prod)?

### SFTP Outbound Publish Fails

**Problem**: `Publishing disabled` message
- **Check**: Is `SFTP_PUBLISH_ENABLED=true` in `.env`?
- **Note**: This is expected if you intentionally disabled publishing

**Problem**: `Authentication failed` during publishing
- **Check**: Is `SFTP_OUTBOUND_PASSWORD` correct?
- **Check**: Is the username correct for this environment?

**Problem**: `Directory not found` during publishing
- **Check**: Does `SFTP_OUTBOUND_REMOTE_PATH` exist?
- **Check**: Is the path correct for your environment (dev/qa/prod)?

---

## Security Best Practices

1. **Never commit `.env` files** - They contain secrets
2. **Use different credentials per environment** - Don't reuse tokens/passwords
3. **Rotate credentials regularly** - Especially Databricks tokens
4. **Limit token permissions** - Grant minimum required access
5. **Use environment-specific `.env` files** - e.g., `.env.dev`, `.env.qa`, `.env.prod`

---

## Example: Switching Environments

### From DEV to QA

```bash
# Backup current config
cp .env .env.backup

# Switch to QA config
cp .env.qa.example .env

# Fill in QA-specific credentials
# - Update DATABRICKS_TOKEN with QA workspace token
# - Update DATABRICKS_HOST with QA workspace hostname
# - Update DATABRICKS_HTTP_PATH with QA warehouse path
# - Update SFTP_INBOUND_PASSWORD with QA SFTP password

# Verify configuration
grep "API_BASE_URL" .env  # Should still be devqa
grep "DATABRICKS_CATALOG" .env  # Should be retail_systems_qa
grep "SFTP_INBOUND_REMOTE_PATH" .env  # Should have /qa/
```

### From QA to PROD

```bash
# Switch to PROD config
cp .env.prod.example .env

# CRITICAL CHANGES for PROD:
# - API_BASE_URL must include /public
# - DATABRICKS_CATALOG must be retail_systems_prod
# - SFTP_INBOUND_REMOTE_PATH must have /prod/
# - All credentials must be PROD credentials

# Double-check PROD-specific values
grep "API_BASE_URL" .env  # Must be prod URL with /public
grep "DATABRICKS_CATALOG" .env  # Must be retail_systems_prod
```

---

## Default Values Reference

All configuration variables have defaults except credentials:

```python
# Defaults from notebook (cell-1)
API_BASE_URL = "https://dataiku-api-devqa.lower.internal.sephora.com"
API_ENDPOINT = "/public/api/v1/mltr/v3/run"
API_TIMEOUT = 30

EMPLOYEES_FILE = "input/employees.csv"
OUTPUT_DIR = "generated_files"
SFTP_LOCAL_DIR = "downloaded_files"
USER_COMPLETION_TEMPLATE_FILE = "docs/sample_files/UserCompletion_v2_YYYY_m_d_1_000001.csv"

DATABRICKS_CATALOG = "retail_systems_dev"
DATABRICKS_SCHEMA = "store_enablement"

SFTP_INBOUND_HOST = "sftp.sephora.com"
SFTP_INBOUND_USER = "SephoraMSL"
SFTP_INBOUND_REMOTE_PATH = "/inbound/BTC/retailData/prod/vendor/mySephoraLearning-archive"

SFTP_OUTBOUND_HOST = "internal-sftp.sephoraus.com"
SFTP_OUTBOUND_USER = "SephoraRDIInternal"
SFTP_OUTBOUND_REMOTE_PATH = "/inbound/BTC/retailData/prod/vendor/mySephoraLearningV2"
SFTP_PUBLISH_ENABLED = "true"
```

💡 Defaults work for DEV environment - only credentials need to be added!
