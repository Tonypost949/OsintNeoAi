targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment which is used to generate a short unique hash for all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

var resourceGroupName = 'rg-${environmentName}'

resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: location
}

output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_LOCATION string = location
