#version 150

uniform float density;
uniform float length;
uniform vec3 gravity;

layout(triangles) in;
layout(triangle_strip, max_vertices = 60) out;

in VS_OUT {
    vec3 normal;
} gs_in[];

out GS_OUT {
    float layer;
    vec3 normal;
} gs_out;

void main()
{
    // for (int i = 0; i < 3; i++) {
    //     gs_out.layer = 1.0f;
    //     gs_out.normal = gs_in[i].normal;
    //     gl_Position = gl_in[i].gl_Position;
    //     EmitVertex();
    // }

    for (int j = 0; j < density; j++) {
        for (int i = 0; i < 3; i++) {
            float layer = float(j + 1) / density;
            float length = length * layer;
            float k = pow(layer, 3);

            gs_out.layer = layer;
            gs_out.normal = gs_in[i].normal;

            gl_Position = gl_in[i].gl_Position + vec4(gs_in[i].normal * layer, 0.0) * length;
            gl_Position.xyz += gravity * k;

            EmitVertex();
        }

        EndPrimitive();
    }
}