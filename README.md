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

## Coverage model

Qoverage uses a simple coverage model. The best way to understand it is to look into the unit tests as examples.

Only line coverage is generated. 

For Javascript statements the line coverage is roughly as you would expect. 

For declarative QML parts, only the declaration line of each UI object is tracked, and coverage for that line incremented whenever an object of that declaration generates a Component.onCompleted event.

Note that for the time being, the tool is not rigorously tested. False positives are very unlikely, but:

* False negatives may happen, either because of an incomplete instrumentation or because of the fact that Qoverage relies on the Application.aboutToQuit signal to dump its results. The timing of this event w.r.t. the rest of the application exiting is not completely known.
* Double positives (multiple hits although only one real hit happened) may also happen because of different instrumentations overlapping on the same line.

This is just a disclaimer in order to be aware and to look critically at the results. Regardless, for the purpose of "was this line ever executed", the exact amount of hits is irrelevant.

## Using the report

Qoverage generates a Cobertura-style XML report. There is no built-in method to generate nice-looking human-readable reports. However, there are some options to go from the XML report to something more readable:

* Using [https://pypi.org/project/pycobertura/](pycobertura), a command-line utility which supports Cobertura XML to HTML conversion.
* Uploading the XML to ah online coverage-tracking site like [app.codecov.io](CodeCov).

## Details

### Collection method

Code is injected to gather execution data per execution block. Object instantiations are tracked by connecting to their Component.onCompleted signal.

Data is collected into global variables in a .js library import.

Gathering the tracked data is a bit tricky because it seems that there is no built-in file IO mechanism in QML (except via file:// HTTP requests, but it seems that doesn't work when called during application exit).

In order to keep this simple without needing any binary plugins, the data is simply output to the console.log output and parsed.
