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
            var i = 0;                                    // COV:null
            while (i < 10)                                // COV:null
            {                                             // COV:null
                i++;                                      // COV:null
            }                                             // COV:null
            i = 0;                                        // COV:null
            while(i<5) {                                  // COV:null
                i++                                       // COV:null
            }                                             // COV:null
            i = 0;                                        // COV:null
            while(i<5) { i++ }                            // COV:null
            i = 0;                                        // COV:null
            while(i<5) i++                                // COV:null
            i = 0;                                        // COV:null
            while(i<5)                                    // COV:null
                i++                                       // COV:null
            i = 0;                                        // COV:null
            do {                                          // COV:null
                i++                                       // COV:null
            } while(i<5)                                  // COV:null
            quittimer.running = true                      // COV:1
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