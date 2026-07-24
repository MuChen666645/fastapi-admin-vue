export default {
  extends: ['stylelint-config-standard'],
  customSyntax: 'postcss-html',
  ignoreFiles: ['**/node_modules/**', '**/dist/**', '**/coverage/**'],
  rules: {
    'custom-property-pattern': null,
    'no-empty-source': null,
    'no-descending-specificity': null,
    'property-no-vendor-prefix': null,
    'selector-class-pattern': null,
    'selector-id-pattern': null,
    'value-no-vendor-prefix': null,
  },
}
