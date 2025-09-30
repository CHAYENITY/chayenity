module.exports = {
  'mobile/**/*.dart': ['pnpm format:mobile, pnpm lint:mobile'],
  'server/**/*.py': ['pnpm format:server', 'pnpm lint:server'],
  '*.{js,json,md}': 'prettier -w --ignore-unknown',
};
