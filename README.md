# Crit Lines

**Physics-based cycling performance simulator** that answers the question: *"How much faster would I be with more power, less weight, or better equipment?"*

Upload a GPX file from Strava, input your rider stats, and get precise time predictions based on real cycling physics.

## What It Does

- **📊 Performance Simulation**: Calculate exact finish times based on your power, weight, and bike setup
- **🏔️ Course Analysis**: Import GPX files from Strava rides and analyze elevation, gradients, and distance  
- **⚖️ Weight Comparison**: See how losing 5kg affects your climbing times
- **⚡ Power Analysis**: Compare performance at different FTP levels
- **🚴‍♂️ Equipment Impact**: Quantify gains from aero wheels, better position, lighter bike
- **🌬️ Wind Effects**: Factor in headwinds, tailwinds, and temperature

## Quick Setup (5 minutes)

### Prerequisites
- Python 3.9+ (check with `python3 --version`)
- That's it! No database or API keys needed.

### Installation

1. **Clone this repository:**
   ```bash
   git clone <your-repo-url>
   cd crit-lines
   ```

2. **Set up Python environment:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Poetry (dependency manager):**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

4. **Install all dependencies:**
   ```bash
   poetry install
   ```

5. **Test it works:**
   ```bash
   ./venv/bin/python run.py sample
   ```
   
   ✅ You should see simulation results for a test course!

## How to Use

### Step 1: Get a GPX File

**From Strava:**
1. Go to any Strava activity
2. Click the "Actions" button (three dots)  
3. Select "Export GPX"
4. Save the file (e.g., `morning-ride.gpx`)

**Other sources:**
- Garmin Connect, Wahoo, RideWithGPS all export GPX
- Any GPS device can create GPX files

### Step 2: Run Your First Simulation

```bash
# Basic simulation with your stats
./venv/bin/python run.py simulate morning-ride.gpx --weight 70 --ftp 250

# With more options
./venv/bin/python run.py simulate morning-ride.gpx \
  --weight 72 \
  --ftp 280 \
  --effort 0.95 \
  --wheels aero_deep \
  --position drops \
  --temp 25 \
  --wind-speed 15 \
  --wind-direction 180
```

**Output Example:**
```
COURSE: Morning Climb
Distance: 25.3 km  
Elevation gain: 847 m
Max gradient: 12.4%

SIMULATION RESULTS
Total time: 01:23:42
Average speed: 18.2 km/h  
Average power: 266 W
Power-to-weight ratio: 3.57 W/kg
📊 Elevation profile saved: morning-ride_elevation.png
📊 Power analysis saved: morning-ride_power.png
```

**Visual Output:**
The tool automatically generates detailed charts showing:
- **Elevation Profile**: Course elevation with speed and gradient overlays
- **Power Analysis**: Breakdown by terrain type (climbing, flat, descending)  
- **Comparison Charts**: Side-by-side time and speed comparisons

### Step 3: Compare Scenarios

**Weight Impact:**
```bash
./venv/bin/python run.py compare-weight morning-ride.gpx --weight-range "65,70,75,80"
```

**Power Impact:**  
```bash  
./venv/bin/python run.py compare-power morning-ride.gpx --ftp-range "220,250,280,310"
```

**Sample Comparison Output:**
```
WEIGHT COMPARISON
Scenario            Time       Speed    Δ Time
65kg                01:21:15   18.7km/h  -147s
70kg                01:23:42   18.2km/h  +0s  
75kg                01:26:23   17.7km/h  +161s
80kg                01:29:18   17.1km/h  +336s
```

## All Commands

### `simulate`
Run a single simulation with your parameters.

```bash
poetry run crit-lines simulate <gpx-file> [OPTIONS]
```

**Options:**
- `--weight, -w`: Rider weight in kg (default: 70)
- `--ftp, -f`: FTP in watts (default: 250)  
- `--effort, -e`: Effort as fraction of FTP, 0.5-1.2 (default: 1.0)
- `--bike-weight`: Bike weight in kg (default: 8.0)
- `--position`: Riding position: `drops`, `hoods`, `tops`, `aero_bars` (default: hoods)
- `--wheels`: Wheel type: `standard`, `aero_shallow`, `aero_deep`, `disc`, `climbing` (default: standard)
- `--temp`: Temperature in Celsius (default: 20)
- `--wind-speed`: Wind speed in km/h (default: 0)
- `--wind-direction`: Wind direction 0-360 degrees (default: 0)

### `compare-weight`
Compare performance at different rider weights.

```bash
poetry run crit-lines compare-weight <gpx-file> --weight-range "65,70,75"
```

### `compare-power`  
Compare performance at different FTP levels.

```bash
poetry run crit-lines compare-power <gpx-file> --ftp-range "230,250,270"
```

### `sample`
Test the tool with a built-in sample course.

```bash
poetry run crit-lines sample
```

## Understanding the Physics

The simulator uses real cycling physics:

**Power Required = Aerodynamic Power + Rolling Resistance + Climbing Power**

- **Aerodynamic Power**: Drag increases with speed² and depends on your position, clothing, bike, and wheels
- **Rolling Resistance**: Constant force proportional to total weight (rider + bike)  
- **Climbing Power**: Power needed to lift total weight against gravity on inclines

**Key Variables:**
- **CdA (drag area)**: Lower is more aero. Drops = 0.30m², hoods = 0.35m², tops = 0.40m²
- **Rolling resistance**: Road bikes ≈ 0.004, varies by tire pressure and surface
- **Air density**: Changes with temperature and altitude

## Real-World Use Cases

### Training Planning
*"Should I focus on losing weight or gaining power for this climbing race?"*

```bash
poetry run crit-lines compare-weight race-course.gpx --weight-range "68,70,72"
poetry run crit-lines compare-power race-course.gpx --ftp-range "280,300,320"
```

### Equipment Decisions
*"Are deep section wheels worth it on this course?"*

```bash
# Compare wheel types
poetry run crit-lines simulate course.gpx --wheels standard
poetry run crit-lines simulate course.gpx --wheels aero_deep
```

### Race Strategy
*"What pace should I target for this course given my current fitness?"*

```bash
# Test different effort levels
poetry run crit-lines simulate race.gpx --effort 0.85  # Sustainable  
poetry run crit-lines simulate race.gpx --effort 1.05  # All-out
```

## Troubleshooting

**"Command not found"**
- Make sure you're in the virtual environment: `source venv/bin/activate`
- Use the full Poetry command: `poetry run crit-lines --help`

**"GPX file not found"**  
- Use full path to GPX file: `poetry run crit-lines simulate /full/path/to/file.gpx`
- Check the file exists: `ls -la *.gpx`

**"Unrealistic results"**
- Check your FTP is reasonable (most cyclists: 150-400W)
- Verify your weight is in kg, not pounds
- Ensure GPX file has elevation data

**"Poetry not found"**
- Install Poetry: `curl -sSL https://install.python-poetry.org | python3 -`
- Or use pip instead: `pip install -r requirements.txt` (you'll need to create this file)

## What's Next?

This tool currently focuses on pure performance simulation. Future versions could add:
- Strava API integration for automatic ride import
- Video analysis for racing line optimization  
- Advanced pacing strategies
- Group ride drafting effects
- Weather API integration

## Contributing

Found a bug or want to add a feature? PRs welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`  
3. Make changes and add tests
4. Ensure tests pass: `pytest`
5. Submit a pull request

## License

[Add your license here]

---

**Made for cyclists who love data and want to go faster 🚴‍♂️💨**