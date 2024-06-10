# POC: Architecture BPMN-PNML-Transformer

## Description
Welcome to this repository, showcasing a Proof of Concept (PoC) for the architecture of a BPMN to PNML Converter.
This converter is implemented as a REST API, deployed on Google Cloud Platform (GCP) utilizing Google Cloud Functions (GCF).
Developed during the "Integrationsseminar" lecture at DHBW Karlsruhe, this project serves as a practical application and extension of the concepts discussed in the accompanying academic paper.




## Prerequisites
- Google Cloud Platform Account with billing enabled
- Installed and authenticated [GCP CLI](https://cloud.google.com/sdk/docs/install-sdk?ref=blog.leandrotoledo.org) 
- A Python installation, preferred version 3.12, miniconda recommended

## Architecture

### Main Architecture Design
![Architecture Drawing](https://github.com/Niyada/bpmn-pnml-transformer-poc/blob/main/docs/imgs/architecture.design.png?raw=true)

Complete architecure and deployment concept overview

### Pipelinde Designs
![CI/CD Workflows](https://github.com/Niyada/bpmn-pnml-transformer-poc/blob/main/docs/imgs/workflows.design.png?raw=true)

CI workflow on the left, CD workflow on the right

## Automated Deployment and Local Development Setup

### GCP Integration with GitHub Actions Setup
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
- use these values to adjust the `<action-name>.yml` of the corresponding github action




### Configuring Local Environment
- Install miniconda from [here](https://docs.conda.io/projects/miniconda/en/latest/)
- Create a new conda envrionment and install the required depenecies from `requirements.txt`.
    ```bash
    conda create -n GCF-BPMN-PNML-transformer pip
    pip install -r requirements.txt
    ```
- After adding new dependencies use the following to update the `requrements.txt`. Do this to ensure compatibility with the pipeline.
    ```bash
    pip list --format=freeze > requirements.txt
    ```

- In VS Code:
  - **Set Code Interpreter:** Hit `CTRL` + `shift` + `P` and type *Pthon: select interpreter* and choose `GCF-BPMN-PNML-transformer`.
  - **Install Extensions:** Install the following extensions: `Ruff`, `GitHub Actions`
  - **Testing Envrionment** Go to the Testing Tab and hit *Configure Python Tests*, then select `pytest` and the the `test` directory.




## Nice2Know & Useful Links

#### Commands
| Command | Description |
| ------- | ----------- |
| `pytest` | Collects and runs all tests locally |
| `ruff check` | Lints the project. Does not output anything, if there aren't any issues. |

#### Links
- [Authorizing GCF access with IAM](https://cloud.google.com/functions/docs/securing/managing-access-iam#console_4)
- [Deploy GCF Github Action](https://github.com/google-github-actions/deploy-cloud-functions)
