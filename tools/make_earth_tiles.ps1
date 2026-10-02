# Cuts concept_art/tiles.png (2x2 sheet: ocean, land / ice, burnt) into four seamless square detail textures gfx/earth/detail_*.png.
# Seamless = the tile is cross-faded with a copy of itself shifted by half a tile (the shifted copy is continuous across the original's border,
# the original is continuous across the shifted copy's border).   Usage: powershell -ExecutionPolicy Bypass -File tools/make_earth_tiles.ps1 [-Size 512]
param([int]$Size = 512)
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System; using System.Drawing; using System.Drawing.Imaging;
public static class Tiles {
	public static void Cut(string sheet, string outDir, int size) {
		Bitmap src = new Bitmap(sheet);
		int cw = src.Width / 2, ch = src.Height / 2;
		string[] names = { "ocean", "land", "ice", "burnt" };
		for (int n = 0; n < 4; n++) {
			int x0 = (n % 2) * cw + (cw - size) / 2, y0 = (n / 2) * ch + (ch - size) / 2;
			Bitmap crop = src.Clone(new Rectangle(x0, y0, size, size), PixelFormat.Format24bppRgb);
			BitmapData d = crop.LockBits(new Rectangle(0, 0, size, size), ImageLockMode.ReadOnly, PixelFormat.Format24bppRgb);
			byte[] px = new byte[d.Stride * size]; System.Runtime.InteropServices.Marshal.Copy(d.Scan0, px, 0, px.Length); int stride = d.Stride; crop.UnlockBits(d);
			Bitmap o = new Bitmap(size, size, PixelFormat.Format24bppRgb);
			BitmapData od = o.LockBits(new Rectangle(0, 0, size, size), ImageLockMode.WriteOnly, PixelFormat.Format24bppRgb);
			byte[] op = new byte[od.Stride * size];
			for (int y = 0; y < size; y++) for (int x = 0; x < size; x++) {
				double mx = Math.Sin(Math.PI * (x + 0.5) / size), my = Math.Sin(Math.PI * (y + 0.5) / size);
				double m = Math.Pow(mx * my, 4.0);            // 0 on the border, flat 1 in the centre (hides the shifted copy's own seam)
				int sx = (x + size / 2) % size, sy = (y + size / 2) % size;
				for (int k = 0; k < 3; k++) {
					double a = px[y * stride + x * 3 + k], b = px[sy * stride + sx * 3 + k];
					op[y * od.Stride + x * 3 + k] = (byte)Math.Round(a * m + b * (1.0 - m));
				}
			}
			// high-pass: subtract a wrapped blur so only fine variation is left (no lighting gradient, no big blobs, no visible seams), keep the mean colour
			double[] mean = new double[3]; for (int i = 0; i < size * size; i++) for (int k = 0; k < 3; k++) mean[k] += op[(i / size) * od.Stride + (i % size) * 3 + k] / (double)(size * size);
			int R = size / 16;
			double[] tmp = new double[size * size * 3], blur = new double[size * size * 3];
			for (int pass = 0; pass < 2; pass++) {
				for (int y = 0; y < size; y++) for (int x = 0; x < size; x++) for (int k = 0; k < 3; k++) {
					double s = 0; for (int dx = -R; dx <= R; dx++) s += (pass == 0 ? op[y * od.Stride + ((x + dx + size) % size) * 3 + k] : blur[(y * size + ((x + dx + size) % size)) * 3 + k]);
					tmp[(y * size + x) * 3 + k] = s / (2 * R + 1); }
				for (int y = 0; y < size; y++) for (int x = 0; x < size; x++) for (int k = 0; k < 3; k++) {
					double s = 0; for (int dy = -R; dy <= R; dy++) s += tmp[(((y + dy + size) % size) * size + x) * 3 + k];
					blur[(y * size + x) * 3 + k] = s / (2 * R + 1); }
			}
			for (int y = 0; y < size; y++) for (int x = 0; x < size; x++) for (int k = 0; k < 3; k++) {
				double v = op[y * od.Stride + x * 3 + k] - blur[(y * size + x) * 3 + k] + mean[k];
				op[y * od.Stride + x * 3 + k] = (byte)Math.Max(0, Math.Min(255, Math.Round(v))); }
			System.Runtime.InteropServices.Marshal.Copy(op, 0, od.Scan0, op.Length); o.UnlockBits(od);
			o.Save(System.IO.Path.Combine(outDir, "detail_" + names[n] + ".png"), ImageFormat.Png);
		}
	}
}
"@ -ReferencedAssemblies System.Drawing
$root = (Get-Location).Path
[Tiles]::Cut("$root\concept_art\tiles.png", "$root\gfx\earth", $Size)
"saved gfx/earth/detail_{ocean,land,ice,burnt}.png ($Size x $Size)"
