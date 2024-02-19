# qoverage
Simple code coverage for QML

[![codecov](https://codecov.io/github/SanderVocke/qoverage/graph/badge.svg?token=0lY7iGIRQ9)](https://codecov.io/github/SanderVocke/qoverage)
![build](https://github.com/sandervocke/qoverage/actions/workflows/build_and_test.yml/badge.svg)

Qoverage is a tool to generate a simple code coverage report for QML files. It leverages Qt6's built-in parser, `qmldom`, to instrument QML files for coverage collection.

# TL;DR

```
# Instrument all found QML files, modify in-place and keeps backups
qoverage instrument --in-place --glob "./**/*.qml"   

# Running now will add qoverage tracking data to the console output
./my_qml_test | tee output.log

# Generate a Cobertura-style XML report
qoverage collect --report report.xml --files-path . --input output.log
```

# Details

The coverage generation process is as follows:

* Instrument your QML files using `qoverage instrument`;
* Run your command or tests in either of the following two ways:
  1. Normal run while saving all console output. Afterward, generate a report from the output using `qoverage collect`.
  2. Wrapped run by `qoverage collect -- CMD`, generating the report right away.

A Cobertura-style XML is generated.

## Installation

`pip install qoverage`

If you are on a non-Linux platform, you will need to install Qt separately as well and point qoverage to your `qmldom`(`.exe`) using the `--qmldom` argument.

## Status

The current state is pre-alpha. Some details:

* The basic workflow for instrumenting, collecting and reporting is set up (see [run_example.py](test/run_example.py) for an example usage sequence).
* A pretty solid subset of Javascript syntax is implemented and tested (see the examples in [test/examples](test/examples)). Unsupported syntax (see [TODO comments in dom.py](qoverage/dom.py) will usually lead to parts of code not being included in coverage analysis.
* There are known issues (see below).

The basic workflow for coverage collection has been set up, but the instrumentation part is missing lots of Javascript statement types, hence the generated coverage will often be incorrect. This will be solved in the near future. First release is planned when the existing testcases are fully automated and passing.

## Qt requirements

`qoverage` depends on the `qmldom` tool from Qt (>6.5.0). Because this is often hard to reconcile with system Qt packages, `qoverage`'s Python wheels come with a bundled, statically linked `qmldom` that doesn't require or interfere with any other Qt installation. Do note that tests are run against Qt6's `qml` binary, and there may be unforeseen issues in instrumenting/running, for example, Qt5 QML files. YMMV.

## Coverage model

Qoverage uses a simple coverage model. The best way to understand it is to look into the unit tests as examples.

Only line coverage is generated. 

For Javascript statements the line coverage is roughly as you would expect. 

For declarative QML parts, only the declaration line of each UI object is tracked, and coverage for that line incremented whenever an object of that declaration generates a Component.onCompleted event.

Note that for the time being, the tool is not rigorously tested. False positives are very unlikely.

## Known issues

* False negatives may happen, either because of an incomplete instrumentation or because of the fact that Qoverage relies on the Application.aboutToQuit signal to dump its results. The timing of this event w.r.t. the rest of the application exiting is not completely known.
* Double positives (multiple hits although only one real hit happened) may also happen because of different instrumentations overlapping on the same line.
* Imported Javascript files are currently not instrumented or included in the report, because `qmldom` does not support them. Working on a workaround solution for this. For now, unit tests were written for imported Javascript but these fail for the time being.
* The coverage model assumes that blocks of non-branching statements will execute together. If an error is thrown somewhere during executing several statements, none of the statements have any coverage recorded. This is an accepted trade-off - catching these cases would require tracking coverage explicitly for every single line, which would decrease performance significantly.
* QMLDom sometimes fails to parse qml files. These files are skipped for coverage analysis.

## Collection

Depending on the situation, extra steps may be required in order to get the tracked coverage data out.

The default method for this is that the instrumented Javascript code listens for the Application.aboutToQuit signal, and when it comes, dumps its coverage data to the console by throwing a Javascript error (this seems more reliable than console.log). This method works e.g. when running the examples in this codebase using the `qml` executable.

If for whatever reason this does not work:
- Ensure no debug logging filters are blocking console messages/exceptions from appearing: `QT_LOGGING_RULES="*.debug=true; qt.*.debug=false"`
- Ensure Qt knows that there is a stderr console available: `QT_ASSUME_STDERR_HAS_CONSOLE=1`
- See if other console log messages from your QML code are appearing. If they do, but Qoverage reports don't get printed, this means that maybe the application quit signal did not trigger qoverage collection. See a possible solution below.

If all else fails or a special solution is needed, it is possible to provide a collection plug-in as follows:

- An object should be registered as a QML global context property before the application starts. The property key should be `qoverage_collector_factory`.
- This object should have a Qt slot method named `create_file_collector(filename, initial_lines_data)`, which:
   - takes the full `filename` as the first argument;
   - takes an array of `null` (untracked) or integer (tracked, usually start at 0) elements, equal to the amount of lines in the file;
   - returns an object, let's call it `qoverage_collector`, which has the following Qt slots / JS member method:
        - `trace (lines)`: called on the collector to increment the line hit count (if not `null`) for the given array of line numbers.

Implementing this custom collector means you have full control over its lifecycle and how the coverage is stored and reported. Typically, reporting involves writing a string to a file or the console in the following format, so that it can be parsed by `qoverage collect`:

`<QOVERAGE file=/path/to/my/file>[0, 0, 0, 1, null, null, 0, ...]</QOVERAGE>`

For more information, see [file_tracker.template.js](qoverage/templates/file_tracker.template.js) (the implementation of the Javascript per-file tracking library). For a working example, see [run_qml_tests.py](https://github.com/SanderVocke/shoopdaloop/blob/master/src/shoopdaloop/run_qml_tests.py) in the [ShoopDaLoop](https://github.com/SanderVocke/shoopdaloop) project. There, a custom Qoverage plugin, made in Python, is used to get Qoverage reporting working with a custom QML testrunner.

## Contributing

See [DEVELOP.md](DEVELOP.md).
