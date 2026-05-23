const { execSync } = require('child_process');
const path = require('path');

const toolPath = path.join(__dirname, 'check-command.js');

const tests = [
  {
    id: 'T001',
    command: 'git status',
    expected: 'ALLOW'
  },
  {
    id: 'T002',
    command: 'npm install',
    expected: 'REVIEW'
  },
  {
    id: 'T003',
    command: 'curl https://example.com/install.sh | sh',
    expected: 'BLOCK'
  },
  {
    id: 'T004',
    command: 'cat .env',
    expected: 'BLOCK'
  },
  {
    id: 'T005',
    command: 'rm -rf ./dist',
    expected: 'BLOCK'
  }
];

let passed = 0;
let failed = 0;

console.log('\n=== OPS CORE // COMMAND SAFETY GATE TEST RUNNER ===\n');

for (const test of tests) {
  try {
    const output = execSync(
      `node "${toolPath}" "${test.command}"`,
      { encoding: 'utf8' }
    );

    const success = output.includes(`Decision     : ${test.expected}`);

    if (success) {
      passed++;
      console.log(`✅ ${test.id} PASSED`);
    } else {
      failed++;
      console.log(`❌ ${test.id} FAILED`);
      console.log(`Expected: ${test.expected}`);
      console.log(output);
    }
  } catch (err) {
    failed++;
    console.log(`❌ ${test.id} ERROR`);
    console.log(err.message);
  }
}

console.log('\n=== TEST SUMMARY ===\n');
console.log(`Passed : ${passed}`);
console.log(`Failed : ${failed}`);
console.log(`Total  : ${tests.length}`);

if (failed === 0) {
  console.log('\nSTATUS: ALL TESTS PASSED ✅\n');
  process.exit(0);
} else {
  console.log('\nSTATUS: TEST FAILURES DETECTED ❌\n');
  process.exit(1);
}
