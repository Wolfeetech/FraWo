# Odoo Email Configuration Setup (PowerShell Helper)
# Stand: 2026-04-22

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Odoo Sender Email Configuration - Manual Setup Guide" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$OdooUrl = "http://odoo.hs27.internal"

Write-Host "📋 Manual Configuration Steps:" -ForegroundColor Yellow
Write-Host ""

# Step 1: Company Email
Write-Host "1️⃣  Set Company Email" -ForegroundColor Green
Write-Host "   URL: $OdooUrl/web#action=52&model=res.company&view_type=form&menu_id=81" -ForegroundColor White
Write-Host "   Steps:" -ForegroundColor White
Write-Host "   - Open Odoo in browser" -ForegroundColor Gray
Write-Host "   - Go to: Settings → Companies → Companies" -ForegroundColor Gray
Write-Host "   - Edit 'FraWo GbR'" -ForegroundColor Gray
Write-Host "   - Set Email: noreply@frawo-tech.de" -ForegroundColor Gray
Write-Host "   - Save" -ForegroundColor Gray
Write-Host ""

# Step 2: User Email
Write-Host "2️⃣  Set User Email" -ForegroundColor Green
Write-Host "   URL: $OdooUrl/web#action=87&model=res.users&view_type=list&menu_id=81" -ForegroundColor White
Write-Host "   Steps:" -ForegroundColor White
Write-Host "   - Go to: Settings → Users & Companies → Users" -ForegroundColor Gray
Write-Host "   - Edit 'admin' user" -ForegroundColor Gray
Write-Host "   - Set Email: wolf@frawo-tech.de" -ForegroundColor Gray
Write-Host "   - Save" -ForegroundColor Gray
Write-Host ""

# Step 3: SMTP Check
Write-Host "3️⃣  Verify SMTP Server" -ForegroundColor Green
Write-Host "   Steps:" -ForegroundColor White
Write-Host "   - Go to: Settings → Activate Developer Mode" -ForegroundColor Gray
Write-Host "   - Settings → Technical → Email → Outgoing Mail Servers" -ForegroundColor Gray
Write-Host "   - Open 'Strato SMTP'" -ForegroundColor Gray
Write-Host "   - Verify settings:" -ForegroundColor Gray
Write-Host "     * SMTP Server: smtp.strato.de" -ForegroundColor DarkGray
Write-Host "     * Port: 587" -ForegroundColor DarkGray
Write-Host "     * Security: TLS (STARTTLS)" -ForegroundColor DarkGray
Write-Host "     * Username: webmaster@frawo-tech.de" -ForegroundColor DarkGray
Write-Host "     * From Filter: noreply@frawo-tech.de" -ForegroundColor DarkGray
Write-Host "   - Click 'Test Connection'" -ForegroundColor Gray
Write-Host ""

# Step 4: Test
Write-Host "4️⃣  Test Email Sending" -ForegroundColor Green
Write-Host "   Test 1: Cancel a quote" -ForegroundColor White
Write-Host "   - Sales → Quotations → Select a quote → Cancel" -ForegroundColor Gray
Write-Host "   - Error should NOT appear" -ForegroundColor Gray
Write-Host ""
Write-Host "   Test 2: Send a quote" -ForegroundColor White
Write-Host "   - Sales → Quotations → Select a quote → Send by Email" -ForegroundColor Gray
Write-Host "   - Email should send successfully" -ForegroundColor Gray
Write-Host ""

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$OpenBrowser = Read-Host "Open Odoo in browser? (y/n)"
if ($OpenBrowser -eq "y" -or $OpenBrowser -eq "Y") {
    Write-Host "🌐 Opening Odoo..." -ForegroundColor Green
    Start-Process "$OdooUrl/web"
    Write-Host ""
    Write-Host "✅ Browser opened. Follow the manual steps above." -ForegroundColor Green
} else {
    Write-Host "📖 Manual URL: $OdooUrl/web" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📚 Full documentation: DOCS/ODOO_SENDER_EMAIL_FIX.md" -ForegroundColor Cyan
Write-Host "📝 Quick reference: artifacts/odoo_email_fix_quickref.md" -ForegroundColor Cyan
Write-Host ""
