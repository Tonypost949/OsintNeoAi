# Deploy OsintNeoAi to Azure via Portal (No CLI needed)

## Step 1: Push Docker image to Docker Hub (free, public registry)

```powershell
# Login to Docker Hub (create account if needed at hub.docker.com)
docker login

# Tag your image
docker tag osintneoai:kali-integrated tonypost949/osintneoai:latest

# Push to Docker Hub
docker push tonypost949/osintneoai:latest
```

## Step 2: Deploy from Docker Hub via Azure Portal

1. Go to **https://portal.azure.com**
2. Log in with your Azure student account
3. Click **Create a resource** (top left)
4. Search for **Container Instances**
5. Click **Create**

Fill in:
- **Subscription**: Your student subscription
- **Resource group**: Create new → `osintneoai-rg`
- **Container name**: `osintneoai-app`
- **Region**: `East US`
- **Image source**: `Docker Hub`
- **Image name**: `tonypost949/osintneoai:latest`
- **OS type**: `Linux`
- **Number of CPU cores**: `1`
- **Memory (GB)**: `2`
- **Restart policy**: `On failure`

6. Click **Networking** tab:
   - **DNS name label**: `osintneoai-app` (creates `osintneoai-app.eastus.azurecontainer.io`)
   - **Ports**: `10000`

7. Click **Review + create** → **Create**

Wait 2-3 minutes. Once deployed, you'll get a public URL in the container details page.

## Step 3: Access your app

Your URL will be: `http://osintneoai-app.eastus.azurecontainer.io:10000`

Share this link—anyone can access it from phone/PC.

## Estimate cost:
- **Free tier student**: First $100/month
- Container Instances: ~$0.0015/hour running (very cheap)
- **Total**: Within free tier
