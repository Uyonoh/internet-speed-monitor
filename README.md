# Internet Speed Monitor

A Python tool to periodically test internet speed and collect data for analysis.

## Features

- **Periodic Testing**: Run speed tests automatically every 30 minutes (configurable)
- **Retry Logic**: Automatically retry failed tests (up to 3 times by default)
- **Data Storage**: Save results to CSV file with timestamps and metadata
- **CLI Interface**: View statistics and manage tests from command line
- **Export Data**: Export collected data to CSV or JSON format

## Installation

1. Clone or download the project
2. Install dependencies:
```bash
pip install -r requirements.txt