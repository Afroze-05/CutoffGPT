#!/bin/bash
# CollegePath AI — Quick Start Script

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║         CollegePath AI — Setup               ║"
echo "╚══════════════════════════════════════════════╝"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.10+ is required"
    exit 1
fi

# Create venv
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Install deps
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

# Setup .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Created .env file — please add your GROQ_API_KEY!"
    echo "   Get a free key at: https://console.groq.com"
    echo ""
    read -p "Enter your Groq API key (or press Enter to skip): " GROQ_KEY
    if [ -n "$GROQ_KEY" ]; then
        sed -i "s/your_groq_api_key_here/$GROQ_KEY/" .env
        echo "✅ API key saved!"
    fi
fi

# Create data dirs
mkdir -p data/uploads data/processed data/vectorstore/chroma

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting CollegePath AI server..."
echo "   URL: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   Admin: http://localhost:8000/admin"
echo ""
echo "📌 First run: Go to Admin panel and click 'Seed Sample Data'"
echo ""

python main.py
