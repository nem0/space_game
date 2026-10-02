# Classifies gfx/earth/earth.png (+ earth_emissive.png) into a splatmap gfx/earth/earth_splat.png (same size, linear):
#   R ocean   G land   B ice / cloud   A scorched (burning ground: emissive map bright)   -- channels sum to ~1
# Usage: powershell -ExecutionPolicy Bypass -File tools/gen_earth_splat.ps1
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System; using System.Drawing; using System.Drawing.Imaging;
public static class Splat {
	static float Ss(float a, float b, float x) { float t = Math.Max(0f, Math.Min(1f, (x - a) / (b - a))); return t * t * (3f - 2f * t); }
	static byte[] Read(Bitmap bmp, int w, int h) {
		Bitmap r = new Bitmap(w, h, PixelFormat.Format32bppArgb);
		using (Graphics g = Graphics.FromImage(r)) { g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic; g.DrawImage(bmp, 0, 0, w, h); }
		BitmapData d = r.LockBits(new Rectangle(0, 0, w, h), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
		byte[] px = new byte[w * h * 4]; System.Runtime.InteropServices.Marshal.Copy(d.Scan0, px, 0, px.Length); r.UnlockBits(d); r.Dispose(); return px;
	}
	public static void Run(string earth, string emissive, string outPath) {
		Bitmap e = new Bitmap(earth), m = new Bitmap(emissive);
		int w = e.Width, h = e.Height;
		byte[] c = Read(e, w, h), em = Read(m, w, h);
		float[] f = new float[w * h * 4];
		for (int i = 0; i < w * h; i++) {
			float b = c[i*4] / 255f, g = c[i*4+1] / 255f, r = c[i*4+2] / 255f;   // BGRA; classification is done on the sRGB values
			float lum = 0.3f * r + 0.59f * g + 0.11f * b;
			float mx = Math.Max(r, Math.Max(g, b)), mn = Math.Min(r, Math.Min(g, b)), sat = mx - mn;
			float fire = Ss(0.25f, 0.6f, Math.Max(em[i*4+2], Math.Max(em[i*4+1], em[i*4])) / 255f);
			float warm = r - b;   // ocean is cool (blue >= red); land, smoke and desert are warm
			float ice = Ss(0.42f, 0.58f, lum) * (1f - Ss(0.18f, 0.30f, sat));
			float ocean = (1f - ice) * (1f - Ss(-0.01f, 0.04f, warm)) * (1f - Ss(0.30f, 0.45f, lum));
			float burnt = fire * (1f - ice);
			float land = Math.Max(0f, 1f - ice - ocean - burnt);
			float s = ice + ocean + burnt + land; if (s < 1e-4f) { land = 1f; s = 1f; }
			f[i*4] = ocean / s; f[i*4+1] = land / s; f[i*4+2] = ice / s; f[i*4+3] = burnt / s;
		}
		// 2 px separable box blur so class borders are soft when the map is magnified
		for (int pass = 0; pass < 2; pass++) {
			float[] t = new float[f.Length];
			for (int y = 0; y < h; y++) for (int x = 0; x < w; x++) for (int k = 0; k < 4; k++) {
				float s = 0; for (int dx = -2; dx <= 2; dx++) s += f[(y * w + ((x + dx + w) % w)) * 4 + k]; t[(y * w + x) * 4 + k] = s / 5f; }
			for (int y = 0; y < h; y++) for (int x = 0; x < w; x++) for (int k = 0; k < 4; k++) {
				float s = 0; for (int dy = -2; dy <= 2; dy++) s += t[(Math.Max(0, Math.Min(h - 1, y + dy)) * w + x) * 4 + k]; f[(y * w + x) * 4 + k] = s / 5f; }
		}
		Bitmap o = new Bitmap(w, h, PixelFormat.Format32bppArgb);
		BitmapData d = o.LockBits(new Rectangle(0, 0, w, h), ImageLockMode.WriteOnly, PixelFormat.Format32bppArgb);
		byte[] px = new byte[w * h * 4];
		for (int i = 0; i < w * h; i++) {
			px[i*4+2] = (byte)Math.Round(255f * f[i*4]); px[i*4+1] = (byte)Math.Round(255f * f[i*4+1]); px[i*4] = (byte)Math.Round(255f * f[i*4+2]); px[i*4+3] = (byte)Math.Round(255f * f[i*4+3]);
		}
		System.Runtime.InteropServices.Marshal.Copy(px, 0, d.Scan0, px.Length); o.UnlockBits(d);
		o.Save(outPath, ImageFormat.Png);
	}
}
"@ -ReferencedAssemblies System.Drawing
$root = (Get-Location).Path
[Splat]::Run("$root\gfx\earth\earth.png", "$root\gfx\earth\earth_emissive.png", "$root\gfx\earth\earth_splat.png")
"saved gfx/earth/earth_splat.png"
