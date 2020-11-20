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

in GS_OUT {
    float layer;
    vec3 normal;
} fs_in;

out vec4 color;

void main()
{
    vec3 normal = normalize(fs_in.normal);
    color = vec4(normal, fs_in.layer);
}