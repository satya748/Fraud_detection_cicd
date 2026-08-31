# How to Deploy Fraud Detection to AWS — Step by Step

**Author: Suresh D R | AI Product Developer & Technology Mentor**
*MLOps Syllabus — Deploy and Retrain ML Models on AWS*

---

## What You Will Do

```
PART 1 — Local Setup (your laptop)
  Step 1  → Run project locally and verify
  Step 2  → Push code to GitHub
  Step 3  → CI/CD pipeline runs automatically (test + build)

PART 2 — AWS Setup (one time only)
  Step 4  → Create AWS account
  Step 5  → Create IAM user with permissions
  Step 6  → Install and configure AWS CLI
  Step 7  → Create Amazon ECR repository
  Step 8  → Push Docker image to ECR from laptop
  Step 9  → Install kubectl and eksctl
  Step 10 → Create EKS cluster

PART 3 — Deploy to AWS
  Step 11 → Add GitHub Secrets (AWS credentials)
  Step 12 → Deploy Kubernetes configuration
  Step 13 → Get your live public URL

PART 4 — Auto Deploy on Every Code Change
  Step 14 → Make a code change
  Step 15 → git push — pipeline auto deploys to AWS
  Step 16 → See change live immediately
```

---

# PART 1 — LOCAL SETUP

---

## STEP 1 — Run Project Locally

```bash
# Open project in VS Code
# Open Git Bash terminal

# Activate venv
source venv/Scripts/activate

# Install libraries
pip install -r requirements.txt

# Generate data and train model
cd src
python generate_data.py
python train.py
cd ..

# Run tests — all 8 must pass
pytest tests/test_model.py -v

# Run Streamlit app locally
streamlit run src/app.py
```

Open browser → `http://localhost:8501` → app works ✅

Stop app → `Ctrl+C`

---

## STEP 2 — Push Code to GitHub

```bash
# Initialise git (if not done)
git init
git config --global user.name "Suresh D R"
git config --global user.email "drsuresh8453@gmail.com"

# Stage and commit
git add .
git commit -m "Initial commit — fraud detection with CI/CD and AWS deployment"

# Create repo on GitHub first:
# Go to github.com → + → New repository
# Name: fraud-detection-aws
# Public → Create repository
# Copy the URL

# Connect and push
git branch -M main
git remote add origin https://github.com/drsuresh8453/fraud-detection-aws.git
git push -u origin main
```

Enter username and Personal Access Token when asked. ✅

---

## STEP 3 — CI/CD Pipeline Runs Automatically

Go to GitHub → **Actions** tab.

You will see pipeline running:
```
✅ Install, Train and Test       — 32 seconds
⏳ Build Docker Image and Push   — waiting for AWS setup
⏳ Deploy to AWS EKS             — waiting for AWS setup
```

**Job 1 (Test) passes immediately.**
Jobs 2 and 3 need AWS setup — do that next.

---

# PART 2 — AWS SETUP (ONE TIME ONLY)

---

## STEP 4 — Create AWS Account

1. Open browser → go to `https://aws.amazon.com`
2. Click **Create an AWS Account**
3. Enter email → set password → account name: `mlops-account`
4. Select **Personal** account type
5. Enter contact details
6. Enter credit/debit card → verification only — Free Tier will not charge
7. Phone verification → OTP → verify
8. Choose **Basic Support — Free**
9. Click **Complete Sign Up** ✅

**Login:**
1. Go to `https://console.aws.amazon.com`
2. Login with your email and password

**Set Region — VERY IMPORTANT:**
- Top right corner → click region dropdown
- Select **Asia Pacific (Mumbai) — ap-south-1**
- Always use Mumbai — closest to India

---

## STEP 5 — Create IAM User with Permissions

> Never use your root account for daily work. Create a specific user with only the permissions needed.

### 5a — Create IAM User

1. In AWS Console → search **IAM** → click IAM
2. Click **Users** in left sidebar
3. Click **Create user**
4. Username: `mlops-user`
5. Click **Next**
6. Select **Attach policies directly**
7. Search and tick these 4 policies:
   - ✅ `AmazonECRFullAccess`
   - ✅ `AmazonEKSFullAccess`
   - ✅ `AmazonEKSClusterPolicy`
   - ✅ `AmazonS3FullAccess`
