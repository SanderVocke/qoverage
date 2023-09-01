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
    property var t1: null                                 //COV:1
    property var t2: true ? 'a' : 'b'                     //COV:1
                                                          //COV:null
    Component.onCompleted: {                              //COV:null
        console.log('Hello World')                        //COV:1
        quittimer.running = true                          //COV:1
                                                          //COV:1
        var i=0;                                          //COV:1
        {                                                 //COV:1
            var a1 = null                                 //COV:1
        }                                                 //COV:null
        {                                                 //COV:1
            var a2 = false ? 'b' : 'a'                    //COV:1
        }                                                 //COV:null
        {                                                 //COV:1
            var a3 = !false                               //COV:1
        }                                                 //COV:null
        {                                                 //COV:1
            var a4 = 5                                    //COV:1
        }                                                 //COV:null
        {                                                 //COV:1
            var a5 = -10                                  //COV:1
        }                                                 //COV:null
        {                                                 //COV:1
            var a6 = (true && false) || false             //COV:1
        }                                                 //COV:null
        {                                                 //COV:1
            var a7 = typeof quittimer                     //COV:1
        }                                                 //COV:null
        {                                                 //COV:1
            var a8 = this                                 //COV:1
        }                                                 //COV:null
        {                                                 //COV:1
            var a9 = [ 1, , 2]                            //COV:1
        }                                                 //COV:null
        {                                                 //COV:1
            var a10 = +10                                 //COV:1
        }                                                 //COV:null
        {                                                 //COV:1
            var a11 = ~i                                  //COV:1
        }                                                 //COV:null
        {                                                 //COV:1
            var a10 = ++i                                 //COV:1
        }                                                 //COV:null
        {                                                 //COV:1
            var a10 = i++                                 //COV:1
        }                                                 //COV:null
        {                                                 //COV:1
            var a10 = --i                                 //COV:1
        }                                                 //COV:null
        {                                                 //COV:1
            var a10 = i--                                 //COV:1
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
