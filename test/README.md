# Qoverage tests

The testing setup for qoverage is set up to make it easy to write example QML files which have the expected coverage included.
To run, just run `pytest` in this directory (or in the root directory of `qoverage`).

`pytest` will trigger `test_examples.py`, which will instantiate a test-case per subfolder of the `examples` folder.

For each testcase:

* The QML files inside are instrumented to a temporary location using Qoverage;
* The QT `qml` executable is used to run the instrumented `main.qml`;
* It waits for the app to finish. Make sure your QML file is self-exiting (see the examples for how to use a Timer for this)
* Coverage is collected and compared with the `//COV:xxx` comments in the source files.
* If they do not match, the test fails and you are pointed to a temporary folder where you can compare the results.

To run a specific testcase:

```
pytest -k 'test_example[while]'
```

To list the available tests:

```
pytest --collect-only
```

There are tests which are expected to fail because of not-yet-implemented functionality. This is handled automatically by prefixing their example folder name by `_notworking_`.

```
pytest 
```

There is also an option to open a file diff tool right away on failure. You can use the `OPEN_DIFF_TOOL` env variable for this. E.g:

```
OPEN_DIFF_TOOL=kdiff3 pytest -k 'test_example[while]'
```

## Troubleshooting

* Sometimes the wrong `qml` executable is in the path (e.g. of an older Qt version). In that case you can override using the QML env variable.
