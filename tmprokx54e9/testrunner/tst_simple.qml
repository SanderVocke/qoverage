

import QtQuick 6.3                                        //COV:null
import QtTest 1.2
import Singly as Qoverage

TestCase { 
property QtObject __qoverage_creation_tracker: QtObject {  Component.onCompleted: { console.log("[qoverage] create obj 0"); Qoverage.Singly.trace_obj_create(0) } }
    name: "MathTests"
    function test_math() {
          compare(2 + 2, 4, "2 + 2 = 4") ; console.log("[qoverage] exec block 1"); Qoverage.Singly.trace_exec_block(1);  
    }

    //Component.onDestruction: QoverageCollector.report()
    //Connections {
    //    target: Window.window
    //    function onDestruction() { console.log("SYMPHONY") }
   // }
    
    Timer {                                               //COV:null
        id: quittimer                                     //COV:null
        running:  { ; console.log("[qoverage] exec block 2"); Qoverage.Singly.trace_exec_block(2); ; return  false  }                                     //COV:1
        interval:  { ; console.log("[qoverage] exec block 3"); Qoverage.Singly.trace_exec_block(3); ; return  200  }                                      //COV:1
        onTriggered:  { ; console.log("[qoverage] exec block 4"); Qoverage.Singly.trace_exec_block(4); ; return  Qt.callLater(Qt.quit)  }                 //COV:1
    }                                                     //COV:null
  }