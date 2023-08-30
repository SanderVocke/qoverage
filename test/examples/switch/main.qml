import QtQuick 6.3                         // COV:null
import QtQuick.Controls 6.3                // COV:null
import QtQuick.Controls.Material 6.3       // COV:null
                                           // COV:null
ApplicationWindow {                        // COV:1
    visible: true                          // COV:1
    width: 200                             // COV:1
    height: 200                            // COV:1
    title: "Test"                          // COV:1
    id: root                               // COV:null
                                           // COV:null
    Item {                                 // COV:1
        anchors.fill: parent               // COV:1
                                           // COV:null
        Component.onCompleted: {           // COV:null
            quittimer.running = true       // COV:1
            let a = 'hello'                // COV:1
            switch (a) {                   // COV:1
                case 'no':                 // COV:null
                    console.log('no')      // COV:0
                    break                  // COV:0
                case 'hello':              // COV:null
                    console.log('world')   // COV:1
                    break                  // COV:1
                default:                   // COV:null
                    console.log('wow')     // COV:0
            }                              // COV:null
            switch (a) {                   // COV:1
                case 'no':                 // COV:null
                    console.log('no')      // COV:0
                    break                  // COV:0
                case 'hello':              // COV:null
                    console.log('world')   // COV:1
                default:                   // COV:null
                    console.log('wow')     // COV:1
            }                              // COV:null
        }                                  // COV:null
    }                                      // COV:null
                                           // COV:null
    Timer {                                // COV:null
        id: quittimer                      // COV:null
        running: false                     // COV:1
        interval: 200                      // COV:1
        onTriggered: Qt.callLater(Qt.quit) // COV:1
    }                                      // COV:null
}                                          // COV:null
                                           // COV:null
