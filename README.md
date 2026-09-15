# riot-autoit

Small Windows CLI tool that keeps my League of Legends custom status updated with current local weather and manages client focus.

I leave League open in the background while working and wanted my status to show current temperature and weather conditions without touching anything. It reads the local Riot lockfile, connects to the League Client Update (LCU) chat API over HTTPS, and polls Open-Meteo every 15 minutes. It also checks the game window state through user32 so it pauses updates whenever an actual match starts.

## Installation

No external packages required, just Python 3.10+ on Windows.

Clone the repo:

    git clone https://github.com/vmarkov/riot-autoit.git
    cd riot-autoit

## Usage

Run it with your coordinates:

    python riot_autoit.py --lat 40.7128 --lon -74.0060

If you want a city label in your status:

    python riot_autoit.py --lat 40.7128 --lon -74.0060 --city NYC

Options:

- `--lat`: latitude (float, required)
- `--lon`: longitude (float, required)
- `--city`: optional prefix label for status display
- `--interval`: refresh interval in seconds (default: 900)
- `--auto-focus`: bring client window to front when queue accept dialog shows up
- `--once`: run a single status update and exit immediately

Example output:

    [14:22:05] lockfile detected at C:\Riot Games\League of Legends\lockfile
    [14:22:06] weather: 18.2C, Partly cloudy
    [14:22:06] status updated: [NYC] 18.2C Partly cloudy
    [14:37:06] game in progress (League of Legends (TM) Client), skipping update

<!-- updated: 2026-09-15 -->
