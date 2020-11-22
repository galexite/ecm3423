#version 150

uniform mat4 PVM;
uniform mat4 VM;
uniform mat3 VMiT;

uniform vec3 color;
uniform float density;
uniform vec3 gravity;

in vec3 position;
in vec3 normal;
in float layer;

out VS_OUT {
    vec3 normal;
    vec3 position_in_view_space;
    float layer;
} vs_out;

void main()
{
    vs_out.normal = normalize(VMiT * normal);
    vs_out.position_in_view_space = vec3(VM * vec4(position, 1.0));
    vs_out.layer = layer;

    gl_Position = PVM * vec4(position + gravity * pow(layer, 3), 1.0);
}