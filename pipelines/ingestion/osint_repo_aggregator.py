#!/usr/bin/env python3
"""
OSINT Repository Aggregator & Auto-Integrator
==============================================
Automatically discovers, clones, and integrates OSINT tools from GitHub.
Scans user repositories and public OSINT repos, extracts capabilities, and integrates them.
"""

import os
import json
import subprocess
import requests
from typing import Dict, List, Optional
from pathlib import Path
import shutil
from datetime import datetime

class GitHubOSINTAggregator:
    """Automatically discovers and integrates OSINT repositories."""
    
    def __init__(self, github_user: str, github_token: Optional[str] = None):
        self.github_user = github_user
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.api_base = 'https://api.github.com'
        self.headers = {}
        
        if self.github_token:
            self.headers['Authorization'] = f'token {self.github_token}'
            self.headers['Accept'] = 'application/vnd.github.v3+json'
        
        self.discovered_repos = []
        self.integrated_tools = []
        self.osint_keywords = [
            'osint', 'intelligence', 'reconnaissance', 'investigation',
            'data-extraction', 'web-scraping', 'api-integration',
            'network-analysis', 'threat-intelligence', 'breach',
            'people-search', 'domain-lookup', 'ip-lookup', 'email-search',
            'social-media', 'dark-web', 'dark-web-monitoring',
            'maltego', 'shodan', 'censys', 'github-osint'
        ]
    
    def discover_user_repos(self) -> List[Dict]:
        """Get all repositories for the user."""
        print(f"\n🔍 Discovering repositories for user: {self.github_user}")
        
        repos = []
        url = f"{self.api_base}/users/{self.github_user}/repos"
        
        try:
            response = requests.get(url, headers=self.headers, params={'per_page': 100})
            response.raise_for_status()
            
            for repo in response.json():
                repos.append({
                    'name': repo['name'],
                    'url': repo['clone_url'],
                    'ssh_url': repo['ssh_url'],
                    'description': repo['description'] or '',
                    'language': repo['language'],
                    'topics': repo.get('topics', []),
                    'stars': repo['stargazers_count'],
                    'is_osint': self._is_osint_repo(repo)
                })
            
            print(f"✅ Found {len(repos)} repositories")
            self.discovered_repos = repos
            return repos
        
        except Exception as e:
            print(f"❌ Error discovering repos: {e}")
            return []
    
    def discover_public_osint_repos(self, limit: int = 50) -> List[Dict]:
        """Discover popular public OSINT repositories."""
        print(f"\n🌐 Discovering public OSINT repositories...")
        
        osint_repos = []
        
        # Search for OSINT repositories
        search_queries = [
            'language:python osint stars:>100',
            'language:python intelligence reconnaissance stars:>50',
            'topic:osint stars:>100',
            'user:Tonypost949 osint'
        ]
        
        for query in search_queries:
            url = f"{self.api_base}/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 20
            }
            
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                for repo in response.json().get('items', []):
                    repo_data = {
                        'name': repo['name'],
                        'owner': repo['owner']['login'],
                        'url': repo['clone_url'],
                        'description': repo['description'] or '',
                        'language': repo['language'],
                        'stars': repo['stargazers_count'],
                        'topics': repo.get('topics', [])
                    }
                    
                    # Avoid duplicates
                    if repo_data not in osint_repos:
                        osint_repos.append(repo_data)
                        if len(osint_repos) >= limit:
                            break
            
            except Exception as e:
                print(f"⚠️  Error in search query: {e}")
                continue
            
            if len(osint_repos) >= limit:
                break
        
        print(f"✅ Found {len(osint_repos)} public OSINT repositories")
        return osint_repos[:limit]
    
    def _is_osint_repo(self, repo: Dict) -> bool:
        """Check if repository is OSINT-related."""
        text = (repo['name'] + ' ' + (repo['description'] or '') + ' ' + 
                ' '.join(repo.get('topics', []))).lower()
        
        return any(keyword in text for keyword in self.osint_keywords)
    
    def clone_repo(self, repo_url: str, target_dir: str) -> bool:
        """Clone a repository."""
        try:
            print(f"  📥 Cloning {repo_url}...")
            subprocess.run(['git', 'clone', repo_url, target_dir], 
                         check=True, capture_output=True, timeout=60)
            print(f"  ✅ Cloned to {target_dir}")
            return True
        except Exception as e:
            print(f"  ❌ Clone failed: {e}")
            return False
    
    def extract_python_functions(self, repo_dir: str) -> List[Dict]:
        """Extract Python functions and classes from repository."""
        functions = []
        
        try:
            import ast
            
            for root, dirs, files in os.walk(repo_dir):
                # Skip common non-source directories
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']]
                
                for file in files:
                    if file.endswith('.py'):
                        filepath = os.path.join(root, file)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                tree = ast.parse(f.read())
                            
                            for node in ast.walk(tree):
                                if isinstance(node, ast.FunctionDef):
                                    functions.append({
                                        'type': 'function',
                                        'name': node.name,
                                        'file': filepath.replace(repo_dir, ''),
                                        'docstring': ast.get_docstring(node) or ''
                                    })
                                elif isinstance(node, ast.ClassDef):
                                    functions.append({
                                        'type': 'class',
                                        'name': node.name,
                                        'file': filepath.replace(repo_dir, ''),
                                        'docstring': ast.get_docstring(node) or ''
                                    })
                        except Exception as e:
                            continue
        
        except Exception as e:
            print(f"  ⚠️  Could not extract functions: {e}")
        
        return functions
    
    def extract_capabilities(self, repo_dir: str, repo_name: str) -> Dict:
        """Extract capabilities from repository."""
        capabilities = {
            'repo_name': repo_name,
            'directory': repo_dir,
            'extracted_at': datetime.now().isoformat(),
            'python_tools': [],
            'scripts': [],
            'requirements': [],
            'readme': '',
            'api_integrations': []
        }
        
        # Extract Python functions
        capabilities['python_tools'] = self.extract_python_functions(repo_dir)
        
        # Find executable scripts
        for root, dirs, files in os.walk(repo_dir):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__']]
            for file in files:
                if file.endswith('.py') and any(file.startswith(prefix) for prefix in ['osint', 'tool', 'main', 'cli', 'app']):
                    capabilities['scripts'].append(os.path.join(root, file))
        
        # Extract requirements
        req_file = os.path.join(repo_dir, 'requirements.txt')
        if os.path.exists(req_file):
            try:
                with open(req_file, 'r') as f:
                    capabilities['requirements'] = [line.strip() for line in f if line.strip()]
            except:
                pass
        
        # Extract README
        readme_file = os.path.join(repo_dir, 'README.md')
        if os.path.exists(readme_file):
            try:
                with open(readme_file, 'r', encoding='utf-8') as f:
                    capabilities['readme'] = f.read()[:1000]  # First 1000 chars
            except:
                pass
        
        # Detect API integrations
        capabilities['api_integrations'] = self._detect_api_integrations(repo_dir)
        
        return capabilities
    
    def _detect_api_integrations(self, repo_dir: str) -> List[str]:
        """Detect which APIs/services are integrated."""
        integrations = set()
        
        api_keywords = {
            'twitter': ['twitter', 'tweepy', 'api.twitter'],
            'github': ['github', 'pygithub', 'api.github'],
            'linkedin': ['linkedin', 'selenium'],
            'facebook': ['facebook', 'fbapiv'],
            'instagram': ['instagram', 'instagrapi'],
            'reddit': ['reddit', 'praw'],
            'shodan': ['shodan'],
            'censys': ['censys'],
            'whois': ['whois', 'whoisxmlapi'],
            'dns': ['dns', 'dnsdb', 'passive'],
            'hibp': ['haveibeenpwned', 'breach'],
            'hunter': ['hunter.io', 'email-finder'],
            'clearbit': ['clearbit'],
            'stripe': ['stripe'],
            'google': ['google api', 'google maps'],
            'selenium': ['selenium', 'webdriver'],
        }
        
        for root, dirs, files in os.walk(repo_dir):
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__']]
            
            for file in files:
                if file.endswith(('.py', '.txt', '.md', '.json')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                        
                        for api, keywords in api_keywords.items():
                            if any(kw in content for kw in keywords):
                                integrations.add(api)
                    except:
                        continue
        
        return sorted(list(integrations))
    
    def create_integration_wrapper(self, capabilities: Dict, output_dir: str) -> str:
        """Create a Python wrapper for integrating the tool."""
        
        wrapper_code = f'''#!/usr/bin/env python3
"""
Auto-generated wrapper for: {capabilities['repo_name']}
Generated: {datetime.now().isoformat()}
"""

import sys
import os

# Add repository to path
REPO_DIR = r"{capabilities['directory']}"
sys.path.insert(0, REPO_DIR)

class {capabilities['repo_name'].replace('-', '_').title().replace('_', '')}Wrapper:
    """Wrapper for {capabilities['repo_name']} OSINT tool."""
    
    def __init__(self):
        self.repo_name = "{capabilities['repo_name']}"
        self.capabilities = {json.dumps(capabilities, indent=2)}
        self.python_tools = {len(capabilities.get('python_tools', []))}
        self.api_integrations = {capabilities.get('api_integrations', [])}
    
    def get_capabilities(self):
        """Get available capabilities."""
        return self.capabilities
    
    def list_tools(self):
        """List available Python tools."""
        return self.capabilities.get('python_tools', [])

if __name__ == '__main__':
    wrapper = {capabilities['repo_name'].replace('-', '_').title().replace('_', '')}Wrapper()
    print(f"✅ {{wrapper.repo_name}} integrated successfully")
    print(f"   Tools: {{wrapper.python_tools}}")
    print(f"   APIs: {{', '.join(wrapper.api_integrations)}}")
'''
        
        output_path = os.path.join(output_dir, f"{capabilities['repo_name']}_wrapper.py")
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(wrapper_code)
            print(f"✅ Created wrapper: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ Error creating wrapper: {e}")
            return None
    
    def aggregate_all(self, output_dir: str = './osint_aggregated') -> Dict:
        """Run complete aggregation workflow."""
        
        print("\n" + "="*80)
        print("🔧 OSINT REPOSITORY AGGREGATOR")
        print("="*80)
        
        os.makedirs(output_dir, exist_ok=True)
        
        all_capabilities = []
        
        # Step 1: Discover user repos
        user_repos = self.discover_user_repos()
        user_osint_repos = [r for r in user_repos if r['is_osint']]
        
        print(f"\n📦 User OSINT repositories: {len(user_osint_repos)}")
        for repo in user_osint_repos[:5]:
            print(f"   - {repo['name']}: {repo['description'][:50]}...")
        
        # Step 2: Discover public repos
        public_repos = self.discover_public_osint_repos(limit=10)
        
        print(f"\n🌐 Public OSINT repositories: {len(public_repos)}")
        for repo in public_repos[:5]:
            print(f"   - {repo['name']} by {repo['owner']}: {repo['stars']} ⭐")
        
        # Step 3: Process repositories
        print(f"\n🔄 Processing repositories...")
        repos_to_process = user_osint_repos[:3] + public_repos[:2]  # Limit for demo
        
        for idx, repo in enumerate(repos_to_process, 1):
            print(f"\n[{idx}/{len(repos_to_process)}] Processing: {repo['name']}")
            
            repo_dir = os.path.join(output_dir, 'repos', repo['name'].replace('/', '_'))
            
            # Clone if from public repos or if not already in user repos
            if 'owner' in repo:  # Public repo
                if self.clone_repo(repo['url'], repo_dir):
                    # Extract capabilities
                    caps = self.extract_capabilities(repo_dir, repo['name'])
                    all_capabilities.append(caps)
                    
                    # Create wrapper
                    self.create_integration_wrapper(caps, output_dir)
        
        # Step 4: Generate aggregation report
        report = {
            'generated_at': datetime.now().isoformat(),
            'user': self.github_user,
            'user_repos_total': len(user_repos),
            'user_osint_repos': len(user_osint_repos),
            'public_osint_discovered': len(public_repos),
            'repos_processed': len(all_capabilities),
            'capabilities': all_capabilities,
            'integration_summary': {
                'total_python_tools': sum(len(c.get('python_tools', [])) for c in all_capabilities),
                'total_api_integrations': len(set(api for c in all_capabilities for api in c.get('api_integrations', []))),
                'unique_apis': sorted(set(api for c in all_capabilities for api in c.get('api_integrations', [])))
            }
        }
        
        # Save report
        report_path = os.path.join(output_dir, 'aggregation_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n" + "="*80)
        print(f"✅ AGGREGATION COMPLETE")
        print(f"="*80)
        print(f"\n📊 Summary:")
        print(f"   User repos scanned: {report['user_repos_total']}")
        print(f"   User OSINT repos: {report['user_osint_repos']}")
        print(f"   Public OSINT repos discovered: {report['public_osint_discovered']}")
        print(f"   Repos processed: {report['repos_processed']}")
        print(f"   Python tools extracted: {report['integration_summary']['total_python_tools']}")
        print(f"   Unique APIs found: {report['integration_summary']['total_api_integrations']}")
        print(f"\n📁 Output directory: {output_dir}")
        print(f"📄 Report: {report_path}")
        print(f"\n🔗 Integrated APIs:")
        for api in report['integration_summary']['unique_apis'][:10]:
            print(f"   - {api}")
        
        return report

if __name__ == '__main__':
    import sys
    
    github_user = sys.argv[1] if len(sys.argv) > 1 else 'Tonypost949'
    
    aggregator = GitHubOSINTAggregator(github_user)
    result = aggregator.aggregate_all()
