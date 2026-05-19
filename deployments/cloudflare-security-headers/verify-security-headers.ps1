# Security Headers Verification Script für frawo-tech.de (PowerShell Version)
# Prüft alle implementierten Security Headers und gibt einen Report aus

param(
    [string]$Domain = "frawo-tech.de"
)

$URL = "https://$Domain"

Write-Host "======================================" -ForegroundColor Blue
Write-Host "Security Headers Test für $Domain" -ForegroundColor Blue
Write-Host "======================================" -ForegroundColor Blue
Write-Host ""

# Funktion zum Prüfen eines Headers
function Check-Header {
    param(
        [string]$HeaderName,
        [string]$ExpectedValue = "",
        [string]$Priority = "MEDIUM"
    )

    $response = Invoke-WebRequest -Uri $URL -Method Head -UseBasicParsing -ErrorAction SilentlyContinue
    $actualValue = $response.Headers[$HeaderName]

    if ($actualValue) {
        Write-Host "✅ $HeaderName" -ForegroundColor Green
        Write-Host "   Wert: $actualValue"

        if ($ExpectedValue -and $actualValue -match $ExpectedValue) {
            Write-Host "   Entspricht Empfehlung" -ForegroundColor Green
        } elseif ($ExpectedValue) {
            Write-Host "   ⚠️  Weicht von Empfehlung ab" -ForegroundColor Yellow
            Write-Host "   Empfohlen: $ExpectedValue"
        }
    } else {
        if ($Priority -eq "HIGH") {
            Write-Host "❌ $HeaderName - FEHLT (PRIORITÄT: HOCH)" -ForegroundColor Red
        } elseif ($Priority -eq "MEDIUM") {
            Write-Host "⚠️  $HeaderName - FEHLT (PRIORITÄT: MITTEL)" -ForegroundColor Yellow
        } else {
            Write-Host "ℹ️  $HeaderName - FEHLT (PRIORITÄT: NIEDRIG)" -ForegroundColor Gray
        }
    }
    Write-Host ""
}

Write-Host "Testing $URL..." -ForegroundColor Yellow
Write-Host ""

# Prüfe jeden Security Header
Write-Host "=== KRITISCHE SECURITY HEADERS ===" -ForegroundColor Blue
Write-Host ""

Check-Header -HeaderName "Strict-Transport-Security" -ExpectedValue "max-age=31536000" -Priority "HIGH"
Check-Header -HeaderName "X-Frame-Options" -ExpectedValue "SAMEORIGIN" -Priority "HIGH"
Check-Header -HeaderName "Content-Security-Policy" -ExpectedValue "default-src" -Priority "HIGH"

Write-Host "=== WICHTIGE SECURITY HEADERS ===" -ForegroundColor Blue
Write-Host ""

Check-Header -HeaderName "X-Content-Type-Options" -ExpectedValue "nosniff" -Priority "MEDIUM"
Check-Header -HeaderName "Referrer-Policy" -ExpectedValue "strict-origin-when-cross-origin" -Priority "MEDIUM"
Check-Header -HeaderName "Permissions-Policy" -Priority "MEDIUM"

Write-Host "=== ZUSÄTZLICHE HEADERS ===" -ForegroundColor Blue
Write-Host ""

Check-Header -HeaderName "X-XSS-Protection" -Priority "LOW"
Check-Header -HeaderName "Server" -Priority "LOW"

