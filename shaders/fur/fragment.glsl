#version 150

uniform vec3 color;
uniform float density;

uniform vec3 light;
uniform sampler2D noise_texture;

in VS_OUT {
    vec3 normal;
    vec3 position_in_view_space;
    float layer;
} fs_in;

out vec4 frag_color;

void main()
{
    vec4 sample = texture(noise_texture, fs_in.normal.xy / density);
    frag_color = vec4(mix(0.2, 1.0, fs_in.layer) * color,
        fs_in.layer == 0.0 ? 1.0 : sample.r * (1 - fs_in.layer));
}