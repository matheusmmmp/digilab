# a run da auditoria PET_VIVO (plano, secao 11), desacoplada do app; corte em 8 h
$log = 'D:\Trab\digilab\v3-pet-vivo-run-log'
Set-Location 'D:\Trab\digilab\v3-pet-vivo-run'
"inicio $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File "$log\estado.txt" -Encoding utf8
$p = Start-Process -FilePath python -ArgumentList '-u','experiments\auditoria_pet_vivo.py','--codigo','D:\Trab\digilab\v3-pet-vivo-a287ba2','--processos','4' -RedirectStandardOutput "$log\saida.txt" -RedirectStandardError "$log\erro.txt" -NoNewWindow -PassThru
$null = $p.Handle
"pid $($p.Id)" | Out-File "$log\estado.txt" -Append -Encoding utf8
if (-not $p.WaitForExit(28800000)) {
  taskkill /PID $p.Id /T /F | Out-Null
  "corte_8h $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File "$log\estado.txt" -Append -Encoding utf8
} else {
  "saida $($p.ExitCode) $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File "$log\estado.txt" -Append -Encoding utf8
}
