#!/usr/bin/env python3
"""
scripts/business/import_bank_csv.py — Universal Bank Statement CSV Importer for FraWo Odoo

Imports bank transactions (Qonto, N26, or generic CSV) directly into
Odoo's `account.bank.statement.line` with automatic deduplication.

Usage:
    python import_bank_csv.py --file /path/to/statement.csv --journal qonto [--dry-run]
    python import_bank_csv.py --file /path/to/n26.csv --journal n26 [--since 2026-04-01]

Journals:
    - qonto: Journal #13 (Qonto — FraWo GbR Hauptkonto)
    - n26:   Journal #11 (N26 — FraWo Space (Wolf))
    - or specify journal ID directly (e.g. --journal 13)
"""

import sys
import os
import csv
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from mcp_odoo_pro_server import odoo_execute

JOURNAL_MAP = {
    'qonto': 13,
    'n26': 11,
}

def parse_amount(val_str):
    if val_str is None:
        return 0.0
    val_str = str(val_str).strip().replace('€', '').replace('EUR', '').replace(' ', '')
    # Handle German format: 1.234,56 or 1234,56
    if ',' in val_str and '.' in val_str:
        if val_str.rfind(',') > val_str.rfind('.'):
            # German 1.234,56 -> 1234.56
            val_str = val_str.replace('.', '').replace(',', '.')
        else:
            # English 1,234.56 -> 1234.56
            val_str = val_str.replace(',', '')
    elif ',' in val_str:
        val_str = val_str.replace(',', '.')
    return float(val_str)

def parse_date(date_str):
    date_str = str(date_str).strip()[:10]
    for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            pass
    raise ValueError(f"Unknown date format: {date_str}")

def detect_and_parse_csv(filepath):
    """Detect delimiter and parse CSV into normalized rows."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        sample = f.read(4096)
        delimiter = ';' if ';' in sample and sample.count(';') > sample.count(',') else ','
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)
        if not rows:
            return []
        
        headers = [h.strip() for h in rows[0].keys() if h]
        normalized = []
        for r in rows:
            row_clean = {k.strip().lower(): v.strip() for k, v in r.items() if k}
            
            # Date
            raw_date = (
                row_clean.get('settled_at') or row_clean.get('settlement_date') or
                row_clean.get('datum') or row_clean.get('date') or
                row_clean.get('valutadatum') or row_clean.get('buchungstag')
            )
            if not raw_date:
                continue
            try:
                date_val = parse_date(raw_date)
            except Exception:
                continue

            # Amount
            raw_amount = (
                row_clean.get('amount') or row_clean.get('betrag') or
                row_clean.get('betrag (eur)') or row_clean.get('amount (eur)') or
                row_clean.get('total')
            )
            if not raw_amount:
                continue
            try:
                amount_val = parse_amount(raw_amount)
            except Exception:
                continue

            # Partner / Counterparty
            partner_name = (
                row_clean.get('counterparty_name') or row_clean.get('empfänger') or
                row_clean.get('empfaenger') or row_clean.get('payee') or
                row_clean.get('beguenstigter/zahlungspflichtiger') or
                row_clean.get('partner') or ''
            )

            # Payment Reference / Label
            payment_ref = (
                row_clean.get('note') or row_clean.get('details') or
                row_clean.get('verwendungszweck') or row_clean.get('payment reference') or
                row_clean.get('buchungstext') or row_clean.get('reference') or
                partner_name or 'Bankbewegung'
            )

            normalized.append({
                'date': date_val,
                'amount': amount_val,
                'partner_name': partner_name,
                'payment_ref': payment_ref
            })
            
        return normalized

def import_statement_lines(lines, journal_id, dry_run=False, since_date=None):
    """Import lines into Odoo with deduplication."""
    print(f"Connecting to Odoo for Journal #{journal_id}...")
    
    domain = [('journal_id', '=', journal_id)]
    if since_date:
        domain.append(('date', '>=', since_date))
        
    existing_recs = odoo_execute('account.bank.statement.line', 'search_read', [domain], {
        'fields': ['date', 'amount', 'payment_ref']
    })
    
    existing_set = set()
    for e in existing_recs:
        key = (e['date'], round(float(e['amount']), 2), (e.get('payment_ref') or '')[:20].strip().lower())
        existing_set.add(key)
        existing_set.add((e['date'], round(float(e['amount']), 2)))

    imported = 0
    skipped = 0

    for idx, line in enumerate(lines, 1):
        if since_date and line['date'] < since_date:
            continue
            
        amt_round = round(line['amount'], 2)
        key_full = (line['date'], amt_round, line['payment_ref'][:20].strip().lower())
        key_loose = (line['date'], amt_round)
        
        if key_full in existing_set or key_loose in existing_set:
            skipped += 1
            continue

        vals = {
            'journal_id': journal_id,
            'date': line['date'],
            'amount': line['amount'],
            'payment_ref': line['payment_ref'],
            'partner_name': line['partner_name']
        }

        if dry_run:
            print(f"[DRY-RUN] Would create: {line['date']} | {line['amount']:>9.2f} € | {line['partner_name'][:20]} | {line['payment_ref'][:40]}")
            imported += 1
        else:
            try:
                line_id = odoo_execute('account.bank.statement.line', 'create', [vals])
                print(f"[OK] #{line_id}: {line['date']} | {line['amount']:>9.2f} € | {line['payment_ref'][:35]}")
                existing_set.add(key_full)
                existing_set.add(key_loose)
                imported += 1
            except Exception as ex:
                print(f"[ERROR] Failed to import line {idx} ({line}): {ex}")

    print(f"\nResult: {imported} imported, {skipped} skipped as duplicates (Total processed: {len(lines)}).")
    return imported, skipped

def main():
    parser = argparse.ArgumentParser(description="Universal Bank Statement CSV Importer for FraWo")
    parser.add_argument('--file', '-f', required=True, help="Path to CSV file")
    parser.add_argument('--journal', '-j', required=True, help="Journal name ('qonto', 'n26') or ID")
    parser.add_argument('--since', help="Only import on or after date (YYYY-MM-DD)")
    parser.add_argument('--dry-run', action='store_true', help="Validate and preview without writing to Odoo")
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
        
    j_str = args.journal.lower()
    if j_str in JOURNAL_MAP:
        journal_id = JOURNAL_MAP[j_str]
    else:
        try:
            journal_id = int(args.journal)
        except ValueError:
            print(f"Error: Unknown journal '{args.journal}'. Use 'qonto', 'n26', or an integer ID.")
            sys.exit(1)

    print(f"Parsing CSV: {args.file} (Journal ID: {journal_id})...")
    lines = detect_and_parse_csv(args.file)
    print(f"Parsed {len(lines)} transaction rows.")
    
    if not lines:
        print("No valid rows found in CSV.")
        sys.exit(0)

    import_statement_lines(lines, journal_id, dry_run=args.dry_run, since_date=args.since)

if __name__ == '__main__':
    main()
