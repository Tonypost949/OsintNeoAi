#!/usr/bin/env python3
"""
Integration Manager - Unified interface for all integrated OSINT tools
======================================================================
"""

import json
import os
from typing import Dict, List
from pathlib import Path
import importlib.util

class OSINTIntegrationManager:
    """Manages all integrated OSINT tools."""
    
    def __init__(self, aggregation_report_path: str = './osint_aggregated/aggregation_report.json'):
        self.report_path = aggregation_report_path
        self.tools = {}
        self.apis = set()
        self.capabilities = {}
        
        if os.path.exists(aggregation_report_path):
            self.load_report()
    
    def load_report(self):
        """Load aggregation report."""
        try:
            with open(self.report_path, 'r') as f:
                report = json.load(f)
            
            for cap in report.get('capabilities', []):
                self.tools[cap['repo_name']] = cap
                self.apis.update(cap.get('api_integrations', []))
                self.capabilities[cap['repo_name']] = cap
            
            print(f"✅ Loaded {len(self.tools)} tools")
            print(f"✅ Loaded {len(self.apis)} unique APIs")
        
        except Exception as e:
            print(f"❌ Error loading report: {e}")
    
    def list_tools(self) -> List[str]:
        """List all integrated tools."""
        return list(self.tools.keys())
    
    def list_apis(self) -> List[str]:
        """List all integrated APIs."""
        return sorted(list(self.apis))
    
    def get_tool_info(self, tool_name: str) -> Dict:
        """Get detailed info about a tool."""
        return self.tools.get(tool_name, {})
    
    def get_tools_by_api(self, api_name: str) -> List[str]:
        """Get tools that use a specific API."""
        return [name for name, tool in self.tools.items() 
                if api_name in tool.get('api_integrations', [])]
    
    def generate_integration_summary(self) -> str:
        """Generate human-readable integration summary."""
        summary = []
        summary.append("\n" + "="*80)
        summary.append("📊 OSINT INTEGRATION SUMMARY")
        summary.append("="*80)
        
        summary.append(f"\n🔧 Total Tools Integrated: {len(self.tools)}")
        for tool_name in self.list_tools():
            tool = self.tools[tool_name]
            summary.append(f"\n  📦 {tool_name}")
            summary.append(f"     Python Tools: {len(tool.get('python_tools', []))}")
            summary.append(f"     APIs: {', '.join(tool.get('api_integrations', [])) or 'None'}")
        
        summary.append(f"\n🌐 Integrated APIs ({len(self.apis)} total):")
        for api in self.list_apis():
            tools = self.get_tools_by_api(api)
            summary.append(f"  - {api} ({len(tools)} tools)")
        
        summary.append("\n" + "="*80)
        return "\n".join(summary)

if __name__ == '__main__':
    manager = OSINTIntegrationManager()
    print(manager.generate_integration_summary())
