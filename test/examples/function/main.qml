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
    property var a_func : () => { return true; }          //COV:null
    property var a_func2 : function() { return true; }    //COV:null
                                                          //COV:null
                                                          //COV:null
    Item {                                                //COV:1
        id: test1                                         //COV:null
        signal testSignal(string arg)                     //COV:null
                                                          //COV:null
        // Note: qmldom does not give an offset for the   //COV:null
        // opening brace before "arg" below. For now,     //COV:null
        // not handling this expression.                  //COV:null
        // TODO: file a bug report with Qt.               //COV:null
        onTestSignal: (arg) => 'hello world: ' + arg      //COV:null
    }                                                     //COV:null
                                                          //COV:null
    function testfunc(a, b) {                             //COV:null
        console.log("funcy")                              //COV:1
    }                                                     //COV:null
                                                          //COV:null
    Item {                                                //COV:1
        anchors.fill: parent                              //COV:1
                                                          //COV:null
        Component.onCompleted: {                          //COV:null
            console.log('Hello World')                    //COV:1
            testfunc(1, 2)                                //COV:1
            test1.testSignal('heyyy')                     //COV:1
            quittimer.running = true                      //COV:1
            let func = () => {                            //COV:1
                console.log("Hello World")                //COV:1
            }                                             //COV:1
            func()                                        //COV:1
            let i=0;                                      //COV:1
            for(i=0;i<10;i++) {                           //COV:1
                func()                                    //COV:10
            }                                             //COV:null
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
