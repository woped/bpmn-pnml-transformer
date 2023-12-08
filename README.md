# POC: Architecture BPMN-PNML-Transformer

## Description
This repo contains a proof of concept (POC) for the architecture of a BPMN to PNML Converter.
The converter is an REST API hosted on Google Cloud Platform (GCP) using Google Cloud Functions (GCF).

This project was created as part of the lecture "Integrationsseminar" at the DHBW Karlsruhe.


## Prerequisites
- Google Cloud Platform Account with billing enabled
- Installed and authenticated [GCP CLI](https://cloud.google.com/sdk/docs/install-sdk?ref=blog.leandrotoledo.org) 


## Infrastructure
In this chaper the design a swell as the process for creating and configuring all necessary infrastructure is explained and documented.

### Design
Project Components
| Component Name | Task |
| -------------- | ---- |
| Google Cloud Functions | FaaS solution hosting \ providing the REST-API |
| Google Cloud Build | Used for building and deploying google cloud functions |
| Google Cloud IAM | Used for authentication and authorization |
| Github | Code versioning system and remote repo |
| Github Actions | CI/CD tool |


### Process
#### Creating GCP Project
1. Creating a Google Cloud Project in the [web interface](https://console.cloud.google.com/projectcreate?ref=blog.leandrotoledo.org)
2. Note the `ProjectId`

#### Creating Workload Identity on GCP
- Required steps are documented in the `github-actions-gcp.sh` script located in the `/scripts` directory
- run the script by typing `./scripts/github-actions-gcp.sh` to create the workload identity and related components

#### Creating the Github Action
- Required Information (can be retrieved from `github-actions-gcp.sh`):
  - `WORKLOAD_IDENTITY_PROVIDER_LOCATION`
  - `SERVICE_ACCOUNT`
  - `PROJECT_ID`
- use these values to adjust the `<action-name>.yml` of the corresponding github action to authenticate at GCP

#### Configuring Local Environment
- Install miniconda from [here](https://docs.conda.io/projects/miniconda/en/latest/)
- Create a new conda envrionment from the provided file `envrionment.yml`.
    ```bash
    conda env create -n GCF-BPMN-PNML-transformer --file envrionment.yml
    ```
- You can make updates to this file by using
    ```bash
    conda env export --no-builds>envrionment.yml
    ```