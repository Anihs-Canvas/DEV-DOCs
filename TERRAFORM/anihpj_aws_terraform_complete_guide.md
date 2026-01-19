# 🚀 Complete AWS Infrastructure Guide for anihpj Job Portal
## Using Terraform, AWS, and Docker for Django Deployment

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Prerequisites](#prerequisites)
4. [Terraform Project Structure](#terraform-project-structure)
5. [AWS VPC & Networking](#aws-vpc-networking)
6. [RDS PostgreSQL Database](#rds-postgresql-database)
7. [ElastiCache Redis](#elasticache-redis)
8. [S3 Storage](#s3-storage)
9. [EC2 & Auto Scaling](#ec2-auto-scaling)
10. [Application Load Balancer](#application-load-balancer)
11. [CloudFront CDN](#cloudfront-cdn)
12. [Route 53 DNS](#route-53-dns)
13. [IAM Roles & Policies](#iam-roles-policies)
14. [Secrets Manager](#secrets-manager)
15. [CloudWatch Monitoring](#cloudwatch-monitoring)
16. [Docker Configuration](#docker-configuration)
17. [CI/CD Pipeline](#cicd-pipeline)
18. [Deployment Steps](#deployment-steps)
19. [Cost Estimation](#cost-estimation)
20. [Troubleshooting](#troubleshooting)

---

## 📊 Project Overview

### anihpj Job Portal Application

**Project Name**: anihpj  
**App Name**: jobpost  
**Purpose**: Job posting and recruitment platform  
**Framework**: Django 5.2.5  
**Database Models**: 5 core models

#### Database Schema

```
┌─────────────────┐
│   Django User   │
│  (Built-in)     │
└────────┬────────┘
         │ OneToOne
         ▼
┌─────────────────┐         ┌─────────────────┐
│     Author      │         │    Location     │
│  - company      │         │  - street       │
│  - designation  │         │  - city         │
└────────┬────────┘         │  - state        │
         │ ForeignKey       │  - country      │
         │                  │  - zip          │
         ▼                  └────────┬────────┘
┌─────────────────┐                 │ OneToOne
│    JobPost      │◄────────────────┘
│  - title        │
│  - description  │         ┌─────────────────┐
│  - salary       │         │     Skills      │
│  - type         │◄────────┤  - name         │
│  - slug         │ M2M     │  (Python, JS,   │
│  - date         │         │   Django, etc)  │
│  - expiry       │         └─────────────────┘
└─────────────────┘
```

#### API Endpoints

| Endpoint | Method | Description | Example Response |
|----------|--------|-------------|------------------|
| `/jobpost/jobs/` | GET | List all job postings | JSON array of jobs |
| `/jobpost/jobs/<id>/` | GET | Get single job details | JSON job object |
| `/jobpost/skills/` | GET | List all skills | JSON array of skills |

---

## 🏗️ Architecture Diagram

### Three-Tier Architecture

```
                                    ┌─────────────────────┐
                                    │   Internet Users    │
                                    └──────────┬──────────┘
                                               │
                                               │ HTTPS
                                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                          AWS CLOUD - us-east-1                        │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     Route 53 DNS                              │   │
│  │              jobs.anihpj.com → CloudFront                     │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                 │                                     │
│                                 ▼                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    CloudFront CDN                             │   │
│  │         Static Files, Media, CSS, JS, Images                  │   │
│  └───────────────────────┬──────────────────────────────────────┘   │
│                          │                                            │
│                          ▼                                            │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              Application Load Balancer (ALB)                  │   │
│  │                    SSL/TLS Termination                        │   │
│  └───────────────────────┬──────────────────────────────────────┘   │
│                          │                                            │
│   ┌──────────────────────┴──────────────────────┐                   │
│   │                VPC: 10.0.0.0/16              │                   │
│   │                                              │                   │
│   │  ┌────────────────────────────────────────┐ │                   │
│   │  │      Public Subnets (ALB Tier)         │ │                   │
│   │  │   10.0.1.0/24 (us-east-1a)             │ │                   │
│   │  │   10.0.2.0/24 (us-east-1b)             │ │                   │
│   │  └────────────────┬───────────────────────┘ │                   │
│   │                   │                          │                   │
│   │  ┌────────────────▼───────────────────────┐ │                   │
│   │  │    Private Subnets (App Tier)          │ │                   │
│   │  │   10.0.10.0/24 (us-east-1a)            │ │                   │
│   │  │   10.0.11.0/24 (us-east-1b)            │ │                   │
│   │  │                                         │ │                   │
│   │  │  ┌──────────┐    ┌──────────┐          │ │                   │
│   │  │  │   EC2    │    │   EC2    │          │ │                   │
│   │  │  │  Django  │    │  Django  │          │ │                   │
│   │  │  │ Gunicorn │    │ Gunicorn │          │ │                   │
│   │  │  │  Nginx   │    │  Nginx   │          │ │                   │
│   │  │  └──────────┘    └──────────┘          │ │                   │
│   │  │                                         │ │                   │
│   │  │       ┌──────────────────┐             │ │                   │
│   │  │       │ ElastiCache Redis│             │ │                   │
│   │  │       │ (Session Store)  │             │ │                   │
│   │  │       └──────────────────┘             │ │                   │
│   │  └────────────────┬───────────────────────┘ │                   │
│   │                   │                          │                   │
│   │  ┌────────────────▼───────────────────────┐ │                   │
│   │  │    Private Subnets (Data Tier)         │ │                   │
│   │  │   10.0.20.0/24 (us-east-1a)            │ │                   │
│   │  │   10.0.21.0/24 (us-east-1b)            │ │                   │
│   │  │                                         │ │                   │
│   │  │       ┌──────────────────┐             │ │                   │
│   │  │       │  RDS PostgreSQL  │             │ │                   │
│   │  │       │   Multi-AZ       │             │ │                   │
│   │  │       │  (Primary + RR)  │             │ │                   │
│   │  │       └──────────────────┘             │ │                   │
│   │  └────────────────────────────────────────┘ │                   │
│   │                                              │                   │
│   │  ┌────────────────────────────────────────┐ │                   │
│   │  │        NAT Gateway (us-east-1a)        │ │                   │
│   │  │        NAT Gateway (us-east-1b)        │ │                   │
│   │  └────────────────────────────────────────┘ │                   │
│   │                                              │                   │
│   └──────────────────────────────────────────────┘                   │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                      S3 Buckets                               │   │
│  │   - anihpj-static (CSS, JS)                                   │   │
│  │   - anihpj-media (User uploads, company logos)                │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                   AWS Secrets Manager                         │   │
│  │   - DB credentials, SECRET_KEY, API keys                      │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    CloudWatch Logs                            │   │
│  │   - Application logs, Access logs, Error logs                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Prerequisites

### Local Development Environment

1. **Install Required Tools**
   ```bash
   # Terraform
   choco install terraform  # Windows
   brew install terraform   # macOS
   
   # AWS CLI
   choco install awscli     # Windows
   brew install awscli      # macOS
   
   # Docker Desktop
   # Download from https://www.docker.com/products/docker-desktop
   
   # Python 3.11+
   choco install python     # Windows
   brew install python      # macOS
   ```

2. **Configure AWS Credentials**
   ```bash
   aws configure
   # AWS Access Key ID: YOUR_ACCESS_KEY
   # AWS Secret Access Key: YOUR_SECRET_KEY
   # Default region name: us-east-1
   # Default output format: json
   ```

3. **Verify Installations**
   ```bash
   terraform version
   aws --version
   docker --version
   python --version
   ```

### AWS Account Setup

- [ ] AWS Account with billing enabled
- [ ] IAM user with AdministratorAccess or specific permissions
- [ ] Route 53 hosted zone for your domain
- [ ] ACM certificate for HTTPS

---

## 📁 Terraform Project Structure

### Recommended Directory Layout

```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   ├── backend.tf
│   │   └── outputs.tf
│   ├── staging/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars
│   │   ├── backend.tf
│   │   └── outputs.tf
│   └── production/
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       ├── backend.tf
│       └── outputs.tf
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── rds/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── ec2/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── alb/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── s3/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── cloudfront/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   ├── elasticache/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── README.md
│   └── iam/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── README.md
└── global/
    ├── route53/
    │   ├── main.tf
    │   └── outputs.tf
    └── acm/
        ├── main.tf
        └── outputs.tf
```

### Create Base Structure

```bash
# Create directory structure
mkdir -p terraform/{environments/{dev,staging,production},modules/{vpc,rds,ec2,alb,s3,cloudfront,elasticache,iam},global/{route53,acm}}

# Create placeholder files
for env in dev staging production; do
  touch terraform/environments/$env/{main.tf,variables.tf,terraform.tfvars,backend.tf,outputs.tf}
done

for module in vpc rds ec2 alb s3 cloudfront elasticache iam; do
  touch terraform/modules/$module/{main.tf,variables.tf,outputs.tf,README.md}
done
```

---

## 🌐 AWS VPC & Networking

### VPC Module Structure

**File**: `terraform/modules/vpc/main.tf`

```hcl
# ============================================
# VPC Module for anihpj Job Portal
# Three-tier architecture: Public, Private App, Private Data
# ============================================

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ============================================
# VPC
# ============================================
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-vpc"
    }
  )
}

# ============================================
# Internet Gateway
# ============================================
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-igw"
    }
  )
}

# ============================================
# Public Subnets (for ALB)
# ============================================
resource "aws_subnet" "public" {
  count = length(var.availability_zones)

  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-public-${var.availability_zones[count.index]}"
      Tier = "public"
    }
  )
}

# ============================================
# Private App Subnets (for EC2/ECS)
# ============================================
resource "aws_subnet" "private_app" {
  count = length(var.availability_zones)

  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_app_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-private-app-${var.availability_zones[count.index]}"
      Tier = "private-app"
    }
  )
}

# ============================================
# Private Data Subnets (for RDS)
# ============================================
resource "aws_subnet" "private_data" {
  count = length(var.availability_zones)

  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_data_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-private-data-${var.availability_zones[count.index]}"
      Tier = "private-data"
    }
  )
}

# ============================================
# Elastic IPs for NAT Gateways
# ============================================
resource "aws_eip" "nat" {
  count  = length(var.availability_zones)
  domain = "vpc"

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-nat-eip-${var.availability_zones[count.index]}"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# ============================================
# NAT Gateways
# ============================================
resource "aws_nat_gateway" "main" {
  count = length(var.availability_zones)

  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-nat-${var.availability_zones[count.index]}"
    }
  )

  depends_on = [aws_internet_gateway.main]
}

# ============================================
# Public Route Table
# ============================================
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-public-rt"
    }
  )
}

# ============================================
# Public Route Table Associations
# ============================================
resource "aws_route_table_association" "public" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# ============================================
# Private App Route Tables
# ============================================
resource "aws_route_table" "private_app" {
  count = length(var.availability_zones)

  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-private-app-rt-${var.availability_zones[count.index]}"
    }
  )
}

