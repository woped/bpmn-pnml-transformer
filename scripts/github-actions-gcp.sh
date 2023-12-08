#!/bin/bash

echo "Please enter the target github repo (User/RepoName):"
read YOUR_GITHUB_REPO


echo "Please enter the GCP Project ID:"
read YOUR_PROJECT_ID

# Set required env variabes
export GITHUB_REPO=$YOUR_GITHUB_REPO
export PROJECT_ID=$YOUR_PROJECT_ID
export SERVICE_ACCOUNT=github-actions-service-account
export WORKLOAD_IDENTITY_POOL=github-identity-pool
export WORKLOAD_IDENTITY_PROVIDER=github-identity-provider


# Setting current GCP project to work with
printf "\n\nSeting current GCP project to work with"
gcloud config set project $PROJECT_ID


# Enable required APIs for Cloud Functions, Cloud Build, IAM Credential
printf "\n\nEnable required APIs for Cloud Functions, Cloud Build, IAM Credential"
gcloud services enable \
   cloudfunctions.googleapis.com \
   cloudbuild.googleapis.com \
   iamcredentials.googleapis.com


# Creating a service account 'github-actions-service-account' that will be used by GitHub Actions
printf "\n\nCreating a service account 'github-actions-service-account' that will be used by GitHub Actions"
gcloud iam service-accounts create $SERVICE_ACCOUNT \
   --display-name="GitHub Actions Service Account"


# Binding the Service Account to the Roles in the Services it must interact with
printf "\n\nBinding the Service Account to the Roles in the Services it must interact with"
gcloud projects add-iam-policy-binding $PROJECT_ID \
   --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
   --role="roles/cloudfunctions.developer"
gcloud projects add-iam-policy-binding $PROJECT_ID \
   --member="serviceAccount:$SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com" \
   --role="roles/iam.serviceAccountUser"


# Creating a workload identity pool for GitHub
printf "\n\nCreating a workload identity pool for GitHub"
gcloud iam workload-identity-pools create $WORKLOAD_IDENTITY_POOL \
   --location="global" \
   --display-name="GitHub pool"


# Creating a Workload Identity Provider for GitHub
printf "\n\nCreating a Workload Identity Provider for GitHub"
gcloud iam workload-identity-pools providers create-oidc $WORKLOAD_IDENTITY_PROVIDER \
   --location="global" \
   --workload-identity-pool=$WORKLOAD_IDENTITY_POOL \
   --display-name="GitHub provider" \
   --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
   --issuer-uri="https://token.actions.githubusercontent.com"


# Retrieving the workload identity pool id
printf "\n\nRetrieving the workload identity pool id"
WORKLOAD_IDENTITY_POOL_ID=$(gcloud iam workload-identity-pools \
   describe $WORKLOAD_IDENTITY_POOL \
   --location="global" \
   --format="value(name)")


# Allowing authentications from the Workload Identity Provider originating from the repository
printf "\n\nAllowing authentications from the Workload Identity Provider originating from the repository"
gcloud iam service-accounts add-iam-policy-binding \
   $SERVICE_ACCOUNT@$PROJECT_ID.iam.gserviceaccount.com \
   --role="roles/iam.workloadIdentityUser" \
   --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL_ID}/attribute.repository/${GITHUB_REPO}"


# Extracting Workload Identity Provider Ressourcenname
printf "\n\nExtracting Workload Identity Provider Ressourcenname"
WORKLOAD_IDENTITY_PROVIDER_LOCATION=$(gcloud iam workload-identity-pools providers \
   describe $WORKLOAD_IDENTITY_PROVIDER \
   --location="global" \
   --workload-identity-pool=$WORKLOAD_IDENTITY_POOL \
   --format="value(name)")

printf "\n\n"
echo " ----------------------------- ALL DONE ----------------------------- "
echo " GITHUB_REPO                        : ${GITHUB_REPO}"
echo " PROJECT_ID                         : ${PROJECT_ID}"
echo " SERVICE_ACCOUNT                    : ${GITHUB_REPO}"
echo " WORKLOAD_IDENTITY_POOL             : ${GITHUB_REPO}"
echo " WORKLOAD_IDENTITY_PROVIDER         : ${WORKLOAD_IDENTITY_PROVIDER}"
echo " WORKLOAD_IDENTITY_POOL_ID          : ${WORKLOAD_IDENTITY_POOL_ID}"
echo " WORKLOAD_IDENTITY_PROVIDER_LOCATION: ${WORKLOAD_IDENTITY_PROVIDER_LOCATION}"
echo " ----------------------------- -------- ----------------------------- "