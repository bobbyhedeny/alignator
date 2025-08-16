# Quick Start Guide

Get up and running with Alignator in 5 minutes!

## 1. Setup

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Get API Key
1. Visit [Congress.gov API Sign-up](https://api.congress.gov/sign-up/)
2. Create a free account
3. Copy your API key

### Configure Environment
1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```
2. Edit `.env` and add your API key:
   ```
   CONGRESS_API_KEY=your_actual_api_key_here
   ```

## 2. Test the Setup

Run the example script to verify everything works:
```bash
python fetch.py
```

You should see output like:
```
🏛️ Alignator - Congress.gov API Example
==================================================
✓ API client initialized

📊 Fetching Congress members...
✓ Found 535 members
✓ Members saved to database

👥 Sample Members:
  1. Nancy Pelosi (D) - CA
  2. Kevin McCarthy (R) - CA
  3. Chuck Schumer (D) - NY
  ...

📜 Fetching bills...
✓ Found 10 bills
✓ Bills saved to database

✅ Data fetching complete!
```

## 3. Explore the Data

### Check Status
```bash
python main.py status
```

### Launch Dashboard
```bash
python main.py dashboard
```

The dashboard will open in your browser at `http://localhost:8501`

## 4. Analyze Political Alignment

### Analyze All Members
```bash
python main.py analyze-alignment
```

### Analyze Specific Member
```bash
python main.py analyze-alignment --member-id MEMBER_ID
```

## 5. Available Commands

```bash
# Fetch data
python main.py fetch-members --congress 118
python main.py fetch-bills --congress 118 --limit 100

# Analyze alignment
python main.py analyze-alignment --congress 118

# Launch dashboard
python main.py dashboard

# Check status
python main.py status
```

## 6. Project Structure

```
alignator/
├── src/
│   ├── api/           # Congress.gov API client
│   ├── analysis/      # Political alignment analysis
│   ├── data/          # Data processing and storage
│   ├── dashboard/     # Streamlit dashboard
│   └── utils/         # Configuration and utilities
├── data/              # SQLite database and data files
├── tests/             # Unit tests
├── main.py           # Main CLI application
├── fetch.py          # Simple example script
└── requirements.txt  # Python dependencies
```

## 7. Troubleshooting

### API Key Issues
- Make sure your `.env` file exists and contains the correct API key
- Verify the API key is valid at [Congress.gov API](https://api.congress.gov/)

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're running from the project root directory

### Database Issues
- The SQLite database is automatically created in the `data/` directory
- If you encounter database errors, delete `data/alignator.db` and restart

### Dashboard Issues
- Make sure Streamlit is installed: `pip install streamlit`
- Check that port 8501 is available
- Try a different port: `streamlit run src/dashboard/app.py --server.port 8502`

## 8. Next Steps

1. **Explore the Dashboard**: Use the interactive dashboard to visualize political alignment
2. **Customize Analysis**: Modify the keyword lists in `src/analysis/alignment_analyzer.py`
3. **Add New Features**: Extend the analysis with additional metrics
4. **Run Tests**: `python -m pytest tests/`

## Support

- Check the [README.md](README.md) for detailed documentation
- Review the code comments for implementation details
- Open an issue on GitHub for bugs or feature requests
