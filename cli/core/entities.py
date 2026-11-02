from pydantic import BaseModel, Field
import uuid

class Entity(BaseModel):
    type: str
    value: str
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    def __str__(self):
        return f"[{self.type}] {self.value}"

class Domain(Entity):
    type: str = "Domain"

class IPAddress(Entity):
    type: str = "IPAddress"

class Email(Entity):
    type: str = "Email"

class Person(Entity):
    type: str = "Person"

class SocialProfile(Entity):
    type: str = "SocialProfile"

class ThreatScore(Entity):
    type: str = "ThreatScore"

class ServiceInfo(Entity):
    type: str = "ServiceInfo"

class WHOISRecord(Entity):
    type: str = "WHOISRecord"

class SSLCertificate(Entity):
    type: str = "SSLCertificate"

class BreachRecord(Entity):
    type: str = "BreachRecord"

class DNSRecord(Entity):
    type: str = "DNSRecord"

class GeoLocation(Entity):
    type: str = "GeoLocation"

class ReputationScore(Entity):
    type: str = "ReputationScore"

class PhoneInfo(Entity):
    type: str = "PhoneInfo"

class URLScanResult(Entity):
    type: str = "URLScanResult"

class ASNInfo(Entity):
    type: str = "ASNInfo"
