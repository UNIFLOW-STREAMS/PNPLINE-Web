param(
    [string]$OutputDirectory = 'F:\pnpline-landing\output\pnpline-cn-home-concept'
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$normalizerSource = @'
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;

public static class PnplineBackgroundNormalizer
{
    private sealed class IntQueue
    {
        private readonly int[] items;
        private int head;
        private int tail;

        public IntQueue(int capacity)
        {
            items = new int[capacity];
        }

        public int Count { get { return tail - head; } }
        public void Enqueue(int value) { items[tail++] = value; }
        public int Dequeue() { return items[head++]; }
    }
    private static bool IsConnectedLightBackground(Color color)
    {
        int max = Math.Max(color.R, Math.Max(color.G, color.B));
        int min = Math.Min(color.R, Math.Min(color.G, color.B));

        return color.R >= 205
            && color.G >= 218
            && color.B >= 222
            && max - min <= 58;
    }

    private static void EnqueueIfBackground(
        Bitmap bitmap,
        bool[] visited,
        IntQueue queue,
        int x,
        int y)
    {
        int width = bitmap.Width;
        int height = bitmap.Height;
        if (x < 0 || y < 0 || x >= width || y >= height)
        {
            return;
        }

        int index = y * width + x;
        if (visited[index])
        {
            return;
        }

        visited[index] = true;
        if (IsConnectedLightBackground(bitmap.GetPixel(x, y)))
        {
            queue.Enqueue(index);
        }
    }

    public static int CreateLightSection(
        string inputPath,
        string outputPath,
        Color gutterColor,
        int canvasWidth,
        int contentWidth,
        int height)
    {
        int contentX = (canvasWidth - contentWidth) / 2;
        using (Image source = Image.FromFile(inputPath))
        using (Bitmap center = new Bitmap(contentWidth, height, PixelFormat.Format24bppRgb))
        {
            using (Graphics centerGraphics = Graphics.FromImage(center))
            {
                centerGraphics.InterpolationMode = InterpolationMode.HighQualityBicubic;
                centerGraphics.CompositingQuality = CompositingQuality.HighQuality;
                centerGraphics.PixelOffsetMode = PixelOffsetMode.HighQuality;
                centerGraphics.DrawImage(source, new Rectangle(0, 0, contentWidth, height));
            }

            bool[] visited = new bool[contentWidth * height];
            IntQueue queue = new IntQueue(contentWidth * height);

            for (int x = 0; x < contentWidth; x++)
            {
                EnqueueIfBackground(center, visited, queue, x, 0);
                EnqueueIfBackground(center, visited, queue, x, height - 1);
            }

            for (int y = 0; y < height; y++)
            {
                EnqueueIfBackground(center, visited, queue, 0, y);
                EnqueueIfBackground(center, visited, queue, contentWidth - 1, y);
            }

            int changedPixels = 0;
            while (queue.Count > 0)
            {
                int index = queue.Dequeue();
                int x = index % contentWidth;
                int y = index / contentWidth;
                center.SetPixel(x, y, gutterColor);
                changedPixels++;

                EnqueueIfBackground(center, visited, queue, x - 1, y);
                EnqueueIfBackground(center, visited, queue, x + 1, y);
                EnqueueIfBackground(center, visited, queue, x, y - 1);
                EnqueueIfBackground(center, visited, queue, x, y + 1);
            }

            using (Bitmap canvas = new Bitmap(canvasWidth, height, PixelFormat.Format24bppRgb))
            {
                using (Graphics graphics = Graphics.FromImage(canvas))
                {
                    graphics.Clear(gutterColor);
                    graphics.DrawImageUnscaled(center, contentX, 0);
                }

                canvas.Save(outputPath, ImageFormat.Png);
            }

            return changedPixels;
        }
    }

    public static void CreateEdgeExtendedSection(
        string inputPath,
        string outputPath,
        int canvasWidth,
        int contentWidth,
        int height)
    {
        int contentX = (canvasWidth - contentWidth) / 2;
        using (Image source = Image.FromFile(inputPath))
        using (Bitmap center = new Bitmap(contentWidth, height, PixelFormat.Format24bppRgb))
        {
            using (Graphics centerGraphics = Graphics.FromImage(center))
            {
                centerGraphics.InterpolationMode = InterpolationMode.HighQualityBicubic;
                centerGraphics.CompositingQuality = CompositingQuality.HighQuality;
                centerGraphics.PixelOffsetMode = PixelOffsetMode.HighQuality;
                centerGraphics.DrawImage(source, new Rectangle(0, 0, contentWidth, height));
            }

            using (Bitmap canvas = new Bitmap(canvasWidth, height, PixelFormat.Format24bppRgb))
            using (Graphics graphics = Graphics.FromImage(canvas))
            {
                for (int y = 0; y < height; y++)
                {
                    using (Pen leftPen = new Pen(center.GetPixel(0, y)))
                    using (Pen rightPen = new Pen(center.GetPixel(contentWidth - 1, y)))
                    {
                        graphics.DrawLine(leftPen, 0, y, contentX - 1, y);
                        graphics.DrawLine(rightPen, contentX + contentWidth, y, canvasWidth - 1, y);
                    }
                }

                graphics.DrawImageUnscaled(center, contentX, 0);
                canvas.Save(outputPath, ImageFormat.Png);
            }
        }
    }
}
'@

$drawingRuntimeDirectory = Split-Path -Parent ([System.Drawing.Bitmap].Assembly.Location)
$drawingReferences = @(
    [System.Drawing.Bitmap].Assembly.Location,
    [System.Drawing.Color].Assembly.Location,
    (Join-Path $drawingRuntimeDirectory 'System.Private.Windows.GdiPlus.dll'),
    (Join-Path $drawingRuntimeDirectory 'System.Private.Windows.Core.dll')
) | Select-Object -Unique
Add-Type -TypeDefinition $normalizerSource -ReferencedAssemblies $drawingReferences

$inputs = @(
    'section-01-hero.png',
    'section-02-flow.png',
    'section-03-customer-paths.png',
    'section-04-services.png',
    'section-05-trust-system.png',
    'section-06-customs.png',
    'section-07-cost.png',
    'section-08-faq.png',
    'section-09-quote-form.png',
    'section-10-footer.png'
)

$outputs = @(
    'section-01-hero-1920-v3.png',
    'section-02-flow-1920-v3.png',
    'section-03-customer-paths-1920-v3.png',
    'section-04-services-1920-v3.png',
    'section-05-trust-system-1920-v3.png',
    'section-06-customs-1920-v3.png',
    'section-07-cost-1920-v3.png',
    'section-08-faq-1920-v3.png',
    'section-09-quote-form-1920-v3.png',
    'section-10-footer-1920-v3.png'
)

$canvasWidth = 1920
$contentWidth = 1440
$sectionHeight = 810
$gutterColor = [System.Drawing.ColorTranslator]::FromHtml('#F6F8F8')
$lightSections = @(0, 1, 2, 3, 4, 5, 7, 9)
$results = @()

for ($index = 0; $index -lt $inputs.Count; $index++) {
    $inputPath = Join-Path $OutputDirectory $inputs[$index]
    $outputPath = Join-Path $OutputDirectory $outputs[$index]

    if ($lightSections -contains $index) {
        $changed = [PnplineBackgroundNormalizer]::CreateLightSection(
            $inputPath,
            $outputPath,
            $gutterColor,
            $canvasWidth,
            $contentWidth,
            $sectionHeight
        )
    }
    else {
        [PnplineBackgroundNormalizer]::CreateEdgeExtendedSection(
            $inputPath,
            $outputPath,
            $canvasWidth,
            $contentWidth,
            $sectionHeight
        )
        $changed = 0
    }

    $results += [PSCustomObject]@{
        Section = $outputs[$index]
        BackgroundPixelsNormalized = $changed
    }
}

$finalHeight = $sectionHeight * $outputs.Count
$finalBitmap = [System.Drawing.Bitmap]::new(
    $canvasWidth,
    $finalHeight,
    [System.Drawing.Imaging.PixelFormat]::Format24bppRgb
)
$finalGraphics = [System.Drawing.Graphics]::FromImage($finalBitmap)

for ($index = 0; $index -lt $outputs.Count; $index++) {
    $image = [System.Drawing.Image]::FromFile((Join-Path $OutputDirectory $outputs[$index]))
    $finalGraphics.DrawImageUnscaled($image, 0, $index * $sectionHeight)
    $image.Dispose()
}

$finalGraphics.Dispose()
$finalPath = Join-Path $OutputDirectory 'pnpline-cn-home-concept-v3-1920x8100.png'
$finalBitmap.Save($finalPath, [System.Drawing.Imaging.ImageFormat]::Png)

$preview = [System.Drawing.Bitmap]::new(
    480,
    2025,
    [System.Drawing.Imaging.PixelFormat]::Format24bppRgb
)
$previewGraphics = [System.Drawing.Graphics]::FromImage($preview)
$previewGraphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$previewGraphics.DrawImage($finalBitmap, [System.Drawing.Rectangle]::new(0, 0, 480, 2025))
$previewGraphics.Dispose()
$previewPath = Join-Path $OutputDirectory 'pnpline-cn-home-concept-v3-preview.png'
$preview.Save($previewPath, [System.Drawing.Imaging.ImageFormat]::Png)
$preview.Dispose()
$finalBitmap.Dispose()

$results

foreach ($path in @($finalPath, $previewPath)) {
    $file = Get-Item -LiteralPath $path
    $image = [System.Drawing.Image]::FromFile($path)
    [PSCustomObject]@{
        Name = $file.Name
        Width = $image.Width
        Height = $image.Height
        Bytes = $file.Length
        FullName = $file.FullName
    }
    $image.Dispose()
}
