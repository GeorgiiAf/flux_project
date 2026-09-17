# Vehicle Compliance Monitor

**AI-Powered Vehicle Compliance Checking System**

An automated system that processes dashcam footage to detect vehicles, read license plates, check them against compliance databases, and generate comprehensive traffic analytics.

## 🎯 Features

- **Vehicle Detection** - YOLOv8-based detection of cars, trucks, buses, motorcycles
- **License Plate Recognition** - OCR-powered plate reading with high accuracy
- **Compliance Checking** - Automatic matching against watchlist databases
- **Violation Reporting** - Detailed reports in CSV, JSON, and text formats
- **Traffic Analytics** - Object counts, time profiles, spatial heatmaps
- **Video Comparison** - Morning vs daytime traffic analysis
- **Annotated Videos** - Visual output with bounding boxes

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Option 1: Docker Setup (Recommended)](#option-1-docker-setup-recommended)
  - [Option 2: Conda Environment](#option-2-conda-environment)
  - [Option 3: Manual pip Installation](#option-3-manual-pip-installation)
- [Google Colab Quick Start](#google-colab-quick-start)
- [Usage](#usage)
- [Watchlist Database Format](#watchlist-database-format)
- [Output Files](#output-files)
- [Troubleshooting](#troubleshooting)
- [Privacy and Ethics](#privacy-and-ethics)

---

## Prerequisites

Before you begin, ensure you have one of the following:

### For Docker Setup:

- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)
  - Windows: Docker Desktop for Windows
  - macOS: Docker Desktop for Mac
  - Linux: Docker Engine

### For Conda Setup:

- **Conda or Miniconda** - [Download here](https://docs.conda.io/en/latest/miniconda.html)
  - Windows: Miniconda3 Windows 64-bit
  - macOS: Miniconda3 macOS 64-bit
  - Linux: Miniconda3 Linux 64-bit

### For Manual Setup:

- **Python 3.10 or higher** - [Download here](https://www.python.org/downloads/)
- **pip** (usually comes with Python)
- **Git** (optional) - [Download here](https://git-scm.com/downloads)

### Hardware Recommendations:

- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 5GB free space
- **GPU**: Optional but recommended (NVIDIA with CUDA support)

---

## Installation

Choose ONE of the following installation methods:

### Option 1: Docker Setup (Recommended)

**Best for**: Beginners, consistent environment across all platforms

#### Step 1: Install Docker Desktop

**Windows:**

1. Download Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Run the installer
3. Restart your computer when prompted
4. Open Docker Desktop and wait for it to start

**macOS:**

1. Download Docker Desktop for Mac
2. Drag Docker.app to Applications folder
3. Open Docker from Applications
4. Follow the setup wizard

**Linux:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

#### Step 2: Clone or Download Project

```bash
# Option A: Clone with Git
git clone https://github.com/your-username/vehicle-compliance-monitor.git
cd vehicle-compliance-monitor

# Option B: Download ZIP
# Download from GitHub and extract
cd vehicle-compliance-monitor
```

#### Step 3: Build Docker Image

```bash
docker build -t vehicle-compliance-monitor .
```

This will take 5-10 minutes as it downloads all dependencies.

#### Step 4: Run the Container

```bash
# Windows (PowerShell)
docker run -v ${PWD}/data/videos:/data/videos -v ${PWD}/outputs:/data/outputs vehicle-compliance-monitor

# macOS/Linux
docker run -v $(pwd)/data/videos:/data/videos -v $(pwd)/outputs:/data/outputs vehicle-compliance-monitor
```

#### Step 5: Verify Installation

Check that outputs were created in the `outputs/` directory.

---

### Option 2: Conda Environment

**Best for**: Python developers, easy environment management

#### Step 1: Install Conda

**Windows:**

1. Download Miniconda from https://docs.conda.io/en/latest/miniconda.html
2. Run the installer (Miniconda3-latest-Windows-x86_64.exe)
3. Check "Add Miniconda3 to PATH" during installation
4. Open a new Command Prompt or PowerShell

**macOS:**

```bash
# Download and install
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh
bash Miniconda3-latest-MacOSX-x86_64.sh
# Follow the prompts, accept the license, and initialize conda
```

**Linux:**

```bash
# Download and install
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
# Follow the prompts, accept the license, and initialize conda
```

#### Step 2: Clone or Download Project

```bash
git clone https://github.com/your-username/vehicle-compliance-monitor.git
cd vehicle-compliance-monitor
```

#### Step 3: Create Conda Environment

```bash
conda env create -f environment.yml
```

This will create an environment named `vehicle-compliance-monitor` with all dependencies.

#### Step 4: Activate Environment

```bash
conda activate vehicle-compliance-monitor
```

You should see `(vehicle-compliance-monitor)` in your terminal prompt.

#### Step 5: Download YOLO Models

The models will download automatically on first run, but you can pre-download:

```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

#### Step 6: Verify Installation

```bash
python src/main.py --help
```

You should see the help message with all available options.

---

### Option 3: Manual pip Installation

**Best for**: Advanced users, custom setups

#### Step 1: Install Python 3.10+

**Windows:**

1. Download from https://www.python.org/downloads/
2. Run installer
3. **Important**: Check "Add Python to PATH"
4. Click "Install Now"

**macOS:**

```bash
# Using Homebrew
brew install python@3.10
```

**Linux:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.10 python3.10-venv python3-pip

# Fedora
sudo dnf install python3.10
```

#### Step 2: Clone or Download Project

```bash
git clone https://github.com/your-username/vehicle-compliance-monitor.git
cd vehicle-compliance-monitor
```

#### Step 3: Create Virtual Environment

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 4: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will take 5-10 minutes depending on your internet speed.

#### Step 5: Download YOLO Models

```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

#### Step 6: Verify Installation

```bash
python src/main.py --help
```

---

## Google Colab Quick Start

**Best for**: No installation, cloud-based processing, free GPU

1. **Open the Notebook**:

   - Upload `notebooks/vehicle_compliance_monitor.ipynb` to Google Drive
   - Right-click → Open with → Google Colaboratory
   - Or visit: [Your Colab Link Here]

2. **Enable GPU** (Recommended):

   - Runtime → Change runtime type → GPU → Save

3. **Run All Cells**:

   - Runtime → Run all
   - Or press Shift+Enter on each cell

4. **Upload Your Videos**:

   - When prompted, upload your MP4/AVI files
   - The notebook will process them automatically

5. **Download Results**:
   - Results will be packaged as a ZIP file
   - Download automatically at the end

---

## Usage

### Basic Usage

Process a single video:

```bash
python src/main.py --video data/videos/Clip1_morning.mp4
```

Process multiple videos:

```bash
python src/main.py --video data/videos/Clip1_morning.mp4 data/videos/Clip2_day.mp4
```

### Advanced Options

Custom output directory:

```bash
python src/main.py --video data/videos/Clip1_morning.mp4 --output results
```

Custom watchlist database:

```bash
python src/main.py --video data/videos/Clip1_morning.mp4 --database data/custom_watchlist.csv
```

Adjust confidence thresholds:

```bash
python src/main.py --video data/videos/Clip1_morning.mp4 \
  --vehicle-conf 0.6 \
  --plate-conf 0.7 \
  --ocr-conf 0.8
```

Faster processing (disable analytics):

```bash
python src/main.py --video data/videos/Clip1_morning.mp4 --no-analytics
```

Verbose logging:

```bash
python src/main.py --video data/videos/Clip1_morning.mp4 --verbose
```

### All Available Options

```
--video           Path(s) to video file(s) [REQUIRED]
--output          Output directory (default: outputs)
--database        Watchlist CSV path (default: data/watchlist.csv)
--fps             Frame extraction rate (default: 5)
--vehicle-conf    Vehicle detection threshold (default: 0.5)
--plate-conf      Plate detection threshold (default: 0.6)
--ocr-conf        OCR threshold (default: 0.7)
--no-analytics    Disable analytics generation
--verbose, -v     Enable debug logging
```

---

## Watchlist Database Format

The system uses a CSV file to store the compliance watchlist.

### Required Format

```csv
plate_number,category,details,date_added
ABC123,expired_inspection,Technical inspection expired on 2023-08-15,2024-01-10
XYZ789,stolen,Reported stolen from Tallinn on 2023-12-20,2023-12-21
DEF456,blacklisted,Multiple unpaid parking fines totaling €450,2024-02-15
```

### Columns

- **plate_number**: License plate (will be normalized to uppercase, no spaces)
- **category**: Violation type (expired_inspection, stolen, blacklisted, wanted)
- **details**: Description of the violation
- **date_added**: Date when entry was added (YYYY-MM-DD format)

### Creating Your Own Watchlist

1. Copy `data/watchlist.csv` as a template
2. Edit in Excel, Google Sheets, or any text editor
3. Save as CSV format
4. Use with `--database your_watchlist.csv`

---

## Output Files

After processing, the system generates multiple output files:

### Violation Reports

- **violations\_[video].csv** - Spreadsheet format with all violations
- **violations\_[video].json** - Machine-readable JSON format
- **summary\_[video].txt** - Human-readable text summary

### Analytics (if enabled)

- **counts\_[video].png** - Bar chart of object counts by class
- **time*profile*[video].png** - Line plot of traffic over time
- **time*profile*[video].csv** - Time-series data
- **heatmap\_[video].png** - Spatial density heatmap

### Comparative Analysis (multiple videos)

- **video_comparison.csv** - Side-by-side statistics
- **video_comparison.png** - Comparison bar chart

### Annotated Videos (if violations found)

- **annotated\_[video].mp4** - Video with bounding boxes and labels

### Example Output Structure

```
outputs/
├── violations_Clip1_morning.csv
├── violations_Clip1_morning.json
├── summary_Clip1_morning.txt
├── counts_Clip1_morning.png
├── time_profile_Clip1_morning.png
├── time_profile_Clip1_morning.csv
├── heatmap_Clip1_morning.png
├── annotated_Clip1_morning.mp4
├── video_comparison.csv
└── video_comparison.png
```

---

## Troubleshooting

### CUDA/GPU Not Detected

**Problem**: System runs on CPU instead of GPU

**Solution**:

- Ensure you have an NVIDIA GPU
- Install CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
- Install PyTorch with CUDA support:
  ```bash
  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
  ```

### Model Download Failures

**Problem**: YOLO models fail to download

**Solution**:

- Check internet connection
- Manually download from: https://github.com/ultralytics/assets/releases
- Place `yolov8n.pt` in project root or `models/` directory

### Video Codec Issues

**Problem**: "Failed to open video file" error

**Solution**:

- Install additional codecs:
  ```bash
  # Windows: Install K-Lite Codec Pack
  # macOS: brew install ffmpeg
  # Linux: sudo apt-get install ffmpeg
  ```
- Convert video to MP4 H.264 format

### Permission Errors

**Problem**: Cannot write to output directory

**Solution**:

- Run with administrator/sudo privileges
- Or change output directory to a writable location:
  ```bash
  python src/main.py --video video.mp4 --output ~/Documents/results
  ```

### Out of Memory Errors

**Problem**: System crashes with memory error

**Solution**:

- Reduce frame extraction rate: `--fps 2`
- Disable analytics: `--no-analytics`
- Process videos one at a time
- Close other applications

### Import Errors

**Problem**: "ModuleNotFoundError" when running

**Solution**:

- Ensure virtual environment is activated
- Reinstall dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Check Python version: `python --version` (must be 3.10+)

---

## Privacy and Ethics

### Privacy Considerations

- **Data Minimization**: Only plate numbers are stored, no personal information
- **Secure Storage**: Keep watchlist databases encrypted and access-controlled
- **Audit Logging**: All compliance checks are logged for accountability
- **Anonymization**: Option to blur faces and compliant plates (Task 14)

### Ethical Use

- **Legitimate Purpose**: Use only for authorized law enforcement or traffic management
- **Transparency**: Inform the public about automated monitoring systems
- **Accuracy**: Regularly validate system accuracy to minimize false positives
- **Human Oversight**: Always have human review before taking enforcement action

### False Positive Mitigation

- Confidence thresholds filter low-quality detections
- Multiple validation stages (detection → OCR → database)
- Manual review recommended before enforcement
- Logging allows audit trail for disputes

### Compliance

- Ensure compliance with local data protection laws (GDPR, etc.)
- Obtain necessary permissions for video surveillance
- Implement data retention policies
- Provide mechanisms for data subject rights

---

## Project Structure

```
vehicle-compliance-monitor/
├── src/                          # Source code
│   ├── models.py                 # Data models
│   ├── video_processor.py        # Frame extraction
│   ├── vehicle_detector.py       # YOLO detection
│   ├── plate_detector.py         # Plate localization
│   ├── ocr_engine.py            # Text recognition
│   ├── compliance_checker.py     # Database queries
│   ├── report_generator.py       # Report creation
│   ├── analytics_engine.py       # Traffic analytics
│   ├── pipeline.py               # Main orchestrator
│   └── main.py                   # CLI entry point
├── data/                         # Data files
│   ├── videos/                   # Input videos
│   └── watchlist.csv             # Compliance database
├── outputs/                      # Generated outputs
├── notebooks/                    # Jupyter notebooks
│   └── vehicle_compliance_monitor.ipynb
├── tests/                        # Test suite
├── models/                       # Downloaded AI models
├── requirements.txt              # Python dependencies
├── environment.yml               # Conda environment
├── Dockerfile                    # Docker configuration
└── README.md                     # This file
```

---

## Technical Details

### AI Models Used

- **YOLOv8n** - Vehicle detection (Ultralytics)
- **EasyOCR** - License plate text recognition
- **Heuristic Plate Detector** - Plate localization (MVP)

### Performance

- **Frame Processing**: ~5 FPS on CPU, ~20 FPS on GPU
- **Video Processing**: ~2-5 minutes per minute of video (CPU)
- **Memory Usage**: ~2-4 GB RAM

### Supported Formats

- **Video**: MP4, AVI, MOV
- **Output**: CSV, JSON, TXT, PNG, MP4

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## License

This project is for educational purposes as part of the AI Traffic Insights Challenge.

---

## Acknowledgments

- **Challenge**: AI Traffic Insights Challenge - Tallinn City Videos
- **Models**: Ultralytics YOLOv8, EasyOCR
- **Team**: [Your Team Name]

---

## Support

For issues or questions:

- Check the [Troubleshooting](#troubleshooting) section
- Review the [Google Colab notebook](notebooks/vehicle_compliance_monitor.ipynb)
- Contact: [Your Email]

---

**Vehicle Compliance Monitor** - Transforming dashcam footage into actionable intelligence for safer cities.
