# Captures the whole Lumix Studio window (game view + in-game HUD included) to a PNG.
# Usage:  powershell -File tools/studio_shot.ps1 [-Out screenshots/studio.png] [-Foreground]
#   -Foreground  raise the window first and copy from the screen (use when PrintWindow returns a black image)
param([string]$Out = "screenshots/studio.png", [switch]$Foreground)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class W {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
}
"@
[void][W]::SetProcessDPIAware()
$p = Get-Process studio -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { Write-Error "Lumix Studio is not running"; exit 1 }
$h = $p.MainWindowHandle
if ([W]::IsIconic($h)) { [void][W]::ShowWindow($h, 9) }   # only un-minimise; never change a maximised / sized window
$r = New-Object W+RECT; [void][W]::GetWindowRect($h, [ref]$r)
$w = $r.R - $r.L; $ht = $r.B - $r.T
$bmp = New-Object System.Drawing.Bitmap $w, $ht
$g = [System.Drawing.Graphics]::FromImage($bmp)
if ($Foreground) {
  [void][W]::SetForegroundWindow($h); Start-Sleep -Milliseconds 400
  $g.CopyFromScreen($r.L, $r.T, 0, 0, (New-Object System.Drawing.Size $w, $ht))
} else {
  $dc = $g.GetHdc(); [void][W]::PrintWindow($h, $dc, 2); $g.ReleaseHdc($dc)   # 2 = PW_RENDERFULLCONTENT
}
$g.Dispose()
$dir = Split-Path -Parent $Out; if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png); $bmp.Dispose()
Write-Output "saved $Out (${w}x${ht})"
