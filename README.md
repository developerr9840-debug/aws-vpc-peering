# AWS VPC Peering Student Project — EWB Cloud Labs

![Project Status](https://img.shields.io/badge/AWS%20CloudFormation-Validated-success)
![AWS Region](https://img.shields.io/badge/AWS%20Region-ap--southeast--2-blue)
![License](https://img.shields.io/badge/License-MIT-green)

This repository contains the complete, production-ready AWS CloudFormation infrastructure template, architecture design, SSH ProxyJump configuration, local validation test suite, and comprehensive student report for the **EWB Cloud Labs — AWS VPC Peering Student Project**.

---

## 📌 Executive Architecture Summary

The infrastructure establishes secure, cross-VPC private connectivity between two non-overlapping Virtual Private Clouds (**VPC A** and **VPC B**) using AWS VPC Peering.

```
+-----------------------------------------------------------------------------------+
|                                 AWS REGION: ap-southeast-2                         |
|                                                                                   |
|  +-------------------------------------+   VPC Peering   +---------------------+  |
|  | VPC A: ewb-vpc-a (10.10.0.0/16)    |  ewb-a-b-peer   | VPC B: ewb-vpc-b    |  |
|  |                                     |<===============>| (10.20.0.0/16)      |  |
|  | +---------------------------------+ |    (pcx-...)    |                     |  |
|  | | Public Subnet: ewb-a-public     | |                 | +-----------------+ |  |
|  | | CIDR: 10.10.1.0/24             | |                 | | Private Subnet  | |  |
|  | | Route: 0.0.0.0/0 -> ewb-igw-a   | |                 | | ewb-b-private   | |  |
|  | |                                 | |                 | | 10.20.1.0/24    | |  |
|  | | [ewb-bastion] 10.10.1.10        | |                 | |                 | |  |
|  | | (Public IPv4 Auto-assigned)     | |                 | | [ewb-app-b]     | |  |
|  | +---------------------------------+ |                 | | 10.20.1.10      | |  |
|  |                                     |                 | | (No Public IP)  | |  |
|  | +---------------------------------+ |                 | +-----------------+ |  |
|  | | Private Subnet: ewb-a-private   | |                 |                     |  |
|  | | CIDR: 10.10.2.0/24             | |                 |                     |  |
|  | |                                 | |                 |                     |  |
|  | | [ewb-app-a] 10.10.2.10          | |                 |                     |  |
|  | | (No Public IP)                  | |                 |                     |  |
|  | +---------------------------------+ |                 |                     |  |
|  +-------------------------------------+                 +---------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 🛠️ Repository Structure

```
.
├── infrastructure/
│   └── vpc-peering.yaml        # Complete AWS CloudFormation Template
├── templates/
│   └── ssh_config              # Local SSH ProxyJump configuration
├── scripts/
│   ├── validate_template.sh    # CloudFormation & YAML syntax linter
│   ├── simulated_tests.py     # Offline network routing & SG logic simulator
│   └── generate_pdf.py         # Student project report PDF generator
├── docs/
│   ├── architecture-diagram.png# High-resolution PNG architecture diagram
│   ├── architecture.svg        # Scalable Vector Graphics architecture diagram
│   └── EWB_VPC_Peering_Report.md # Full Markdown Student Project Report
├── Akhil_EWB_VPC_Peering.pdf   # Formatted Final Student Deliverable PDF
└── README.md                   # Project overview & deployment documentation
```

---

## 📊 Resource Inventory Plan

| Resource Name | Type | CIDR / IP | Subnet / VPC | Security Group | Public IPv4 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ewb-vpc-a** | AWS::EC2::VPC | `10.10.0.0/16` | N/A | N/A | N/A |
| **ewb-a-public** | AWS::EC2::Subnet | `10.10.1.0/24` | VPC A | N/A | Enabled |
| **ewb-a-private** | AWS::EC2::Subnet | `10.10.2.0/24` | VPC A | N/A | Disabled |
| **ewb-vpc-b** | AWS::EC2::VPC | `10.20.0.0/16` | N/A | N/A | N/A |
| **ewb-b-private** | AWS::EC2::Subnet | `10.20.1.0/24` | VPC B | N/A | Disabled |
| **ewb-igw-a** | AWS::EC2::InternetGateway | N/A | VPC A | N/A | N/A |
| **ewb-a-b-peer** | AWS::EC2::VPCPeeringConnection | Peering | VPC A <-> VPC B | N/A | N/A |
| **ewb-bastion** | AWS::EC2::Instance (t3.micro)| `10.10.1.10` | ewb-a-public | `ewb-sg-bastion` | Yes (Auto) |
| **ewb-app-a** | AWS::EC2::Instance (t3.micro)| `10.10.2.10` | ewb-a-private | `ewb-sg-app-a` | No |
| **ewb-app-b** | AWS::EC2::Instance (t3.micro)| `10.20.1.10` | ewb-b-private | `ewb-sg-app-b` | No |

---

## 🚦 Security Group Rules Matrix

| Security Group | Ingress Traffic | Source IP / Range | Port / Protocol | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **ewb-sg-bastion** | SSH | Admin Public IP /32 | TCP / 22 | Administration from laptop |
| **ewb-sg-app-a** | SSH | `10.10.1.10/32` | TCP / 22 | ProxyJump access from Bastion |
| **ewb-sg-app-a** | ICMP Echo Request | `10.20.1.10/32` | Custom ICMP (8/0) | Verification ping from App-B |
| **ewb-sg-app-b** | SSH | `10.10.1.10/32` | TCP / 22 | ProxyJump access from Bastion |
| **ewb-sg-app-b** | ICMP Echo Request | `10.10.2.10/32` | Custom ICMP (8/0) | Verification ping from App-A |

---

## 🧪 Testing Distinction & Validation Summary

Testing for this project is strictly categorized into three distinct domains:

### 1. Static Validation
* Executed via `./scripts/validate_template.sh` (`cfn-lint 1.58.0` and Python YAML schema verification).
* **Result:** 0 syntax errors, 0 warnings. All 20 required CloudFormation resources are defined.

### 2. Offline Simulated Network Tests
* Executed via `python3 scripts/simulated_tests.py`.
* **Note:** These 6 simulated tests validate route table and security group **logic** in software. They represent dry-run verification and are **not proof of live AWS network connectivity**.
* **Simulated Test Results:**
  - `Test 01 (Simulated Baseline)`: PASS (Ping fails before peering routes added)
  - `Test 02 (Simulated Forward Path)`: PASS (App-A -> App-B 0% packet loss)
  - `Test 03 (Simulated Reverse Path)`: PASS (App-B -> App-A 0% packet loss)
  - `Test 04 (Simulated Controlled Failure)`: PASS (Removing SG ICMP rule drops traffic)
  - `Test 05 (Simulated Controlled Recovery)`: PASS (Restoring SG ICMP rule resumes traffic)
  - `Test 06 (Simulated Isolation Check)`: PASS (App-A & App-B have no public IPv4 addresses)

### 3. Live AWS Operational Observations & Diagnosis
* **Observed Live Behavior:** Executing a ping directly from the Bastion host (`10.10.1.10`) to App-B (`10.20.1.10`) resulted in **100% packet loss** (`Request timed out`).
* **Technical Analysis:** This packet loss is **expected, correct, and by design**. According to workbook page 6, App-B's security group (`ewb-sg-app-b`) strictly allows ICMP Echo Requests from App-A (`10.10.2.10/32`), **NOT from the Bastion host (`10.10.1.10/32`)**. The packet drop proves that Security Group ingress filtering is functioning correctly. End-to-end live ICMP verification requires running the ping directly inside App-A (`10.10.2.10`) after stack deployment.
* **Status:** End-to-end live AWS connectivity is pending deployment and live execution inside App-A.

---

## 🚀 AWS CloudFormation Deployment Instructions

To deploy this stack to your AWS Account in region `ap-southeast-2`:

### Step 1: Create Lab Key Pair
Create an EC2 RSA Key Pair named `ewb-lab` in `ap-southeast-2`:
```bash
aws ec2 create-key-pair \
  --key-name ewb-lab \
  --key-type rsa \
  --key-format pem \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/ewb-lab.pem

chmod 400 ~/.ssh/ewb-lab.pem
```
*Note: Store `~/.ssh/ewb-lab.pem` safely on your local client machine. Never upload or commit private keys to GitHub or EC2 instances.*

### Step 2: Deploy CloudFormation Stack
```bash
aws cloudformation create-stack \
  --stack-name ewb-vpc-peering-lab \
  --template-body file://infrastructure/vpc-peering.yaml \
  --parameters \
      ParameterKey=KeyPairName,ParameterValue=ewb-lab \
      ParameterKey=SSHLocation,ParameterValue=$(curl -s https://checkip.amazonaws.com)/32 \
      ParameterKey=StudentName,ParameterValue=Akhil \
  --region ap-southeast-2
```

### Step 3: Monitor Stack Creation
```bash
aws cloudformation wait stack-create-complete \
  --stack-name ewb-vpc-peering-lab \
  --region ap-southeast-2
```

---

## 🔑 SSH ProxyJump Configuration & Testing

Add the contents of `templates/ssh_config` to your local `~/.ssh/config`:

```sshconfig
Host ewb-bastion
    HostName <BASTION_PUBLIC_IP>
    User ec2-user
    IdentityFile ~/.ssh/ewb-lab.pem
    IdentitiesOnly yes

Host ewb-app-a
    HostName 10.10.2.10
    User ec2-user
    IdentityFile ~/.ssh/ewb-lab.pem
    IdentitiesOnly yes
    ProxyJump ewb-bastion

Host ewb-app-b
    HostName 10.20.1.10
    User ec2-user
    IdentityFile ~/.ssh/ewb-lab.pem
    IdentitiesOnly yes
    ProxyJump ewb-bastion
```

### Testing Connections
```bash
# Connect to Bastion
ssh ewb-bastion

# Connect to App-A via Bastion ProxyJump
ssh ewb-app-a

# Connect to App-B via Bastion ProxyJump
ssh ewb-app-b
```

---

## 🧹 AWS Resource Cleanup Procedure

To avoid ongoing AWS charges after completing the lab:

```bash
aws cloudformation delete-stack \
  --stack-name ewb-vpc-peering-lab \
  --region ap-southeast-2

aws cloudformation wait stack-delete-complete \
  --stack-name ewb-vpc-peering-lab \
  --region ap-southeast-2
```

---

## 📄 Student Deliverable PDF

The complete project report is compiled in `Akhil_EWB_VPC_Peering.pdf`. It contains all detailed technical answers, architecture breakdown, route table matrices, controlled failure explanations, simulation logs, and live AWS diagnostic observations.
