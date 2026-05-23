const fs = require('fs');
const path = require('path');

const rulesPath = path.join(__dirname, 'rules.json');
const auditPath = path.join(__dirname, 'audit-log.json');
const reportPath = path.join(__dirname, 'coverage-report.json');

const rules = JSON.parse(fs.readFileSync(rulesPath, 'utf8'));
let auditLog = [];

if (fs.existsSync(auditPath)) {
  try {
    auditLog = JSON.parse(fs.readFileSync(auditPath, 'utf8'));
  } catch {
    auditLog = [];
  }
}

const patterns = rules.patterns || [];
const scoreBands = rules.scoreBands || [];

const byDecision = {};
const byRiskClass = {};
const bySeverity = {};
const matchedRuleIds = new Set();
let highestObservedScore = 0;

for (const entry of auditLog) {
  byDecision[entry.decision] = (byDecision[entry.decision] || 0) + 1;
  byRiskClass[entry.riskClass] = (byRiskClass[entry.riskClass] || 0) + 1;
  bySeverity[entry.severity] = (bySeverity[entry.severity] || 0) + 1;

  if (typeof entry.score === 'number' && entry.score > highestObservedScore) {
    highestObservedScore = entry.score;
  }

  for (const match of entry.matches || []) {
    matchedRuleIds.add(match.id);
  }
}

const patternCategories = patterns.reduce((acc, rule) => {
  acc[rule.riskClass] = (acc[rule.riskClass] || 0) + 1;
  return acc;
}, {});

const coverage = {
  generatedAt: new Date().toISOString(),
  tool: rules.name,
  version: rules.version,
  principle: rules.principle,
  ruleCount: patterns.length,
  scoreBandCount: scoreBands.length,
  riskClassesCoveredByRules: Object.keys(patternCategories).sort(),
  ruleDistributionByRiskClass: patternCategories,
  auditEntries: auditLog.length,
  observedDecisions: byDecision,
  observedRiskClasses: byRiskClass,
  observedSeverities: bySeverity,
  matchedRuleCount: matchedRuleIds.size,
  matchedRuleIds: Array.from(matchedRuleIds).sort(),
  unmatchedRuleIds: patterns
    .map(rule => rule.id)
    .filter(id => !matchedRuleIds.has(id))
    .sort(),
  highestObservedScore,
  governanceCoveragePercent: patterns.length === 0
    ? 0
    : Math.round((matchedRuleIds.size / patterns.length) * 100)
};

fs.writeFileSync(reportPath, JSON.stringify(coverage, null, 2));

console.log('\n=== OPS CORE // GOVERNANCE COVERAGE REPORT ===\n');
console.log(`Tool Version          : ${coverage.version}`);
console.log(`Rule Count            : ${coverage.ruleCount}`);
console.log(`Score Bands           : ${coverage.scoreBandCount}`);
console.log(`Risk Classes Covered  : ${coverage.riskClassesCoveredByRules.join(', ')}`);
console.log(`Audit Entries         : ${coverage.auditEntries}`);
console.log(`Matched Rules         : ${coverage.matchedRuleCount}`);
console.log(`Coverage              : ${coverage.governanceCoveragePercent}%`);
console.log(`Highest Score Seen    : ${coverage.highestObservedScore}`);

console.log('\nObserved Decisions:');
console.log(JSON.stringify(coverage.observedDecisions, null, 2));

console.log('\nRule Distribution by Risk Class:');
console.log(JSON.stringify(coverage.ruleDistributionByRiskClass, null, 2));

console.log(`\nReport written to     : ${reportPath}`);
console.log('\nHuman remains owner. AI remains tool.\n');
