pragma Singleton
import QtQuick
import "./tst_simple.qml.qoverage.js" as QoverageCollector

QtObject {
     function trace_obj_create(idx) { QoverageCollector.trace_object_create(idx); }
     function trace_exec_block (idx) { QoverageCollector.trace_exec_block(idx); }

     Component.onDestruction: {
          console.log("Singly destructing");
          QoverageCollector.report()
     }

     Component.onCompleted: console.log("Created Singly")
}