#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const rulesPath = path.join(__dirname, 'rules.json');
const rules = JSON.parse(fs.readFileSync(rulesPath, 'utf8'));

const input = process.argv.slice(2).join(' ').trim();

if (!input) {
  console.log('Usage: node check-command.js "<terminal command>"');
  process.exit(1);
}

let matches = [];
let highestScore = 0;
let highestDecision = 'ALLOW';
let highestRiskClass = 'C0';

const decisionPriority = {
  ALLOW: 0,
  REVIEW: 1,
  SANDBOX: 2,
  REPLACE: 3,
  BLOCK: 4
};

for (const rule of rules.patterns) {
  const regex = new RegExp(rule.regex, 'i');

  if (regex.test(input)) {
    matches.push(rule);

    if (rule.score > highestScore) {
      highestScore = rule.score;
    }

    if (decisionPriority[rule.decision] > decisionPriority[highestDecision]) {
      highestDecision = rule.decision;
      highestRiskClass = rule.riskClass;
    }
  }
}

let scoreBand = rules.scoreBands.find(
  band => highestScore >= band.min && highestScore <= band.max
);

if (!scoreBand) {
  scoreBand = {
    label: 'unbekannt',
    decision: highestDecision
  };
}

const auditEntry = {
  timestamp: new Date().toISOString(),
  command: input,
  score: highestScore,
  severity: scoreBand.label,
  decision: highestDecision,
  riskClass: highestRiskClass,
  matches: matches.map(m => ({
    id: m.id,
    reason: m.reason
  }))
};

const auditPath = path.join(__dirname, 'audit-log.json');

let auditLog = [];

if (fs.existsSync(auditPath)) {
  try {
    auditLog = JSON.parse(fs.readFileSync(auditPath, 'utf8'));
  } catch {
    auditLog = [];
  }
}

auditLog.push(auditEntry);
fs.writeFileSync(auditPath, JSON.stringify(auditLog, null, 2));

console.log('\n=== OPS CORE // COMMAND SAFETY GATE ===\n');
console.log(`Command      : ${input}`);
console.log(`Decision     : ${highestDecision}`);
console.log(`Risk Class   : ${highestRiskClass}`);
console.log(`Risk Score   : ${highestScore}`);
console.log(`Severity     : ${scoreBand.label}`);

if (matches.length > 0) {
  console.log('\nTriggered Rules:');

  for (const match of matches) {
    console.log(`- ${match.id}: ${match.reason}`);
  }
} else {
  console.log('\nNo specific risk patterns matched.');
}

console.log(`\nAudit Log    : ${auditPath}`);
console.log('\nHuman remains owner. AI remains tool.\n');
