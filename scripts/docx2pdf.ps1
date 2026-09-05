param([string]$Src, [string]$Dst)
# 用 Microsoft Word 把 docx 轉成 PDF。
# 🚨 不要用 LibreOffice：文件含隨頁註腳時，soffice --convert-to pdf 會把最後一頁整個吃掉
#    （docx 本身完整，只有 PDF 少一頁），門檻與註文長度有關，浮動且難繞。
$Src = (Resolve-Path $Src).Path
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
  $doc = $word.Documents.Open($Src)
  $doc.Fields.Update() | Out-Null
  $doc.SaveAs2($Dst, 17)          # 17 = wdFormatPDF
  $doc.Close(0)
  Write-Output "PDF: $Dst"
} finally {
  $word.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
