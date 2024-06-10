# Bake-Dubs

A simple web interface for recording narration for markdown-based textbooks, like the [Python Bakery](https://python-bakery.github.io/).

Uses `Bottle` for the web server.

## Installation

1. Clone the repository
2. Install the requirements with `pip install -r requirements.txt`
3. Run the server with `python main.py`
4. Open the web interface at `http://localhost:8080`
5. Start recording!

## Dubs

In order to record a dub, you will need to have converted your original markdown files into Dubs using the Bake-Mark tool. This will create a `dubs.json` file.