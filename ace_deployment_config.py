"""
DEPLOYMENT & SCHEDULING CONFIGURATION
Wires the ACE (Auto Correlation Enrichment) engine into Azure runtime.
"""

# ============================================================================
# AZURE FUNCTIONS HOST CONFIGURATION (function_app.json)
# ============================================================================

AZURE_FUNCTIONS_CONFIG = {
    "version": "2.0",
    "logging": {
        "applicationInsights": {
            "samplingSettings": {
                "isEnabled": True,
                "maxTelemetryItemsPerSecond": 20,
                "evaluationInterval": "01:00:00",
                "initialSamplingPercentage": 100.0,
                "samplingPercentageIncreaseTimeout": "01:01:00",
                "samplingPercentageDecreaseTimeout": "01:05:00",
                "minSamplingPercentage": 0.1,
                "maxSamplingPercentage": 100.0,
                "movingAverageRatio": 0.25
            }
        }
    },
    "extensionBundle": {
        "id": "Microsoft.Azure.Functions.ExtensionBundle",
        "version": "[3.*, 4.0.0)"
    },
    "functionTimeout": "00:10:00"
}

# ============================================================================
# AZURE FUNCTION HOST.JSON (enable ACE functions)
# ============================================================================

HOST_JSON_UPDATES = {
    "version": "2.0",
    "functionTimeout": "00:10:00",
    "logging": {
        "fileLoggingMode": "debugOnly",
        "logLevel": {
            "default": "Information",
            "Worker": "Information"
        }
    },
    "extensions": {
        "http": {
            "routePrefix": "api"
        },
        "timers": {
            "maxDegreeOfParallelism": 1
        }
    }
}

# ============================================================================
# APP SERVICE CONFIGURATION
# ============================================================================

APP_SETTINGS = {
    "AzureWebJobsStorage": "DefaultEndpointsProtocol=https;...",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "FUNCTIONS_EXTENSION_VERSION": "~4",
    
    # ACE Configuration
    "ACE_GCP_PROJECT": "noble-beanbag-497411-m4",
    "ACE_CORRELATION_INTERVAL": "300",
    "ACE_ENRICHMENT_BATCH_SIZE": "1000",
    "ACE_ENTITY_THRESHOLD": "0.85",
    
    # BigQuery datasets
    "ACE_BQ_EVIDENCE_DATASET": "evidence_correlations",
    "ACE_BQ_PHOTOS_DATASET": "google_photos_index",
    "ACE_BQ_DRIVE_DATASET": "drive_file_index",
    "ACE_BQ_FORENSIC_DATASET": "npi_forensic",
    
    # Output paths
    "ACE_OUTPUT_ENDPOINT": "data/correlation_results.json",
    "ACE_GRAPH_OUTPUT": "data/correlation_graph.json",
    
    # Google Cloud credentials (injected from KeyVault)
    "GOOGLE_APPLICATION_CREDENTIALS": "/home/site/wwwroot/gcp_adc.json"
}

# ============================================================================
# GITHUB ACTIONS WORKFLOW — Auto-Deploy ACE on Push
# ============================================================================

GITHUB_ACTIONS_WORKFLOW = """
name: Deploy ACE to Azure

on:
  push:
    branches: [main]
    paths:
      - 'auto_correlation_enrichment_engine.py'
      - 'azure_functions_correlation.py'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Azure Functions Core Tools
      run: npm install -g azure-functions-core-tools@4 --unsafe-perm true
    
    - name: Install Python dependencies
      run: |
        cd azure_functions_correlation
        pip install -r requirements.txt
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Deploy to Azure Functions
      run: |
        func azure functionapp publish osintneoai-app-949 --build remote
    
    - name: Test ACE Endpoint
      run: |
        curl -X GET https://osintneoai-app-949.azurewebsites.net/api/correlation/status
"""

# ============================================================================
# LOCAL DEPLOYMENT SCRIPT
# ============================================================================

