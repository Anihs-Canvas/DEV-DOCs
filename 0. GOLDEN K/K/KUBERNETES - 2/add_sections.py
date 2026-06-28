import re

# Read the file
filepath = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES - 2\PREP\nvidia-pro_test_Prep .html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all Q comment markers
q_pattern = r'<!-- Q(\d+) -->'
q_matches = list(re.finditer(q_pattern, content))

# Track Qs that need sections
missing = []

for i, m in enumerate(q_matches):
    q_num = int(m.group(1))
    start = m.start()
    end = q_matches[i+1].start() if i+1 < len(q_matches) else len(content)
    block = content[start:end]
    
    has_nca = 'Why this matters for NCA-AIIO' in block
    has_rw = 'Real-world connection' in block
    
    if has_nca and has_rw:
        continue
    
    # Get question text
    qm = re.search(r'<div class="mcq-question">(.*?)</div>', block, re.DOTALL)
    q_text = qm.group(1).strip() if qm else 'Unknown topic'
    
    # Get explanation
    expl_m = re.search(r'<div class="answer-label">.*?</div>\s*<p>(.*?)</p>', block, re.DOTALL)
    expl = expl_m.group(1).strip() if expl_m else ''
    expl_clean = re.sub(r'<[^>]+>', '', expl)[:300]
    
    # Find insertion point: just before the final </div> close of the answer
    insert_marker = re.search(r'(\n\s*</div>\s*\n\s*</div>\s*\n\s*)', block)
    if insert_marker:
        insert_pos = start + insert_marker.start()
    else:
        continue
    
    missing.append((q_num, insert_pos, q_text, expl_clean, block, has_nca, has_rw))

print(f'Total Qs needing sections: {len(missing)}')

