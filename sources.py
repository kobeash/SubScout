import requests
from utils import normalize_subdomain
from concurrent.futures import ThreadPoolExecutor

def from_crtsh(domain: str) -> set:
    """
    Get subdomains from crt.sh (certificate transparency logs).
    """
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        subs = {normalize_subdomain(x["name_value"]) for x in data}
        return {s for s in subs if s.endswith(domain)}
    except Exception:
        return set()

def from_otx(domain: str) -> set:
    """
    Get subdomains from AlienVault OTX.
    """
    url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        subs = {normalize_subdomain(entry["hostname"]) for entry in data.get("passive_dns", [])}
        return {s for s in subs if s and s.endswith(domain)}
    except Exception:
        return set()

def from_rapiddns(domain: str) -> set:
    """
    Get subdomains from RapidDNS.
    """
    url = f"https://rapiddns.io/subdomain/{domain}?full=1#result"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        subs = set()
        for line in r.text.splitlines():
            if domain in line and "<td>" in line:
                part = line.split("<td>")[1].split("</td>")[0]
                subs.add(normalize_subdomain(part))
        return {s for s in subs if s and s.endswith(domain)}
    except Exception:
        return set()

def gather_subdomains(domain: str) -> list:
    """
    Aggregate from multiple sources and return a unique list.
    """
    sources = [from_crtsh, from_otx, from_rapiddns]
    all_subs = set()

    with ThreadPoolExecutor(max_workers=len(sources)) as executor:
        futures = [executor.submit(src, domain) for src in sources]
        for f in futures:
            all_subs |= f.result()

    return sorted(all_subs)
