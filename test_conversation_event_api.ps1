$body = @{
    conversation_id = "conv_test_$(Get-Date -Format 'yyyyMMddHHmmss')"
    user_id = "user_test"
    bot_type = "TALK"
    bot_id = "talk_test"
    bot_name = "Test Talk Bot"
    start_time = "2025-11-26T10:00:00Z"
    end_time = "2025-11-26T10:20:00Z"
    conversation_log = @(
        @{
            speaker = "pika"
            turn_id = 1
            text = "Hello! Ready to talk?"
        }
    )
} | ConvertTo-Json -Depth 10

Write-Host "Testing POST /v1/conversations/end"
Write-Host "Body: $body"
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri 'http://localhost:30020/v1/conversations/end' `
        -Method Post `
        -Body $body `
        -ContentType 'application/json'
    
    Write-Host "✅ SUCCESS - Status: 202 Accepted" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ FAILED" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.ErrorDetails) {
        Write-Host "Details: $($_.ErrorDetails.Message)"
    }
}




