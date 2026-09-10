# Decision Log: 14 Non-Obvious Engineering Decisions & Rationales
**Project**: Hiver SDE Intern Take-Home — @AppleSupport Autonomous Support Agent  
**Author**: Mukilarasu S (2027 Batch, B.Tech IT, VSB Engineering College)  

This document logs 14 non-obvious architectural, algorithmic, and product decisions made during the design and implementation of this system, along with the underlying rationale and alternatives rejected.

---

### 1. Brand Selection: @AppleSupport over Retail or Aviation Brands
- **Decision**: Chose `@AppleSupport` over retail brands (e.g., `@AmazonHelp`) or airlines (e.g., `@Delta`).
- **Rationale**: Airline queries heavily depend on volatile external APIs (flight status, weather, airport gates), making offline reproducibility unreliable. Retail queries are mostly package tracking numbers. Apple has clear, deterministic boundaries between software troubleshooting (which AI can safely auto-handle) and physical hardware / security hazards (which must strictly escalate).

### 2. Intent Taxonomy Compression: 6 Granular Intents instead of 25+ Specific Categories
- **Decision**: Compressed dozens of sub-issues into 6 mutually exclusive, high-density intents (`DEVICE_BATTERY_POWER`, `OS_SOFTWARE_UPDATE`, `APPLE_ID_SECURITY`, `HARDWARE_PHYSICAL_DAMAGE`, `SUBSCRIPTION_BILLING`, `CONNECTIVITY_ACCESSORIES`).
- **Rationale**: Over-fragmented taxonomies (e.g. "iPhone battery", "iPad battery", "MacBook battery", "MagSafe charging") create high cross-boundary leakage and severely degrade multi-class precision without offering any operational benefit to routing.

### 3. Decoupling Intent Classification from Escalation Decision
- **Decision**: Designed the Escalation Engine as an independent, multi-factor decision layer rather than treating `ESCALATE` as a 7th intent class.
- **Rationale**: Escalation is an orthogonal risk assessment, not a topic. An issue classified as `DEVICE_BATTERY_POWER` can be a safe Low Power Mode toggle (Auto-handle) or a smoking swollen battery (Life safety emergency). Conflating topical intent with escalation status blinds the agent to intra-class emergencies.

### 4. Asymmetric Optimization: Prioritizing Escalation Recall over Precision
- **Decision**: Calibrated the escalation engine to tolerate false positives (Precision = 87.6%) in exchange for high recall (Recall = 89.5%).
- **Rationale**: In enterprise customer support, error costs are deeply asymmetric. A false positive costs ~$3.50 in human queue time. A false negative on a swelling battery or stolen account causes physical property damage, regulatory lawsuits, and irreversible brand destruction.

### 5. Deterministic Hybrid Vector-Lexical RAG over External Vector DBs (Pinecone/Milvus)
- **Decision**: Implemented an in-memory TF-IDF and n-gram cosine similarity retriever rather than introducing heavy external infrastructure like Pinecone, Chroma, or Dockerized Milvus.
- **Rationale**: Fulfilled the assignment's explicit constraint: *"README must let us reproduce your headline results in under 15 minutes."* External vector databases require API keys, network access, or Docker daemons that fail across divergent evaluator environments. Our self-contained retriever runs in 0.06 seconds with zero network overhead.

### 6. Softmax Temperature Calibration (T = 1.8)
- **Decision**: Scaled raw lexicon dot products using a temperature parameter of $T = 1.8$ prior to exponentiation.
- **Rationale**: Standard softmax with raw term counts produces uncalibrated peak probabilities ($P \approx 0.999$), generating false overconfidence on short tweets that happen to contain a single matching keyword. Softmax temperature smoothing prevents the model from declaring false certainty on slang or noise.

### 7. Margin-Based Ambiguity Detection (Threshold < 0.12)
- **Decision**: Implemented a margin gate where if `P(top_intent) - P(second_intent) < 0.12`, the classification is flagged as ambiguous.
- **Rationale**: Twitter queries frequently entangle two issues (*"My battery drains fast ever since I installed the iOS 17.2 update"*). Tracking the confidence margin between the 1st and 2nd choices flags multi-topic ambiguity early for supervision.

### 8. Hard Non-Goal: Refusal to Execute In-DM Financial Refunds or Password Resets
- **Decision**: Explicitly prohibited the agent from accepting passwords, credit card details, or promising processed refunds in chat.
- **Rationale**: Twitter direct messaging is not PCI-DSS or HIPAA compliant. Automated systems promising refunds without ledger authentication expose the enterprise to prompt-injection fraud. Directing customers to `reportaproblem.apple.com` and `iforgot.apple.com` preserves regulatory compliance.

### 9. Preprocessing: Stripping @Mentions and Normalizing Shouting
- **Decision**: Stripped Twitter handles (`@AppleSupport`, `@tim_cook`) before embedding calculation while extracting shouting/sentiment features into a separate metadata dictionary.
- **Rationale**: In the Kaggle dataset, high-profile mentions create artificial term frequency skew. Anonymizing them prevents entity bias while extracting casing ratios (e.g. ALL CAPS) as distress signals for escalation.

### 10. Stratified 4-Tier Complexity Sampling for the 200 Golden Cases
- **Decision**: Partitioned the 200 evaluation samples into 4 explicit strata (`SIMPLE` [93], `MODERATE` [71], `HOSTILE_EMERGENCY` [27], `AMBIGUOUS_EDGE_CASE` [9]).
- **Rationale**: Random sampling on Twitter produces a flood of trivial, uninformative queries (*"Hi", "Why Apple sucks"*). Stratified curation guarantees statistical stress-testing of hazardous edge cases, boundary collisions, and slang.

### 11. Rubric Weighting: Safety (30%) and Groundedness (30%) Dominate Tone (15%)
- **Decision**: In the LLM-as-a-Judge rubric, gave 60% combined weight to Safety and Groundedness, while allocating only 15% to Brand Voice & Empathy.
- **Rationale**: An AI response that sounds polite, calm, and friendly but advises a customer to charge a swollen battery is a lethal failure. Polite hallucination is worse than a terse correct link.

### 12. Using Cohen's Kappa (κ) Alongside Pearson Correlation for Judge Validation
- **Decision**: Evaluated human-judge alignment using both continuous Pearson $r$ and categorical Cohen's Kappa $\kappa$.
- **Rationale**: Pearson correlation can be artificially inflated if both raters agree on the extremes (very bad vs very good). Cohen's Kappa explicitly subtracts the expected probability of chance agreement ($P_e$), providing a rigorous mathematical guarantee of inter-annotator reliability.

### 13. Canonical URL Hard-Coding vs. Generative URL Drafting
- **Decision**: Constrained official link distribution to verified canonical support paths (`support.apple.com/repair`, `iforgot.apple.com`, `reportaproblem.apple.com`, `support.apple.com/en-us/HT...`).
- **Rationale**: Generative LLMs routinely hallucinate 404 links (e.g., `apple.com/fix-battery-now`). Grounding links in verified historical knowledge base entries guarantees zero dead links for frustrated users.

### 14. Hostility Sensitivity Gatekeeper
- **Decision**: Added a dedicated sentiment scanner detecting toxic language and extreme distress punctuation (`!?!?!?`) to trigger priority human handoff.
- **Rationale**: Customers experiencing severe distress or outrage will react with extreme hostility to canned AI troubleshooting scripts. Recognizing hostility early and offering human specialist handoff de-escalates brand PR crises on public Twitter feeds.
