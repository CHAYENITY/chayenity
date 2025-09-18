module.exports = {
  'server/**/*.py': ['pnpm format:server', 'pnpm lint:server'],
  '*.{js,json,md}': 'prettier -w --ignore-unknown',
};
