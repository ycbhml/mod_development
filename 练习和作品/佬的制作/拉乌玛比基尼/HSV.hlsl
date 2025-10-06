Texture2D<float4> DecalResultTex : register(t40);
SamplerState s0_s : register(s0);
Texture1D<float4> IniParams : register(t120);
#define INPUT_VALUE IniParams[24].xyzw
// INPUT_VALUE.x = H (0..1 -> полный круг)
// INPUT_VALUE.y = S (-1..+1, 0 = без изменений)
// INPUT_VALUE.z = V (-1..+1, 0 = без изменений)
// INPUT_VALUE.w = не используется

struct vs2ps {
    float4 pos : SV_Position;
    float2 uv  : TEXCOORD0;
};

#ifdef VERTEX_SHADER
void main(out vs2ps output, uint vertex_id : SV_VertexID) {
    output.uv = float2((vertex_id << 1) & 2, vertex_id & 2);
    output.pos = float4(output.uv * float2(2.0, -2.0) + float2(-1.0, 1.0), 0.0, 1.0);
}
#endif

float3 rgb2hsv(float3 c)
{
    float r = c.r, g = c.g, b = c.b;
    float maxc = max(r, max(g, b));
    float minc = min(r, min(g, b));
    float d = maxc - minc;

    float h = 0.0;
    if (d > 1e-6)
    {
        if (maxc == r)       h = fmod(((g - b) / d), 6.0);
        else if (maxc == g)  h = ((b - r) / d) + 2.0;
        else                 h = ((r - g) / d) + 4.0;

        h = h / 6.0;
        if (h < 0.0) h += 1.0;
    }

    float s = (maxc <= 0.0) ? 0.0 : d / maxc;
    float v = maxc;
    return float3(h, s, v);
}

float3 hsv2rgb(float3 hsv)
{
    float h = hsv.x * 6.0;
    float s = hsv.y;
    float v = hsv.z;

    float i_f = floor(h);
    int i = (int)i_f; 
    float f = h - i_f;
    float p = v * (1.0 - s);
    float q = v * (1.0 - s * f);
    float t = v * (1.0 - s * (1.0 - f));

    i = i % 6;
    if (i == 0) return float3(v, t, p);
    if (i == 1) return float3(q, v, p);
    if (i == 2) return float3(p, v, t);
    if (i == 3) return float3(p, q, v);
    if (i == 4) return float3(t, p, v);
    return float3(v, p, q);
}

#ifdef PIXEL_SHADER
void main(vs2ps input, out float4 result : SV_Target0)
{
    float4 texColor = DecalResultTex.Sample(s0_s, input.uv);
    float originalAlpha = texColor.a;

    float3 hsv = rgb2hsv(texColor.rgb);

    // H: добавляем значение в диапазоне [0..1] (это уже 0..360°)
    hsv.x = hsv.x + INPUT_VALUE.x;
    hsv.x = hsv.x - floor(hsv.x); // wrap в [0..1)

    // S: значение в [-1..+1], где 0 = без изменений
    if (INPUT_VALUE.y < 0.0)
        hsv.y = hsv.y * (1.0 + INPUT_VALUE.y); // -1 -> 0
    else
        hsv.y = saturate(hsv.y + INPUT_VALUE.y);

    // V: значение в [-1..+1], где 0 = без изменений
    if (INPUT_VALUE.z < 0.0)
        hsv.z = hsv.z * (1.0 + INPUT_VALUE.z); // -1 -> 0
    else
        hsv.z = saturate(hsv.z + INPUT_VALUE.z);

    hsv.y = saturate(hsv.y);
    hsv.z = saturate(hsv.z);

    float3 finalRGB = hsv2rgb(hsv);
    finalRGB = saturate(finalRGB);

    result = float4(finalRGB, originalAlpha);
}
#endif
