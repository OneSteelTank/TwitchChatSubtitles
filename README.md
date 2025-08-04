# Twitch Chat to ASS Subtitle Converter

This Python script converts Twitch chat logs in JSON format into Advanced SubStation Alpha (.ass) subtitle files. This allows you to overlay a customizable chat box onto your video content. Written with Gemini 2.5 Pro.

## Features

* **Twitch Chat Overlay:** Renders chat messages as subtitles on top of your video.
* **Customizable Appearance:** Easily configure settings at the top of the script:
    * Video resolution (width and height)
    * Font face and size
    * Chat box size and position
    * Maximum number of messages to display
    * Text outline with adjustable thickness and transparency
    * Text shadow with adjustable distance and transparency
    * Fade in/out animations for new messages
* **User-Specific Colors:** Displays usernames in their assigned Twitch colors.
* **Badges:** Shows icons for Broadcaster, Moderator, and VIP users.
* **Batch Processing:** Convert a single JSON file or all JSON files in a directory at once.
<img width="399" height="207" alt="image" src="https://github.com/user-attachments/assets/3b3b1670-cd50-43da-b6dc-ff593d9de3c3" />

## Requirements

* The script is written in Python 3 and does not require any external libraries.
* Your chat log `.json` files must be downloaded using [TwitchDownloader](https://github.com/lay295/TwitchDownloader).

## Installation

1.  Clone this repository or download the `converter.py` script.
2.  No further installation is needed.

## Usage

You can run the script from your terminal.

### Converting a Single File

To convert a single JSON file, provide the path to the file:

```bash
python converter.py /path/to/your/chatlog.json
```

### Converting All Files in a Directory

To convert all `.json` files in the current directory, use the `--all` flag:

```bash
python converter.py --all
```

To process all `.json` files in a specific directory, provide the path to the directory along with the `--all` flag:

```bash
python converter.py /path/to/your/logs --all
```

The script will create an `.ass` file with the same name as the input JSON file in the same directory.

## Customization

To change the appearance of the chat overlay (e.g., fonts, colors, sizes, etc.), you can modify the user-definable variables at the top of the `converter.py` script.

```python
# --- User-definable Variables ---
# Video settings
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Font and Text settings
FONT_NAME = "Roobert"
FONT_SIZE = 20

# Chat Box settings
MAX_MESSAGES = 10
MAX_DURATION = 10  # in seconds

# ... and more
```
