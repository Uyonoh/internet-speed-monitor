# Internet Speed Monitor

A Python tool to periodically test internet speed and collect data for analysis.

## Features

- **Periodic Testing**: Run speed tests automatically every 30 minutes (configurable)
- **Retry Logic**: Automatically retry failed tests (up to 3 times by default)
- **Data Storage**: Save results to CSV file with timestamps and metadata
- **CLI Interface**: View statistics and manage tests from command line
- **Export Data**: Export collected data to CSV or JSON format

## Installation

### Linux/Windows/Mac

1. Clone or download the project
```bash
git clone https://github.com/uyonoh/internet-speed-monitor.git
````

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run
```bash
python main.py run
# python main.py --help to view help
```

### Android

1. Install Termux from it's github page or the F-droid android application
2. Update termux
```bash
pkg update
```
3. Install git and clone the repo
```bash
pkg install git
git clone https://github.com/uyonoh/internet-speed-monitor.git
cd internet-speed-monitor
```
4. Run the install script.
```bash
chmod a+x termux_installer.sh
./termux_installer.sh
```
5. Run
```bash
python main.py run
# python main.py --help to view help
```
