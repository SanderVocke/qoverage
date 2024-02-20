// Static properties which are the result of code instrumentation
const ids_to_lines = {"1": [7], "2": [12], "3": [13], "4": [14], "0": [3]}
const include_lines = [3, 7, 12, 13, 14]
const n_lines = 17
const n_annotations = 5
const debug = true

function get_filename() {
    return new Error().stack.split('\n')[0].replace(/.*file:\/\//, "").replace(/.qoverage.js:.*/, "")
}

// This class implements the single-file collector interface and is the default
// collector.
class QoverageDefaultFileCollector {
    // initial_line_states should be an array of 0 or null (untracked) values.
    constructor(filename, initial_line_states) {
        this.filename = filename
        this.line_states = initial_line_states
    }

    trace(lines) {
        lines.forEach( line => {
            if (this.line_states[line] !== null) {
                this.line_states[line]++
            }
        })
    }

    report() {
        // Note: from experience, throwing an error is the most reliable
        // way to get text to the console. Console.log seems to not always
        // work in different types of Qt apps.
        // Since this error is thrown in a signal handler, it will not
        // crash the app.
        throw new Error(
            '<QOVERAGERESULT file="' + this.filename + '">' +
                JSON.stringify(this.line_states) +
                '</QOVERAGERESULT>'
        )
    }
}

class QoverageCollector {
    constructor(filename, include_lines, ids_to_lines, n_lines) {
        this.ids_to_lines = ids_to_lines
        console.log("Hello world!")

        let data = Array(n_lines)
        for(let i = 0; i < n_lines; i++) {
            data[i] = include_lines.includes(i) ? 0 : null
        }

        // By default, create our own collector which will report on app aboutToQuit.
        // If a global collector is defined, use that instead to get a per-file collector
        // instance.
        try {
            this.collector = qoverage_collector_factory.create_file_collector(filename, data)
        } catch (e) {
            console.log("Using default collector")
            this.collector = new QoverageDefaultFileCollector(filename, data)
            console.log(Qt.application, Qt.application.aboutToQuit, Window.window)
            Qt.application.aboutToQuit.connect(() => {
                console.log('About to quit')
                this.collector.report()
            })
            // Window.window.closing.connect(() => {
            //     console.log("Window closing")
            // })
        }
    }

    trace(annotation_id) {
        this.collector.trace(this.ids_to_lines[annotation_id])
    }

    report() {
        this.collector.report()
    }
}

var qoverage_global_collector = new QoverageCollector(get_filename(), include_lines, ids_to_lines, n_lines)

// Functions below are called from instrumented QML

function trace_obj_create(id) {
    qoverage_global_collector.trace(id)
}

function trace_exec_block(id) {
    qoverage_global_collector.trace(id)
}

function report() {
    qoverage_global_collector.report()
}