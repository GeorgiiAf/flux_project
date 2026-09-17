# Quick Start Guide

## ✅ Setup Complete!

Your Vehicle Compliance Monitor is now installed and ready to use.

## 🚀 Running the System

### Option 1: Use the Batch Script (Easiest)

**Double-click** `run_system.bat` in Windows Explorer

This will automatically process both your videos and generate all outputs.

### Option 2: Command Line

Open Command Prompt or Git Bash in this directory and run:

```bash
# Process both videos
python src/main.py --video data/videos/Clip1_morning.mp4 data/videos/Clip2_day.mp4

# Or process one video
python src/main.py --video data/videos/Clip1_morning.mp4
```

### Option 3: Test First

To verify everything is working:

```bash
# Double-click test_setup.bat
# Or run:
python test_imports.py
python src/main.py --help
```

## 📊 What Gets Generated

After processing, check the `outputs/` folder for:

- **violations_Clip1_morning.csv** - Violation reports
- **violations_Clip2_day.csv** - Violation reports
- **summary\_\*.txt** - Human-readable summaries
- **counts\_\*.png** - Object count bar charts
- **time*profile*\*.png** - Traffic over time plots
- **heatmap\_\*.png** - Spatial density maps
- **video_comparison.csv** - Morning vs daytime comparison
- **video_comparison.png** - Comparison visualization
- **annotated\_\*.mp4** - Videos with bounding boxes (if violations found)

## ⚙️ Custom Options

```bash
# Adjust confidence thresholds
python src/main.py --video data/videos/Clip1_morning.mp4 --vehicle-conf 0.6 --ocr-conf 0.8

# Change output directory
python src/main.py --video data/videos/Clip1_morning.mp4 --output results

# Faster processing (no analytics)
python src/main.py --video data/videos/Clip1_morning.mp4 --no-analytics

# Verbose logging
python src/main.py --video data/videos/Clip1_morning.mp4 --verbose
```

## 🎯 Expected Processing Time

- **With GPU**: ~5-10 minutes per video
- **Without GPU (CPU only)**: ~15-30 minutes per video

## 📝 Next Steps

1. **Run the system** on your videos
2. **Review the outputs** in the `outputs/` folder
3. **Use the visualizations** for your presentation
4. **Check the summary reports** for statistics

## 🆘 Troubleshooting

### If you get "Module not found" errors:

```bash
python -m pip install -r requirements.txt
```

### If processing is very slow:

- Use `--fps 2` to process fewer frames
- Use `--no-analytics` to skip visualizations
- Close other applications to free up RAM

### If videos don't process:

- Ensure videos are in `data/videos/` folder
- Check video format (MP4, AVI, MOV supported)
- Try converting to MP4 H.264 format

## 📖 Full Documentation

See `README.md` for complete documentation including:

- Detailed installation instructions
- All command-line options
- Watchlist database format
- Privacy and ethics considerations

---

**Ready to go!** Run `run_system.bat` or use the command line to process your videos! 🚀
