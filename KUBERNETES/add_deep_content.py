"""Add deeper explanatory content to lighter chapters (Ch 14-19)."""
import re

FPATH = r'c:\Users\owner\Desktop\DEV-DOCs\KUBERNETES\finOps_eng.html'
with open(FPATH, 'r', encoding='utf-8') as f:
    content = f.read()

enriched = 0

# Additional content for specific section IDs in lighter chapters
deep_content = {
    # Ch 14 — Exam Strategy: more study tips
    's14-1': '<p><strong>Why exam structure knowledge matters:</strong> The FCE exam isn\'t just testing your FinOps knowledge — it\'s testing your ability to perform under time pressure. Knowing that you have ~70 seconds per question helps you calibrate. Knowing there\'s no penalty for wrong answers frees you to guess on uncertain questions rather than freezing. The most common reason candidates fail isn\'t lack of knowledge — it\'s poor time management. They spend 3 minutes on a hard question early, then rush through easy questions at the end. Use the 3-pass strategy religiously.</p>',
    's14-1a': '<p><strong>What "multiple choice" really means on the FCE exam:</strong> Single-answer questions have exactly ONE correct answer among 4 options. Multi-select questions may have 2-4 correct answers — you must select ALL correct options to get credit. Partial credit is NOT awarded. Scenario-based questions present a paragraph-long scenario followed by 1-2 questions. These test your ability to APPLY FinOps principles, not just recall them. Expect to spend the most time on scenario questions (2-3 minutes each).</p>',
    's14-2': '<p><strong>Study prioritization by domain weight:</strong> Don\'t study all domains equally — weight your time by exam percentage. Cloud Financial Management (26%) deserves the most study hours. Optimization (22%) is second. Use domain-level practice tests to identify weak areas. If you score 90% on CFM but 50% on Principles, shift your study time to Principles even though it\'s a smaller domain — you need balanced competency to pass.</p>',
    
    # Ch 15 — Labs: add real-world context
    's15-1': '<p><strong>Why this lab matters for the exam:</strong> Cost allocation modeling is tested in multiple ways on the FCE exam. You may be asked to calculate proportional splits, identify the correct allocation method for a scenario, or troubleshoot why a team disputes their allocation. Practicing with real numbers (anihpj\'s $14,200/month bill, 5 teams, shared EKS costs) builds the muscle memory you need to answer these questions quickly and accurately on exam day.</p>',
    's15-2': '<p><strong>Tagging is the foundation of ALL FinOps:</strong> Without accurate tags, you can\'t allocate costs, can\'t do chargeback, and can\'t identify optimization opportunities. The FCE exam knows this — expect multiple questions about tagging strategy, enforcement, and troubleshooting. The hands-on lab of writing a Kyverno policy that enforces tags gives you practical experience that directly translates to policy-as-code questions on the exam.</p>',
    
    # Ch 17 — Multi-Cloud: add strategic depth
    's17-1': '<p><strong>The hidden cost of multi-cloud:</strong> While multi-cloud offers resilience and negotiation leverage, it comes with hidden costs that many organizations underestimate. Each additional cloud requires separate expertise (AWS vs Azure vs GCP have different consoles, APIs, and best practices). Cross-cloud data transfer adds latency AND cost. Tool consolidation becomes harder — you now need multi-cloud cost tools instead of cloud-native free tools. For anihpj at 15 engineers, multi-cloud would be counterproductive — the operational overhead exceeds any theoretical savings. The FCE exam may ask you to evaluate whether multi-cloud is right for a given scenario.</p>',
    's17-2': '<p><strong>Normalization is the key to multi-cloud cost comparison:</strong> AWS bills per-second for EC2, Azure bills per-minute, and GCP bills per-second with sustained use discounts. You can\'t directly compare an AWS EC2 bill line to an Azure VM bill line. You must normalize: convert everything to a common unit like $/vCPU-hour or $/GB-month. This is tedious but essential — without normalization, you\'re comparing apples to oranges. Third-party tools (CloudHealth, Vantage) automate this normalization, which is why they\'re worth the investment for multi-cloud organizations.</p>',
    's17-3': '<p><strong>Data gravity — the overlooked constraint:</strong> "Data gravity" refers to the tendency of data to attract applications and services. Once you have 10TB of data in AWS S3, moving it to Azure is expensive ($0.09/GB egress = $900) and slow (days at typical transfer speeds). Applications naturally cluster around where the data lives. This is why multi-cloud strategies often end up with different workloads on different clouds (analytics on GCP, web serving on AWS) rather than the same workload spanning clouds. The FCE exam tests awareness of data gravity as a constraint on cloud arbitrage and workload mobility.</p>',
    
    # Ch 18 — SaaS & Managed Services: expand build-vs-buy
    's18-1': '<p><strong>The SaaS cost visibility gap:</strong> At many organizations, SaaS spend equals 20-40% of cloud infrastructure spend but receives 0% of the FinOps attention. Why? Because SaaS tools don\'t appear in cloud bills. Your AWS CUR shows every EC2 instance to the penny, but a $150/month Salesforce license renewal? Invisible. The FCE exam increasingly tests awareness that FinOps scope extends beyond IaaS to include ALL technology costs — SaaS, managed services, support plans, and even software licenses. A mature FinOps practice tracks the full technology cost portfolio, not just the cloud bill.</p>',
    's18-3': '<p><strong>The managed service paradox:</strong> Managed services cost more per unit but almost always cost less in TOTAL when you include people costs. An engineer earning $150/hr who spends 2 hours/month on database maintenance costs $300/month — far more than the $14/month RDS premium. Yet organizations routinely self-manage to "save money." This is the #1 blind spot the FCE exam tests: always calculate TOTAL cost = infrastructure + (engineering hours x hourly rate). For most organizations under 500 engineers, managed services are the cheaper option when fully accounted for.</p>',
    
    # Ch 19 — Culture: add practical guidance
    's19-1': '<p><strong>The "cost-aware, not cost-obsessed" balance:</strong> The goal of FinOps culture isn\'t to make engineers think about costs constantly — it\'s to make cost a natural part of engineering decisions, like performance or security. An engineer shouldn\'t spend hours optimizing a $5/month resource. But they SHOULD know that choosing a larger instance type adds $100/month. The FCE exam tests this balance: the correct answer never involves extreme cost-cutting at the expense of reliability or velocity, but it also never ignores cost entirely. The FinOps Practitioner\'s role is to provide the data and guardrails that make cost-aware decisions easy.</p>',
    's19-2': '<p><strong>Gamification done right:</strong> The most successful FinOps gamification programs celebrate COST EFFICIENCY, not cost cutting. A team that reduced unit cost by 20% while growing traffic 30% deserves celebration. A team that cut costs 30% by disabling features is NOT a success story. Good metrics for gamification: unit cost trend (down = good), RI/SP coverage improvement, waste elimination (zombie resources cleaned up). Bad metrics: absolute spend (punishes teams that own more services), cost per engineer (creates headcount pressure).</p>',
    's19-3': '<p><strong>Training cadence that works:</strong> Annual FinOps training doesn\'t work — it\'s forgotten within weeks. The most effective training model: (1) 30-minute onboarding session for all new engineers (cost dashboard walkthrough, "this is where to see your costs"), (2) Monthly 15-minute "FinOps win of the month" in engineering all-hands (celebrate a team\'s optimization success), (3) Quarterly 45-minute deep-dive on a specific topic (Spot adoption, rightsizing, tagging strategy). Short, frequent, practical sessions beat long, infrequent lectures every time.</p>',
}

for sec_id, extra_para in deep_content.items():
    # Find section id
    id_pos = content.find(f'id="{sec_id}"')
    if id_pos == -1:
        continue
    
    # Find the h3/h4 closing tag
    h_end = content.find('</h4>', id_pos)
    if h_end == -1:
        h_end = content.find('</h3>', id_pos)
    if h_end == -1:
        continue
    
    # Find the first paragraph end after the heading
    p_end = content.find('</p>', h_end)
    if p_end == -1:
        continue
    
    # Insert after first paragraph
    content = content[:p_end + 4] + '\n' + extra_para + content[p_end + 4:]
    enriched += 1
    print(f'  +{sec_id}')

print(f'\nAdded {enriched} deep-content paragraphs')
with open(FPATH, 'w', encoding='utf-8') as f:
    f.write(content)
print('Saved.')
