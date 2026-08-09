import os
import sys
import importlib.util
from maltego_trx.maltego import MaltegoMsg, MaltegoTransform

class LocalTRXExecutor:
    def __init__(self, transforms_dir="transforms"):
        self.transforms_dir = transforms_dir
        if not os.path.exists(self.transforms_dir):
            os.makedirs(self.transforms_dir)

    def list_transforms(self):
        """Returns a list of available transforms in the transforms directory."""
        if not os.path.exists(self.transforms_dir):
            return []
        
        transforms = []
        for file in os.listdir(self.transforms_dir):
            if file.endswith(".py") and file != "__init__.py":
                transforms.append(file[:-3])
        return transforms

    def execute_transform(self, transform_name, entity_value, entity_type="maltego.Phrase"):
        """Executes a local transform script and returns the discovered entities."""
        file_path = os.path.join(self.transforms_dir, f"{transform_name}.py")
        
        if not os.path.exists(file_path):
            return None, f"Transform {transform_name} not found."

        # Dynamically load the transform module
        spec = importlib.util.spec_from_file_location(transform_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Look for the class matching the transform name
        if not hasattr(module, transform_name):
            return None, f"Class {transform_name} not found in script."

        transform_class = getattr(module, transform_name)

        # Construct a mock MaltegoMsg for the transform
        msg = MaltegoMsg()
        msg.Value = entity_value
        msg.Type = entity_type
        msg.Weight = 100
        msg.Slider = 100

        # Construct a MaltegoTransform response object
        response = MaltegoTransform()

        try:
            # Execute the create_entities classmethod
            transform_class.create_entities(msg, response)
            
            # Extract entities from the response
            results = []
            for entity in response.entities:
                results.append({
                    "type": entity.entityType,
                    "value": entity.value,
                    "weight": entity.weight
                })
            
            return results, None
        except Exception as e:
            return None, f"Execution failed: {str(e)}"
