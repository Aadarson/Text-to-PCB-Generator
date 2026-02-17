# Deploying Text-to-PCB Generator to Google Cloud

The Text-to-PCB Generator is now packaged as a Docker container, making it easy to deploy on platforms like Google Cloud Run. 
Because the application relies on KiCad (a large desktop application), standard Python deployments won't work. You must deploy the Docker container.

## Prerequisites

1.  **Google Cloud Account**: Create a project and enable billing.
2.  **Google Cloud CLI (`gcloud`)**: Installed and initialized.
3.  **Docker Desktop**: Installed and running.

## Step 1: Build the Docker Image

### Option A: Local Build (Requires Docker Desktop)
Open a terminal in the project root (`a:\Text-to-PCB Generator`) and run:

```bash
docker build -t text-to-pcb-app .
```

### Option B: Cloud Build (No Docker Required) ☁️
If you don't have Docker installed, you can build directly on Google Cloud:

1.  Enable Cloud Build API:
    ```bash
    gcloud services enable cloudbuild.googleapis.com
    ```
2.  Submit the build:
    ```bash
    gcloud builds submit --tag us-central1-docker.pkg.dev/YOUR-PROJECT-ID/my-repo/text-to-pcb-app .
    ```
*(This uploads your code to Google Cloud, builds it there, and stores it in the registry automatically.)*

### Option C: Git Push Deployment (Recommended) 🚀
To deploy automatically every time you push to GitHub:

1.  Push this code to a **GitHub Repository**.
2.  Go to the [Google Cloud Console > Cloud Build > Triggers](https://console.cloud.google.com/cloud-build/triggers).
3.  Click **Create Trigger**.
4.  Select your GitHub Source Repository.
5.  Under Configuration, select **Cloud Build configuration file (yaml or json)**.
6.  Point it to the `cloudbuild.yaml` file I just created.
7.  Click **Create**.

Now, whenever you run `git push origin main`, Google Cloud will automatically build your Docker container and deploy the new version!

## Step 2: Push to Google Artifact Registry (If using Option A)

*Skip this if you used Option B or C.*

1.  Enable Artifact Registry API:
    ```bash
    gcloud services enable artifactregistry.googleapis.com
    ```
2.  Create a Docker repository:
    ```bash
    gcloud artifacts repositories create my-repo --repository-format=docker --location=us-central1
    ```
3.  Configure Docker to use gcloud credentials:
    ```bash
    gcloud auth configure-docker us-central1-docker.pkg.dev
    ```
4.  Tag and Push the image:
    ```bash
    docker tag text-to-pcb-app us-central1-docker.pkg.dev/YOUR-PROJECT-ID/my-repo/text-to-pcb-app
    docker push us-central1-docker.pkg.dev/YOUR-PROJECT-ID/my-repo/text-to-pcb-app
    ```

## Step 3: Deploy to Cloud Run

Run the deploy command. Note that we need generous memory (2GB+) because KiCad is heavy.

```bash
gcloud run deploy text-to-pcb-service \
    --image us-central1-docker.pkg.dev/YOUR-PROJECT-ID/my-repo/text-to-pcb-app \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 4Gi \
    --cpu 2
```

## Step 4: Access Your App

Once the deployment finishes, Google Cloud will provide a URL (e.g., `https://text-to-pcb-service-xyz.a.run.app`).
Open this URL in your browser to use the generator live!

## Notes

- **Initial Cold Start**: The first request might take 10-20 seconds as KiCad initializes in the cloud.
- **Storage**: Generated files are ephemeral in Cloud Run. For persistent storage, you would need to integrate Google Cloud Storage (GCS) to save the `.kicad_pcb` files permanently.
