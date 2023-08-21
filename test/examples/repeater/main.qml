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
    Repeater {                             // COV:null
        model: 10                          // COV:null
                                           // COV:null
        Label {                            // COV:10
            anchors.fill: parent           // COV:null
            text: "Hello World"            // COV:null
                                           // COV:null
            Component.onCompleted: {       // COV:10
                console.log('Foo')         // COV:10
                quittimer.running = true   // COV:10
            }                              // COV:10
        }                                  // COV:null
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