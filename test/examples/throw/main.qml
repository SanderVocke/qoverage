import QtQuick 6.3                         //COV:null
import QtQuick.Controls 6.3                //COV:null
import QtQuick.Controls.Material 6.3       //COV:null
                                           //COV:null
ApplicationWindow {                        //COV:1
    visible: true                          //COV:1
    width: 200                             //COV:1
    height: 200                            //COV:1
    title: "Test"                          //COV:1
    id: root                               //COV:null
                                           //COV:null
    Item {                                 //COV:1
        anchors.fill: parent               //COV:1
                                           //COV:null
        Component.onCompleted: {           //COV:null
            console.log("hi")              //COV:1
            quittimer.running = true       //COV:1
            throw new Error()              //COV:1
            console.log("ho")              //COV:0
            console.log("hi")              //COV:0
        }                                  //COV:null
    }                                      //COV:null
                                           //COV:null
    Timer {                                //COV:null
        id: quittimer                      //COV:null
        running: false                     //COV:1
        interval: 200                      //COV:1
        onTriggered: Qt.callLater(Qt.quit) //COV:1
    }                                      //COV:null
}                                          //COV:null
                                           //COV:null
