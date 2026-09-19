#!/usr/bin/env python3
"""
TabCopy Ingestion Tool
Processes tab lists pasted via Ctrl+Shift+X shortcut.
"""

import os
import json
import urllib.request
import datetime

def ingest_tabs(raw_text, session_name='tabcopy_session'):
    user_folder = r'C:\Amd949609_Antigravity_v1'
    output_dir = os.path.join(user_folder, 'tools', 'tabcopy', session_name)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f'Ingesting TabCopy payload into {output_dir}...')
    with open(os.path.join(output_dir, 'raw_payload.txt'), 'w', encoding='utf-8') as f:
        f.write(raw_text)
    
    print('TabCopy ingestion complete.')

if __name__ == '__main__':
    print('TabCopy AI Tool Registered & Active.')
