import QtQuick 6.3                         //COV:null
import QtQuick.Controls 6.3                //COV:null
                                           //COV:null
ApplicationWindow {                        //COV:1
    visible: true                          //COV:1
    width: 200                             //COV:1
    height: 200                            //COV:1
    title: "Test"                          //COV:1
    id: root                               //COV:null
                                           //COV:null
    function throw_me_something() {        //COV:null
        throw new Error ("i")              //COV:1
    }                                      //COV:null
                                           //COV:null
    Item {                                 //COV:1
        anchors.fill: parent               //COV:1
                                           //COV:null
        Component.onCompleted: {           //COV:null
            console.log('Hello World')     //COV:1
            quittimer.running = true       //COV:1
            try {                          //COV:1
                console.log("a")           //COV:1
            } catch (e) {                  //COV:null
                console.log("b")           //COV:0
            }                              //COV:null
                                           //COV:null
            try {                          //COV:1
                console.log("b")           //COV:1
                throw new Error ("c")      //COV:1
                console.log("d")           //COV:0
            } catch (e) {                  //COV:null
                console.log("e")           //COV:1
            }                              //COV:null
                                           //COV:null
            // Note: below is the expected //COV:null
            // behavior, even though it is //COV:null
            // not ideal                   //COV:null
            try {                          //COV:1
                console.log("f")           //COV:0
                throw_me_something()       //COV:0
                console.log("g")           //COV:0
            } catch (e) {                  //COV:null
                console.log("h")           //COV:1
            }                              //COV:null
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
