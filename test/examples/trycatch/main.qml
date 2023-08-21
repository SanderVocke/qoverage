import QtQuick 6.3                         // COV:null
import QtQuick.Controls 6.3                // COV:null
import QtQuick.Controls.Material 6.3       // COV:null
                                           // COV:null
ApplicationWindow {                        // COV:1
    visible: true                          // COV:null
    width: 200                             // COV:null
    height: 200                            // COV:null
    title: "Test"                          // COV:null
    id: root                               // COV:null
                                           // COV:null
    Item {                                 // COV:1
        anchors.fill: parent               // COV:null
                                           // COV:null
        Component.onCompleted: {           // COV:1
            console.log("hi")              // COV:1
            quittimer.running = true       // COV:1
            try {                          // COV:1
                console.log("try")         // COV:1
            } catch {                      // COV:0
                console.log("catch")       // COV:0
            } finally {                    // COV:1
                console.log("finally")     // COV:1
            }                              // COV:1
            try {                          // COV:1
                console.log("try again")   // COV:1
                throw new Error()          // COV:1
            } catch (e) {                  // COV:1
                console.log("catch")       // COV:1
            } finally {                    // COV:1
                console.log("finally")     // COV:1
            }                              // COV:1
        }                                  // COV:1
    }                                      // COV:null
                                           // COV:null
    Timer {                                // COV:null
        id: quittimer                      // COV:null
        running: false                     // COV:null
        interval: 200                      // COV:null
        onTriggered: Qt.callLater(Qt.quit) // COV:null
    }                                      // COV:null
}                                          // COV:null
                                           // COV:null