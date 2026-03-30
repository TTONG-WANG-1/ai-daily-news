#!/usr/bin/env python3
"""Fix news links for direct jump and mobile compatibility"""

from pathlib import Path

HTML_FILE = Path('/home/wangtong/openclaw/workspace/ai-daily-news/index.html')
content = HTML_FILE.read_text(encoding='utf-8')

# Fix 1: Remove &btnI=1 which can cause intermediate pages
content = content.replace('&btnI=1', '')

# Fix 2: Add rel="noopener noreferrer" for security and mobile compatibility
content = content.replace('target="_blank"', 'target="_blank" rel="noopener noreferrer"')

HTML_FILE.write_text(content, encoding='utf-8')
print("✅ Links fixed!")
print("   - Removed &btnI=1 parameter")
print("   - Added rel='noopener noreferrer'")
