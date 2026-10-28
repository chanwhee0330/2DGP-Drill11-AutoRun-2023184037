# Windows PowerShell: .\tools\render_state_diagram.ps1
# PNG geometry and labels are editable here; the transition source is in docs/state_diagram.mmd.
Add-Type -AssemblyName System.Drawing

$diagramRoot = Split-Path -Parent $PSScriptRoot
$diagramOutput = Join-Path $diagramRoot 'docs\state_diagram.png'
$diagramBitmap = New-Object System.Drawing.Bitmap(1800, 1300)
$diagramGraphics = [System.Drawing.Graphics]::FromImage($diagramBitmap)
$diagramGraphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$diagramGraphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$diagramGraphics.Clear([System.Drawing.Color]::White)
$diagramFont = New-Object System.Drawing.Font('Malgun Gothic', 24, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
$diagramTitleFont = New-Object System.Drawing.Font('Malgun Gothic', 38, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
$diagramNodeFont = New-Object System.Drawing.Font('Malgun Gothic', 34, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
$diagramSmallFont = New-Object System.Drawing.Font('Malgun Gothic', 22, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
$diagramTextBrush = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml('#172033'))
$diagramWhiteBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$diagramFormat = New-Object System.Drawing.StringFormat
$diagramFormat.Alignment = [System.Drawing.StringAlignment]::Center
$diagramFormat.LineAlignment = [System.Drawing.StringAlignment]::Center
$diagramArrowPen = New-Object System.Drawing.Pen([System.Drawing.ColorTranslator]::FromHtml('#475569'), 3)
$diagramArrowCap = New-Object System.Drawing.Drawing2D.AdjustableArrowCap(5, 6, $true)
$diagramArrowPen.CustomEndCap = $diagramArrowCap

function Draw-DiagramArrow([object[]] $coordinates) {
    $points = [System.Drawing.PointF[]] @(
        for ($index = 0; $index -lt $coordinates.Length; $index += 2) {
            New-Object System.Drawing.PointF([single]$coordinates[$index], [single]$coordinates[$index + 1])
        }
    )
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $path.AddLines($points)
    $diagramGraphics.DrawPath($diagramArrowPen, $path)
    $path.Dispose()
}

function Draw-DiagramLabel([string] $text, [single] $x, [single] $y, [single] $width, [single] $height) {
    $rect = New-Object System.Drawing.RectangleF(($x - $width / 2), ($y - $height / 2), $width, $height)
    $diagramGraphics.FillRectangle($diagramWhiteBrush, $rect)
    $diagramGraphics.DrawString($text, $diagramFont, $diagramTextBrush, $rect, $diagramFormat)
}

function Draw-DiagramState([string] $name, [string] $subtitle, [single] $x, [single] $y, [single] $width, [single] $height, [string] $fill) {
    $left = $x - $width / 2
    $top = $y - $height / 2
    $radius = 24
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $path.AddArc($left, $top, $radius, $radius, 180, 90)
    $path.AddArc(($left + $width - $radius), $top, $radius, $radius, 270, 90)
    $path.AddArc(($left + $width - $radius), ($top + $height - $radius), $radius, $radius, 0, 90)
    $path.AddArc($left, ($top + $height - $radius), $radius, $radius, 90, 90)
    $path.CloseFigure()
    $brush = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml($fill))
    $pen = New-Object System.Drawing.Pen([System.Drawing.ColorTranslator]::FromHtml('#64748b'), 2)
    $diagramGraphics.FillPath($brush, $path)
    $diagramGraphics.DrawPath($pen, $path)
    $nameRect = New-Object System.Drawing.RectangleF($left, ($y - 42), $width, 52)
    $detailRect = New-Object System.Drawing.RectangleF($left, ($y + 13), $width, 42)
    $diagramGraphics.DrawString($name, $diagramNodeFont, $diagramTextBrush, $nameRect, $diagramFormat)
    $diagramGraphics.DrawString($subtitle, $diagramSmallFont, $diagramTextBrush, $detailRect, $diagramFormat)
    $pen.Dispose()
    $brush.Dispose()
    $path.Dispose()
}

try {
    $titleRect = New-Object System.Drawing.RectangleF(60, 35, 1680, 70)
    $diagramGraphics.DrawString('Drill #11 · 소년 상태 다이어그램', $diagramTitleFont, $diagramTextBrush, $titleRect, $diagramFormat)

    Draw-DiagramArrow @(220, 650, 430, 650)
    Draw-DiagramArrow @(770, 620, 1180, 620)
    Draw-DiagramArrow @(1180, 680, 770, 680)
    Draw-DiagramArrow @(550, 585, 550, 295)
    Draw-DiagramArrow @(650, 295, 650, 585)
    Draw-DiagramArrow @(770, 230, 1350, 230, 1350, 585)
    Draw-DiagramArrow @(550, 715, 550, 1005)
    Draw-DiagramArrow @(650, 1005, 650, 715)
    Draw-DiagramArrow @(780, 1080, 1350, 1080, 1350, 715)

    $diagramGraphics.FillEllipse($diagramTextBrush, 180, 630, 40, 40)
    Draw-DiagramLabel '시작' 315 604 130 45
    Draw-DiagramLabel '← / → 키 누름' 975 567 350 48
    Draw-DiagramLabel "방향키 모두 해제`n또는 양쪽 입력" 975 747 400 80
    Draw-DiagramLabel "Idle에서`n5초 대기" 375 440 250 85
    Draw-DiagramLabel 'Space 키' 790 440 230 55
    Draw-DiagramLabel '← / → 키 누름' 1060 180 420 55
    Draw-DiagramLabel 'A 키 누름' 380 855 240 55
    Draw-DiagramLabel '5초 경과' 800 855 240 55
    Draw-DiagramLabel "← / → 키로 취소`n누른 방향의 일반 Run" 1070 1150 450 85

    Draw-DiagramState 'Idle' '대기 · 기본 크기' 600 650 340 130 '#e8f1fc'
    Draw-DiagramState 'Run' '300 px/s · 100 × 100' 1350 650 340 130 '#e6f5ef'
    Draw-DiagramState 'Sleep' 'Space 또는 방향키로 깨어남' 600 230 340 130 '#f0eafa'
    Draw-DiagramState 'AutoRun' '600 px/s · 200 × 200' 600 1080 360 150 '#fff0dd'

    $footerRect = New-Object System.Drawing.RectangleF(90, 1230, 1620, 48)
    $diagramGraphics.DrawString('AutoRun: 속도 ×2 · 크기 ×2 · 키 없이 자동 이동 · 좌우 끝에서 자동 방향 전환', $diagramSmallFont, $diagramTextBrush, $footerRect, $diagramFormat)
    $diagramBitmap.Save($diagramOutput, [System.Drawing.Imaging.ImageFormat]::Png)
    Write-Output $diagramOutput
}
finally {
    $diagramArrowPen.Dispose()
    $diagramArrowCap.Dispose()
    $diagramFormat.Dispose()
    $diagramTextBrush.Dispose()
    $diagramWhiteBrush.Dispose()
    $diagramFont.Dispose()
    $diagramTitleFont.Dispose()
    $diagramNodeFont.Dispose()
    $diagramSmallFont.Dispose()
    $diagramGraphics.Dispose()
    $diagramBitmap.Dispose()
}
