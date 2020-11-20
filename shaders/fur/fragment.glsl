#version 150

uniform sampler2D noise_texture;

in GS_OUT {
    float layer;
    vec3 normal;
} fs_in;

out vec4 color;

void main()
{
    vec3 normal = normalize(fs_in.normal);
    color = texture(noise_texture, normal.xy);
    color.a *= 1 - fs_in.layer;
}