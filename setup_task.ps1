param(
    [string]$TaskName = "BrokerResearchScraper",
    [string]$Time = "07:20"
)

$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$bat = Join-Path $repo "run_scraper.bat"

if (-not (Test-Path $bat)) {
    Write-Error "Không tìm thấy run_scraper.bat"
    exit 1
}

$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$bat`"" -WorkingDirectory $repo
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Description "Tự động tải báo cáo HSC và Vietcap về E:\Báo cáo" -Force

Write-Host "Đã tạo Task Scheduler: $TaskName chạy hàng ngày lúc $Time"
Write-Host "Muốn đổi giờ: powershell -ExecutionPolicy Bypass -File .\setup_task.ps1 -Time 12:30"
