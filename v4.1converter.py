import json
import argparse
import os
import sys

# --- User-definable Variables ---
# Video settings
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080

# Font and Text settings
FONT_NAME = "Roboto"
FONT_SIZE = 20

# Chat Box settings
MAX_MESSAGES = 10
MAX_DURATION = 20  # in seconds

# Outline settings
OUTLINE_ENABLED = False
OUTLINE_THICKNESS = 2
# 0 = Opaque, 100 = Fully Transparent
OUTLINE_TRANSPARENCY_PERCENT = 0

# Shadow settings
SHADOW_ENABLED = True
SHADOW_DISTANCE = 2
# 0 = Opaque, 100 = Fully Transparent
SHADOW_TRANSPARENCY_PERCENT = 50

# Fade settings
FADE_IN_ENABLED = False
FADE_OUT_ENABLED = True
FADE_DURATION_MS = 200
# --- End of User-definable Variables ---

def format_time(seconds):
    """Converts seconds into H:MM:SS.ss format."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 100)
    return f"{h:01d}:{m:02d}:{s:02d}.{ms:02d}"

def format_user_color(hex_color):
    """Converts a hex color like #FF69B4 to ASS format &HBBGGRR&."""
    if not hex_color:
        return "&HFFFFFF&"  # Default to white if no color
    hex_color = hex_color.lstrip('#')
    r = hex_color[0:2]
    g = hex_color[2:4]
    b = hex_color[4:6]
    return f"&H{b}{g}{r}&"

def create_ass_file(json_path):
    """Creates an .ass subtitle file from a Twitch chat JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading {json_path}: {e}")
        return

    comments = sorted(data.get('comments', []), key=lambda x: x['content_offset_seconds'])
    if not comments:
        print(f"No comments found in {json_path}.")
        return

    # Calculate chat box dimensions and margins
    chat_box_width = VIDEO_WIDTH // 4
    chat_box_height = VIDEO_HEIGHT // 4
    margin_l = 10
    margin_v = 10
    margin_r = VIDEO_WIDTH - chat_box_width - margin_l

    # Define the clipping rectangle coordinates
    clip_x1 = margin_l
    clip_y1 = VIDEO_HEIGHT - chat_box_height - margin_v
    clip_x2 = margin_l + chat_box_width
    clip_y2 = VIDEO_HEIGHT - margin_v
    clip_command = f"{{\\clip({clip_x1}, {clip_y1}, {clip_x2}, {clip_y2})}}"

    # Calculate outline color with transparency
    outline_transparency_value = int(OUTLINE_TRANSPARENCY_PERCENT / 100 * 255)
    hex_outline_transparency = f"{outline_transparency_value:02X}"
    outline_color = f"&H{hex_outline_transparency}000000&"

    # Calculate shadow color with transparency
    shadow_transparency_value = int(SHADOW_TRANSPARENCY_PERCENT / 100 * 255)
    hex_shadow_transparency = f"{shadow_transparency_value:02X}"
    shadow_color = f"&H{hex_shadow_transparency}000000&"

    # Determine outline and shadow values based on enabled flags
    outline_value = OUTLINE_THICKNESS if OUTLINE_ENABLED else 0
    shadow_value = SHADOW_DISTANCE if SHADOW_ENABLED else 0
    
    # Construct fade command
    fade_in_time = FADE_DURATION_MS if FADE_IN_ENABLED else 0
    fade_out_time = FADE_DURATION_MS if FADE_OUT_ENABLED else 0
    fade_command = ""
    if fade_in_time > 0 or fade_out_time > 0:
        fade_command = f"{{\\fad({fade_in_time},{fade_out_time})}}"


    ass_header = f"""[Script Info]
