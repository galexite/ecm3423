#version 140

uniform mat4 PVM;
uniform mat3 VMiT;

uniform vec3 color;
uniform float density;
uniform vec3 gravity;

in vec3 position;
in vec3 normal;
in float layer;

out vec3 fs_normal;
out float fs_layer;

void main()
{
    fs_normal = normalize(VMiT * normal);
    fs_layer = layer;

    gl_Position = PVM * vec4(position + gravity * pow(layer, 3), 1.0);
}