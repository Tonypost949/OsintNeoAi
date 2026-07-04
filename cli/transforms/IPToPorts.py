from maltego_trx.entities import Port
from maltego_trx.transform import DiscoverableTransform

class IPToPorts(DiscoverableTransform):
    """
    Looks up open ports for an IP address. 
    (Simulated for proof-of-concept, but easily swappable with Shodan API).
    """

    @classmethod
    def create_entities(cls, request, response):
        ip_address = request.Value
        
        # In a real transform, we would hit Shodan or Nmap here.
        # For now, we return mock ports to prove the pipeline works.
        mock_ports = ["80", "443", "22", "3389"]
        
        for port in mock_ports:
            # We create a new Port entity connected to the original IP
            port_entity = response.addEntity(Port, port)
            port_entity.addProperty("ip", "IP Address", "strict", ip_address)
            port_entity.addProperty("service", "Service", "strict", "Unknown")
