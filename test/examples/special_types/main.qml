import QtQuick 6.3                                        //COV:null
import QtQuick.Controls 6.3                               //COV:null
                                                          //COV:null
ApplicationWindow {                                       //COV:1
    visible: true                                         //COV:1
    width: 200                                            //COV:1
    height: 200                                           //COV:1
    title: "Test"                                         //COV:1
    id: root                                              //COV:null
                                                          //COV:null
    Component.onCompleted: {                              //COV:null
        quittimer.running = true                          //COV:1
    }                                                     //COV:null
                                                          //COV:null
    Timer {                                               //COV:null
        id: quittimer                                     //COV:null
        running: false                                    //COV:1
        interval: 200                                     //COV:1
        onTriggered: Qt.callLater(Qt.quit)                //COV:1
    }                                                     //COV:null
                                                          //COV:null
    Item {                                                //COV:1
        anchors {                                         //COV:null
            fill: parent                                  //COV:1
        }                                                 //COV:null
    }                                                     //COV:null
                                                          //COV:null
    Repeater {                                            //COV:null
        id: repeater                                      //COV:null
                                                          //COV:null
        Item {}                                           //COV:0
    }                                                     //COV:null
                                                          //COV:null
    Connections {                                         //COV:null
        target: root                                      //COV:1
        onWidthChanged: {                                 //COV:null
            console.log("a")                              //COV:0
        }                                                 //COV:null
                                                          //COV:null
    }                                                     //COV:null
                                                          //COV:null
    Component {                                           //COV:null
        id: delegate                                      //COV:null
        Rectangle {                                       //COV:0
            width: 100                                    //COV:0
            height: 100                                   //COV:0
            color: "red"                                  //COV:0
        }                                                 //COV:null
    }                                                     //COV:null
}                                                         //COV:null
                                                          //COV:null
