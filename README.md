# Alignator - Political Alignment Analysis

A Python project for analyzing political alignment of Congress members through their bills and floor addresses using the Congress.gov API.

## Features

- **Congress.gov API Integration**: Pulls data from the official Congress.gov API v3
- **Bill Analysis**: Analyzes bill content, sponsors, and voting patterns
- **Floor Address Analysis**: Processes floor speeches and statements
- **Political Alignment Assessment**: Uses NLP techniques to assess political positioning
- **Data Visualization**: Interactive dashboards and charts
- **Export Capabilities**: Export analysis results in various formats

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Setup**:
   - Get a free API key from [Congress.gov](https://api.congress.gov/sign-up/)
   - Create a `.env` file with your API key:
     ```
     CONGRESS_API_KEY=your_api_key_here
     ```

3. **Run the Application**:
   ```bash
   python main.py
   ```

## Project Structure

```
alignator/
├── src/
│   ├── api/           # Congress.gov API client
│   ├── analysis/      # Political alignment analysis
│   ├── data/          # Data processing and storage
│   ├── models/        # ML/NLP models
│   └── utils/         # Utility functions
├── data/              # Data storage
├── notebooks/         # Jupyter notebooks for exploration
├── tests/             # Unit tests
├── requirements.txt   # Python dependencies
└── main.py           # Main application entry point
```

## API Endpoints Used

- `/bill` - Bill information and text
- `/member` - Member information
- `/congressional-record` - Floor speeches and statements
- `/vote` - Voting records

## Analysis Methods

1. **Text Analysis**: NLP processing of bill text and speeches
2. **Voting Pattern Analysis**: Statistical analysis of voting behavior
3. **Network Analysis**: Co-sponsorship and voting coalitions
4. **Topic Modeling**: Identifying key policy areas and positions

## License

MIT License - see LICENSE file for details.
