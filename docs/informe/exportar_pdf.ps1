# Actualiza la tabla de contenido del .docx y lo exporta a PDF con Microsoft Word.
# Uso: powershell -File exportar_pdf.ps1 <entrada.docx> <salida.pdf>
param([string]$docx, [string]$pdf)
$ErrorActionPreference = "Stop"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$word.Options.UpdateLinksAtOpen = $false
try {
    # Open(FileName, ConfirmConversions, ReadOnly, AddToRecentFiles)
    $doc = $word.Documents.Open($docx, $false, $false, $false)
    "abierto"
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    "toc actualizada"
    $doc.Save()
    $doc.ExportAsFixedFormat($pdf, 17)   # 17 = wdExportFormatPDF
    "Paginas: " + $doc.ComputeStatistics(2)
    $doc.Close($false)
    "PDF generado: $pdf"
} finally {
    $word.Quit()
}
