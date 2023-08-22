// Static properties which are the result of code instrumentation
const ids_to_lines = $ids_to_lines
const include_lines = $include_lines
const n_lines = $n_lines
const n_annotations = $n_annotations
const debug = $debug

function get_filename() {
    return new Error().stack.split('\n')[0].replace(/.*file:\/\//, "").replace(/.qoverage.js:.*/, "")
}

class CoverageTracker {
    constructor(n) {
        if (debug) { console.log("[qoverage] db init", get_filename(), ', app: ', Qt.application) }

        // the data field tracks how often each instrumentation
        // annotation was triggered.
        this.data = Array(n).fill(0)

        // Ensure that we report on exit
        Qt.application.aboutToQuit.connect(() => {
            this.finalize(get_filename())
        })
        if(qoverage_global_context) {
            qoverage_global_context.report("Hello world!")
            qoverage_global_context.onRequestReport.connect((report_fn) => {
                this.finalize(get_filename(), report_fn)
            })
        }
    }

    trace(id) {
        this.data[id]++
    }

    finalize(filename, report_fn = (msg) => { throw new Error (msg) } ) {
        if (debug) { console.log("[qoverage] db finalize", get_filename()) }

        // Map the annotation triggers to line coverage.

        var lines_data = Array(n_lines).fill(null)
        include_lines.forEach( l => {
            lines_data[l] = 0
        })

        this.data.forEach( (n,id) => {
            var lines = ids_to_lines[id]
            lines.forEach( line => {
                lines_data[line]+=n
            })
        })

        report_fn(
            '<QOVERAGERESULT file="' + filename + '">' +
            JSON.stringify(lines_data) +
            '</QOVERAGERESULT>'
        )
    }
}

var tracked_coverage = new CoverageTracker(n_annotations)

function trace_obj_create(id) {
    tracked_coverage.trace(id)
}

function trace_exec_block(id) {
    tracked_coverage.trace(id)
}