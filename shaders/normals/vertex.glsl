#version 150

uniform mat4 PVM;
uniform mat4 VM;
uniform mat3 VMiT;

in vec3 position;
in vec3 normal;

out VS_OUT {
    vec3 normal;
} vs_out;

void main()
{
    vs_out.normal = normalize(VMiT * normal);
    gl_Position = PVM * vec4(position, 1.0f);
}