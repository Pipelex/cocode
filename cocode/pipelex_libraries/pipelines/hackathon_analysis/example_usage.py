"""Example usage of the hackathon analysis pipeline."""

import asyncio
from pathlib import Path

from pipelex import pretty_print
from pipelex.core.stuffs.stuff_content import TextContent
from pipelex.hub import get_pipeline_tracker, get_report_delegate
from pipelex.pipelex import Pipelex
from pipelex.pipeline.execute import execute_pipeline


async def analyze_hackathon_project(codebase_content: str) -> str:
    """Analyze a hackathon project and return HTML report.

    Args:
        codebase_content: Text representation of the codebase

    Returns:
        HTML report as string
    """
    # Run the pipeline
    pipe_output = await execute_pipeline(
        pipe_code="analyze_codebase_v2",
        input_memory={
            "codebase": codebase_content,
        },
    )

    # Return the HTML report
    return pipe_output.main_stuff_as_str


async def main():
    """Main example function."""

    # Example codebase content (you would replace this with actual codebase analysis)
    sample_codebase = """
# Weather App - Hackathon Project

## File Structure:
- app.py (Flask backend)
- templates/index.html (Frontend)
- static/style.css (Styling)
- weather_api.py (Weather service)
- requirements.txt (Dependencies)
- tests/test_weather.py (Unit tests)
- .github/workflows/ci.yml (CI/CD)
- README.md (Documentation)

## app.py:
```python
from flask import Flask, render_template, request, jsonify
from weather_api import WeatherService
import os

app = Flask(__name__)
weather_service = WeatherService(api_key=os.getenv('WEATHER_API_KEY'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/weather/<city>')
def get_weather(city):
    try:
        weather_data = weather_service.get_current_weather(city)
        return jsonify(weather_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/forecast/<city>')
def get_forecast(city):
    try:
        forecast_data = weather_service.get_forecast(city)
        return jsonify(forecast_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
```

## weather_api.py:
```python
import requests
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class WeatherData:
    temperature: float
    humidity: int
    description: str
    city: str

class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_current_weather(self, city: str) -> Dict:
        url = f"{self.base_url}/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        return {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description'],
            'city': data['name']
        }
    
    def get_forecast(self, city: str) -> List[Dict]:
        url = f"{self.base_url}/forecast"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        forecast = []
        
        for item in data['list'][:5]:  # Next 5 forecasts
            forecast.append({
                'datetime': item['dt_txt'],
                'temperature': item['main']['temp'],
                'description': item['weather'][0]['description']
            })
        
        return forecast
```

## tests/test_weather.py:
```python
import pytest
from unittest.mock import Mock, patch
from weather_api import WeatherService

class TestWeatherService:
    def setup_method(self):
        self.weather_service = WeatherService("test_api_key")
    
    @patch('weather_api.requests.get')
    def test_get_current_weather_success(self, mock_get):
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'main': {'temp': 25.5, 'humidity': 60},
            'weather': [{'description': 'clear sky'}],
            'name': 'London'
        }
        mock_get.return_value = mock_response
        
        result = self.weather_service.get_current_weather('London')
        
        assert result['temperature'] == 25.5
        assert result['humidity'] == 60
        assert result['description'] == 'clear sky'
        assert result['city'] == 'London'
    
    @patch('weather_api.requests.get')
    def test_get_forecast_success(self, mock_get):
        # Mock successful forecast API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'list': [
                {
                    'dt_txt': '2024-01-01 12:00:00',
                    'main': {'temp': 20.0},
                    'weather': [{'description': 'sunny'}]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = self.weather_service.get_forecast('London')
        
        assert len(result) == 1
        assert result[0]['temperature'] == 20.0
        assert result[0]['description'] == 'sunny'
```

## .github/workflows/ci.yml:
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## requirements.txt:
```
Flask==2.3.3
requests==2.31.0
python-dotenv==1.0.0
```

## README.md:
```markdown
# Weather App

A real-time weather application built for the hackathon.

## Features
- Current weather for any city
- 5-day weather forecast
- Clean, responsive UI
- Real-time data from OpenWeatherMap API
- Error handling and validation
- Unit tests with 90%+ coverage
- CI/CD pipeline

## Technology Stack
- Backend: Flask (Python)
- Frontend: HTML5, CSS3, JavaScript
- API: OpenWeatherMap
- Testing: pytest
- CI/CD: GitHub Actions

## Setup
1. Get API key from OpenWeatherMap
2. Set environment variable: `export WEATHER_API_KEY=your_key`
3. Install dependencies: `pip install -r requirements.txt`
4. Run tests: `pytest`
5. Start app: `python app.py`

## API Endpoints
- GET `/api/weather/<city>` - Current weather
- GET `/api/forecast/<city>` - 5-day forecast

## Testing
Run tests with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Security
- API keys stored as environment variables
- Input validation on all endpoints
- Error handling prevents information leakage
```
    """

    # Start Pipelex
    Pipelex.make()

    # Analyze the codebase
    print("Analyzing hackathon project...")
    html_report = await analyze_hackathon_project(sample_codebase)

    # Save the report
    output_path = Path("hackathon_analysis_report.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_report)

    print(f"Analysis complete! Report saved to: {output_path}")

    # Display cost report
    get_report_delegate().generate_report()

    # Output pipeline flowchart
    get_pipeline_tracker().output_flowchart()


if __name__ == "__main__":
    asyncio.run(main())
