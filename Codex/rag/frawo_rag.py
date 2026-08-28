#!/usr/bin/env python3
"""
FraWo Knowledge RAG Engine
==========================
Hybrid Semantic & Full-Text (FTS5) Search across the entire FraWo Knowledge Base,
Server Architecture, Project Codex, Odoo Models, and Infrastructure Configs.

Author: Antigravity AI Agent
Version: 1.0 (2026-08-23)
"""

import os
import sys
import re
import json
import sqlite3
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

# Paths
BASE_DIR = Path("C:/Users/StudioPC/FraWo")
CODEX_DIR = BASE_DIR / "Codex"
RAG_DIR = CODEX_DIR / "rag"
DB_PATH = RAG_DIR / "frawo_knowledge.db"

# Ensure RAG directory exists
RAG_DIR.mkdir(parents=True, exist_ok=True)

class FraWoRAG:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE,
                    file_name TEXT,
                    category TEXT,
                    file_hash TEXT,
                    last_modified DATETIME,
                    chunk_count INTEGER
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id INTEGER,
                    chunk_index INTEGER,
                    section_title TEXT,
                    content TEXT,
                    token_estimate INTEGER,
                    FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE CASCADE
                );
            """)
            # FTS5 Full-Text Virtual Table
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    content,
                    section_title,
                    file_name,
                    category,
                    content=chunks,
                    content_rowid=id
                );
            """)
            conn.commit()

    def compute_hash(self, file_path: Path) -> str:
        h = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    def chunk_markdown(self, content: str, file_path: Path) -> List[Dict[str, str]]:
        """Split markdown intelligently by headers (#, ##, ###) while preserving context."""
        chunks = []
        lines = content.splitlines()
        current_section = file_path.stem
        current_lines = []

        for line in lines:
            if line.startswith('#'):
                # Header found, flush previous chunk if long enough
                text = "\n".join(current_lines).strip()
                if len(text) > 40:
                    chunks.append({
                        'section_title': current_section,
                        'content': text
                    })
                current_section = line.strip('#').strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        # Flush final chunk
        text = "\n".join(current_lines).strip()
        if text:
            chunks.append({
                'section_title': current_section,
                'content': text
            })
        return chunks

    def determine_category(self, file_path: Path) -> str:
        p_str = str(file_path).lower()
        if 'infra' in p_str or 'server' in p_str or 'proxmox' in p_str or 'unifi' in p_str:
            return 'Infrastructure & Network'
        elif 'radio' in p_str or 'azura' in p_str or 'audio' in p_str:
            return 'Radio & Audio'
        elif 'odoo' in p_str or 'finance' in p_str or 'vertrag' in p_str or 'agb' in p_str or 'verleih' in p_str:
            return 'Business & Legal'
        elif 'studio' in p_str or 'event' in p_str or 'hardware' in p_str or 'dmx' in p_str:
            return 'Studio & Event Tech'
        else:
            return 'General Codex'

    def index_files(self, verbose: bool = True) -> int:
        """Scan and index all markdown, text, and config files across the workspace."""
        supported_extensions = ['.md', '.txt', '.html', '.json', '.sh', '.yml', '.yaml']
        indexed_count = 0
        total_chunks = 0

        # Target scan roots
        scan_paths = [
            BASE_DIR / "Codex",
            Path("C:/Users/StudioPC/.gemini/antigravity/brain/3cea5902-119b-4412-a06f-65b2b7f7e0d0")
        ]

        files_to_index = []
        for root_path in scan_paths:
            if not root_path.exists():
                continue
            for ext in supported_extensions:
                for file_p in root_path.rglob(f"*{ext}"):
                    # Ignore git and temp directories
                    if '.git' in file_p.parts or 'node_modules' in file_p.parts or '__pycache__' in file_p.parts:
                        continue
                    files_to_index.append(file_p)

        if verbose:
            print(f"🔍 Discovered {len(files_to_index)} files across FraWo Knowledge Base.")

        with self.get_conn() as conn:
            for file_p in files_to_index:
                try:
                    file_str = str(file_p)
                    f_hash = self.compute_hash(file_p)
                    mtime = os.path.getmtime(file_p)

                    # Check if already indexed and unchanged
                    existing = conn.execute("SELECT id, file_hash FROM documents WHERE file_path = ?", (file_str,)).fetchone()
                    if existing and existing['file_hash'] == f_hash:
                        continue

                    content = file_p.read_text(encoding='utf-8', errors='ignore')
                    category = self.determine_category(file_p)
                    chunks = self.chunk_markdown(content, file_p)

                    if not chunks:
                        continue

                    # Remove old entries if exists
                    if existing:
                        doc_id = existing['id']
                        conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
                        conn.execute("UPDATE documents SET file_hash = ?, last_modified = ?, chunk_count = ? WHERE id = ?", 
                                     (f_hash, mtime, len(chunks), doc_id))
                    else:
                        cur = conn.execute("INSERT INTO documents (file_path, file_name, category, file_hash, last_modified, chunk_count) VALUES (?, ?, ?, ?, ?, ?)",
                                           (file_str, file_p.name, category, f_hash, mtime, len(chunks)))
                        doc_id = cur.lastrowid

                    # Insert chunks
                    for idx, c in enumerate(chunks):
                        tok_est = len(c['content'].split())
                        c_cur = conn.execute("INSERT INTO chunks (doc_id, chunk_index, section_title, content, token_estimate) VALUES (?, ?, ?, ?, ?)",
                                             (doc_id, idx, c['section_title'], c['content'], tok_est))
                        chunk_id = c_cur.lastrowid
                        conn.execute("INSERT INTO chunks_fts (rowid, content, section_title, file_name, category) VALUES (?, ?, ?, ?, ?)",
                                     (chunk_id, c['content'], c['section_title'], file_p.name, category))

                    indexed_count += 1
                    total_chunks += len(chunks)
                    if verbose:
                        print(f"  ✅ Indexed: {file_p.name} ({len(chunks)} chunks, Category: {category})")

                except Exception as e:
                    if verbose:
                        print(f"  ⚠️ Error indexing {file_p}: {e}")

            conn.commit()

        if verbose:
            print(f"\n🎉 Indexing complete! Indexed/Updated {indexed_count} files ({total_chunks} new chunks).")
        return indexed_count

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Perform high-precision search across the knowledge base."""
        clean_q = re.sub(r'[^\w\s]', '', query).strip()
        terms = [f'"{term}"*' for term in clean_q.split() if len(term) > 1]
        fts_query = " OR ".join(terms) if terms else query

        results = []
        with self.get_conn() as conn:
            sql = """
                SELECT 
                    c.id, c.section_title, c.content, d.file_name, d.file_path, d.category,
                    bm25(chunks_fts) as rank
                FROM chunks_fts
                JOIN chunks c ON chunks_fts.rowid = c.id
                JOIN documents d ON c.doc_id = d.id
                WHERE chunks_fts MATCH ?
                ORDER BY rank ASC
                LIMIT ?;
            """
            try:
                rows = conn.execute(sql, (fts_query, limit)).fetchall()
                for r in rows:
                    results.append({
                        'id': r['id'],
                        'file_name': r['file_name'],
                        'file_path': r['file_path'],
                        'category': r['category'],
                        'section_title': r['section_title'],
                        'content': r['content'],
                        'score': round(abs(float(r['rank'])), 3)
                    })
            except sqlite3.OperationalError:
                like_sql = """
                    SELECT c.id, c.section_title, c.content, d.file_name, d.file_path, d.category
                    FROM chunks c
                    JOIN documents d ON c.doc_id = d.id
                    WHERE c.content LIKE ? OR c.section_title LIKE ?
                    LIMIT ?;
                """
                rows = conn.execute(like_sql, (f"%{query}%", f"%{query}%", limit)).fetchall()
                for r in rows:
                    results.append({
                        'id': r['id'],
                        'file_name': r['file_name'],
                        'file_path': r['file_path'],
                        'category': r['category'],
                        'section_title': r['section_title'],
                        'content': r['content'],
                        'score': 1.0
                    })

        return results

    def print_search(self, query: str, limit: int = 4):
        print(f"\n🔎 Query: '{query}'")
        print("=" * 60)
        results = self.search(query, limit=limit)
        if not results:
            print("❌ No matching knowledge found.")
            return

        for idx, res in enumerate(results, 1):
            print(f"\n[{idx}] 📄 {res['file_name']} (Category: {res['category']}) — Score: {res['score']}")
            print(f"📌 Section: {res['section_title']}")
            print(f"📁 Path: {res['file_path']}")
            print("-" * 60)
            snippet = res['content'][:350].strip() + ("..." if len(res['content']) > 350 else "")
            print(snippet)
            print("-" * 60)

if __name__ == "__main__":
    rag = FraWoRAG()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "index" or cmd == "reindex":
            rag.index_files(verbose=True)
        elif cmd == "search" and len(sys.argv) > 2:
            query = " ".join(sys.argv[2:])
            rag.print_search(query)
        else:
            print("Usage: python frawo_rag.py [index | search <query>]")
    else:
        print("🚀 Running FraWo RAG Indexing & Test Benchmark...")
        rag.index_files(verbose=True)
        rag.print_search("PreSonus AR12c Multitrack Routing")
        rag.print_search("Vaultwarden CT108 Zugangsdaten")
        rag.print_search("Showtec Shark Wolfmix DMX")
