#version 150

uniform mat4 PVM;
uniform mat4 VM;
uniform mat3 VMiT;

uniform vec3 light;

uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float Ns;

uniform vec3 Ia;
uniform vec3 Id;
uniform vec3 Is;

uniform float density;
uniform float length;
uniform vec3 gravity;
uniform sampler2D noise_texture;

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