# ============================================
# Private App Route Table Associations
# ============================================
resource "aws_route_table_association" "private_app" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.private_app[count.index].id
  route_table_id = aws_route_table.private_app[count.index].id
}

# ============================================
# Private Data Route Tables
# ============================================
resource "aws_route_table" "private_data" {
  count = length(var.availability_zones)

  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-private-data-rt-${var.availability_zones[count.index]}"
    }
  )
}

# ============================================
# Private Data Route Table Associations
# ============================================
resource "aws_route_table_association" "private_data" {
  count = length(var.availability_zones)

  subnet_id      = aws_subnet.private_data[count.index].id
  route_table_id = aws_route_table.private_data[count.index].id
}

# ============================================
# VPC Flow Logs
# ============================================
resource "aws_flow_log" "main" {
  iam_role_arn    = aws_iam_role.vpc_flow_log.arn
  log_destination = aws_cloudwatch_log_group.vpc_flow_log.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-vpc-flow-log"
    }
  )
}

resource "aws_cloudwatch_log_group" "vpc_flow_log" {
  name              = "/aws/vpc/${var.project_name}"
  retention_in_days = 30

  tags = var.common_tags
}

resource "aws_iam_role" "vpc_flow_log" {
  name = "${var.project_name}-vpc-flow-log-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "vpc-flow-logs.amazonaws.com"
      }
    }]
  })

  tags = var.common_tags
}