8. Click **Next** → **Create user** ✅

### 5b — Create Access Keys

1. Click on `mlops-user` (click the name)
2. Click **Security credentials** tab
3. Scroll to **Access keys** section
4. Click **Create access key**
5. Select **Command Line Interface (CLI)**
6. Tick the confirmation checkbox
7. Click **Next** → **Create access key**
8. **DOWNLOAD CSV FILE immediately!**

```
You will see:
AWS_ACCESS_KEY_ID     = AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY = wJalrXUtnFEMI/K7MDENG
```

> ⚠️ Download the CSV NOW — you cannot see the secret key again after closing this page.
> Save in a safe place — Notepad or password manager.

---

## STEP 6 — Install and Configure AWS CLI

### 6a — Install AWS CLI

**Check if already installed:**
```bash
aws --version
```

**If not installed:**
1. Open browser → go to `https://aws.amazon.com/cli/`
2. Click **Download AWS CLI** → Windows (64-bit)
3. Run the installer → **Next** → **Next** → **Finish**
4. Close and reopen Git Bash

**Verify:**
```bash
aws --version
```
```
aws-cli/2.13.0 Python/3.11 Windows ✅
```

### 6b — Configure AWS CLI

```bash
aws configure
```

Enter each value:
```
AWS Access Key ID: AKIAIOSFODNN7EXAMPLE
AWS Secret Access Key: wJalrXUtnFEMI/K7MDENG
Default region name: ap-south-1
Default output format: json
```

**Verify connection:**
```bash
aws sts get-caller-identity
```

**You will see:**
```json
{
    "UserId": "AIDAEXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/mlops-user"
}
```

AWS CLI is connected. ✅

---

## STEP 7 — Create Amazon ECR Repository

```bash
aws ecr create-repository \
    --repository-name fraud-detection \
    --region ap-south-1
```

**You will see:**
```json
{
    "repository": {
        "repositoryUri": "123456789012.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection",
        "repositoryName": "fraud-detection",
        "registryId": "123456789012"
    }
}
```

**Copy the `repositoryUri`** — you need this everywhere.

```
Your ECR URL = 123456789012.dkr.ecr.ap-south-1.amazonaws.com
Your ECR Repository = fraud-detection
```

---

## STEP 8 — Push Docker Image to ECR from Laptop

### 8a — Build Docker Image Locally

```bash
# Make sure you are in project root
pwd
# Should show: /c/Users/Suresh D R/.../fraud-detection-aws

# Make sure model exists
ls models/
# Should show: fraud_model.pkl

# Build Docker image
# Stay on MOBILE HOTSPOT — WiFi blocks Docker
docker build -t fraud-detection:v1.0 .
```

Wait 5-10 minutes first time. You will see:
```
[+] Building 65.3s (8/8) FINISHED
=> naming to fraud-detection:v1.0 ✅
```

### 8b — Login to ECR

```bash
aws ecr get-login-password --region ap-south-1 | \
docker login --username AWS --password-stdin \
123456789012.dkr.ecr.ap-south-1.amazonaws.com
```
```
Login Succeeded ✅
```

### 8c — Tag and Push to ECR

```bash
# Tag
docker tag fraud-detection:v1.0 \
123456789012.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection:latest

docker tag fraud-detection:v1.0 \
123456789012.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection:v1.0

# Push
docker push 123456789012.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection:latest
docker push 123456789012.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection:v1.0
```

**You will see:**
```
latest: digest: sha256:abc123... size: 892MB
Pushed ✅
```

**Verify on AWS Console:**
Go to ECR → Repositories → fraud-detection → you see your image ✅

---

## STEP 9 — Install kubectl and eksctl

### Install kubectl

```bash
# Download kubectl
curl -LO "https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe"

# Move to a folder in your PATH (create if needed)
mkdir -p ~/bin
mv kubectl.exe ~/bin/kubectl

# Verify
kubectl version --client
```
```
Client Version: v1.28.0 ✅
```