# Cookie-Sicherheit prüfen
Write-Host "=== COOKIE SECURITY ===" -ForegroundColor Blue
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri $URL -UseBasicParsing -ErrorAction Stop
    $cookies = $response.Headers['Set-Cookie']

    if ($cookies) {
        Write-Host "✅ Cookies gefunden" -ForegroundColor Green

        if ($cookies -is [array]) {
            foreach ($cookie in $cookies) {
                Write-Host ""
                $cookieName = ($cookie -split ';')[0] -split '=' | Select-Object -First 1
                Write-Host "Cookie: $cookieName"

                if ($cookie -match "Secure") {
                    Write-Host "  ✅ Secure Flag vorhanden" -ForegroundColor Green
                } else {
                    Write-Host "  ❌ Secure Flag FEHLT" -ForegroundColor Red
                }

                if ($cookie -match "HttpOnly") {
                    Write-Host "  ✅ HttpOnly Flag vorhanden" -ForegroundColor Green
                } else {
                    Write-Host "  ⚠️  HttpOnly Flag fehlt" -ForegroundColor Yellow
                }

                if ($cookie -match "SameSite") {
                    $sameSite = ($cookie -split ';' | Where-Object { $_ -match "SameSite" }).Trim()
                    Write-Host "  ✅ $sameSite" -ForegroundColor Green
                } else {
                    Write-Host "  ❌ SameSite Attribut FEHLT" -ForegroundColor Red
                }
            }
        } else {
            Write-Host ""
            $cookieName = ($cookies -split ';')[0] -split '=' | Select-Object -First 1
            Write-Host "Cookie: $cookieName"

            if ($cookies -match "Secure") {
                Write-Host "  ✅ Secure Flag vorhanden" -ForegroundColor Green
            } else {
                Write-Host "  ❌ Secure Flag FEHLT" -ForegroundColor Red
            }

            if ($cookies -match "HttpOnly") {
                Write-Host "  ✅ HttpOnly Flag vorhanden" -ForegroundColor Green
            } else {
                Write-Host "  ⚠️  HttpOnly Flag fehlt" -ForegroundColor Yellow
            }

            if ($cookies -match "SameSite") {
                $sameSite = ($cookies -split ';' | Where-Object { $_ -match "SameSite" }).Trim()
                Write-Host "  ✅ $sameSite" -ForegroundColor Green
            } else {
                Write-Host "  ❌ SameSite Attribut FEHLT" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "ℹ️  Keine Cookies im Response (normal für Startseite)" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Konnte Cookies nicht prüfen: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""

# SSL/TLS Test (vereinfacht für PowerShell)
Write-Host "=== SSL/TLS CONFIGURATION ===" -ForegroundColor Blue
Write-Host ""

try {
    $request = [System.Net.WebRequest]::Create($URL)
    $request.Method = "HEAD"
    $response = $request.GetResponse()

    if ($response.ResponseUri.Scheme -eq "https") {
        Write-Host "✅ HTTPS aktiv" -ForegroundColor Green
    }

    $response.Close()
} catch {
    Write-Host "⚠️  SSL/TLS Test fehlgeschlagen" -ForegroundColor Yellow
}

Write-Host ""

# DNS Check
Write-Host "=== DNS CONFIGURATION ===" -ForegroundColor Blue
Write-Host ""

try {
    $dnsResult = Resolve-DnsName -Name $Domain -ErrorAction SilentlyContinue

    $ipv4 = $dnsResult | Where-Object { $_.Type -eq "A" } | Select-Object -First 1
    if ($ipv4) {
        Write-Host "✅ IPv4: $($ipv4.IPAddress)" -ForegroundColor Green
    }

    $ipv6 = $dnsResult | Where-Object { $_.Type -eq "AAAA" } | Select-Object -First 1
    if ($ipv6) {
        Write-Host "✅ IPv6: $($ipv6.IPAddress)" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  DNS Lookup fehlgeschlagen" -ForegroundColor Yellow
}

# Cloudflare Detection
try {
    $response = Invoke-WebRequest -Uri $URL -Method Head -UseBasicParsing -ErrorAction SilentlyContinue
    $cfRay = $response.Headers['CF-RAY']

    if ($cfRay) {
        Write-Host "✅ Cloudflare aktiv (CF-RAY: $cfRay)" -ForegroundColor Green
    }
} catch {
    # Ignore
}

Write-Host ""

# Gesamtbewertung
Write-Host "=== GESAMTBEWERTUNG ===" -ForegroundColor Blue
Write-Host ""

$criticalCount = 0
$criticalTotal = 3

try {
    $response = Invoke-WebRequest -Uri $URL -Method Head -UseBasicParsing -ErrorAction Stop

    if ($response.Headers['Strict-Transport-Security']) { $criticalCount++ }
    if ($response.Headers['X-Frame-Options']) { $criticalCount++ }
    if ($response.Headers['Content-Security-Policy']) { $criticalCount++ }

    Write-Host "Kritische Security Headers: $criticalCount/$criticalTotal"

    if ($criticalCount -eq $criticalTotal) {
        Write-Host "✅ AUSGEZEICHNET - Alle kritischen Header vorhanden" -ForegroundColor Green
        $grade = "A"
    } elseif ($criticalCount -eq 2) {
        Write-Host "⚠️  GUT - 1 kritischer Header fehlt" -ForegroundColor Yellow
        $grade = "B"
    } elseif ($criticalCount -eq 1) {
        Write-Host "⚠️  BEFRIEDIGEND - 2 kritische Header fehlen" -ForegroundColor Yellow
        $grade = "C"
    } else {
        Write-Host "❌ MANGELHAFT - Alle kritischen Header fehlen" -ForegroundColor Red
        $grade = "D"
    }
} catch {
    Write-Host "❌ Fehler bei der Bewertung: $($_.Exception.Message)" -ForegroundColor Red
    $grade = "F"
}

Write-Host ""
Write-Host "Security Grade: $grade" -ForegroundColor Blue
Write-Host ""

# Online Tests empfehlen
Write-Host "=== EMPFOHLENE ONLINE-TESTS ===" -ForegroundColor Blue
Write-Host ""
Write-Host "1. Security Headers: https://securityheaders.com/?q=$URL"
Write-Host "2. Mozilla Observatory: https://observatory.mozilla.org/analyze/$Domain"
Write-Host "3. SSL Labs: https://www.ssllabs.com/ssltest/analyze.html?d=$Domain"
Write-Host ""

# Zusammenfassung
Write-Host "======================================" -ForegroundColor Blue
Write-Host "Test abgeschlossen für $Domain" -ForegroundColor Blue
Write-Host "======================================" -ForegroundColor Blue

# Exit Code basierend auf Grade
switch ($grade) {
    "A" { exit 0 }
    "B" { exit 0 }
    "C" { exit 1 }
    "D" { exit 1 }
    default { exit 2 }
}
