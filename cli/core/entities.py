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
