#version 140

uniform vec3 color;
uniform float density;

uniform vec3 light;
uniform sampler2D noise_texture;

in vec3 fs_normal;
in vec3 fs_color;
in float fs_layer;

out vec4 frag_color;

void main()
{
    // Sample the fur texture. Only the red component will be meaningful, and this will be used as the fur's alpha.
    vec4 sample = texture(noise_texture, fs_normal.xy / density);

    // Draw the fur based
    frag_color = vec4(smoothstep(0.2, 1.0, fs_layer) * fs_color,
        fs_layer == 0.0 ? 1.0 : sample.r * (1 - fs_layer));
}
