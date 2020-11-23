#version 140

uniform vec3 color;
uniform float density;

uniform vec3 light;
uniform sampler2D noise_texture;

in vec3 fs_normal;
in vec4 fs_color;
in float fs_layer;

out vec4 frag_color;

void main()
{
    vec4 sample = texture(noise_texture, fs_normal.xy / density);
    frag_color = vec4(mix(0.2, 1.0, fs_layer) * color,
        fs_layer == 0.0 ? 1.0 : sample.r * (1 - fs_layer));
}
