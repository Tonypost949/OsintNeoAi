"""
DNS collector for OSINT Independent Platform.
Handles DNS queries, zone transfers, and DNS enumeration.
"""
import asyncio
import socket
from typing import Any, Dict, List, Optional, Set

import dns.asyncresolver
import dns.zone
import dns.query
import dns.rdatatype
import dns.exception

from .base import BaseCollector, CollectorResult, collector
from ..core.models import Entity, EntityType, Observation, Source, SourceType, ConfidenceLevel


@collector(
    name="dns",
    description="DNS intelligence collector - records, zone transfers, subdomain enumeration",
    supported_types=[EntityType.DOMAIN, EntityType.IP],
    rate_limit=100,
    timeout=10
)
class DNSCollector(BaseCollector):
    """DNS intelligence collector."""
    
    RECORD_TYPES = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA', 'PTR', 'CAA', 'SRV', 'DNSKEY', 'DS']
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.resolver = dns.asyncresolver.Resolver()
        self.resolver.timeout = self.timeout
        self.resolver.lifetime = self.timeout
        self.resolver.nameservers = ['8.8.8.8', '1.1.1.1', '9.9.9.9', '208.67.222.222']
    
    async def collect(self, target: str, **kwargs) -> CollectorResult:
        """Collect DNS intelligence on a target."""
        await self._wait_for_rate_limit()
        job = self._start_job(target, kwargs)
        result = CollectorResult()
        
        try:
            if self._is_domain(target):
                await self._collect_domain(target, result)
            elif self._is_ip(target):
                await self._collect_ip(target, result)
            else:
                result.errors.append(f"Unsupported target: {target}")
                
        except Exception as e:
            self.logger.error(f"DNS collection failed for {target}: {e}")
            result.errors.append(str(e))
        finally:
            self._complete_job(result)
        
        return result
    
    async def _collect_domain(self, domain: str, result: CollectorResult) -> None:
        """Collect DNS records for a domain."""
        # Create domain entity
        domain_entity = self._create_entity(
            EntityType.DOMAIN, domain,
            source_name="dns",
            source_type=SourceType.DNS,
            attributes={'collection_method': 'dns_enumeration'}
        )
        result.entities.append(domain_entity)
        
        # Query all record types
        for record_type in self.RECORD_TYPES:
            try:
                records = await self._query_record(domain, record_type)
                if records:
                    await self._process_records(domain, record_type, records, domain_entity.id, result)
            except Exception as e:
                self.logger.debug(f"Failed to query {record_type} for {domain}: {e}")
        
        # Attempt zone transfer
        await self._try_zone_transfer(domain, result)
        
        # Subdomain enumeration via common names
        await self._enumerate_subdomains(domain, result)
    
    async def _collect_ip(self, ip: str, result: CollectorResult) -> None:
        """Collect reverse DNS for an IP."""
        try:
            ptr_records = await self._query_reverse(ip)
            if ptr_records:
                for ptr in ptr_records:
                    domain_entity = self._create_entity(
                        EntityType.DOMAIN, ptr,
                        source_name="dns",
                        source_type=SourceType.DNS,
                        attributes={'ptr_for': ip, 'record_type': 'PTR'}
                    )
                    result.entities.append(domain_entity)
                    result.relationships.append({
                        'source_id': domain_entity.id,
                        'target': ip,
                        'relationship_type': 'resolves_to',
                        'description': f'{ptr} resolves to {ip}'
                    })
        except Exception as e:
            self.logger.debug(f"Reverse DNS failed for {ip}: {e}")
    
    async def _query_record(self, domain: str, record_type: str) -> List[dns.rrset.RRset]:
        """Query a specific DNS record type."""
        try:
            answer = await self.resolver.resolve(domain, record_type)
            return [answer]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            return []
        except Exception:
            return []
    
    async def _query_reverse(self, ip: str) -> List[str]:
        """Query PTR records for an IP."""
        try:
            rev_name = dns.reversename.from_address(ip)
            answer = await self.resolver.resolve(rev_name, 'PTR')
            return [str(r) for r in answer]
        except Exception:
            return []
    
    async def _process_records(self, domain: str, record_type: str, 
                               records: List[dns.rrset.RRset], 
                               source_entity_id: str, result: CollectorResult) -> None:
        """Process DNS records and create entities."""
        for rrset in records:
            for rdata in rrset:
                value = str(rdata).rstrip('.')
                
                if record_type in ('A', 'AAAA'):
                    # IP address
                    ip_entity = self._create_entity(
                        EntityType.IP, value,
                        source_name="dns",
                        source_type=SourceType.DNS,
                        attributes={
                            'record_type': record_type,
                            'domain': domain,
                            'ttl': rrset.ttl
                        }
                    )
                    result.entities.append(ip_entity)
                    result.relationships.append({
                        'source_id': source_entity_id,
                        'target_id': ip_entity.id,
                        'relationship_type': 'resolves_to',
                        'description': f'{domain} {record_type} {value}'
                    })
                
                elif record_type == 'CNAME':
                    cname_entity = self._create_entity(
                        EntityType.DOMAIN, value.rstrip('.'),
                        source_name="dns",
                        source_type=SourceType.DNS,
                        attributes={'record_type': 'CNAME', 'source_domain': domain, 'ttl': rrset.ttl}
                    )
                    result.entities.append(cname_entity)
                    result.relationships.append({
                        'source_id': source_entity_id,
                        'target_id': cname_entity.id,
                        'relationship_type': 'cname_to',
                        'description': f'{domain} CNAME {value}'
                    })
                
                elif record_type == 'MX':
                    mx_domain = value.split()[-1].rstrip('.')
                    mx_entity = self._create_entity(
                        EntityType.DOMAIN, mx_domain,
                        source_name="dns",
                        source_type=SourceType.DNS,
                        attributes={'record_type': 'MX', 'priority': value.split()[0], 'ttl': rrset.ttl}
                    )
                    result.entities.append(mx_entity)
                    result.relationships.append({
                        'source_id': source_entity_id,
                        'target_id': mx_entity.id,
                        'relationship_type': 'mx_for',
                        'description': f'{domain} MX {value}'
                    })
                
                elif record_type == 'NS':
                    ns_domain = value.rstrip('.')
                    ns_entity = self._create_entity(
                        EntityType.DOMAIN, ns_domain,
                        source_name="dns",
                        source_type=SourceType.DNS,
                        attributes={'record_type': 'NS', 'ttl': rrset.ttl}
                    )
                    result.entities.append(ns_entity)
                
                elif record_type == 'TXT':
                    result.observations.append(self._create_observation(source_entity_id, {
                        'type': 'dns_txt',
                        'domain': domain,
                        'value': value,
                        'ttl': rrset.ttl
                    }))
                
                elif record_type == 'SOA':
                    result.observations.append(self._create_observation(source_entity_id, {
                        'type': 'dns_soa',
                        'domain': domain,
                        'mname': str(rdata.mname),
                        'rname': str(rdata.rname),
                        'serial': rdata.serial,
                        'ttl': rrset.ttl
                    }))
                
                elif record_type == 'CAA':
                    result.observations.append(self._create_observation(source_entity_id, {
                        'type': 'dns_caa',
                        'domain': domain,
                        'flags': rdata.flags,
                        'tag': rdata.tag,
                        'value': rdata.value,
                        'ttl': rrset.ttl
                    }))
    
    async def _try_zone_transfer(self, domain: str, result: CollectorResult) -> None:
        """Attempt zone transfer on NS records."""
        try:
            ns_records = await self._query_record(domain, 'NS')
            for rrset in ns_records:
                for rdata in rrset:
                    ns = str(rdata).rstrip('.')
                    try:
                        # Get NS IP
                        ns_ips = []
                        for rt in ('A', 'AAAA'):
                            try:
                                ans = await self.resolver.resolve(ns, rt)
                                ns_ips.extend([str(r) for r in ans])
                            except Exception:
                                pass
                        
                        for ns_ip in ns_ips:
                            try:
                                zone = dns.zone.from_xfr(dns.query.xfr(ns_ip, domain, lifetime=self.timeout))
                                self.logger.info(f"Zone transfer successful for {domain} from {ns}")
                                for name, node in zone.nodes.items():
                                    if name != '@':
                                        subdomain = f"{name}.{domain}"
                                        sub_entity = self._create_entity(
                                            EntityType.DOMAIN, subdomain,
                                            source_name="dns",
                                            source_type=SourceType.DNS,
                                            attributes={'source': 'zone_transfer', 'ns': ns}
                                        )
                                        result.entities.append(sub_entity)
                                        result.observations.append(self._create_observation(sub_entity.id, {
                                            'type': 'zone_transfer',
                                            'subdomain': subdomain,
                                            'ns_server': ns
                                        }))
                                break  # Only need one successful transfer
                            except Exception:
                                continue
                    except Exception:
                        continue
        except Exception as e:
            self.logger.debug(f"Zone transfer failed for {domain}: {e}")
    
    async def _enumerate_subdomains(self, domain: str, result: CollectorResult) -> None:
        """Enumerate common subdomains."""
        common = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'ns2',
            'dns1', 'dns2', 'mx1', 'mx2', 'autodiscover', 'autoconfig', 'cpanel', 'whm',
            'admin', 'login', 'portal', 'api', 'dev', 'test', 'staging', 'prod', 'app',
            'blog', 'shop', 'store', 'support', 'help', 'docs', 'wiki', 'git', 'ci',
            'vpn', 'remote', 'vps', 'cloud', 'cdn', 'static', 'assets', 'media', 'img',
            'images', 'video', 'files', 'download', 'upload', 'backup', 'db', 'database',
            'sql', 'mysql', 'postgres', 'redis', 'mongo', 'elastic', 'kibana', 'grafana',
            'prometheus', 'jenkins', 'gitlab', 'github', 'bitbucket', 'jira', 'confluence'
        ]
        
        semaphore = asyncio.Semaphore(50)
        
        async def check_subdomain(sub: str) -> None:
            async with semaphore:
                subdomain = f"{sub}.{domain}"
                try:
                    ans = await self.resolver.resolve(subdomain, 'A')
                    for r in ans:
                        ip = str(r)
                        sub_entity = self._create_entity(
                            EntityType.DOMAIN, subdomain,
                            source_name="dns",
                            source_type=SourceType.DNS,
                            attributes={'source': 'enumeration', 'subdomain_of': domain}
                        )
                        result.entities.append(sub_entity)
                        ip_entity = self._create_entity(
                            EntityType.IP, ip,
                            source_name="dns",
                            source_type=SourceType.DNS,
                            attributes={'record_type': 'A', 'domain': subdomain}
                        )
                        result.entities.append(ip_entity)
                        result.relationships.append({
                            'source_id': sub_entity.id,
                            'target_id': ip_entity.id,
                            'relationship_type': 'resolves_to',
                            'description': f'{subdomain} A {ip}'
                        })
                except Exception:
                    pass
        
        await asyncio.gather(*[check_subdomain(s) for s in common])
    
    def _is_domain(self, target: str) -> bool:
        import re
        return re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', target) is not None
    
    def _is_ip(self, target: str) -> bool:
        import re
        return re.match(r'^(\d{1,3}\.){3}\d{1,3}$', target) is not None


