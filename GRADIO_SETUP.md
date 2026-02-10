# Gradio Web Application - Setup Guide

## Overview

The BTC Fake project now includes a **web-based interface** using Gradio. Instead of running Jupyter notebooks, you can use a browser-based UI to:

- Upload employee CSV files
- Configure simulation parameters
- Run simulations with real-time progress
- Download generated files
- Preview employee data
- Test API connections
- View current configuration

---

## Quick Start

### 1. Install Dependencies

First, ensure Gradio is installed:

```bash
pip install -r requirements.txt
```

This will install `gradio>=4.0.0` along with all other dependencies.

### 2. Configure Environment

Make sure your `.env` file is properly configured:

```bash
# Copy example if you don't have .env yet
cp .env.example .env

# Edit .env with your credentials
nano .env
```

**Required settings:**
- `DATABRICKS_TOKEN` - Personal access token
- `DATABRICKS_HOST` - Databricks workspace hostname
- `DATABRICKS_HTTP_PATH` - SQL warehouse path
- `SFTP_INBOUND_PASSWORD` - SFTP inbound password
- `SFTP_OUTBOUND_PASSWORD` - SFTP outbound password (if publishing)

### 3. Launch the Application

```bash
python app.py
```

You'll see output like:

```
Running on local URL:  http://0.0.0.0:7860

To create a public link, set `share=True` in `launch()`.
```

### 4. Open in Browser

Open your browser and navigate to:

```
http://localhost:7860
```

---

## Using the Web Interface

### Tab 1: Run Simulation

This is the main interface for running simulations.

**Steps:**

1. **Upload Employees CSV**
   - Click "Upload Employees CSV"
   - Select your employee file (e.g., `input/employees.csv`)
   - File must have columns: `employee_id`, `employee_edu_type`

2. **Set Parameters**
   - **Number of Employees**: Limit processing (0 = process all)
   - **Enable SFTP Publishing**: Check to upload files to SFTP outbound

3. **Run Simulation**
   - Click "🚀 Run Simulation"
   - Watch progress updates in real-time
   - View summary when complete

4. **Download Results**
   - Click "Download Generated Files (ZIP)"
   - Extract to see all generated CSV files:
     - `ContentUserCompletion_V2_*.csv`
     - `Non_Completed_Assignments_V2_*.csv`
     - `UserCompletion_v2_*.csv`

**Example Summary Output:**

```
Processing 10 employees

Employee 319994 (b): Completed 1 training(s)
  - 2,033,875 (source: manager)
Employee 1233203 (a): Completed 5 training(s)
  - 2,033,875 (source: manager)
  - 2,030,735 (source: manager)
  - 2,021,630 (source: manager)
  - 1,915,085 (source: AI)
  - 892,298 (source: AI)

Total completions: 15

✓ Generated: ContentUserCompletion_V2_2026_2_6_1_abc123.csv
✓ Generated: Non_Completed_Assignments_V2_2026_2_6_1_abc123.csv
✓ Generated: UserCompletion_v2_2026_2_6_1_abc123.csv

================================================================================
SIMULATION COMPLETE
================================================================================
```

### Tab 2: Preview Employees

Preview employee data before running simulation.

**Steps:**

1. Upload employee CSV file
2. Click "👁️ Preview File"
3. View summary statistics and first 20 rows

**Example Output:**

```
Total employees: 1845

Employee types:
b    922
a    615
f    308

First 20 rows:
   employee_id employee_edu_type
0       319994                 b
1      1233203                 a
2      2371156                 b
...
```

### Tab 3: Test API

Test connectivity to ML Training Recommender API.

**Steps:**

1. Enter an employee ID (e.g., `88563`)
2. Click "🧪 Test API Connection"
3. View API response and recommendations

**Example Success:**

```
✓ API Success!

Recommendations for employee 88563:
  - 1915085
  - 892298
  - 1561228
```

**Example Error:**

```
✗ API Error: Connection timeout
```

### Tab 4: Configuration

View current configuration loaded from `.env` file.

Shows all settings:
- API configuration
- Databricks connection
- SFTP servers
- File paths

---

## Advanced Usage

### Custom Port

Run on a different port:

```python
# Edit app.py, change the last line:
app.launch(
    server_name="0.0.0.0",
    server_port=8080,  # Changed from 7860
    share=False
)
```

### Public Access (Share Mode)

Create a temporary public URL for sharing:

```python
# Edit app.py:
app.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=True  # Creates public URL
)
```

You'll get output like:

```
Running on local URL:  http://0.0.0.0:7860
Running on public URL: https://abc123xyz.gradio.live

This share link expires in 72 hours.
```