### Install eksctl

```bash
# Download eksctl
curl -sLO "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_Windows_amd64.zip"

# Unzip
unzip eksctl_Windows_amd64.zip -d ~/bin/

# Verify
eksctl version
```
```
0.157.0 ✅
```

---

## STEP 10 — Create EKS Cluster

> ⚠️ This costs money — approximately ₹600-800 per day.
> Always delete the cluster when you are done practicing.

```bash
eksctl create cluster \
  --name fraud-detection-cluster \
  --region ap-south-1 \
  --nodegroup-name workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 3 \
  --managed
```

**This takes 15-20 minutes.** You will see:

```
2024-04-14 10:00:00 [i]  Creating cluster fraud-detection-cluster
2024-04-14 10:05:00 [i]  Creating nodegroup workers
2024-04-14 10:18:00 [✔]  EKS cluster fraud-detection-cluster is ready ✅
```

**Verify cluster is running:**
```bash
kubectl get nodes
```
```
NAME                STATUS   ROLES    AGE   VERSION
ip-10-0-1-100.ap    Ready    <none>   2m    v1.28.5 ✅
ip-10-0-2-200.ap    Ready    <none>   2m    v1.28.5 ✅
```

2 nodes running. ✅

---

# PART 3 — DEPLOY TO AWS

---

## STEP 11 — Add GitHub Secrets

This allows GitHub Actions to push to ECR and deploy to EKS automatically.

1. Go to your GitHub repository
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret** — add these one by one:

| Secret Name | Value |
|-------------|-------|
| `AWS_ACCESS_KEY_ID` | Your IAM access key |
| `AWS_SECRET_ACCESS_KEY` | Your IAM secret key |
| `AWS_REGION` | `ap-south-1` |
| `ECR_REGISTRY` | `123456789012.dkr.ecr.ap-south-1.amazonaws.com` |
| `ECR_REPOSITORY` | `fraud-detection` |
| `EKS_CLUSTER_NAME` | `fraud-detection-cluster` |

**All 6 secrets added** ✅

---

## STEP 12 — Update Kubernetes YAML with Your Account ID

Open `k8s/deployment.yml` in VS Code.

Find this line:
```yaml
image: ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection:latest
```

Replace `ACCOUNT_ID` with your actual AWS account ID:
```yaml
image: 123456789012.dkr.ecr.ap-south-1.amazonaws.com/fraud-detection:latest
```

Save — `Ctrl+S`

---

## STEP 13 — Deploy Kubernetes Configuration

```bash
# Connect to EKS cluster
aws eks update-kubeconfig \
  --region ap-south-1 \
  --name fraud-detection-cluster

# Apply deployment
kubectl apply -f k8s/deployment.yml
```

**You will see:**
```
deployment.apps/fraud-detection created
service/fraud-detection-service created
```

**Check pods are running:**
```bash
kubectl get pods
```
```
NAME                                READY   STATUS    AGE
fraud-detection-7d9f8b-abc12        1/1     Running   2m ✅
fraud-detection-7d9f8b-def34        1/1     Running   2m ✅
```

**Get the public URL:**
```bash
kubectl get service fraud-detection-service
```
```
NAME                       TYPE           EXTERNAL-IP
fraud-detection-service    LoadBalancer   abc123.ap-south-1.elb.amazonaws.com
```

**Copy the EXTERNAL-IP.**

Open browser:
```
http://abc123.ap-south-1.elb.amazonaws.com:8501
```

**Your fraud detection app is LIVE on AWS!** 🎉

---

# PART 4 — AUTO DEPLOY ON EVERY CODE CHANGE

---

## STEP 14 — Make a Code Change

Open `src/train.py` in VS Code.

Find:
```python
model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42, n_jobs=-1)
```

Change to:
```python
model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)
```

Save — `Ctrl+S`

---

## STEP 15 — Push to GitHub

```bash
git add src/train.py
git commit -m "Improve model — 200 trees, depth 10 for better accuracy"
git push
```

**The moment you push — GitHub Actions triggers automatically.**

---

## STEP 16 — Watch It Deploy to AWS Automatically

Go to GitHub → **Actions** tab.