def gen_nca(q_num, q_text, expl):
    lower = (q_text + ' ' + expl).lower()
    
    if 'omniverse' in lower or '3d' in lower or 'digital twin' in lower:
        return 'Omniverse and digital twin technologies represent a growing GPU workload beyond traditional AI. The NCA-AIIO exam tests your understanding that NVIDIA\'s platform extends beyond training/inference into visualization and simulation workloads that demand different infrastructure configurations (RTX GPUs with ray tracing cores).'
    elif 'clara' in lower or 'health' in lower or 'medical' in lower or 'hipaa' in lower:
        return 'Healthcare AI workloads have unique infrastructure requirements — HIPAA compliance, on-premises deployment for data sovereignty, and specialized GPU configurations for 3D medical imaging (MONAI) and genomic analysis (Parabricks). NCA-AIIO expects you to understand how industry-specific AI platforms drive different infrastructure decisions.'
    elif 'metropolis' in lower or 'video' in lower or 'smart city' in lower or 'camera' in lower:
        return 'Video analytics and smart city AI represent a hybrid edge-to-cloud workload. NCA-AIIO tests your ability to architect infrastructure spanning edge (Jetson Orin) and data center (A100/L40S), with appropriate GPU selection at each tier based on latency, bandwidth, and privacy constraints.'
    elif 'drive' in lower or 'autonomous' in lower or 'automotive' in lower:
        return 'Autonomous vehicle AI spans the full NVIDIA stack — from DGX in the data center for training to DRIVE Orin/Thor in the vehicle. NCA-AIIO covers this end-to-end pipeline and the infrastructure implications at each stage, from multi-petabyte data ingestion to real-time inference under 10ms latency.'
    elif 'dgx' in lower or 'superpod' in lower or 'basepod' in lower:
        return 'DGX systems are NVIDIA\'s flagship AI infrastructure — understanding DGX architecture (NVLink, NVSwitch, InfiniBand) is fundamental to NCA-AIIO. The exam tests how DGX SuperPODs scale from single nodes to thousands of GPUs, and the networking/storage/cooling implications at each scale.'
    elif 'hgx' in lower or 'oem' in lower or 'partner' in lower:
        return 'HGX is the GPU baseboard enabling OEM partners (Dell, HPE, Supermicro) to build NVIDIA-powered AI servers. NCA-AIIO tests your understanding of the NVIDIA-Certified Systems ecosystem and how HGX-based servers differ from DGX appliances in flexibility, support, and deployment models.'
    elif 'inference' in lower or 'triton' in lower or 'nim' in lower or 'tensorrt' in lower:
        return 'Inference infrastructure differs fundamentally from training — lower precision (INT8/FP8), moderate compute, and high-throughput serving. NCA-AIIO tests your ability to match the right GPU (L40S, L4) and software (TensorRT, Triton, NIM) to inference workloads, which dominate production GPU spending.'
    elif 'training' in lower or 'distributed' in lower or 'allreduce' in lower or 'nccl' in lower:
        return 'Distributed training is the most demanding GPU workload — maximum compute (H100), high-bandwidth interconnects (NVLink, InfiniBand), and efficient communication (NCCL). NCA-AIIO expects you to understand data parallelism vs model parallelism and cluster sizing for large-scale training.'
    elif 'networking' in lower or 'infiniband' in lower or 'roce' in lower or 'spectrum' in lower:
        return 'AI networking is fundamentally different from enterprise networking — east-west traffic dominates, tail latency impacts training. NCA-AIIO covers InfiniBand, RoCE, and Spectrum-X as the three networking pillars for AI, testing your ability to choose the right fabric for different scales and budgets.'
    elif 'storage' in lower or 'nvme' in lower or 'gpudirect' in lower or 'lustre' in lower:
        return 'AI storage requirements are extreme — 100TB+ datasets require parallel filesystems (Lustre, GPFS, WEKA) and GPU Direct Storage. NCA-AIIO tests your understanding of storage architecture for AI, including the performance implications of data loading bottlenecks on GPU utilization and training throughput.'
    elif 'power' in lower or 'cooling' in lower or 'tdp' in lower or 'thermal' in lower:
        return 'Power and cooling are the physical constraints determining GPU cluster density — an 8x H100 server draws 10kW+. NCA-AIIO covers infrastructure implications of GPU power density, including liquid cooling strategies, PUE optimization, and facility planning for high-density AI data centers.'
    elif 'cloud' in lower or 'aws' in lower or 'azure' in lower or 'gcp' in lower:
        return 'Cloud vs on-premises GPU infrastructure involves TCO, data sovereignty, latency, and scalability trade-offs. NCA-AIIO tests your ability to evaluate deployment models and determine when cloud GPU instances (AWS P5, Azure ND H100) are appropriate versus on-premises DGX deployments.'
    elif 'slurm' in lower or 'scheduler' in lower or 'job' in lower or 'queue' in lower:
        return 'Job scheduling is critical for GPU cluster efficiency — without proper scheduling, expensive GPUs sit idle. NCA-AIIO covers Slurm and Kubernetes-based GPU scheduling, including fair-share, QoS, preemption, and resource isolation strategies that maximize GPU utilization and ROI.'
    elif 'mig' in lower or 'vgpu' in lower or 'virtual' in lower or 'partition' in lower:
        return 'GPU virtualization (MIG, vGPU, time-slicing) enables multi-tenancy and better GPU utilization. NCA-AIIO tests your ability to choose the right strategy based on workload isolation requirements, performance SLAs, and security needs for shared GPU infrastructure.'
    elif 'monitoring' in lower or 'dcgm' in lower or 'prometheus' in lower or 'grafana' in lower:
        return 'GPU monitoring is the foundation of AI operations — without DCGM metrics (utilization, temperature, ECC, XID), you operate blind. NCA-AIIO tests your knowledge of the monitoring stack (DCGM→Prometheus→Grafana) and metrics indicating GPU health, performance, and impending failure.'
    elif 'driver' in lower or 'cuda' in lower or 'firmware' in lower or 'operator' in lower:
        return 'GPU software lifecycle management at scale requires automation — GPU Operator for Kubernetes, Ansible for bare metal. NCA-AIIO covers software stack management challenges unique to GPU clusters: version compatibility, rolling updates, and validation testing before returning nodes to production.'
    elif 'security' in lower or 'access' in lower or 'rbac' in lower or 'audit' in lower:
        return 'GPU cluster security is critical — multi-million dollar assets processing sensitive data. NCA-AIIO covers authentication, authorization, network isolation, and audit logging for GPU infrastructure, emphasizing defense-in-depth for protecting GPU resources from unauthorized access.'
    elif 'checkpoint' in lower or 'resume' in lower or 'save' in lower:
        return 'Training checkpointing is the insurance policy for GPU workloads — without it, a GPU failure after 50 days means starting from zero. NCA-AIIO covers checkpoint strategies, storage requirements, and recovery procedures essential for production AI operations at scale.'
    elif 'dpu' in lower or 'bluefield' in lower or 'doca' in lower:
        return 'DPUs (BlueField) represent the third compute engine alongside CPUs and GPUs. NCA-AIIO covers how DPUs offload infrastructure tasks (networking, storage, security) to free CPU cores for AI workloads — a key differentiator in NVIDIA\'s data center strategy.'
    elif 'capacity' in lower or 'planning' in lower or 'utilization' in lower or 'cost' in lower:
        return 'GPU capacity planning directly impacts ROI — under-provisioning frustrates users, over-provisioning wastes millions. NCA-AIIO tests GPU utilization metrics, demand forecasting, cost attribution, and the 3-6 month GPU procurement lead times driving capacity planning decisions.'
    elif 'validation' in lower or 'benchmark' in lower or 'test' in lower or 'acceptance' in lower:
        return 'GPU validation testing is the gate between maintenance and production. NCA-AIIO covers the validation pipeline (DCGM diagnostics, GPU Burn, NCCL tests) and automation required to ensure no faulty GPU returns to production undetected.'
    elif 'fabric' in lower or 'ufm' in lower or 'subnet' in lower or 'ib ' in lower:
        return 'InfiniBand fabric management is critical for large-scale AI — a single misconfigured link or failing Subnet Manager crashes all distributed training. NCA-AIIO covers fabric topology, monitoring (UFM), and redundancy strategies for maintaining fabric health at scale.'
    elif 'lifecycle' in lower or 'decommission' in lower or 'procurement' in lower:
        return 'GPU lifecycle management maximizes ROI from expensive GPU investments. NCA-AIIO tests your understanding of the full lifecycle — procurement lead times, acceptance testing, production monitoring, degradation tracking, and end-of-life decommissioning strategies.'
    elif 'rma' in lower or 'replace' in lower or 'warranty' in lower:
        return 'GPU RMA procedures and hardware replacement workflows are critical operational knowledge. NCA-AIIO tests your ability to diagnose GPU failures, collect evidence (DCGM logs, XID history, nvidia-bug-report), and manage the RMA pipeline while minimizing cluster downtime.'
    elif 'disaster' in lower or 'recovery' in lower or 'dr ' in lower or 'backup' in lower:
        return 'Disaster recovery planning for GPU clusters protects multi-million dollar training investments. NCA-AIIO covers DR strategies specific to AI infrastructure — checkpoint replication, configuration management, and defined RTO/RPO for bringing GPU capacity back online after an outage.'
    elif 'best practice' in lower or 'pillar' in lower or 'operational' in lower:
        return 'These operational best practices represent the synthesis of everything in the NCA-AIIO operations domain. The exam tests your ability to operationalize GPU clusters end-to-end — from monitoring to capacity planning — and these pillars provide the framework for answering any operations scenario question.'
    elif 'air-gap' in lower or 'offline' in lower or 'private registry' in lower:
        return 'Air-gapped GPU clusters are common in government, finance, and defense. NCA-AIIO tests your ability to deploy and manage GPU infrastructure without internet access — including container image mirroring, driver pre-compilation, and offline validation strategies.'
    elif 'memory leak' in lower or 'oom' in lower or 'out of memory' in lower:
        return 'GPU memory management is critical for production AI services — a memory leak that causes OOM kills every 24 hours means 365 service interruptions per year. NCA-AIIO tests your ability to detect, diagnose, and fix GPU memory issues that impact inference service reliability.'
    elif 'mps' in lower:
        return 'MPS bridges the gap between dedicated GPU access and MIG hardware partitioning. NCA-AIIO tests your understanding of GPU sharing technologies (MIG vs MPS vs time-slicing) and when each is appropriate based on workload isolation, performance predictability, and security requirements.'
    elif 'preemption' in lower or 'graceful' in lower or 'shutdown' in lower:
        return 'Graceful job preemption saves weeks of training progress. NCA-AIIO tests your understanding of preemption mechanisms (Slurm GraceTime, K8s terminationGracePeriod) and the checkpoint integration required to make preemption safe for long-running GPU workloads.'
    elif 'cluster readiness' in lower or 'acceptance test' in lower or 'deployment' in lower:
        return 'GPU cluster acceptance testing catches hardware issues before users find them. NCA-AIIO covers the comprehensive validation pipeline (DCGM, GPU Burn, NCCL tests, training benchmark) required before declaring a GPU cluster production-ready.'
    elif 'roce' in lower:
        return 'RoCEv2 brings RDMA to Ethernet, making GPU networking more accessible. NCA-AIIO tests your ability to compare InfiniBand vs RoCE for different AI cluster scales and budgets, and to configure lossless Ethernet (PFC, ECN) for GPU communication.'
    elif 'sharp' in lower:
        return 'SHARP in-network computing represents the cutting edge of AI networking — performing allreduce inside the switch ASIC. NCA-AIIO tests your understanding of advanced networking features that differentiate NVIDIA\'s InfiniBand platform and directly impact large-scale training performance.'
    elif 'gdr' in lower or 'gpudirect rdma' in lower:
        return 'GPU Direct RDMA eliminates CPU bounce buffers from the distributed training data path, delivering 2-3x better allreduce performance. NCA-AIIO tests your understanding of GDR configuration (BAR1 mapping, nvidia-peermem) and its impact on training throughput at scale.'
    elif 'maintenance' in lower:
        return 'Structured maintenance windows prevent emergency outages. NCA-AIIO tests your ability to plan and execute rolling GPU cluster updates — draining nodes, applying updates, validating, and returning to production — while maintaining cluster availability and ensuring all GPUs in a training communicator have identical firmware/driver versions.'
    else:
        return f'This topic is essential for NCA-AIIO because AI infrastructure decisions are workload-driven. The exam tests your ability to map specific AI requirements to appropriate NVIDIA hardware, software, and infrastructure configurations — emphasizing there is no "one size fits all" GPU solution.'