DEPLOYMENT_SCRIPT = """#!/bin/bash
# Deploy ACE to Azure App Service

set -e

echo "================================"
echo "AUTO-CORRELATION ENRICHMENT DEPLOYMENT"
echo "================================"

# 1. Create Azure Function project structure
mkdir -p azure_functions_correlation
cd azure_functions_correlation

# 2. Create requirements.txt
cat > requirements.txt <<EOF
azure-functions
google-cloud-bigquery
google-cloud-storage
google-auth
google-auth-httplib2
google-auth-oauthlib
EOF

# 3. Copy main function files
cp ../auto_correlation_enrichment_engine.py .
cp ../azure_functions_correlation.py function_app.py

# 4. Create host.json
cat > host.json <<'HOSTJSON'
{
  "version": "2.0",
  "functionTimeout": "00:10:00",
  "logging": {
    "fileLoggingMode": "debugOnly"
  },
  "extensions": {
    "timers": {
      "maxDegreeOfParallelism": 1
    }
  }
}
HOSTJSON

# 5. Initialize local project
func init --docker

# 6. Test locally
echo "Testing locally..."
func start &
FUNC_PID=$!
sleep 5
curl http://localhost:7071/api/correlation/status || true
kill $FUNC_PID

# 7. Deploy to Azure
echo "Deploying to Azure..."
az functionapp deployment source config-zip \\
  --resource-group neoai-rg \\
  --name osintneoai-app-949 \\
  --src azure_functions_correlation.zip

echo "================================"
echo "✅ ACE DEPLOYED SUCCESSFULLY"
echo "================================"
echo "Timer trigger: Every 5 minutes"
echo "Status endpoint: https://osintneoai-app-949.azurewebsites.net/api/correlation/status"
echo "Manual trigger: https://osintneoai-app-949.azurewebsites.net/api/correlation/trigger"
"""

# ============================================================================
# DOCKER CONTAINER (For local development)
# ============================================================================

DOCKERFILE_ACE = """
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \\
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY auto_correlation_enrichment_engine.py ${AzureWebJobsScriptRoot}/
COPY azure_functions_correlation.py ${AzureWebJobsScriptRoot}/
COPY requirements.txt ${AzureWebJobsScriptRoot}/

RUN cd ${AzureWebJobsScriptRoot} && \\
    pip install -r requirements.txt

EXPOSE 7071
"""

# ============================================================================
# INFRASTRUCTURE AS CODE — BICEP
# ============================================================================

BICEP_ACE = """
param location string = 'eastus'
param appServiceName string = 'osintneoai-app-949'
param functionAppName string = 'osintneoai-ace'
param storageAccountName string = 'osintneoaiace'

resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'ACE_GCP_PROJECT'
          value: 'noble-beanbag-497411-m4'
        }
        {
          name: 'ACE_CORRELATION_INTERVAL'
          value: '300'
        }
        {
          name: 'GOOGLE_APPLICATION_CREDENTIALS'
          value: '/home/site/wwwroot/gcp_adc.json'
        }
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};EndpointSuffix=core.windows.net;SharedAccessSignature=${storageAccount.listKeys().keys[0].value}'
        }
      ]
    }
  }
}

resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: '${functionAppName}-plan'
  location: location
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
}

output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'
"""

# ============================================================================
# KUBERNETES CRONJOB (For on-prem deployments)
# ============================================================================

K8S_CRONJOB_ACE = """
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ace-correlation-engine
  namespace: osintneoai
spec:
  schedule: "*/5 * * * *"  # Every 5 minutes
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: ace-worker
          containers:
          - name: ace
            image: osintneoai/ace:latest
            imagePullPolicy: Always
            env:
            - name: GCP_PROJECT
              value: "noble-beanbag-497411-m4"
            - name: CORRELATION_INTERVAL
              value: "300"
            - name: GOOGLE_APPLICATION_CREDENTIALS
              value: "/var/secrets/google/key.json"
            volumeMounts:
            - name: google-cloud-key
              mountPath: /var/secrets/google
            - name: correlation-output
              mountPath: /data
            resources:
              limits:
                memory: "1Gi"
                cpu: "500m"
              requests:
                memory: "512Mi"
                cpu: "250m"
          volumes:
          - name: google-cloud-key
            secret:
              secretName: google-cloud-credentials
          - name: correlation-output
            persistentVolumeClaim:
              claimName: ace-output-pvc
          restartPolicy: OnFailure
"""

# ============================================================================
# DEPLOYMENT COMMANDS
# ============================================================================

DEPLOYMENT_COMMANDS = """
# 1. Deploy to Azure Functions (recommended - fully managed)
az functionapp create \\
  --resource-group neoai-rg \\
  --consumption-plan-location eastus \\
  --runtime python \\
  --runtime-version 3.11 \\
  --functions-version 4 \\
  --name osintneoai-ace \\
  --storage-account osintneoaiace

# 2. Configure app settings
az functionapp config appsettings set \\
  --name osintneoai-ace \\
  --resource-group neoai-rg \\
  --settings ACE_GCP_PROJECT="noble-beanbag-497411-m4" \\
              ACE_CORRELATION_INTERVAL="300" \\
              GOOGLE_APPLICATION_CREDENTIALS="/home/site/wwwroot/gcp_adc.json"

# 3. Deploy code
func azure functionapp publish osintneoai-ace --build remote

# 4. Verify deployment
curl https://osintneoai-ace.azurewebsites.net/api/correlation/status

# 5. View logs
az functionapp logs tail --name osintneoai-ace --resource-group neoai-rg
"""

print(__doc__)
print("\\nDeployment configuration loaded. Use 'deploy.ps1' or 'deploy.sh' to deploy.")
