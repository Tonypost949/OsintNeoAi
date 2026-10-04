class GraphSchema:
    """Standardized declarative Graph Schema defining allowable Node and Relationship types."""
    
    # Allowable Node Types (Labels)
    NODE_PERSON = "PERSON"
    NODE_ORGANIZATION = "ORGANIZATION"
    NODE_ADDRESS = "ADDRESS"
    NODE_PROPERTY = "PROPERTY"
    NODE_PPP_LOAN = "PPP_LOAN"
    NODE_CASE = "CASE"
    NODE_ATTORNEY = "ATTORNEY"
    NODE_STATE = "STATE"
    NODE_ARTICLE = "ARTICLE"
    
    NODE_TYPES = {
        NODE_PERSON,
        NODE_ORGANIZATION,
        NODE_ADDRESS,
        NODE_PROPERTY,
        NODE_PPP_LOAN,
        NODE_CASE,
        NODE_ATTORNEY,
        NODE_STATE,
        NODE_ARTICLE
    }
    
    # Allowable Relationship Types
    REL_OWNS = "OWNS"
    REL_RECEIVED_PPP = "RECEIVED_PPP"
    REL_REGISTERED_AT = "REGISTERED_AT"
    REL_LOCATED_IN = "LOCATED_IN"
    REL_OFFICER_OF = "OFFICER_OF"
    REL_DIRECTOR_OF = "DIRECTOR_OF"
    REL_LITIGANT_IN = "LITIGANT_IN"
    REL_REPRESENTED_BY = "REPRESENTED_BY"
    REL_CONNECTED_TO = "CONNECTED_TO"
    
    RELATIONSHIP_TYPES = {
        REL_OWNS,
        REL_RECEIVED_PPP,
        REL_REGISTERED_AT,
        REL_LOCATED_IN,
        REL_OFFICER_OF,
        REL_DIRECTOR_OF,
        REL_LITIGANT_IN,
        REL_REPRESENTED_BY,
        REL_CONNECTED_TO
    }
    
    @classmethod
    def validate_node(cls, label):
        """Verify that a node label matches our formal schema definition."""
        return label in cls.NODE_TYPES
        
    @classmethod
    def validate_relationship(cls, rel_type):
        """Verify that a relationship type matches our formal schema definition."""
        return rel_type in cls.RELATIONSHIP_TYPES
