import QtQuick 6.3                                        // COV:null
import QtQuick.Controls 6.3                               // COV:null
import QtQuick.Controls.Material 6.3                      // COV:null
                                                          // COV:null
ApplicationWindow {                                       // COV:1
    visible: true                                         // COV:null
    width: 200                                            // COV:null
    height: 200                                           // COV:null
    title: "Test"                                         // COV:null
    id: root                                              // COV:null
                                                          // COV:null
    Item {                                                // COV:1
        anchors.fill: parent                              // COV:null
                                                          // COV:null
        Component.onCompleted: {                          // COV:1
            quittimer.running = true                      // COV:1
            let func = () => {                            // COV:1
                console.log("Hello World")                // COV:11
            }                                             // COV:1
            func()                                        // COV:1
            let i=0;                                      // COV:1
            for(i=0;i<10;i++) {                           // COV:11
                func()                                    // COV:11
            }                                             // COV:11
        }                                                 // COV:1
    }                                                     // COV:null
                                                          // COV:null
    Timer {                                               // COV:null
        id: quittimer                                     // COV:null
        running: false                                    // COV:null
        interval: 200                                     // COV:null
        onTriggered: Qt.callLater(Qt.quit)                // COV:null
    }                                                     // COV:null
}                                                         // COV:null
                                                          // COV:null