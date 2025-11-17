.PHONY: install build serve clean help

# Default target
help:
	@echo "Live SWE-Agent Leaderboard - Build Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make build      - Build static site"
	@echo "  make serve      - Build and serve site locally"
	@echo "  make clean      - Remove build artifacts"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -e .

# Build static site
build:
	@echo "Building site..."
	python3 build.py

# Build and serve locally
serve: build
	@echo ""
	@echo "Starting local server at http://localhost:8000"
	@echo "Press Ctrl+C to stop"
	@echo ""
	cd dist && python3 -m http.server 8000

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/
	rm -rf *.pyc __pycache__
	@echo "Done!"
