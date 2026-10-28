# AWS VPC Peering Student Project Report

**Student Name:** Akhil
**Batch:** AWS Architect Associate
**Project Title:** AWS VPC Peering & Cross-VPC Secure Communication
**AWS Region:** ap-southeast-2 (Sydney)
**Completion Date:** 28 October 2026

---

## 1. Executive Summary & Project Objectives

This project implements a secure, isolated cross-VPC networking architecture connecting two independent Virtual Private Clouds (**VPC A** and **VPC B**) using **AWS VPC Peering**.

### Core Architectural Goals:
1. Establish non-overlapping IP address spaces (`10.10.0.0/16` for VPC A and `10.20.0.0/16` for VPC B).
2. Maintain strict workload isolation: EC2 instances `ewb-app-a` and `ewb-app-b` are strictly private with **no public IPv4 addresses** and no direct internet access.
3. Provide secure administrative access using a Bastion Host (`ewb-bastion`) located in VPC A's public subnet via SSH **ProxyJump**.
4. Enable direct, encrypted, private cross-VPC communication over the AWS network backbone via VPC Peering Connection (`ewb-a-b-peer`).
5. Enforce defense-in-depth security using stateful Security Groups scoped tightly to individual private `/32` IP addresses.

---

## 2. Resource Inventory & Network Specification

### 2.1 VPC & Subnet Allocation Matrix

| Resource Name | Type | CIDR Block | Parent VPC | Auto-Assign Public IPv4 |
| :--- | :--- | :--- | :--- | :--- |
| `ewb-vpc-a` | AWS::EC2::VPC | `10.10.0.0/16` | N/A | N/A |
| `ewb-a-public` | AWS::EC2::Subnet | `10.10.1.0/24` | `ewb-vpc-a` | Enabled (`true`) |
| `ewb-a-private` | AWS::EC2::Subnet | `10.10.2.0/24` | `ewb-vpc-a` | Disabled (`false`) |
| `ewb-vpc-b` | AWS::EC2::VPC | `10.20.0.0/16` | N/A | N/A |
| `ewb-b-private` | AWS::EC2::Subnet | `10.20.1.0/24` | `ewb-vpc-b` | Disabled (`false`) |

### 2.2 Compute Workload Inventory

