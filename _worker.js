// FraWo Security Headers Worker
// Deployed via Cloudflare Workers

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Fetch the original response from origin
  const response = await fetch(request)

  // Create new response with modified headers
  const newHeaders = new Headers(response.headers)
  const url = new URL(request.url)

  // Scoped exception: allow the HA touchscreen dashboard (internal LAN only)
  // to embed this one read-only widget endpoint. Everything else on the
  // site keeps the full frame-ancestors 'self' lockdown from #621.
  if (url.pathname === '/api/agent/tasks_widget') {
    newHeaders.set('Content-Security-Policy', "frame-ancestors 'self' http://10.1.0.40:8123")
    newHeaders.delete('X-Frame-Options')
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders,
    })
  }

  // Critical Security Headers
  newHeaders.set('X-Frame-Options', 'SAMEORIGIN')
  newHeaders.set('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com https://www.google-analytics.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https: blob:; connect-src 'self' https://funk.frawo-tech.de http://10.1.0.38:8000 http://10.1.0.38 https://www.google-analytics.com; frame-ancestors 'self'; base-uri 'self'; form-action 'self'")
  newHeaders.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
  newHeaders.set('X-Content-Type-Options', 'nosniff')
  newHeaders.set('X-XSS-Protection', '1; mode=block')
  newHeaders.set('Referrer-Policy', 'strict-origin-when-cross-origin')
  newHeaders.set('Permissions-Policy', 'geolocation=(), microphone=(), camera=(), payment=()')

  // Remove information disclosure headers
  newHeaders.delete('Server')
  newHeaders.delete('X-Powered-By')

  // Return modified response
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders
  })
}
