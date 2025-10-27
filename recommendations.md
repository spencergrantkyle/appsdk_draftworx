# Draftworx Tool Optimization Recommendations

## Current Tool Analysis

### Existing Tools and Their Discovery Potential

1. **draftworx.collect_context**
   - Current: "Use this when the user needs to specify or confirm entity details like jurisdiction, entity type, year end, and framework before client creation or upload."
   - **Issue**: Too technical, assumes user knows they need Draftworx
   - **Discovery Score**: 3/10

2. **draftworx.upload_trial_balance**
   - Current: "Use this when the user wants to upload a trial balance file and begin mapping. Do not use for invoice or bank export files."
   - **Issue**: Assumes user knows what a trial balance is
   - **Discovery Score**: 2/10

3. **draftworx.map_accounts**
   - Current: "Use this when a trial balance has been imported and mappings must be reviewed. Presents low confidence accounts for confirmation or correction."
   - **Issue**: Very technical, only relevant after other steps
   - **Discovery Score**: 1/10

4. **draftworx.recommend_template**
   - Current: "Use this when the user needs the correct template based on entity and jurisdiction. Do not use after a template has already been confirmed."
   - **Issue**: Assumes user knows about templates
   - **Discovery Score**: 2/10

5. **draftworx.create_draft**
   - Current: "Use this when context, mapping, and template are set and a Draftworx file should be created."
   - **Issue**: Final step, won't help with discovery
   - **Discovery Score**: 1/10

## Recommended New Tools for Better Discovery

### 1. Financial Statement Assessment Tool
```python
{
    "name": "draftworx.assess_financial_requirements",
    "title": "Assess Financial Statement Requirements",
    "description": "Use this when users ask about financial statements, annual reports, compliance requirements, or whether they need to prepare financial statements. Helps determine if they need IFRS, GAAP, or other reporting standards based on their business type, size, and jurisdiction.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "businessType": {"type": "string", "enum": ["company", "partnership", "sole_proprietor", "trust", "ngo", "government", "other"]},
            "jurisdiction": {"type": "string", "enum": ["ZA", "UK", "US", "AU", "CA", "EU", "other"]},
            "annualRevenue": {"type": "string", "enum": ["under_100k", "100k_to_1m", "1m_to_10m", "10m_to_50m", "over_50m", "unknown"]},
            "employeeCount": {"type": "string", "enum": ["1_to_10", "11_to_50", "51_to_250", "over_250", "unknown"]},
            "publicCompany": {"type": "boolean"},
            "industry": {"type": "string", "enum": ["manufacturing", "retail", "services", "financial", "technology", "construction", "healthcare", "education", "other"]}
        },
        "required": ["businessType", "jurisdiction"],
        "additionalProperties": False
    }
}
```

### 2. Financial Statement Education Tool
```python
{
    "name": "draftworx.explain_financial_statements",
    "title": "Explain Financial Statement Process",
    "description": "Use this when users ask 'what are financial statements', 'how to prepare financial statements', 'what is a trial balance', 'what is IFRS', 'what is GAAP', or need education about accounting standards and financial reporting requirements.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "topic": {"type": "string", "enum": ["what_are_financial_statements", "trial_balance_explanation", "ifrs_vs_gaap", "reporting_standards", "audit_requirements", "compliance_deadlines", "accounting_software"]},
            "jurisdiction": {"type": "string", "enum": ["ZA", "UK", "US", "AU", "CA", "EU", "other"]},
            "userLevel": {"type": "string", "enum": ["beginner", "intermediate", "professional"]}
        },
        "required": ["topic"],
        "additionalProperties": False
    }
}
```

### 3. Compliance Requirements Tool
```python
{
    "name": "draftworx.check_compliance_requirements",
    "title": "Check Compliance Requirements",
    "description": "Use this when users ask about filing deadlines, regulatory requirements, audit requirements, or compliance obligations for their business type and jurisdiction. Helps determine what financial statements they need to file and when.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "jurisdiction": {"type": "string", "enum": ["ZA", "UK", "US", "AU", "CA", "EU", "other"]},
            "entityType": {"type": "string", "enum": ["company", "partnership", "sole_prop", "ngo", "trust"]},
            "companySize": {"type": "string", "enum": ["micro", "small", "medium", "large", "public"]},
            "yearEnd": {"type": "string", "description": "YYYY-MM-DD"},
            "publicCompany": {"type": "boolean"}
        },
        "required": ["jurisdiction", "entityType"],
        "additionalProperties": False
    }
}
```

### 4. Trial Balance Preparation Guide
```python
{
    "name": "draftworx.guide_trial_balance_preparation",
    "title": "Guide Trial Balance Preparation",
    "description": "Use this when users ask 'how to prepare a trial balance', 'what is a trial balance', 'trial balance format', or need help understanding how to extract data from their accounting system for financial statement preparation.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "accountingSystem": {"type": "string", "enum": ["quickbooks", "xero", "sage", "pastel", "excel", "manual", "other"]},
            "dataFormat": {"type": "string", "enum": ["excel", "csv", "pdf", "printout", "digital_export"]},
            "userExperience": {"type": "string", "enum": ["beginner", "intermediate", "experienced"]}
        },
        "required": [],
        "additionalProperties": False
    }
}
```

## Optimized Existing Tools

