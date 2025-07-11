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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)