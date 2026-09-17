#!/bin/bash
# Script to upload Vehicle Compliance Monitor to GitHub

echo "========================================="
echo "Upload to GitHub - Vehicle Compliance Monitor"
echo "========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed!"
    echo "Please install Git from: https://git-scm.com/downloads"
    exit 1
fi

echo "✓ Git is installed"
echo ""

# Check if already initialized
if [ -d .git ]; then
    echo "⚠ Git repository already initialized"
    echo ""
else
    echo "Initializing Git repository..."
    git init
    echo "✓ Git initialized"
    echo ""
fi

# Show what will be committed
echo "Files to be uploaded:"
echo "-------------------"
git status --short 2>/dev/null || git add . && git status --short
echo ""

# Add all files
echo "Adding files to git..."
git add .
echo "✓ Files added"
echo ""

# Create commit
echo "Creating commit..."
git commit -m "Initial commit: Vehicle Compliance Monitor

- Complete AI-powered vehicle compliance monitoring system
- YOLO-based vehicle detection
- License plate OCR
- Compliance database checking
- Traffic analytics (counts, heatmaps, time profiles)
- Google Colab notebook
- Comprehensive documentation
- Challenge submission ready"

echo "✓ Commit created"
echo ""

# Instructions for GitHub
echo "========================================="
echo "Next Steps:"
echo "========================================="
echo ""
echo "1. Go to https://github.com/new"
echo "2. Create a new repository named: vehicle-compliance-monitor"
echo "3. DON'T initialize with README"
echo "4. After creating, run these commands:"
echo ""
echo "   git remote add origin https://github.com/YOUR-USERNAME/vehicle-compliance-monitor.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "Replace YOUR-USERNAME with your GitHub username"
echo ""
echo "========================================="
echo "✓ Ready to push to GitHub!"
echo "========================================="
