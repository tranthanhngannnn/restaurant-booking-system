const { spawnSync } = require('child_process');
const path = require('path');

const args = process.argv.slice(2);
const usesFrontendPath = args.some(arg => arg.includes('frontend' + path.sep) || arg.includes('frontend/'));

const escapeArg = (arg) => {
  if (/\s|"|\'/g.test(arg)) {
    return `"${arg.replace(/"/g, '\\"')}"`;
  }
  return arg;
};

if (usesFrontendPath) {
  const frontendArgs = args.map((arg) => {
    if (arg.startsWith('frontend/') || arg.startsWith('frontend\\')) {
      return arg.replace(/^frontend[\\/]+/, '');
    }
    return arg;
  });
  const command = `npm test --prefix frontend -- ${frontendArgs.map(escapeArg).join(' ')}`;
  const result = spawnSync(command, {
    stdio: 'inherit',
    shell: true,
  });
  process.exit(result.status !== null ? result.status : 1);
} else {
  const command = `npx jest ${args.map(escapeArg).join(' ')}`;
  const result = spawnSync(command, {
    stdio: 'inherit',
    shell: true,
  });
  process.exit(result.status || 1);
}
