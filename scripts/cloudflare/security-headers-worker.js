/**
 * FraWo Security Headers - Cloudflare Worker
 *
 * This worker adds critical security headers to all responses from www.frawo-tech.de
 *
 * Deployment:
 * 1. Go to https://dash.cloudflare.com
 * 2. Select your domain (frawo-tech.de)
 * 3. Go to Workers & Pages → Create Worker
 * 4. Paste this code
 * 5. Click "Save and Deploy"
 * 6. Go to Website → Workers Routes → Add Route
 * 7. Route: www.frawo-tech.de/*
 * 8. Worker: security-headers
 *
 * Created: 2026-05-15
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Fetch the original response from origin
  const response = await fetch(request)

  // Create new response with modified headers
  const newHeaders = new Headers(response.headers)

  // X-Frame-Options - Prevent clickjacking attacks
  // Only allow framing from same origin
  newHeaders.set('X-Frame-Options', 'SAMEORIGIN')

  // Content-Security-Policy - Mitigate XSS attacks
  // Note: Odoo requires 'unsafe-inline' and 'unsafe-eval' for functionality
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com https://www.google-analytics.com",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com data:",
    "img-src 'self' data: https: blob:",
    "connect-src 'self' https://www.google-analytics.com",
    "frame-ancestors 'self'",
    "base-uri 'self'",
    "form-action 'self'"
  ].join('; ')
  newHeaders.set('Content-Security-Policy', csp)

  // Strict-Transport-Security (HSTS) - Force HTTPS
  // max-age=31536000 = 1 year
  // includeSubDomains = apply to all subdomains
  newHeaders.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')

  // X-Content-Type-Options - Prevent MIME sniffing
  // (Already set by Odoo, but we ensure it)
  newHeaders.set('X-Content-Type-Options', 'nosniff')

  // X-XSS-Protection - Legacy XSS protection for older browsers
  // Modern browsers use CSP instead
  newHeaders.set('X-XSS-Protection', '1; mode=block')

  // Referrer-Policy - Control referrer information
  // strict-origin-when-cross-origin = send full URL for same-origin, only origin for cross-origin
  newHeaders.set('Referrer-Policy', 'strict-origin-when-cross-origin')

  // Permissions-Policy - Restrict browser features
  // Disable camera, microphone, geolocation, payment
  newHeaders.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=(), payment=()')

  // Remove server information disclosure headers
  newHeaders.delete('Server')
  newHeaders.delete('X-Powered-By')

  // Return modified response
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders
  })
}