You will see new pipeline run:
```
⏳ MLOps CI/CD Pipeline — running
   Improve model — 200 trees, depth 10
```

**Watch each job:**
```
✅ Install, Train and Test       — 32 seconds
✅ Build Docker Image and Push   — 4 minutes (new image in ECR)
✅ Deploy to AWS EKS             — 2 minutes (rolling update)
```

**What happened automatically:**
```
Your code change detected
        ↓
Python installed on runner
        ↓
New model trained with 200 trees
        ↓
All 8 tests passed
        ↓
New Docker image built
        ↓
Image pushed to ECR with new tag
        ↓
EKS rolling update:
  New pod starts with new image ✅
  Old pod stops
  New pod starts ✅
  Old pod stops
        ↓
New model live — zero downtime ✅
```

Open your live URL:
```
http://abc123.ap-south-1.elb.amazonaws.com:8501
```

**The improved model is now serving predictions live!** ✅

---

## STEP 17 — Delete Cluster When Done (Save Cost)

> ⚠️ Always delete after practice. Cost is ₹600-800/day.

```bash
eksctl delete cluster \
  --name fraud-detection-cluster \
  --region ap-south-1
```

Wait 10-15 minutes. You will see:
```
All cluster resources were deleted ✅
```

---

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `docker daemon not running` | Docker Desktop closed | Open Docker Desktop |
| `docker pull hangs` | WiFi blocking Docker | Switch to mobile hotspot |
| `aws: command not found` | AWS CLI not installed | Install from aws.amazon.com/cli |
| `Unable to connect to cluster` | Wrong kubeconfig | Run `aws eks update-kubeconfig` again |
| `ImagePullBackOff` | EKS cannot pull from ECR | Check IAM permissions on EKS |
| `CrashLoopBackOff` | Container keeps crashing | `kubectl logs pod-name` to see error |
| `Pending` pods | Not enough EC2 capacity | Wait or increase node count |
| `Access denied ECR` | IAM missing ECR permission | Add `AmazonECRFullAccess` to IAM user |
| Pipeline Job 2 fails | GitHub Secrets not set | Add all 6 secrets in GitHub Settings |

---

## All Commands — Quick Reference

```bash
# ── Local setup ─────────────────────────────────────
source venv/Scripts/activate
pip install -r requirements.txt
cd src && python generate_data.py && python train.py && cd ..
pytest tests/test_model.py -v
streamlit run src/app.py

# ── Git ─────────────────────────────────────────────
git add . && git commit -m "message" && git push

# ── AWS CLI ─────────────────────────────────────────
aws configure
aws sts get-caller-identity
aws ecr create-repository --repository-name fraud-detection --region ap-south-1

# ── Docker + ECR ────────────────────────────────────
docker build -t fraud-detection:v1.0 .
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <ECR_URL>
docker tag fraud-detection:v1.0 <ECR_URL>/fraud-detection:latest
docker push <ECR_URL>/fraud-detection:latest

# ── EKS cluster ─────────────────────────────────────
eksctl create cluster --name fraud-detection-cluster --region ap-south-1 --node-type t3.medium --nodes 2
aws eks update-kubeconfig --region ap-south-1 --name fraud-detection-cluster
eksctl delete cluster --name fraud-detection-cluster --region ap-south-1

# ── Kubernetes ──────────────────────────────────────
kubectl apply -f k8s/deployment.yml
kubectl get pods
kubectl get service fraud-detection-service
kubectl logs <pod-name>
kubectl describe pod <pod-name>
kubectl rollout status deployment/fraud-detection
kubectl get nodes
```

---

## Cost Warning

```
EKS Control Plane  → $0.10/hour = ₹8/hour = ₹200/day
EC2 t3.medium x2   → $0.10/hour = ₹8/hour = ₹400/day
ECR storage        → free up to 500MB

Total per day running = ₹600-800/day

Always run:
eksctl delete cluster --name fraud-detection-cluster --region ap-south-1
after practice! ⚠️
```

---

*MLOps Syllabus — Deploy and Retrain ML Models on AWS*
*Author: Suresh D R | AI Product Developer & Technology Mentor*
