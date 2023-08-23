# qoverage
Simple code coverage for QML

(note: not working yet, WIP)

Qoverage is a tool to generate a simple code coverage report for QML files.

It leverages Qt6's built-in parser, qmldom.

The coverage generation process is as follows:

* Instrument your QML files using `qoverage instrument`;
* Run your command or tests in either of the following two ways:
  1. Normal run while saving all console output. Afterward, generate a report from the output using `qoverage collect`.
  2. Wrapped run by `qoverage collect -- CMD`, generating the report right away.

A Cobertura-style XML is generated.

## Qt requirements

`qoverage` is meant to be used with Qt6. To instrument qml sources, it requires the `qmldom` tool from at least Qt6.5. However, the instrumented sources should still work with older Qt6 versons. See below for a way to to run `qoverage` instrumentaton on systems with a Qt6 older than 6.5.

## Coverage model

Qoverage uses a simple coverage model. The best way to understand it is to look into the unit tests as examples.

Only line coverage is generated. 

For Javascript statements the line coverage is roughly as you would expect. 

For declarative QML parts, only the declaration line of each UI object is tracked, and coverage for that line incremented whenever an object of that declaration generates a Component.onCompleted event.

Note that for the time being, the tool is not rigorously tested. False positives are very unlikely, but:

* False negatives may happen, either because of an incomplete instrumentation or because of the fact that Qoverage relies on the Application.aboutToQuit signal to dump its results. The timing of this event w.r.t. the rest of the application exiting is not completely known.
* Double positives (multiple hits although only one real hit happened) may also happen because of different instrumentations overlapping on the same line.

This is just a disclaimer in order to be aware and to look critically at the results. Regardless, for the purpose of "was this line ever executed", the exact amount of hits is irrelevant.

## Collection

Depending on the situation, extra steps may be required in order to get the tracked coverage data out.

The default method for this is that the instrumented Javascript code listens for the Application.aboutToQuit signal, and when it comes, dumps its coverage data to the console by throwing a Javascript error (this seems more reliable than console.log). This method works e.g. when running the examples in this codebase using the `qml` executable.

If for whatever reason this does not work, it is possible to provide a collection plug-in as follows:

- An object should be registered as a QML global context property before the application starts. The property key should be `qoverage_collector_factory`.
- This object should have a Qt slot method named `create_file_collector(filename, initial_lines_data)`, which:
   - takes the full `filename` as the first argument;
   - takes an array of `null` (untracked) or integer (tracked, usually start at 0) elements, equal to the amount of lines in the file;
   - returns an object, let's call it `qoverage_collector`, which has the following Qt slots / JS member method:
        - `trace (lines)`: called on the collector to increment the line hit count (if not `null`) for the given array of line numbers.

Implementing this custom collector means you have full control over its lifecycle and how the coverage is stored and reported. Typically, reporting involves writing a string to a file or the console in the following format, so that it can be parsed by `qoverage collect`:

`<QOVERAGE file=/path/to/my/file>[0, 0, 0, 1, null, null, 0, ...]</QOVERAGE>`

For more information, see [file_tracker.template.js](qoverage/templates/file_tracker.template.js) (the implementation of the Javascript per-file tracking library). For a working example, see [run_qml_tests.py](https://github.com/SanderVocke/shoopdaloop/blob/master/src/shoopdaloop/run_qml_tests.py) in the [ShoopDaLoop](https://github.com/SanderVocke/shoopdaloop) project. There, a custom Qoverage plugin, made in Python, is used to get Qoverage reporting working with a custom QML testrunner.

## Using qoverage from a container

If your system has a pre-6.5 Qt6, you can just run Qoverage from a container which has the correct Qt6 version. Alternatively, you can pass a containerized command as the QMLDOM env variable such that qoverage will run the `qmldom` tool in a container.