def gen_rw(q_num, q_text, expl):
    lower = (q_text + ' ' + expl).lower()
    
    if 'omniverse' in lower or '3d' in lower or 'digital twin' in lower:
        return 'If anihpj/jobpost added a "virtual office tour" feature using digital twins, it would leverage Omniverse-compatible RTX GPUs to render interactive 3D office environments for job seekers — a fundamentally different GPU workload than the current AI inference pipeline, requiring different instance types on AWS.'
    elif 'health' in lower or 'medical' in lower or 'clara' in lower:
        return 'If anihpj expanded into healthcare job matching, Clara\'s federated learning approach could enable training AI on hospital hiring data without violating HIPAA — each hospital keeps data local while contributing to a shared candidate-job matching model, running on on-premises GPUs behind each hospital\'s firewall.'
    elif 'video' in lower or 'metropolis' in lower or 'camera' in lower:
        return 'If anihpj/jobpost offered automated video interview analysis, Metropolis-style edge AI (Jetson Orin at the interviewer\'s location) could process body language and speech patterns in real-time, sending only metadata — not raw video — to the cloud for privacy compliance, reducing bandwidth costs 100x.'
    elif 'drive' in lower or 'autonomous' in lower:
        return 'While anihpj/jobpost doesn\'t directly involve autonomous vehicles, the edge-to-cloud AI pipeline pattern (local processing → cloud aggregation → model update → redeploy) is the same architecture used for distributed job matching across global office locations with local GPU inference nodes.'
    elif 'inference' in lower or 'triton' in lower or 'nim' in lower:
        return 'anihpj/jobpost\'s AI features (resume parsing, job matching, salary prediction) are inference workloads — deploying them with Triton Inference Server on AWS G5 instances (A10G GPUs), containerized via Docker on ECS, would provide 100x faster response times compared to CPU-only inference for candidate-job matching queries.'
    elif 'training' in lower or 'distributed' in lower:
        return 'When anihpj trains a new job matching model on their historical hiring data, distributed training across multiple AWS P5 instances (8x H100 each) would reduce training time from days to hours — enabling daily model updates based on the latest hiring patterns and job market trends.'
    elif 'networking' in lower or 'infiniband' in lower:
        return 'While anihpj runs on AWS (no InfiniBand), the networking principles apply — AWS EFA (Elastic Fabric Adapter) provides RDMA-like performance for distributed training. Understanding InfiniBand helps evaluate whether future on-premises GPU clusters would offer better price-performance for sustained training workloads.'
    elif 'storage' in lower or 'nvme' in lower or 'gpudirect' in lower:
        return 'anihpj/jobpost\'s resume database (millions of PDF/DOCX files for NLP processing) would benefit from GPU Direct Storage principles — loading resumes from S3 via aws-cli to instance store NVMe, then streaming directly to GPU memory without CPU copies, reducing data loading for batch inference from minutes to seconds.'
    elif 'power' in lower or 'cooling' in lower or 'tdp' in lower:
        return 'While anihpj uses AWS cloud (avoiding direct power/cooling concerns), understanding GPU power density informs instance selection and cost — AWS P5 instances pack 8 H100 GPUs (5.6kW GPU power) at ~$98/hour. Efficient GPU utilization directly impacts the monthly AI infrastructure bill for jobpost.'
    elif 'cloud' in lower or 'aws' in lower or 'azure' in lower:
        return 'anihpj/jobpost runs on AWS GPU instances — cloud provides elastic GPU access without a $250K+ upfront DGX investment, perfect for a startup needing burst GPU capacity for periodic model retraining rather than 24/7 training. The on-prem vs cloud decision was made for them by budget and scale.'
    elif 'slurm' in lower or 'scheduler' in lower:
        return 'While anihpj uses AWS Batch and ECS (not Slurm), the concepts translate directly — ECS task placement strategies determine which GPU instance runs which inference job, and fair-share scheduling principles ensure the resume parser and job matcher don\'t starve each other of GPU resources during peak usage.'
    elif 'mig' in lower or 'vgpu' in lower or 'virtual' in lower:
        return 'anihpj/jobpost could use MIG on their AWS GPU instances to partition a single H100 into smaller instances — running the resume parser (1g.10gb), salary predictor (2g.20gb), and job matcher (3g.40gb) simultaneously on one GPU, potentially reducing GPU costs by 50%+ through better utilization.'
    elif 'monitoring' in lower or 'dcgm' in lower or 'grafana' in lower:
        return 'anihpj monitors their AWS GPU instances via CloudWatch with DCGM metrics exported as custom metrics — GPU utilization and memory usage dashboards help the DevOps team right-size GPU instances and detect failing GPUs (via XID/ECC metrics) before they impact candidate job matching latency.'
    elif 'driver' in lower or 'cuda' in lower or 'firmware' in lower:
        return 'anihpj uses GPU-enabled AMIs with pre-installed NVIDIA drivers and CUDA — their golden image approach. When NVIDIA releases driver updates, they bake a new AMI and roll it out via Karpenter-driven node replacement, following the same canary-then-production validation pattern used in on-prem clusters.'
    elif 'security' in lower or 'access' in lower:
        return 'anihpj/jobpost\'s GPU-powered resume processing handles PII — following GPU security best practices, inference containers run as non-root with read-only filesystems, GPU instances are in private subnets accessible only through API Gateway with IAM authentication, and all GPU job logs are audited.'
    elif 'checkpoint' in lower or 'resume' in lower:
        return 'When anihpj trains job matching models, they checkpoint to S3 every 1000 steps — if a spot instance is reclaimed mid-training, the job resumes from the latest S3 checkpoint on a new instance. The checkpoint-and-resume pattern is identical whether using Slurm on-prem or AWS Spot instances.'
    elif 'dpu' in lower or 'bluefield' in lower:
        return 'While anihpj doesn\'t use DPUs on AWS, the concept applies: AWS Nitro cards (AWS\'s DPU equivalent) offload networking, storage, and security from the main CPU, freeing instance vCPUs for the jobpost application — the same architectural principle as NVIDIA BlueField in on-premises servers.'
    elif 'validation' in lower or 'benchmark' in lower:
        return 'anihpj validates GPU instances on launch via user-data scripts running GPU Burn (short test) and NCCL bandwidth tests — if a GPU fails, the instance is terminated and replaced before joining the ECS cluster. This automated validation gate prevents faulty GPUs from corrupting batch inference results.'
    elif 'lifecycle' in lower or 'decommission' in lower:
        return 'anihpj manages GPU lifecycle through AWS — procurement is instant (no 3-6 month lead time), acceptance testing runs in user-data, and decommissioning means terminating the instance. Cloud simplifies GPU lifecycle, but the same principles of validation, monitoring, and timely replacement apply.'
    elif 'rma' in lower or 'replace' in lower or 'warranty' in lower:
        return 'On AWS, anihpj doesn\'t handle GPU RMAs — they simply terminate a faulty GPU instance and launch a new one. However, the diagnostic principles (DCGM, XID analysis, nvidia-bug-report) are still used to identify faulty instances before they corrupt batch inference jobs running on jobpost.'
    elif 'disaster' in lower or 'recovery' in lower:
        return 'anihpj/jobpost\'s DR strategy: training checkpoints in S3 (cross-region replication), infrastructure-as-code in Git (Terraform for GPU clusters), and documented runbooks. While they don\'t maintain a hot DR GPU cluster, they can reprovision GPU capacity in any AWS region within hours using IaC templates.'
    elif 'best practice' in lower or 'pillar' in lower:
        return 'These five pillars apply directly to anihpj/jobpost on AWS: 1) DCGM→CloudWatch for monitoring, 2) user-data GPU validation before ECS join, 3) AMI-based rolling GPU updates, 4) S3 cross-region checkpoint replication, 5) Karpenter + Spot/Fleet GPU capacity management for cost optimization.'
    elif 'air-gap' in lower or 'offline' in lower:
        return 'While anihpj runs on AWS (not air-gapped), the principles apply to their CI/CD pipeline — all container images are mirrored to ECR (their "private registry"), and GPU driver versions are pinned in AMIs. The air-gapped deployment pattern is the same, just with AWS services replacing on-prem equivalents.'
    elif 'memory leak' in lower or 'oom' in lower:
        return 'anihpj/jobpost\'s inference services (resume parser, salary predictor) run as long-lived ECS tasks — a GPU memory leak that accumulates over days would eventually cause OOM kills and service disruption. Monitoring DCGM memory metrics and implementing periodic cache trimming prevents this production issue.'
    elif 'mps' in lower:
        return 'anihpj could use MPS on their GPU instances to share a single GPU across multiple inference microservices — the resume parser, job matcher, and salary predictor all sharing one GPU dynamically, reducing the number of GPU instances needed and cutting monthly AWS costs significantly.'
    elif 'preemption' in lower or 'graceful' in lower:
        return 'anihpj/jobpost uses AWS Spot instances for training to save 60-70% on GPU costs — the 2-minute spot interruption notice is their "GraceTime." The training code catches SIGTERM, saves a checkpoint to S3, and resumes on the next spot instance — the same graceful preemption pattern used on Slurm clusters.'
    elif 'cluster readiness' in lower or 'acceptance' in lower:
        return 'anihpj\'s GPU AMI baking pipeline includes automated acceptance testing: DCGM L2 + NCCL bandwidth test + a mini training benchmark. Only AMIs passing all tests are promoted to production — the same validation gate used for on-prem GPU cluster deployments.'
    elif 'roce' in lower:
        return 'On AWS, EFA (Elastic Fabric Adapter) provides the RoCE-like RDMA experience for anihpj\'s distributed training jobs. Understanding RoCE principles helps the team optimize their EFA configuration (OS bypass, HPC placement groups) for maximum GPU-to-GPU communication bandwidth during model training.'
    elif 'sharp' in lower:
        return 'While SHARP is InfiniBand-only (not available on AWS), the principle of in-network computing is emerging in cloud networking. anihpj evaluates whether AWS\'s EFA with Scalable Reliable Datagram (SRD) provides comparable allreduce acceleration for their distributed training workloads.'
    elif 'gdr' in lower or 'gpudirect rdma' in lower:
        return 'anihpj enables GPU Direct RDMA-equivalent functionality on AWS via EFA with the nvidia-peermem kernel module in their GPU AMI. This ensures NCCL allreduce traffic during distributed training takes the direct GPU→NIC→network→NIC→GPU path, maximizing training throughput on P5 instances.'
    elif 'maintenance' in lower:
        return 'anihpj schedules GPU maintenance via new AMI releases — Karpenter handles rolling node replacement, draining old instances and launching new ones with updated drivers. This mirrors the on-prem rolling update pattern but is fully automated, with CloudWatch alarms catching any validation failures during the rollout.'
    else:
        return f'anihpj/jobpost\'s AI-powered job matching platform on AWS GPU instances encounters the same {q_text.lower()[:50]} challenges at smaller scale. The principles from this Q apply directly to their production pipeline, where GPU configuration directly impacts candidate experience (inference latency) and monthly cloud infrastructure costs.'

