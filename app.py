from flask import Flask, render_template, jsonify, send_from_directory
import os
import base64
from PIL import Image
import io

app = Flask(__name__)

# Create static/TileSets directory if it doesn't exist
os.makedirs('data/TileSets', exist_ok=True)


@app.route('/')
def hello_world():
    return render_template('render.html')


@app.route('/api/boulder-image')
def get_boulder_image():
    """
    Process and return boulder image data
    This endpoint handles image processing on the backend
    """
    try:
        # Path to your boulder image
        boulder_path = 'data/TileSets/Pokemon Gen 4 Characters And A Few Objects - Vanilla Sunshine/Object boulder.png'

        # Check if image exists
        if not os.path.exists(boulder_path):
            # Create a placeholder boulder image if none exists
            create_placeholder_boulder(boulder_path)

        # Process the image (you can add filtering, resizing, etc. here)
        with Image.open(boulder_path) as img:
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # Optional: Resize image for optimal WebGL performance
            max_size = 512  # Maximum texture size
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            # Convert to base64 for JSON response
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return jsonify({
                'success': True,
                'image_data': f'data:image/png;base64,{image_data}',
                'width': img.width,
                'height': img.height
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def create_placeholder_boulder(path):
    """Create a placeholder boulder image if none exists"""
    # Create a simple boulder-like image
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))

    # You could use PIL to draw a simple boulder shape here
    # For now, just create a gray circle as placeholder
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 206, 206], fill=(120, 100, 80, 255))
    draw.ellipse([60, 60, 196, 196], fill=(140, 120, 100, 255))

    img.save(path)


@app.route('/tilesets/<filename>')
def serve_tileset(filename):
    """Serve images from static/TileSets directory"""
    return send_from_directory('data/TileSets', filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)