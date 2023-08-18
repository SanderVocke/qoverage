import QtQuick 6.3                                        //COV:null
import QtQuick.Controls 6.3                               //COV:null
import QtQuick.Controls.Material 6.3                      //COV:null
                                                          //COV:null
ApplicationWindow {                                       //COV:1
    visible: true                                         //COV:1
    width: 200                                            //COV:1
    height: 200                                           //COV:1
    title: "Test"                                         //COV:1
    id: root                                              //COV:null
                                                          //COV:null
    Item {                                                //COV:1
        anchors.fill: parent                              //COV:1
                                                          //COV:null
        Component.onCompleted: {                          //COV:null
            var i = 0;                                    //COV:1
            while (i < 10)                                //COV:1
            {                                             //COV:null
                i++;                                      //COV:10
            }                                             //COV:null
            i = 0;                                        //COV:1
            while(i<5) {                                  //COV:1
                i++                                       //COV:5
            }                                             //COV:null
            i = 0;                                        //COV:1
            while(i<5) { i++ }                            //COV:6
            i = 0;                                        //COV:1
            while(i<5) i++                                //COV:6
            i = 0;                                        //COV:1
            while(i<5)                                    //COV:1
                i++                                       //COV:5
            i = 0;                                        //COV:1
            do {                                          //COV:1
                i++                                       //COV:5
            } while(i<5)                                  //COV:null
            quittimer.running = true                      //COV:1
        }                                                 //COV:null
    }                                                     //COV:null
                                                          //COV:null
    Timer {                                               //COV:null
        id: quittimer                                     //COV:null
        running: false                                    //COV:1
        interval: 200                                     //COV:1
        onTriggered: Qt.callLater(Qt.quit)                //COV:1
    }                                                     //COV:null
}                                                         //COV:null
                                                          //COV:null
