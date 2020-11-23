#version 140

uniform mat4 PVM;
uniform mat4 VM;
uniform mat3 VMiT;

uniform vec3 color;

uniform vec3 light;
uniform vec3 Ia;
uniform vec3 Id;
uniform vec3 Is;
uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float Ns;

uniform float density;
uniform vec3 gravity;

in vec3 position;
in vec3 normal;
in float layer;

out vec3 fs_normal;
out vec4 fs_color;
out float fs_layer;

void main()
{
    fs_normal = normalize(VMiT * normal);
    vec3 position_vs = vec3(VM * vec4(position, 1.0f));
    vec3 light_direction = normalize(light - position_vs);

    vec3 ambient = Ia * Ka;
    vec3 diffuse = Id * Kd * max(0.0f, dot(light_direction, fs_normal));
    vec3 specular = Is * Ks * pow(max(0.0, dot(
        reflect(light_direction, position_vs), normalize(position_vs)))
    , Ns);

    float distance_from_light = length(light - position_vs);
    float attenuation = min(1.0,
        1.0 / (pow(distance_from_light, 2) * 0.005) + 1.0 / (distance_from_light * 0.05));

    fs_color = vec4(color * (ambient + attenuation * (diffuse + specular)), 1.0f);

    fs_layer = layer;

    gl_Position = PVM * vec4(position + gravity * pow(layer, 3), 1.0);
}
