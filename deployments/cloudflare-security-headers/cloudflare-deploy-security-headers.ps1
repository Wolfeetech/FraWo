# Cloudflare Security Headers Deployment Script (PowerShell)
# Verwendet Cloudflare API um Transform Rules automatisch zu erstellen

Write-Host "========================================" -ForegroundColor Blue
Write-Host "Cloudflare Security Headers Deployment" -ForegroundColor Blue
Write-Host "========================================" -ForegroundColor Blue
Write-Host ""

# API Credentials abfragen
Write-Host "Cloudflare API Credentials benötigt:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Login zu Cloudflare Dashboard: https://dash.cloudflare.com/"
Write-Host "2. My Profile → API Tokens → Create Token"
Write-Host "3. Template: Edit zone DNS + Transform Rules"
Write-Host "4. Zone Resources: Include → Specific zone → frawo-tech.de"
Write-Host ""

$CF_API_TOKEN = Read-Host "Cloudflare API Token"
$CF_ZONE_ID = Read-Host "Cloudflare Zone ID (Dashboard → Overview → Zone ID)"
$CF_EMAIL = Read-Host "Cloudflare Account Email"

Write-Host ""
Write-Host "Testing API Connection..." -ForegroundColor Blue

# Test API Connection
$headers = @{
    "Authorization" = "Bearer $CF_API_TOKEN"
    "Content-Type" = "application/json"
}

try {
    $zoneInfo = Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID" `
        -Method Get -Headers $headers

    if ($zoneInfo.result.name -eq "frawo-tech.de") {
        Write-Host "✅ API Connection successful - Zone: $($zoneInfo.result.name)" -ForegroundColor Green
    } else {
        Write-Host "❌ Wrong Zone: $($zoneInfo.result.name)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ API Connection failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Creating Transform Rule for Security Headers..." -ForegroundColor Blue

# Rule Payload
$rulePayload = @{
    description = "Add Security Headers for frawo-tech.de"
    action = "execute"
    expression = "true"
    action_parameters = @{
        headers = @{
            "Strict-Transport-Security" = @{
                operation = "set"
                value = "max-age=31536000; includeSubDomains; preload"
            }
            "X-Frame-Options" = @{
                operation = "set"
                value = "SAMEORIGIN"
            }
            "X-Content-Type-Options" = @{
                operation = "set"
                value = "nosniff"
            }
            "Referrer-Policy" = @{
                operation = "set"
                value = "strict-origin-when-cross-origin"
            }
            "Permissions-Policy" = @{
                operation = "set"
                value = "geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=()"
            }
            "Content-Security-Policy" = @{
                operation = "set"
                value = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://challenges.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' wss: https:; frame-src 'self' https://challenges.cloudflare.com; frame-ancestors 'self';"
            }
        }
    }
    enabled = $true
} | ConvertTo-Json -Depth 10

# Get existing ruleset
try {
    $rulesetResponse = Invoke-RestMethod `
        -Uri "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/rulesets/phases/http_response_headers_transform/entrypoint" `
        -Method Get -Headers $headers

    $rulesetId = $rulesetResponse.result.id

    if ($rulesetId) {
        Write-Host "Adding rule to existing ruleset: $rulesetId" -ForegroundColor Yellow

        $updateResponse = Invoke-RestMethod `
            -Uri "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/rulesets/$rulesetId/rules" `
            -Method Post -Headers $headers -Body $rulePayload

        if ($updateResponse.success) {
            Write-Host "✅ Security Headers Rule added successfully!" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to add rule" -ForegroundColor Red
            Write-Host ($updateResponse | ConvertTo-Json)
            exit 1
        }
    }
} catch {
    Write-Host "Creating new ruleset..." -ForegroundColor Yellow

    $newRulesetPayload = @{
        name = "Security Headers Transform Rules"
        kind = "zone"
        phase = "http_response_headers_transform"
        rules = @($rulePayload | ConvertFrom-Json)
    } | ConvertTo-Json -Depth 10

    try {
        $createResponse = Invoke-RestMethod `
            -Uri "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/rulesets" `
            -Method Post -Headers $headers -Body $newRulesetPayload

        if ($createResponse.success) {
            Write-Host "✅ Security Headers Rule created successfully!" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to create rule" -ForegroundColor Red
            Write-Host ($createResponse | ConvertTo-Json)
            exit 1
        }
    } catch {
        Write-Host "❌ Error creating ruleset: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Purging Cloudflare Cache..." -ForegroundColor Blue

# Purge cache
try {
    $purgePayload = @{
        purge_everything = $true
    } | ConvertTo-Json

    $purgeResponse = Invoke-RestMethod `
        -Uri "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/purge_cache" `
        -Method Post -Headers $headers -Body $purgePayload

    if ($purgeResponse.success) {
        Write-Host "✅ Cache purged successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Cache purge may have failed (check manually)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Cache purge error: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Wait 5-10 minutes for changes to propagate"
Write-Host "2. Test headers: curl -I https://frawo-tech.de"
Write-Host "3. Verify online: https://securityheaders.com/?q=https://frawo-tech.de"
Write-Host "4. Check website functionality (login, navigation, etc.)"
Write-Host ""
Write-Host "Monitor for 24-48 hours:" -ForegroundColor Blue
Write-Host "- Cloudflare Dashboard → Analytics → Security"
Write-Host "- Browser Console (F12) for CSP errors"
Write-Host ""
Write-Host "Rollback if needed:" -ForegroundColor Red
Write-Host "- Dashboard → Rules → Transform Rules → Disable rule"
Write-Host "- Or delete rule via API"
Write-Host ""
