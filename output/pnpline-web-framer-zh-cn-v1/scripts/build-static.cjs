const { spawnSync } = require('node:child_process');

const result = spawnSync(process.execPath, [require.resolve('next/dist/bin/next'), 'build', '--turbopack'], {
  env: { ...process.env, PNPLINE_STATIC_EXPORT: '1' },
  stdio: 'inherit',
});

if (result.error) throw result.error;
process.exitCode = result.status ?? 1;
