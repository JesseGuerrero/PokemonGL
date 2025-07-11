precision mediump float;
uniform sampler2D u_image;
uniform vec2 u_tileSize;
uniform vec2 u_tileIndex;
uniform vec2 u_imageSize;
varying vec2 v_texCoord;

void main() {
    // Calculate the UV coordinates for the specific tile
    vec2 tileUV = (u_tileIndex * u_tileSize) / u_imageSize;
    vec2 tileSizeUV = u_tileSize / u_imageSize;

    // Map the texture coordinate to the specific tile
    vec2 finalUV = tileUV + (v_texCoord * tileSizeUV);

    gl_FragColor = texture2D(u_image, finalUV);
}