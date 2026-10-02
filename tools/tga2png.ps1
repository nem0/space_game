# TGA -> PNG without Blender (uncompressed 24/32 bpp TGA, as written by Studio screenshots): powershell -File tools/tga2png.ps1 in.tga out.png
param([string]$In, [string]$Out)
Add-Type -AssemblyName System.Drawing
$b = [IO.File]::ReadAllBytes((Resolve-Path $In))
$w = $b[12] + 256 * $b[13]; $h = $b[14] + 256 * $b[15]; $n = $b[16] / 8; $o = 18 + $b[0]; $top = ($b[17] -band 0x20) -ne 0
$px = New-Object byte[] ($w * $h * 4)
for ($y = 0; $y -lt $h; $y++) { $sy = if ($top) { $y } else { $h - 1 - $y }; for ($x = 0; $x -lt $w; $x++) { $s = $o + ($sy * $w + $x) * $n; $t = ($y * $w + $x) * 4; $px[$t] = $b[$s]; $px[$t+1] = $b[$s+1]; $px[$t+2] = $b[$s+2]; $px[$t+3] = 255 } }
$bmp = New-Object Drawing.Bitmap $w, $h, ([Drawing.Imaging.PixelFormat]::Format32bppArgb)
$d = $bmp.LockBits((New-Object Drawing.Rectangle 0, 0, $w, $h), 'WriteOnly', 'Format32bppArgb')
[Runtime.InteropServices.Marshal]::Copy($px, 0, $d.Scan0, $px.Length); $bmp.UnlockBits($d)
$bmp.Save((Join-Path (Get-Location) $Out)); "saved $Out (${w}x${h})"
