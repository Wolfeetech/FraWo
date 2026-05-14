#!/usr/bin/env python3
"""Test FraWo Website with Google PageSpeed Insights API"""
import requests
import json
import sys

# Google PageSpeed Insights API (no key needed for basic use)
API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
WEBSITE_URL = "https://www.frawo-tech.de/"

def test_pagespeed(strategy='mobile'):
    """Test website with PageSpeed Insights"""
    params = {
        'url': WEBSITE_URL,
        'strategy': strategy,  # 'mobile' or 'desktop'
        'category': ['performance', 'accessibility', 'best-practices', 'seo']
    }

    print(f"\n[*] Testing {strategy.upper()} performance...")

    try:
        response = requests.get(API_URL, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        # Extract scores
        lighthouse = data.get('lighthouseResult', {})
        categories = lighthouse.get('categories', {})

        print(f"\n{'='*50}")
        print(f"  {strategy.upper()} SCORES")
        print(f"{'='*50}")

        for category, details in categories.items():
            score = details.get('score', 0)
            title = details.get('title', category)
            score_pct = int(score * 100) if score else 0
            print(f"  {title:20s}: {score_pct:3d}/100")

        # Core Web Vitals
        audits = lighthouse.get('audits', {})

        print(f"\n{'='*50}")
        print(f"  CORE WEB VITALS")
        print(f"{'='*50}")

        # LCP (Largest Contentful Paint)
        lcp = audits.get('largest-contentful-paint', {})
        lcp_value = lcp.get('displayValue', 'N/A')
        print(f"  LCP (Largest Contentful Paint): {lcp_value}")

        # CLS (Cumulative Layout Shift)
        cls = audits.get('cumulative-layout-shift', {})
        cls_value = cls.get('displayValue', 'N/A')
        print(f"  CLS (Cumulative Layout Shift): {cls_value}")

        # FCP (First Contentful Paint)
        fcp = audits.get('first-contentful-paint', {})
        fcp_value = fcp.get('displayValue', 'N/A')
        print(f"  FCP (First Contentful Paint): {fcp_value}")

        # Speed Index
        si = audits.get('speed-index', {})
        si_value = si.get('displayValue', 'N/A')
        print(f"  Speed Index: {si_value}")

        # Top opportunities for improvement
        print(f"\n{'='*50}")
        print(f"  TOP OPPORTUNITIES")
        print(f"{'='*50}")

        opportunities = []
        for audit_id, audit_data in audits.items():
            if audit_data.get('score') and audit_data.get('score') < 1:
                if audit_data.get('details', {}).get('type') == 'opportunity':
                    savings = audit_data.get('details', {}).get('overallSavingsMs', 0)
                    if savings > 100:  # Only show if >100ms savings
                        opportunities.append({
                            'title': audit_data.get('title', audit_id),
                            'savings': savings,
                            'description': audit_data.get('description', '')
                        })

        # Sort by savings
        opportunities.sort(key=lambda x: x['savings'], reverse=True)

        for i, opp in enumerate(opportunities[:5], 1):
            print(f"\n  {i}. {opp['title']}")
            print(f"     Savings: {opp['savings']/1000:.1f}s")

        return True

    except requests.exceptions.RequestException as e:
        print(f"[FAIL] API request failed: {e}")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

if __name__ == '__main__':
    print(f"\n{'='*50}")
    print(f"  Google PageSpeed Insights Test")
    print(f"  {WEBSITE_URL}")
    print(f"{'='*50}")

    # Test both mobile and desktop
    test_pagespeed('mobile')
    print("\n" + "="*50 + "\n")
    test_pagespeed('desktop')

    print(f"\n{'='*50}")
    print(f"  Test Complete!")
    print(f"{'='*50}\n")
