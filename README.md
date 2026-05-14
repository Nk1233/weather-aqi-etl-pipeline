# Weather Data Automation Project

Automated weather and air quality data collection system that fetches data from OpenWeather API and WAQI API, then stores it in a PostgreSQL database.

## Features

- **Automated Data Collection**: Fetches weather and AQI data for 277 cities worldwide
- **Error Handling**: Robust error handling for API failures and timeouts
- **Database Storage**: Stores data in PostgreSQL database (Supabase)
- **Scheduled Automation**: Runs automatically every 6 hours via GitHub Actions
- **JSON Backup**: Maintains JSON backups of all collected data

## Project Structure

```
Weather Project/
├── Assets/
│   └── Cities.py              # City data with IDs
├── Json_data/                # JSON data storage
├── Learning/                 # Jupyter notebooks for learning
├── Notebooks/                # Jupyter notebooks for data processing
├── .github/
│   └── workflows/
│       └── weather_automation.yml  # GitHub Actions workflow
├── automate_weather.py       # Main automation script
├── requirements.txt          # Python dependencies
└── .env                      # Environment variables (not in git)
```

## Setup Instructions

### 1. Local Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Weather Project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file**
   Create a `.env` file in the project root with:
   ```
   OPENWEATHER_API_KEY=your_openweather_api_key
   WAQIP_API_KEY=your_waqi_api_key
   DATABASE_URL=your_postgresql_database_url
   ```

5. **Run automation manually**
   ```bash
   python automate_weather.py
   ```

### 2. GitHub Setup

1. **Create a new repository on GitHub**

2. **Add remote and push**
   ```bash
   git remote add origin <your-github-repo-url>
   git branch -M main
   git push -u origin main
   ```

3. **Add GitHub Secrets**
   Go to your GitHub repository → Settings → Secrets and variables → Actions
   
   Add the following secrets:
   - `OPENWEATHER_API_KEY`: Your OpenWeather API key
   - `WAQIP_API_KEY`: Your WAQI API key
   - `DATABASE_URL`: Your PostgreSQL database URL

4. **Enable GitHub Actions**
   - Go to Actions tab in your repository
   - Enable GitHub Actions
   - The workflow will run automatically every 6 hours
   - You can also manually trigger it from the Actions tab

## API Keys Required

### OpenWeather API
- Get your API key from: https://openweathermap.org/api
- Sign up for free and get your API key

### WAQI API
- Get your API key from: https://aqicn.org/api/
- Sign up for free and get your API token

### Database
- This project uses PostgreSQL (Supabase recommended)
- Get your database connection string from your database provider

## Data Collected

The system collects the following data for each city:

### Weather Data
- Temperature, feels like, min/max temperature
- Pressure, humidity
- Wind speed and direction
- Cloudiness, visibility
- Weather conditions and descriptions
- Sunrise/sunset times

### Air Quality Data
- AQI (Air Quality Index)
- PM2.5, PM10, O3, NO2, SO2, CO levels
- Temperature, humidity, pressure
- Wind speed, direction, gust
- Dew point

### Forecast Data
- PM2.5 forecasts (avg, max, min)

## Automation Schedule

The GitHub Actions workflow runs:
- **Every 6 hours** (00:00, 06:00, 12:00, 18:00 UTC)
- **Manual trigger** available from Actions tab

## Database Schema

The data is stored in the following tables:
- `city`: City information and coordinates
- `weather_records`: Weather measurements
- `aqi_stations`: AQI monitoring stations
- `aqi_records`: Air quality measurements
- `forecast_records`: Air quality forecasts

## Troubleshooting

### API Rate Limits
- OpenWeather API: 60 calls/minute (free tier)
- WAQI API: 1000 requests/day (free tier)
- The script handles rate limits with error handling

### Database Connection Issues
- Verify your DATABASE_URL is correct
- Ensure your database allows remote connections
- Check firewall settings

### GitHub Actions Failures
- Check that all secrets are properly set
- Review the Actions logs for specific errors
- Ensure the workflow file is in `.github/workflows/`

## License

This project is for educational purposes.

## Contributing

Feel free to submit issues and enhancement requests!
