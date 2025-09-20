# Hybrid Code Review Methodology

## Overview
This document provides a comprehensive prompting strategy that combines automated MCP code review tools with manual critical analysis to achieve thorough, accurate, and actionable code reviews.

## Background
Based on comparative analysis, automated tools excel at comprehensive scanning and precise line identification, while manual review provides superior depth for security, architecture, and business logic assessment. This hybrid approach leverages the complementary strengths of both methods.

## Methodology

### Optimal Hybrid Code Review Prompt Template

```
Please conduct a comprehensive code review of [filename] using both automated MCP tools and manual critical analysis. Structure your review using this hybrid methodology:

**PHASE 1: Automated Comprehensive Scanning**
- Run MCP general code review for syntax, style, and basic patterns (use full file path like "C:\\Users\\..." for file_path parameter)
- Execute MCP security analysis for vulnerability detection (use full file path like "C:\\Users\\..." for file_path parameter)
- Perform MCP performance analysis for optimization opportunities (use full file path like "C:\\Users\\..." for file_path parameter)
- Conduct MCP API handling analysis for integration best practices (use full file path like "C:\\Users\\..." for file_path parameter)
- [Add data processing analysis if applicable for data-heavy scripts] (use full file path like "C:\\Users\\..." for file_path parameter)

**PHASE 2: Manual Critical Analysis**
- Architecture review: Design patterns, coupling, global state, code organization
- Security deep-dive: Hardcoded credentials, input validation, data exposure risks
- Business logic validation: Domain rules, calculations, data flow correctness
- Error handling strategy: Exception types, propagation, recovery patterns
- Maintainability assessment: Code complexity, testability, documentation

**PHASE 3: Synthesis & Cross-Validation**
- Compare automated vs manual findings
- Identify issues caught by only one method
- Validate and prioritize by severity and business impact
- Note any false positives or tool limitations

**PHASE 4: Actionable Recommendations**
- Immediate fixes: Specific line-level changes
- Strategic improvements: Architecture and design enhancements  
- Implementation priority: Critical → High → Medium → Low
- Provide code examples for key improvements

Please ensure you leverage the complementary strengths of both approaches: automated tools for comprehensive coverage and precise identification, manual analysis for context, domain understanding, and critical security/architecture issues that tools typically miss.
```

## Context-Specific Variations

### For Data Processing Scripts
```
"Please conduct a comprehensive code review of [filename] using both automated MCP tools and manual critical analysis. This is a data processing script that handles API calls, performs [specific domain] calculations, and processes [type] metrics. Pay special attention to data validation, API security, performance with large datasets, and business logic correctness for [domain-specific] calculations."
```

### For Web Applications
```
"Please conduct a comprehensive code review of [filename] using both automated MCP tools and manual critical analysis. This is a web application component that handles [functionality]. Focus particularly on security vulnerabilities, input validation, authentication/authorization, and web-specific performance concerns."
```

### For API Integration Code
```
"Please conduct a comprehensive code review of [filename] using both automated MCP tools and manual critical analysis. This code integrates with external APIs for [purpose]. Emphasize API security, error handling, retry logic, rate limiting, and data transformation accuracy."
```

## Why This Approach Works

### Addresses Key Analysis Gaps
1. **Security Coverage**: Manual analysis catches hardcoded credentials and architectural vulnerabilities that automated tools miss
2. **Performance Optimization**: MCP tools provide line-specific performance issues while manual review adds context about memory management and scalability
3. **Code Quality**: Automated tools catch style violations comprehensively, manual review assesses maintainability and design patterns
4. **Business Logic**: Manual analysis validates domain-specific calculations and data flow that tools can't understand

### Leverages Complementary Strengths

| Aspect | Automated Tools | Manual Analysis | Combined Benefit |
|--------|----------------|-----------------|------------------|
| **Coverage** | Comprehensive scanning | Deep, contextual | Complete assessment |
| **Precision** | Exact line numbers | Strategic insights | Actionable specificity |
| **Speed** | Instant analysis | Thoughtful review | Efficient thoroughness |
| **Expertise** | Consistent rules | Domain knowledge | Balanced perspective |

## Expected Outcomes

Using this hybrid methodology, you should receive:
- ✅ **Comprehensive coverage** from automated scanning
- ✅ **Critical insights** from human judgment  
- ✅ **Prioritized recommendations** based on real impact
- ✅ **Actionable solutions** with specific implementation guidance

## Best Practices

1. **Always specify the code type/domain** in your prompt for better context
2. **Request both immediate fixes and strategic improvements**
3. **Ask for cross-validation** between automated and manual findings
4. **Emphasize areas of particular concern** based on the code's purpose
5. **Request code examples** for recommended improvements

## Usage Examples

### Basic Usage
```
Please conduct a comprehensive code review of user_authentication.py using both automated MCP tools and manual critical analysis. [rest of template]
```

### With Domain Context
```
Please conduct a comprehensive code review of payment_processor.py using both automated MCP tools and manual critical analysis. This handles financial transactions and PCI compliance requirements. Pay special attention to security vulnerabilities, data encryption, and regulatory compliance patterns. [rest of template]
```

### For Legacy Code
```
Please conduct a comprehensive code review of legacy_data_migration.py using both automated MCP tools and manual critical analysis. This is legacy code that needs modernization. Focus on identifying technical debt, deprecated patterns, and modernization opportunities alongside standard security and performance concerns. [rest of template]
```

---

*This methodology was developed based on empirical comparison of automated MCP tool analysis versus manual code review, identifying the unique strengths and blind spots of each approach.*