### 1. Enhanced Collect Context
```python
{
    "name": "draftworx.collect_context",
    "title": "Collect Entity Context",
    "description": "Use this when users need to specify entity details for financial statement preparation. Triggers when users mention company registration, business type, reporting jurisdiction, year-end dates, or accounting standards like IFRS or GAAP.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "entityType": {"type": "string", "enum": ["company", "partnership", "sole_prop", "ngo", "trust"]},
            "jurisdiction": {"type": "string", "enum": ["ZA", "UK", "US", "AU", "CA", "EU", "other"]},
            "yearEnd": {"type": "string", "description": "YYYY-MM-DD"},
            "framework": {"type": "string", "enum": ["IFRS", "IFRS_SMEs", "US_GAAP", "UK_GAAP", "other"]}
        },
        "required": ["entityType", "jurisdiction", "yearEnd", "framework"],
        "additionalProperties": False
    }
}
```

### 2. Enhanced Upload Trial Balance
```python
{
    "name": "draftworx.upload_trial_balance",
    "title": "Upload Trial Balance",
    "description": "Use this when users want to upload their trial balance, general ledger, or accounting data for financial statement preparation. Accepts Excel, CSV files from QuickBooks, Xero, Sage, or other accounting systems.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "clientId": {"type": "string"},
            "fileId": {"type": "string"},
            "fileType": {"type": "string", "enum": ["xlsx", "csv", "zip"]},
            "accountingSystem": {"type": "string", "enum": ["quickbooks", "xero", "sage", "pastel", "excel", "other"]}
        },
        "required": ["clientId", "fileId", "fileType"],
        "additionalProperties": False
    }
}
```

### 3. Enhanced Map Accounts
```python
{
    "name": "draftworx.map_accounts",
    "title": "Map Chart of Accounts",
    "description": "Use this when trial balance data has been imported and account mappings need to be reviewed for financial statement preparation. Helps align general ledger accounts with standard financial statement line items.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "tbId": {"type": "string"},
            "confidenceThreshold": {"type": "number", "minimum": 0, "maximum": 1},
            "mappingType": {"type": "string", "enum": ["automatic", "manual", "hybrid"]}
        },
        "required": ["tbId", "confidenceThreshold"],
        "additionalProperties": False
    }
}
```

### 4. Enhanced Recommend Template
```python
{
    "name": "draftworx.recommend_template",
    "title": "Recommend Financial Statement Template",
    "description": "Use this when users need the appropriate financial statement template based on their entity type, jurisdiction, and reporting requirements. Helps select the correct format for IFRS, GAAP, or other standards.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "jurisdiction": {"type": "string", "enum": ["ZA", "UK", "US", "AU", "CA", "EU", "other"]},
            "entityType": {"type": "string", "enum": ["company", "partnership", "sole_prop", "ngo", "trust"]},
            "framework": {"type": "string", "enum": ["IFRS", "IFRS_SMEs", "US_GAAP", "UK_GAAP", "other"]},
            "companySize": {"type": "string", "enum": ["micro", "small", "medium", "large", "public"]}
        },
        "required": ["jurisdiction", "entityType", "framework"],
        "additionalProperties": False
    }
}
```

### 5. Enhanced Create Draft
```python
{
    "name": "draftworx.create_draft",
    "title": "Create Financial Statement Draft",
    "description": "Use this when all prerequisites are complete and users are ready to generate their financial statement draft. Creates professional financial statements including balance sheet, income statement, and cash flow statement.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "clientId": {"type": "string"},
            "tbId": {"type": "string"},
            "templateId": {"type": "string"},
            "includeNotes": {"type": "boolean"},
            "includeCashFlow": {"type": "boolean"}
        },
        "required": ["clientId", "tbId", "templateId"],
        "additionalProperties": False
    }
}
```

## Implementation Strategy

### Phase 1: Add Discovery Tools
1. Implement `assess_financial_requirements` - Highest priority for discovery
2. Implement `explain_financial_statements` - Educational tool for beginners
3. Implement `check_compliance_requirements` - Regulatory guidance

### Phase 2: Enhance Existing Tools
1. Update descriptions to include more natural language triggers
2. Add additional input parameters for better context
3. Include accounting system references

### Phase 3: Add Preparation Tools
1. Implement `guide_trial_balance_preparation`
2. Add workflow guidance tools
3. Create deadline reminder tools

## Key Discovery Triggers to Include

### Natural Language Patterns
- "Do I need financial statements?"
- "How to prepare annual reports?"
- "What is IFRS?"
- "Trial balance format"
- "Accounting compliance"
- "Financial reporting requirements"
- "Year-end financial statements"
- "Audit requirements"
- "Filing deadlines"

### Business Context Triggers
- Company registration discussions
- Compliance conversations
- Accounting software mentions
- Business size discussions
- Industry-specific requirements

## Expected Impact

### Discovery Improvement
- **Current**: 2/10 average discovery score
- **Target**: 8/10 average discovery score
- **Method**: Natural language triggers + educational tools

### User Journey Enhancement
1. **Awareness**: Assessment tools help users understand requirements
2. **Education**: Explanation tools build knowledge
3. **Preparation**: Guidance tools assist with data preparation
4. **Execution**: Existing tools handle the technical workflow

This approach transforms Draftworx from a technical tool that users must know about to a comprehensive financial statement solution that ChatGPT can proactively suggest based on user needs and questions.
