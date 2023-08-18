import QtQuick 6.3                                                                     //COV:null
import QtQuick.Controls 6.3                                                            //COV:null
import QtQuick.Controls.Material 6.3                                                   //COV:null
                                                                                       //COV:null
ApplicationWindow {                                                                    //COV:1
    visible: true                                                                      //COV:1
    width: 200                                                                         //COV:1
    height: 200                                                                        //COV:1
    title: "Test"                                                                      //COV:1
    id: root                                                                           //COV:null
                                                                                       //COV:null
    Component.onCompleted: {                                                           //COV:null
        let test_var = true                                                            //COV:1
        if (test_var)                                                                  //COV:1
        {                                                                              //COV:null
            console.log("test_var is true")                                            //COV:1
        } else                                                                         //COV:null
        {                                                                              //COV:null
            console.log("nope")                                                        //COV:0
        }                                                                              //COV:null
        if (test_var) {                                                                //COV:1
            console.log("test_var is true")                                            //COV:1
        } else {                                                                       //COV:null
            console.log("nope")                                                        //COV:0
        }                                                                              //COV:null
        if (test_var) { console.log("test_var is true") } else { console.log("nope") } //COV:2
        if (test_var)                                                                  //COV:1
          console.log("test_var is true")                                              //COV:1
        else                                                                           //COV:null
          console.log("nope")                                                          //COV:0
        quittimer.running = true                                                       //COV:1
    }                                                                                  //COV:null
                                                                                       //COV:null
    Timer {                                                                            //COV:null
        id: quittimer                                                                  //COV:null
        running: false                                                                 //COV:1
        interval: 200                                                                  //COV:1
        onTriggered: Qt.callLater(Qt.quit)                                             //COV:1
    }                                                                                  //COV:null
}                                                                                      //COV:null
                                                                                       //COV:null