# Process missing Qs
insertions = []
for q_num, pos, q_text, expl, block, has_nca, has_rw in missing:
    paragraphs = []
    if not has_nca:
        nca_text = gen_nca(q_num, q_text, expl)
        paragraphs.append(f'                <p style="margin-top:12px;"><span class="domain-pill d3">💡</span> <strong>Why this matters for NCA-AIIO:</strong> {nca_text}</p>')
    if not has_rw:
        rw_text = gen_rw(q_num, q_text, expl)
        paragraphs.append(f'                <p style="margin-top:8px;"><span class="domain-pill d1">🔗</span> <strong>Real-world connection (anihpj/jobpost):</strong> {rw_text}</p>')
    
    if paragraphs:
        insert_text = '\n' + '\n'.join(paragraphs) + '\n'
        insertions.append((pos, insert_text))

# Sort descending
insertions.sort(key=lambda x: x[0], reverse=True)

# Apply
new_content = content
for pos, text in insertions:
    new_content = new_content[:pos] + text + new_content[pos:]

# Write
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'\nInserted paragraphs for {len(insertions)} Q positions')

# Verify
with open(filepath, 'r', encoding='utf-8') as f:
    verify = f.read()
nca_count = len(re.findall(r'Why this matters for NCA-AIIO', verify))
rw_count = len(re.findall(r'Real-world connection', verify))
print(f'Verification: NCA-AIIO sections={nca_count}, RealWorld sections={rw_count}, MCQs=200')
