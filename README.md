# SubScout — Subdomain Discovery & Port Verification

> Goal: Find subdomains of a target domain from the open internet (passive & active), verify which are alive, and present a human-friendly report. Fast by default, configurable when you need depth.

## Features
- Passive subdomain discovery from multiple sources (crt.sh, OTX, BufferOver, Riddler, RapidDNS, Chaos, etc.) with per-source toggles & rate limiting.
- Active discovery (optional): DNS bruteforce with wordlists (SecLists compatible) + permutations (dnsgen-style) with wildcard filtering.
- Alive checks:
  - Ping-only (ICMP where permitted; TCP/HTTP fallback when ICMP blocked)
  - Port scan presets: top10, top100, or custom list (--ports 80,443,8080,8443)
  - Async TCP connect scan with timeouts, optional lightweight HTTP(S) service/banner grabs
- Human-friendly output: rich, colorized CLI tables with ✅/⚠️/❌, plus HTML, CSV, JSON export
- Respectful & robust: concurrency controls, jittered requests, caching & resume, retries with exponential backoff
- Actionable insights: HTTP title/status, TLS CN/issuer/expiry, CDN/WAF hints, potential subdomain takeover signals
- Pluggable architecture: add new sources or custom checks easily

> Legal/Ethics: Only scan assets you own or have explicit permission.

## Quick Start
```
cd /SubScout
pip install -r requirements.txt


python subscout acme.com --mode ping
python subscout acme.com --mode top10
python subscout acme.com --mode top100 --html dist/acme.html --csv dist/acme.csv --json dist/acme.json
python subscout acme.com --ports 80,443,8080,8443 --concurrency 300 --timeout 2.0
python subscout acme.com --mode top10 --resume
```

## How it Works
1. Collect: parallel queries to passive sources; results deduplicated & normalized
2. Vet: DNS resolve candidates using a resolver pool; wildcard detection avoids false positives
3. Verify: ICMP ping (or TCP/HTTP fallback) and/or TCP connect scans
4. Enrich: TLS cert metadata, CDN/WAF heuristics, dangling CNAME checks
5. Report: terminal table + HTML/CSV/JSON export (HTML searchable/sortable)

## CLI Options
```
--mode [ping|top10|top100]
--ports TEXT
--sources TEXT
--bruteforce PATH
--permutations
--resolvers PATH
--concurrency INTEGER
--timeout FLOAT
--retries INTEGER
--user-agent TEXT
--proxy TEXT
--html PATH
--csv PATH
--json PATH
--resume
--no-color
-v, --verbose
--help
```

## Output Schema (JSON)
```
{
  "domain": "acme.com",
  "generated_at": "2025-08-14T03:21:00Z",
  "ports_profile": "top100",
  "subdomains": [
    {
      "name": "api.acme.com",
      "a_records": ["203.0.113.10"],
      "aaaa_records": [],
      "cname": "api.acme.com.cdnprovider.net.",
      "wildcard": false,
      "alive": true,
      "checks": {
        "icmp": "filtered",
        "tcp": {"443": "open", "80": "closed"}
      },
      "http": {
        "scheme": "https",
        "status": 200,
        "title": "ACME API",
        "server": "nginx",
        "tls": {"cn": "api.acme.com", "issuer": "Let's Encrypt", "not_after": "2026-01-02"}
      },
      "notes": ["cdn", "https"]
    }
  ]
}
```

## Performance Notes
- Async I/O (asyncio, httpx, TCP sockets) with configurable semaphore
- DNS: dnspython or aiodns; supports DoH and resolver pools
- Rate limits + jittered requests for politeness
- Caching (SQLite/JSONL) enables resume; TTL-based per-subdomain results

## Port Presets

### Top 10
| Port | Service | Description |
|------|---------|-------------|
| 80   | HTTP      | Web server |
| 443  | HTTPS     | HTTP over TLS |
| 22   | SSH       | Secure Shell |
| 21   | FTP       | File Transfer Protocol |
| 25   | SMTP      | Mail Transfer |
| 53   | DNS       | Domain Name System |
| 445  | SMB       | Microsoft-DS/SMB |
| 3389 | RDP       | Remote Desktop Protocol |
| 3306 | MySQL     | MySQL database |
| 8080 | HTTP-Proxy| HTTP proxy / alt |

### Top 100
Full curated list included in repo; covers common web, infra, and admin services.

## Additional Features / Roadmap
- Subdomain takeover detection (dangling CNAMEs)
- Screenshots of HTTP(S) services (Playwright)
- WAF/CDN detection
- Service & tech fingerprints
- TLS analysis & expiry alerts
- CI/CD integration (JUnit XML), Slack/Teams notifications
- IPv6 & proxy/Tor support
- Docker image / PyInstaller binaries

## Notes on ICMP vs TCP "Ping"
- ICMP often blocked; SubScout tries ICMP first, then TCP connect (common web ports) to infer liveness
- --http-probe optionally checks HEAD / for title/status

## Responsible Use
- Default concurrency/timeouts are conservative
- Honor robots.txt for passive scraping
- Include contact info in UA string when scanning your org

## Acknowledgements
SecLists, OWASP Amass, ProjectDiscovery ecosystem, and open datasets.
