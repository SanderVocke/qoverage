import QtQuick 6.3                                                                     // COV:null
import QtQuick.Controls 6.3                                                            // COV:null
import QtQuick.Controls.Material 6.3                                                   // COV:null
                                                                                       // COV:null
ApplicationWindow {                                                                    // COV:1
    visible: true                                                                      // COV:null
    width: 200                                                                         // COV:null
    height: 200                                                                        // COV:null
    title: "Test"                                                                      // COV:null
    id: root                                                                           // COV:null
                                                                                       // COV:null
    Component.onCompleted: {                                                           // COV:1
        let test_var = true                                                            // COV:1
        if (test_var)                                                                  // COV:1
        {                                                                              // COV:1
            console.log("test_var is true")                                            // COV:1
        } else                                                                         // COV:1
        {                                                                              // COV:0
            console.log("nope")                                                        // COV:0
        }                                                                              // COV:0
        if (test_var) {                                                                // COV:1
            console.log("test_var is true")                                            // COV:1
        } else {                                                                       // COV:0
            console.log("nope")                                                        // COV:0
        }                                                                              // COV:0
        if (test_var) { console.log("test_var is true") } else { console.log("nope") } // COV:1
        if (test_var)                                                                  // COV:0
          console.log("test_var is true")                                              // COV:1
        else                                                                           // COV:0
          console.log("nope")                                                          // COV:0
        quittimer.running = true                                                       // COV:1
    }                                                                                  // COV:1
                                                                                       // COV:null
    Timer {                                                                            // COV:null
        id: quittimer                                                                  // COV:null
        running: false                                                                 // COV:null
        interval: 200                                                                  // COV:null
        onTriggered: Qt.callLater(Qt.quit)                                             // COV:null
    }                                                                                  // COV:null
}                                                                                      // COV:null
                                                                                       // COV:null