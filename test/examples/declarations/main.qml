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
    Component.onCompleted: {               // COV:null
        var j = 1                          // COV:null
        quittimer.running = true           // COV:null
        lets()                             // COV:null
        var i = 3                          // COV:null
    }                                      // COV:null
                                           // COV:null
    function lets() {                      // COV:null
        let a = 10                         // COV:null
        let b = 20                         // COV:null
    }                                      // COV:null
                                           // COV:null
    function consts() {                    // COV:null
        const a = 10                       // COV:null
        const b = 20                       // COV:null
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