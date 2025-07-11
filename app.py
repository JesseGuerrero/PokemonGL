from flask import Flask, render_template, jsonify, send_from_directory
import os
import base64
from PIL import Image
import io
from functools import lru_cache

app = Flask(__name__)

# Configuration for tileset
TILESET_ROWS = 4
TILESET_COLS = 4
BOULDER_IMAGE_PATH = 'data/TileSets/Pokemon Gen 4 Characters And A Few Objects - Vanilla Sunshine/Object boulder.png'


@app.route('/')
def hello_world():
    return render_template('render.html')


@lru_cache(maxsize=32)
def get_tileset_image():
    """
    Load and cache the main tileset image
    Returns the PIL Image object or None if not found
    """
    try:
        if not os.path.exists(BOULDER_IMAGE_PATH):
            create_placeholder_boulder(BOULDER_IMAGE_PATH)

        with Image.open(BOULDER_IMAGE_PATH) as img:
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Create a copy to avoid issues with the context manager
            return img.copy()
    except Exception as e:
        print(f"Error loading tileset image: {e}")
        return None


def slice_tile(image, row, col, total_rows=TILESET_ROWS, total_cols=TILESET_COLS):
    """
    Extract a single tile from the tileset image

    Args:
        image: PIL Image object of the full tileset
        row: Row index (1-based)
        col: Column index (1-based)
        total_rows: Total number of rows in tileset
        total_cols: Total number of columns in tileset

    Returns:
        PIL Image object of the extracted tile
    """
    if not image:
        return None

    # Convert to 0-based indexing
    row_idx = row - 1
    col_idx = col - 1

    # Calculate tile dimensions
    tile_width = image.width // total_cols
    tile_height = image.height // total_rows

    # Calculate crop coordinates
    left = col_idx * tile_width
    top = row_idx * tile_height
    right = left + tile_width
    bottom = top + tile_height

    # Extract the tile
    tile = image.crop((left, top, right, bottom))
    return tile


@app.route('/api/boulder-image/<int:row>/<int:col>')
def get_boulder_tile(row, col):
    """
    Get a specific tile from the boulder tileset

    Args:
        row: Row index (1-4)
        col: Column index (1-4)

    Returns:
        JSON response with base64 encoded tile image
    """
    # Validate input ranges
    if not (1 <= row <= TILESET_ROWS and 1 <= col <= TILESET_COLS):
        return jsonify({
            'success': False,
            'error': f'Invalid tile coordinates. Row and column must be between 1 and {TILESET_ROWS}'
        }), 400

    try:
        # Get the main tileset image
        tileset_image = get_tileset_image()
        if not tileset_image:
            return jsonify({
                'success': False,
                'error': 'Failed to load tileset image'
            }), 500

        # Extract the specific tile
        tile = slice_tile(tileset_image, row, col)
        if not tile:
            return jsonify({
                'success': False,
                'error': 'Failed to extract tile'
            }), 500

        # Optional: Resize tile for optimal WebGL performance
        max_size = 256  # Maximum tile size
        if tile.width > max_size or tile.height > max_size:
            tile.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # Convert to base64 for JSON response
        buffer = io.BytesIO()
        tile.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'image_data': f'data:image/png;base64,{image_data}',
            'width': tile.width,
            'height': tile.height,
            'row': row,
            'col': col
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/boulder-image')
def get_boulder_image():
    """
    Legacy endpoint - returns the full tileset image
    This maintains backward compatibility with existing code
    """
    try:
        tileset_image = get_tileset_image()
        if not tileset_image:
            return jsonify({
                'success': False,
                'error': 'Failed to load tileset image'
            }), 500

        # Optional: Resize image for optimal WebGL performance
        max_size = 512  # Maximum texture size
        if tileset_image.width > max_size or tileset_image.height > max_size:
            tileset_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # Convert to base64 for JSON response
        buffer = io.BytesIO()
        tileset_image.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'image_data': f'data:image/png;base64,{image_data}',
            'width': tileset_image.width,
            'height': tileset_image.height,
            'tileset_info': {
                'rows': TILESET_ROWS,
                'cols': TILESET_COLS,
                'total_tiles': TILESET_ROWS * TILESET_COLS
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/tileset-info')
def get_tileset_info():
    """
    Get information about the tileset structure
    """
    try:
        tileset_image = get_tileset_image()
        if not tileset_image:
            return jsonify({
                'success': False,
                'error': 'Failed to load tileset image'
            }), 500

        tile_width = tileset_image.width // TILESET_COLS
        tile_height = tileset_image.height // TILESET_ROWS

        return jsonify({
            'success': True,
            'tileset': {
                'rows': TILESET_ROWS,
                'cols': TILESET_COLS,
                'total_tiles': TILESET_ROWS * TILESET_COLS,
                'full_width': tileset_image.width,
                'full_height': tileset_image.height,
                'tile_width': tile_width,
                'tile_height': tile_height
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def create_placeholder_boulder(path):
    """Create a placeholder 4x4 tileset image if none exists"""
    # Create a 4x4 tileset with different colored tiles
    tile_size = 64
    img_width = tile_size * TILESET_COLS
    img_height = tile_size * TILESET_ROWS

    img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))

    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)

    # Create different colored tiles for the 4x4 grid
    colors = [
        (120, 100, 80, 255),  # Brown boulder
        (140, 120, 100, 255),  # Light brown boulder
        (100, 80, 60, 255),  # Dark brown boulder
        (160, 140, 120, 255),  # Very light brown boulder
        (80, 60, 40, 255),  # Very dark brown boulder
        (130, 110, 90, 255),  # Medium brown boulder
        (150, 130, 110, 255),  # Light medium brown boulder
        (110, 90, 70, 255),  # Dark medium brown boulder
        (170, 150, 130, 255),  # Lightest brown boulder
        (90, 70, 50, 255),  # Second darkest brown boulder
        (125, 105, 85, 255),  # Another brown variation
        (135, 115, 95, 255),  # Yet another brown variation
        (145, 125, 105, 255),  # More brown variation
        (155, 135, 115, 255),  # Even more brown variation
        (165, 145, 125, 255),  # Almost lightest brown
        (105, 85, 65, 255),  # Another dark brown
    ]

    for row in range(TILESET_ROWS):
        for col in range(TILESET_COLS):
            x = col * tile_size
            y = row * tile_size

            # Use different colors for each tile
            color_idx = row * TILESET_COLS + col
            color = colors[color_idx % len(colors)]

            # Draw a boulder-like shape for each tile
            margin = 8
            draw.ellipse([
                x + margin, y + margin,
                x + tile_size - margin, y + tile_size - margin
            ], fill=color)

            # Add some shading
            lighter_color = tuple(min(255, c + 20) for c in color[:3]) + (255,)
            draw.ellipse([
                x + margin + 4, y + margin + 4,
                x + tile_size - margin - 8, y + tile_size - margin - 8
            ], fill=lighter_color)

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


@app.route('/tilesets/<filename>')
def serve_tileset(filename):
    """Serve images from data/TileSets directory"""
    return send_from_directory('data/TileSets', filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)