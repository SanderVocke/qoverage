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
    Component.onCompleted: {               //COV:null
        console.log('Hello World')         //COV:1
        var j = 1                          //COV:1
        quittimer.running = true           //COV:1
        consts()                           //COV:1
        lets()                             //COV:1
        var i = 3                          //COV:1
    }                                      //COV:null
                                           //COV:null
    function lets() {                      //COV:null
        let a = 10                         //COV:1
        let b = 20                         //COV:1
    }                                      //COV:null
                                           //COV:null
    function consts() {                    //COV:null
        const a = 10                       //COV:1
        const b = 20                       //COV:1
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
