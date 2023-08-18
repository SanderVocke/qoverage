
// Shared global state
.pragma library

const ids_to_lines = {"0": [22, 23, 24], "1": [24, 25, 26], "2": [4, 30], "3": [15, 29], "4": [18, 28]}

const include_lines = [4, 15, 18, 22, 23, 24, 25, 26, 28, 29, 30]

const n_lines = 32

class CoverageTracker {
    constructor(n) {
        this.data = Array(n).fill(0)
    }

    trace(id) {
        this.data[id]++
    }

    finalize(file_url) {
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

        console.log(
            '<QOVERAGERESULT file="' + file_url + '">' +
            JSON.stringify(lines_data) +
            '</QOVERAGERESULT>'
        )
    }
}

var tracked_coverage = new CoverageTracker(5)

function trace_finalize(our_filename) {
    tracked_coverage.finalize(our_filename)
}

function trace_obj_create(id) {
    tracked_coverage.trace(id)
}

function trace_exec_block(id) {
    tracked_coverage.trace(id)
}