@collector(
    name="whois",
    description="WHOIS domain registration intelligence",
    supported_types=[EntityType.DOMAIN, EntityType.IP, EntityType.ASN],
    rate_limit=20,
    timeout=15
)
class WhoisCollector(BaseCollector):
    """WHOIS intelligence collector."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.whois_servers = {
            'com': 'whois.verisign-grs.com',
            'net': 'whois.verisign-grs.com',
            'org': 'whois.pir.org',
            'io': 'whois.nic.io',
            'co': 'whois.nic.co',
            'ai': 'whois.nic.ai',
            'default': 'whois.iana.org'
        }
    
    async def collect(self, target: str, **kwargs) -> CollectorResult:
        """Collect WHOIS data for a target."""
        await self._wait_for_rate_limit()
        job = self._start_job(target, kwargs)
        result = CollectorResult()
        
        try:
            if self._is_domain(target):
                await self._collect_domain_whois(target, result)
            elif self._is_ip(target):
                await self._collect_ip_whois(target, result)
            else:
                result.errors.append(f"Unsupported target: {target}")
        except Exception as e:
            self.logger.error(f"WHOIS collection failed for {target}: {e}")
            result.errors.append(str(e))
        finally:
            self._complete_job(result)
        
        return result
    
    async def _collect_domain_whois(self, domain: str, result: CollectorResult) -> None:
        """Collect WHOIS for a domain."""
        tld = domain.split('.')[-1].lower()
        server = self.whois_servers.get(tld, self.whois_servers['default'])
        
        whois_data = await self._query_whois(server, domain)
        if not whois_data:
            return
        
        # Create domain entity
        domain_entity = self._create_entity(
            EntityType.DOMAIN, domain,
            source_name="whois",
            source_type=SourceType.WHOIS,
            attributes={'whois_server': server}
        )
        result.entities.append(domain_entity)
        
        # Parse WHOIS data
        parsed = self._parse_whois(whois_data)
        
        # Create organization entity if found
        if parsed.get('registrant_org'):
            org_entity = self._create_entity(
                EntityType.ORGANIZATION, parsed['registrant_org'],
                source_name="whois",
                source_type=SourceType.WHOIS,
                attributes={'source': 'whois_registrant'}
            )
            result.entities.append(org_entity)
            result.relationships.append({
                'source_id': org_entity.id,
                'target_id': domain_entity.id,
                'relationship_type': 'owns',
                'description': f'{parsed["registrant_org"]} owns {domain}'
            })
        
        # Create person entity if found
        if parsed.get('registrant_name'):
            person_entity = self._create_entity(
                EntityType.PERSON, parsed['registrant_name'],
                source_name="whois",
                source_type=SourceType.WHOIS,
                attributes={'source': 'whois_registrant', 'role': 'registrant'}
            )
            result.entities.append(person_entity)
        
        # Add observations for key data
        for key, value in parsed.items():
            if value and key not in ('raw',):
                result.observations.append(self._create_observation(domain_entity.id, {
                    'type': 'whois',
                    'field': key,
                    'value': value
                }))
        
        # Store raw WHOIS
        result.observations.append(self._create_observation(domain_entity.id, {
            'type': 'whois_raw',
            'domain': domain,
            'server': server,
            'data': whois_data[:10000]  # Limit size
        }))
    
    async def _collect_ip_whois(self, ip: str, result: CollectorResult) -> None:
        """Collect WHOIS for an IP (via RIR)."""
        # Determine RIR server
        server = 'whois.arin.net'
        # Could add logic to determine correct RIR based on IP range
        
        whois_data = await self._query_whois(server, ip)
        if not whois_data:
            return
        
        ip_entity = self._create_entity(
            EntityType.IP, ip,
            source_name="whois",
            source_type=SourceType.WHOIS,
            attributes={'whois_server': server}
        )
        result.entities.append(ip_entity)
        
        parsed = self._parse_whois(whois_data)
        
        # ASN info
        if parsed.get('origin_as'):
            asn = parsed['origin_as']
            asn_entity = self._create_entity(
                EntityType.ASN, asn,
                source_name="whois",
                source_type=SourceType.WHOIS,
                attributes={'source': 'whois_origin'}
            )
            result.entities.append(asn_entity)
            result.relationships.append({
                'source_id': asn_entity.id,
                'target_id': ip_entity.id,
                'relationship_type': 'originates',
                'description': f'AS{asn} originates {ip}'
            })
        
        # Org info
        if parsed.get('org_name'):
            org_entity = self._create_entity(
                EntityType.ORGANIZATION, parsed['org_name'],
                source_name="whois",
                source_type=SourceType.WHOIS,
                attributes={'source': 'whois_org'}
            )
            result.entities.append(org_entity)
            result.relationships.append({
                'source_id': org_entity.id,
                'target_id': ip_entity.id,
                'relationship_type': 'owns',
                'description': f'{parsed["org_name"]} owns {ip}'
            })
        
        result.observations.append(self._create_observation(ip_entity.id, {
            'type': 'whois_raw',
            'ip': ip,
            'server': server,
            'data': whois_data[:10000]
        }))
    
    async def _query_whois(self, server: str, query: str) -> Optional[str]:
        """Query a WHOIS server."""
        try:
            reader, writer = await asyncio.open_connection(server, 43, ssl=False)
            writer.write(f"{query}\r\n".encode())
            await writer.drain()
            
            data = b""
            while True:
                chunk = await reader.read(4096)
                if not chunk:
                    break
                data += chunk
            
            writer.close()
            await writer.wait_closed()
            return data.decode('utf-8', errors='ignore')
        except Exception as e:
            self.logger.debug(f"WHOIS query failed for {query} @ {server}: {e}")
            return None
    
    def _parse_whois(self, data: str) -> Dict[str, Any]:
        """Parse WHOIS data into structured fields."""
        parsed = {'raw': data}
        
        # Common patterns
        patterns = {
            'domain': r'Domain Name:\s*(.+)',
            'registrar': r'Registrar:\s*(.+)',
            'registrar_url': r'Registrar URL:\s*(.+)',
            'creation_date': r'Creation Date:\s*(.+)',
            'expiration_date': r'Registry Expiry Date:\s*(.+)',
            'updated_date': r'Updated Date:\s*(.+)',
            'registrant_name': r'Registrant Name:\s*(.+)',
            'registrant_org': r'Registrant Organization:\s*(.+)',
            'registrant_email': r'Registrant Email:\s*(.+)',
            'registrant_phone': r'Registrant Phone:\s*(.+)',
            'registrant_address': r'Registrant Street:\s*(.+)',
            'registrant_city': r'Registrant City:\s*(.+)',
            'registrant_state': r'Registrant State/Province:\s*(.+)',
            'registrant_country': r'Registrant Country:\s*(.+)',
            'admin_name': r'Admin Name:\s*(.+)',
            'admin_org': r'Admin Organization:\s*(.+)',
            'admin_email': r'Admin Email:\s*(.+)',
            'tech_name': r'Tech Name:\s*(.+)',
            'tech_org': r'Tech Organization:\s*(.+)',
            'tech_email': r'Tech Email:\s*(.+)',
            'name_servers': r'Name Server:\s*(.+)',
            'dnssec': r'DNSSEC:\s*(.+)',
            'status': r'Domain Status:\s*(.+)',
            'origin_as': r'OriginAS:\s*(.+)',
            'org_name': r'(?:OrgName|Organization):\s*(.+)',
            'org_address': r'(?:OrgAddress|Address):\s*(.+)',
            'netrange': r'NetRange:\s*(.+)',
            'cidr': r'CIDR:\s*(.+)',
            'netname': r'NetName:\s*(.+)',
        }
        
        import re
        for key, pattern in patterns.items():
            matches = re.findall(pattern, data, re.IGNORECASE)
            if matches:
                parsed[key] = matches[0] if len(matches) == 1 else matches
        
        return parsed
    
    def _is_domain(self, target: str) -> bool:
        import re
        return re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$', target) is not None
    
    def _is_ip(self, target: str) -> bool:
        import re
        return re.match(r'^(\d{1,3}\.){3}\d{1,3}$', target) is not None