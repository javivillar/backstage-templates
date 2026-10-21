// Karma configuration file, see link for more information
// https://karma-runner.github.io/1.0/config/configuration-file.html

// Reporter "specs": every spec with its result and time, in $KARMA_SPECS (the CI: ../quality/specs.json), for the
// quality report (.github/quality.py). Written here so the tests need no other package.
function SpecsReporter(baseReporterDecorator) {
  baseReporterDecorator(this);
  const specs = [];
  this.onSpecComplete = (_browser, result) => {
    specs.push({
      suite: result.suite,
      description: result.description,
      status: result.skipped || result.pending ? 'skipped' : result.success ? 'passed' : 'failed',
      time: result.time,
      message: (result.log || []).join('\n').split('\n').slice(0, 5).join('\n'),
    });
  };
  this.onRunComplete = () => {
    const out = process.env.KARMA_SPECS;
    if (!out) return;
    const fs = require('fs');
    fs.mkdirSync(require('path').dirname(out), { recursive: true });
    fs.writeFileSync(out, JSON.stringify(specs, null, 1));
  };
}
SpecsReporter.$inject = ['baseReporterDecorator'];

module.exports = function (config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine'],
    plugins: [
      require('karma-jasmine'),
      require('karma-chrome-launcher'),
      require('karma-firefox-launcher'),
      require('karma-jasmine-html-reporter'),
      require('karma-coverage'),
      { 'reporter:specs': ['type', SpecsReporter] },
    ],
    client: {
      jasmine: {
        // you can add configuration options for Jasmine here
        // the possible options are listed at https://jasmine.github.io/api/edge/Configuration.html
        // for example, you can disable the random execution with `random: false`
        // or set a specific seed with `seed: 4321`
      },
    },
    jasmineHtmlReporter: {
      suppressAll: true // removes the duplicated traces
    },
    coverageReporter: {
      dir: require('path').join(__dirname, './coverage/frontend'),
      subdir: '.',
      reporters: [
        { type: 'html' },
        { type: 'text-summary' },
        // read by the quality report of the CI (.github/quality.py): the coverage of each file, and the lines
        // its tests do not run
        { type: 'json-summary' },
        { type: 'json' }
      ],
      check: {
        global: { statements: 70, branches: 60, functions: 70, lines: 70 }
      }
    },
    reporters: ['progress', 'kjhtml', 'specs'],
    // KARMA_BROWSER=FirefoxHeadless where there is no Chrome
    browsers: [process.env.KARMA_BROWSER || 'ChromeHeadlessCI'],
    customLaunchers: {
      ChromeHeadlessCI: { base: 'ChromeHeadless', flags: ['--no-sandbox'] },
    },
    restartOnFileChange: true
  });
};
