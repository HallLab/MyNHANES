# Rule Documentation: rule_00002

## Rule Information
- **Rule Name:** rule_00002
- **Version:** 1.0
- **Description:** This rule identifies participants who use medications associated with cholesterol management and adjusts their LDL and total cholesterol levels to values that would be expected without medication use. The rule generates a new variable identifying these participants and provides the adjusted LDL and total cholesterol variables in the Normalized dataset.

Distribution of Samples with use one of these drugs:

- ATORVASTATIN_CALCIUM
- SIMVASTATIN
- PRAVASTATIN_SODIUM
- FLUVASTATIN_SODIUM

# LDL and TC values are reduced by 30% and 20% respectively
df_nhanes['LBDLDL_N'] = df_nhanes.apply(lambda row: row['LBDLDL'] / 0.7 if row.name in df_medications.index else row['LBDLDL'], axis=1)
df_nhanes['LBXTC_N'] = df_nhanes.apply(lambda row: row['LBXTC'] / 0.8 if row.name in df_medications.index else row['LBXTC'], axis=1)
- **Status:** Active
- **Last Updated At:** 2024-08-30 19:04:49
- **Repository URL:** [https://github.com/Garon-Sys/MyNHANES/tree/main/rules/rule_00002](https://github.com/Garon-Sys/MyNHANES/tree/main/rules/rule_00002)

## Variables Involved
### Input Variables:
[('nhanes', 'RXQ_RX', 'RXDDRGID'), ('nhanes', 'all datasets', 'LBDLDL'), ('nhanes', 'all datasets', 'LBXTC')]

### Output Variables:
[('normalized', 'all datasets', 'LBDLDL_WO_DRUG'), ('normalized', 'all datasets', 'LBXTC_WO_DRUG'), ('normalized', 'all datasets', 'USE_CHOLESTEROL_DRUG')]

## Rule Explanation
Provide a detailed explanation of the rule here.

## Methodology
Explain the methodology used in this rule. Include any important details about the transformations applied, algorithms used, or special considerations.

## Supporting Literature
- [Link to Paper 1](https://example.com)
- [Link to Paper 2](https://example.com)

## Known Issues & Limitations
- Describe any known issues or limitations of this rule.

## Future Enhancements
- Describe any potential future enhancements or modifications that could improve the rule.

## Contact Information
- **Author:** [Your Name](mailto:your.email@example.com)
- **Project:** [Project Name](https://projecturl.com)