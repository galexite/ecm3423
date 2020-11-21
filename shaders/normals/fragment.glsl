#version 150

in VS_OUT {
    vec3 normal;
} fs_in;

out vec4 color;

void main()
{
    vec3 normal = normalize(fs_in.normal);
    color = vec4(0.0,0.0,0.0, 1.0);
}