⚠️ **Warning**: Public links expose your application to the internet. Only use for demos/testing.

### Authentication

Add password protection:

```python
# Edit app.py:
app.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False,
    auth=("username", "password")  # Add authentication
)
```

### Running in Background

Use `nohup` to keep running after logout:

```bash
nohup python app.py > gradio.log 2>&1 &

# Check if running
ps aux | grep app.py

# View logs
tail -f gradio.log

# Stop
pkill -f app.py
```

---

## Deployment Options

### Option 1: Local Development

Best for: Personal use, development

```bash
python app.py
# Access at http://localhost:7860
```

### Option 2: Internal Server

Best for: Team access on internal network

1. Deploy to internal server (e.g., Linux VM)
2. Run with systemd for auto-restart
3. Configure firewall to allow port 7860
4. Team accesses via `http://server-ip:7860`

**Example systemd service** (`/etc/systemd/system/btc-fake.service`):

```ini
[Unit]
Description=BTC Fake Gradio Application
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/btc_fake
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl enable btc-fake
sudo systemctl start btc-fake
sudo systemctl status btc-fake
```

### Option 3: Docker Container

Best for: Consistent deployment, isolation

**Dockerfile**:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["python", "app.py"]
```

**Build and run**:

```bash
# Build
docker build -t btc-fake-gradio .

# Run
docker run -p 7860:7860 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/generated_files:/app/generated_files \
  btc-fake-gradio
```

### Option 4: Cloud Deployment

Best for: Remote access, sharing with stakeholders

**Hugging Face Spaces** (Free hosting for Gradio apps):

1. Create account at https://huggingface.co
2. Create new Space (select Gradio)
3. Push code to Space repository
4. App auto-deploys

**Note**: For production with sensitive data, use internal deployment options.

---

## Comparison: Gradio vs Jupyter Notebook

| Feature | Jupyter Notebook | Gradio Web App |
|---------|------------------|----------------|
| **Interface** | Code cells | Web forms |
| **Ease of Use** | Technical users | Non-technical users |
| **Access** | Local VS Code | Browser (shareable) |
| **Customization** | High (code) | Medium (UI) |
| **Team Use** | Individual | Multi-user |
| **Deployment** | Not applicable | Server/cloud |
| **Progress Feedback** | Print statements | Real-time UI |
| **File Management** | Manual | Automatic download |

---

## Troubleshooting

### Issue: Port Already in Use

**Error**: `OSError: [Errno 48] Address already in use`

**Solution**:

```bash
# Find process using port 7860
lsof -i :7860

# Kill the process
kill -9 <PID>

# Or change port in app.py
```

### Issue: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'gradio'`

**Solution**:

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: File Upload Fails

**Error**: CSV parsing errors

**Solution**:

- Ensure CSV has required columns: `employee_id`, `employee_edu_type`
- Check for proper CSV formatting
- Remove any malformed rows
- Test with sample file: `input/employees.csv`

### Issue: API Connection Timeout

**Error**: API calls fail in "Test API" tab

**Solution**:

- Verify `.env` has correct `API_BASE_URL`
- Check network connectivity
- Test API endpoint manually with curl:

```bash
curl -X POST https://dataiku-api-devqa.lower.internal.sephora.com/public/api/v1/mltr/v3/run \
  -H "Content-Type: application/json" \
  -d '{"data": {"ba_id": 88563}}'
```

### Issue: Slow Performance

**Problem**: Simulation takes too long

**Solution**:

- Use "Number of Employees" slider to limit processing
- Start with small test (10-50 employees)
- Check API response times in "Test API" tab
- Consider caching API responses for development

---

## Features Roadmap

Future enhancements planned:

- [ ] SFTP file download via web UI
- [ ] Real-time SFTP publishing progress
- [ ] Databricks query results preview
- [ ] Batch simulation comparison
- [ ] Export configuration profiles
- [ ] Simulation history/logs
- [ ] CSV validation before simulation
- [ ] Dark mode theme
- [ ] Mobile-responsive design

---

## Getting Help

If you encounter issues:

1. Check the troubleshooting section above
2. Review `.env` configuration
3. Test individual components (API, file upload, etc.)
4. Check Gradio logs in terminal
5. Verify all dependencies are installed

---

## Summary

The Gradio web interface provides an easy-to-use alternative to Jupyter notebooks:

✅ **User-friendly** - No code knowledge required
✅ **Shareable** - Run on server, access from any browser
✅ **Interactive** - Real-time feedback and progress
✅ **Accessible** - Perfect for demos and team collaboration

**To get started:**

```bash
pip install -r requirements.txt
python app.py
# Open http://localhost:7860
```

Enjoy the web interface!
