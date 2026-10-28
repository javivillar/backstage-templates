// @ts-check
const eslint = require("@eslint/js");
const tseslint = require("typescript-eslint");
const angular = require("angular-eslint");

module.exports = tseslint.config(
  // generated from backend/openapi.json (npm run gen:api)
  { ignores: ["src/app/api/*-schema.ts"] },
  {
    files: ["**/*.ts"],
    extends: [
      eslint.configs.recommended,
      ...tseslint.configs.recommended,
      ...tseslint.configs.stylistic,
      ...angular.configs.tsRecommended,
    ],
    processor: angular.processInlineTemplates,
    rules: {
      "@angular-eslint/directive-selector": [
        "error",
        {
          type: "attribute",
          prefix: "app",
          style: "camelCase",
        },
      ],
      "@angular-eslint/component-selector": [
        "error",
        {
          type: "element",
          prefix: "app",
          style: "kebab-case",
        },
      ],
    },
  },
  // Security (part `security` of the quality report: .github/quality.py counts these rules apart). Code that turns
  // off what protects the web: evaluating text as code, HTML written by hand, Angular's sanitizer bypassed.
  {
    files: ["**/*.ts"],
    ignores: ["**/*.spec.ts"],
    rules: {
      "no-eval": "error",
      "no-implied-eval": "error",
      "no-new-func": "error",
      "no-script-url": "error",
      "no-restricted-syntax": [
        "error",
        {
          selector: "CallExpression[callee.property.name=/^bypassSecurityTrust/]",
          message: "[security] DomSanitizer.bypassSecurityTrust* turns off Angular's sanitization of that value",
        },
        {
          selector: "AssignmentExpression > MemberExpression.left[property.name=/^(innerHTML|outerHTML)$/]",
          message: "[security] HTML written by hand is not sanitized: bind it in the template instead",
        },
        {
          selector: "CallExpression[callee.property.name=/^(insertAdjacentHTML|write|writeln)$/]",
          message: "[security] HTML written by hand (insertAdjacentHTML / document.write) is not sanitized",
        },
        {
          selector: "CallExpression[callee.object.name=/^(localStorage|sessionStorage)$/][callee.property.name='setItem'][arguments.0.value=/token/i]",
          message: "[security] a token in web storage can be read by any script of the page: keep it in memory (refresquito-angular does)",
        },
      ],
    },
  },
  {
    files: ["**/*.html"],
    extends: [
      ...angular.configs.templateRecommended,
      ...angular.configs.templateAccessibility,
    ],
    rules: {},
  }
);