| Instance Name | Instance Type | Private IPv4 | Public IPv4 | Subnet | Security Group | Key Pair |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ewb-bastion` | `t3.micro` | `10.10.1.10` | Auto-assigned | `ewb-a-public` | `ewb-sg-bastion` | `ewb-lab` |
| `ewb-app-a` | `t3.micro` | `10.10.2.10` | None | `ewb-a-private` | `ewb-sg-app-a` | `ewb-lab` |
| `ewb-app-b` | `t3.micro` | `10.20.1.10` | None | `ewb-b-private` | `ewb-sg-app-b` | `ewb-lab` |

---

## 3. Route Table Architecture & Peering Configuration

### 3.1 Route Tables Matrix

#### 1. `ewb-rt-a-public` (Associated with `ewb-a-public`)
| Destination | Target | Purpose / Traffic Description |
| :--- | :--- | :--- |
| `10.10.0.0/16` | `local` | Existing VPC A intra-VPC communication |
| `0.0.0.0/0` | `ewb-igw-a` | Bastion internet egress / SSH ingress |
| `10.20.0.0/16` | `ewb-a-b-peer` (pcx-...) | Bastion SSH ProxyJump route to VPC B |

#### 2. `ewb-rt-a-private` (Associated with `ewb-a-private`)
| Destination | Target | Purpose / Traffic Description |
| :--- | :--- | :--- |
| `10.10.0.0/16` | `local` | Existing VPC A intra-VPC communication |
| `10.20.0.0/16` | `ewb-a-b-peer` (pcx-...) | Forward path for App-A to VPC B (`10.20.1.10`) |

#### 3. `ewb-rt-b-private` (Associated with `ewb-b-private`)
| Destination | Target | Purpose / Traffic Description |
| :--- | :--- | :--- |
| `10.20.0.0/16` | `local` | Existing VPC B intra-VPC communication |
| `10.10.0.0/16` | `ewb-a-b-peer` (pcx-...) | Return path to VPC A (`10.10.2.10` & `10.10.1.10`) |

---

## 4. Security Group Rules & Ingress Control

### 4.1 Security Group Configuration Matrix

| Security Group | Ingress Type / Port | Source Address | Rationale & Security Scope |
| :--- | :--- | :--- | :--- |
| `ewb-sg-bastion` | SSH / TCP 22 | Admin IP (`<your-public-ip>/32`) | Restricts administrative access strictly to approved workstation. |
| `ewb-sg-app-a` | SSH / TCP 22 | `10.10.1.10/32` | Permits SSH connections strictly from Bastion private IP. |
| `ewb-sg-app-a` | ICMP Echo Request | `10.20.1.10/32` | Permits verification ping strictly from App-B private IP. |
| `ewb-sg-app-b` | SSH / TCP 22 | `10.10.1.10/32` | Permits SSH connections strictly from Bastion private IP. |
| `ewb-sg-app-b` | ICMP Echo Request | `10.10.2.10/32` | Permits verification ping strictly from App-A private IP. |

---

## 5. Verification, Testing & Controlled Failure Experiments

### 5.1 Verification Acceptance Suite

```
+----------------------------------------------------------------------------------------------------+
| Test # | Description / Command               | Location | Expected Result            | Status      |
+----------------------------------------------------------------------------------------------------+
| Test 01| Baseline Ping before Peering        | App-A    | ping -c 4 10.20.1.10       | PASSED      |
|        |                                     |          | Result: 100% packet loss   |             |
+----------------------------------------------------------------------------------------------------+
| Test 02| Forward Path Ping after Peering     | App-A    | ping -c 4 10.20.1.10       | PASSED      |
|        |                                     |          | Result: 4 replies, 0% loss |             |
+----------------------------------------------------------------------------------------------------+
| Test 03| Reverse Path Ping after Peering     | App-B    | ping -c 4 10.10.2.10       | PASSED      |
|        |                                     |          | Result: 4 replies, 0% loss |             |
+----------------------------------------------------------------------------------------------------+
| Test 04| Private SSH Access via ProxyJump    | Laptop   | ssh ewb-app-b              | PASSED      |
|        |                                     |          | Result: Shell on App-B     |             |
+----------------------------------------------------------------------------------------------------+
| Test 05| Workload Isolation Verification     | Console  | Public IPv4 field empty    | PASSED      |
|        |                                     |          | for App-A and App-B        |             |
+----------------------------------------------------------------------------------------------------+
```

### 5.2 Controlled Failure & Recovery Experiment

1. **Failure Injection:** Temporarily removed the inbound ICMP Echo Request rule (`10.10.2.10/32`) from `ewb-sg-app-b`.
2. **Observation:** Executing `ping -c 4 10.20.1.10` from `ewb-app-a` resulted in immediate request timeouts (`100% packet loss`).
3. **Technical Explanation:** Security Group ingress rules operate at the ENI level. Dropping the packet at the destination interface prevented ICMP Echo Requests from reaching the OS protocol stack.
4. **Recovery:** Restored the ICMP Echo Request rule (`10.10.2.10/32`) in `ewb-sg-app-b`.
5. **Result:** Rerunning `ping -c 4 10.20.1.10` from `ewb-app-a` immediately restored 100% packet transmission (`0% packet loss`).

---

## 6. Technical Viva & Troubleshooting Guide

### Q1: Why is the return route required in `ewb-rt-b-private`?
**Answer:** IP routing is inherently bidirectional. While the forward route in `ewb-rt-a-private` directs traffic destined for `10.20.1.10` across `ewb-a-b-peer` to VPC B, `ewb-app-b` must generate reply packets destined back to `10.10.2.10`. Without a return route pointing `10.10.0.0/16` to `ewb-a-b-peer` in `ewb-rt-b-private`, the return packets are dropped at the VPC B router, causing a timeout at the requester.

### Q2: Why is the App-B SSH source IP address the Bastion private IP (`10.10.1.10`)?
**Answer:** When connecting via SSH ProxyJump (`ssh -J ewb-bastion ec2-user@10.20.1.10`), the local client establishes an SSH tunnel to the Bastion host. The Bastion host then opens a separate TCP socket to `10.20.1.10` originating from its own private ENI (`10.10.1.10`). Therefore, `ewb-app-b` sees the incoming SSH connection originating from `10.10.1.10`, not the client's public IP.

### Q3: Why does an Active VPC Peering status not guarantee successful ping reachability?
**Answer:** An "Active" peering connection simply indicates that the AWS network link between VPCs is established. Successful end-to-end communication requires two additional layers:
1. **VPC Route Tables:** Both the source and destination subnets must have explicit routes pointing traffic to the peering connection ID (`pcx-...`).
2. **Security Groups & Network ACLs:** The destination host's Security Group must explicitly permit inbound ICMP/TCP traffic from the source IP address.

### Q4: Can VPC B access the Internet using VPC A's Internet Gateway over peering?
**Answer:** **No.** AWS VPC Peering **does not support edge-to-edge routing or gateway transit**. An Internet Gateway attached to VPC A cannot be utilized by instances in VPC B across a peering connection. To share internet access, a Transit Gateway or proxy solution must be deployed.

---

## 7. AWS Pre-Deployment Impact & Safety Report

- **Target AWS Region:** `ap-southeast-2` (Sydney)
- **Deployment Mechanism:** AWS CloudFormation (`infrastructure/vpc-peering.yaml`)
- **Resource Count:** 20 Managed AWS Resources (2 VPCs, 3 Subnets, 1 IGW, 3 Route Tables, 1 VPC Peering, 3 Security Groups, 3 EC2 Instances).
- **Estimated Cost:** < $0.05 USD per lab hour (Utilizes `t3.micro` Free Tier eligible instances; no NAT Gateways created).
- **Permissions Required:** `ec2:*`, `cloudformation:*`, `ssm:GetParameters`.

---

## 8. Responsible Cleanup & Termination

To ensure zero ongoing charges:
1. Delete the CloudFormation stack: `aws cloudformation delete-stack --stack-name ewb-vpc-peering-lab --region ap-southeast-2`
2. Verify all EC2 instances, EBS volumes, ENIs, Security Groups, and VPCs are fully terminated.
