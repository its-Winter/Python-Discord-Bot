. "$env:USERPROFILE\Documents\Github\Python-Discord-Bot\Scripts\activate.ps1"
Clear-Host
Function Start-Bot
{
      Start-Process python main.py -PassThru -Wait
      Write-Host $LASTEXITCODE
}
Start-Bot
if ($LASTEXITCODE -eq 26)
{
      Write-Host "Restarting Bot..."
      Start-Bot
}
Write-Host $LASTEXITCODE