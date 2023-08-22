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
            for (var i=0; i<10; i++)                      // COV:null
            {                                             // COV:null
                console.log(i)                            // COV:null
                if (i == 5) break;                        // COV:null
                console.log('a')                          // COV:null
            }                                             // COV:null
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