resource "aws_iam_role_policy" "vpc_flow_log" {
  name = "${var.project_name}-vpc-flow-log-policy"
  role = aws_iam_role.vpc_flow_log.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ]
      Effect   = "Allow"
      Resource = "*"
    }]
  })
}
```

### VPC Variables

**File**: `terraform/modules/vpc/variables.tf`

```hcl
variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "anihpj"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_app_subnet_cidrs" {
  description = "CIDR blocks for private app subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "private_data_subnet_cidrs" {
  description = "CIDR blocks for private data subnets"
  type        = list(string)
  default     = ["10.0.20.0/24", "10.0.21.0/24"]
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "anihpj"
    ManagedBy   = "Terraform"
    Environment = "dev"
  }
}
```

### VPC Outputs

**File**: `terraform/modules/vpc/outputs.tf`

```hcl
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  description = "IDs of private app subnets"
  value       = aws_subnet.private_app[*].id
}

output "private_data_subnet_ids" {
  description = "IDs of private data subnets"
  value       = aws_subnet.private_data[*].id
}

output "nat_gateway_ids" {
  description = "IDs of NAT gateways"
  value       = aws_nat_gateway.main[*].id
}

output "internet_gateway_id" {
  description = "ID of the internet gateway"
  value       = aws_internet_gateway.main.id
}
```

---

*This is Part 1 of the documentation. Would you like me to continue with the next sections (RDS PostgreSQL Database, ElastiCache Redis, etc.) step by step?*