Title: {data.get('video', {}).get('title', 'Twitch Chat')}
ScriptType: v4.00+
WrapStyle: 0
PlayResX: {VIDEO_WIDTH}
PlayResY: {VIDEO_HEIGHT}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{FONT_NAME},{FONT_SIZE},&HFFFFFF,&HFFFFFF,{outline_color},{shadow_color},0,0,0,0,100,100,0,0,1,{outline_value},{shadow_value},1,{margin_l},{margin_r},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    ass_events = []
    
    for i, comment in enumerate(comments):
        start_time_sec = comment['content_offset_seconds']
        
        end_time_sec = comments[i + 1]['content_offset_seconds'] if i + 1 < len(comments) else start_time_sec + MAX_DURATION

        if end_time_sec > start_time_sec + MAX_DURATION:
            end_time_sec = start_time_sec + MAX_DURATION

        visible_comments = []
        for c in comments[i::-1]:
            if c['content_offset_seconds'] >= start_time_sec - MAX_DURATION:
                visible_comments.insert(0, c)
            else:
                break
        
        visible_comments = visible_comments[-MAX_MESSAGES:]

        dialogue_text = []
        for c in visible_comments:
            user = c['commenter']['display_name']
            color = format_user_color(c['message']['user_color'])
            badges = c['message'].get('user_badges', [])
            
            badge_prefix = ""
            badge_map = {
                'broadcaster': '🎤',
                'moderator': '⚔️',
                'vip': '💎'
            }
            
            if any(badge['_id'] == 'broadcaster' for badge in badges):
                badge_prefix = badge_map['broadcaster'] + " "
            elif any(badge['_id'] == 'moderator' for badge in badges):
                badge_prefix = badge_map['moderator'] + " "
            elif any(badge['_id'] == 'vip' for badge in badges):
                badge_prefix = badge_map['vip'] + " "

            user_part = f"{badge_prefix}{{\\c{color}}}{{\\b1}}{user}:{{\\b0}}{{\\c&HFFFFFF&}} "
            
            message_parts = []
            for fragment in c['message']['fragments']:
                text = fragment['text']
                if fragment.get('emoticon'):
                    message_parts.append(f"{{\\i1}}{text}{{\\i0}}")
                else:
                    message_parts.append(text)
            
            message = "".join(message_parts)
            line = user_part + message
            dialogue_text.append(line)
        
        # Apply fade only to the newest message
        if dialogue_text and (fade_in_time > 0 or fade_out_time > 0):
            dialogue_text[-1] = f"{fade_command}{dialogue_text[-1]}"

        # We now use \N to stack messages, and the renderer handles wrapping
        full_dialogue = "\\N".join(dialogue_text)
        
        start_time = format_time(start_time_sec)
        end_time = format_time(end_time_sec)
        
        # Add the clip command to the start of the dialogue text
        event = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{clip_command}{full_dialogue}"
        ass_events.append(event)


    output_path = os.path.splitext(json_path)[0] + '.ass'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ass_header)
        for event in ass_events:
            f.write(event + '\n')
    
    print(f"Successfully created {output_path}")
    print("\n--- Settings Used ---")
    print(f"  Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
    print(f"  Font: {FONT_NAME}, Size: {FONT_SIZE}")
    print(f"  Max Messages: {MAX_MESSAGES}, Max Duration: {MAX_DURATION}s")
    print(f"  Outline: {'Enabled' if OUTLINE_ENABLED else 'Disabled'}, Thickness: {OUTLINE_THICKNESS if OUTLINE_ENABLED else 'N/A'}, Transparency: {OUTLINE_TRANSPARENCY_PERCENT if OUTLINE_ENABLED else 'N/A'}%")
    print(f"  Shadow: {'Enabled' if SHADOW_ENABLED else 'Disabled'}, Distance: {SHADOW_DISTANCE if SHADOW_ENABLED else 'N/A'}, Transparency: {SHADOW_TRANSPARENCY_PERCENT if SHADOW_ENABLED else 'N/A'}%")
    print(f"  Fade In: {'Enabled' if FADE_IN_ENABLED else 'Disabled'}, Fade Out: {'Enabled' if FADE_OUT_ENABLED else 'Disabled'}, Duration: {FADE_DURATION_MS}ms")
    print("---------------------\n")


def main():
    parser = argparse.ArgumentParser(description="Convert Twitch chat JSON to ASS subtitle files.")
    parser.add_argument('path', nargs='?', default='.', help="Path to a JSON file or a directory.")
    parser.add_argument('--all', action='store_true', help="Process all JSON files in the specified directory.")
    
    args = parser.parse_args()
    
    if args.all:
        directory = args.path if os.path.isdir(args.path) else '.'
        json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
        
        if not json_files:
            print("No JSON files found in the directory.")
            return

        print("The following files will be processed:")
        for f in json_files:
            print(f" - {f}")
        
        confirm = input("Do you want to proceed? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
            
        for file_name in json_files:
            json_path = os.path.join(directory, file_name)
            create_ass_file(json_path)
    else:
        if not os.path.exists(args.path):
            print(f"Error: Path '{args.path}' does not exist.")
            sys.exit(1)
            
        if os.path.isdir(args.path):
            print("Please specify a single JSON file or use the --all flag to process a directory.")
            sys.exit(1)
            
        create_ass_file(args.path)

if __name__ == '__main__':
    main()
