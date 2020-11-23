#version 140

uniform mat4 PVM;
uniform mat4 VM;
uniform mat3 VMiT;

uniform vec3 color;

// Lighting parameters.
uniform vec3 light;
uniform vec3 Ia;
uniform vec3 Id;
uniform vec3 Is;
uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float Ns;

// Fur parameters.
uniform float density;
uniform vec3 gravity;

in vec3 position;
in vec3 normal;
in float layer;

out vec3 fs_normal;
out vec3 fs_color;
flat out float fs_layer;

void main()
{
    /* This shader implements Gouraud shading whilst adding gravity to extrude
     * the fur out and away from the model for each successive layer of fur. */
    fs_normal = normalize(VMiT * normal);
    vec3 position_vs = vec3(VM * vec4(position, 1.0f));
    vec3 light_direction = normalize(light - position_vs);

    // Lighting components for Gouraud shading.
    vec3 ambient = Ia * Ka;
    vec3 diffuse = Id * Kd * max(0.0f, dot(light_direction, fs_normal));
    vec3 specular = Is * Ks * pow(max(0.0, dot(
        reflect(light_direction, position_vs), normalize(position_vs)))
    , Ns);

    /* Implement the inverse square law and reduce the light intensity over
     * distance from the light source. */
    float distance_from_light = length(light - position_vs);
    float attenuation = min(1.0,
        1.0 / (pow(distance_from_light, 2) * 0.005));

    fs_color = color * (ambient + attenuation * (diffuse + specular));

    // Pass the layer information through to the fragment shader.
    fs_layer = layer;

    // Add gravity for each layer of fur.
    gl_Position = PVM * vec4(position + gravity * pow(layer, 3), 1.0);
}
