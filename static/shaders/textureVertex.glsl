attribute vec2 a_position;
attribute vec2 a_texCoord;
uniform vec2 u_resolution;
uniform vec2 u_translation;
uniform vec2 u_scale;
varying vec2 v_texCoord;

void main() {
    vec2 position = (a_position * u_scale) + u_translation;
    vec2 clipSpace = ((position / u_resolution) * 2.0) - 1.0;
    gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
    v_texCoord = a_texCoord;
}