import QtQuick 6.3                         // COV:null
import QtQuick.Controls 6.3                // COV:null
import QtQuick.Controls.Material 6.3       // COV:null
                                           // COV:null
.import 'included.js' as Included          // COV:null
                                           // COV:null
ApplicationWindow {                        // COV:1
    visible: true                          // COV:null
    width: 200                             // COV:null
    height: 200                            // COV:null
    title: "Test"                          // COV:null
    id: root                               // COV:null
                                           // COV:null
    Component.onCompleted: {               // COV:null
        quittimer.running = true           // COV:null
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