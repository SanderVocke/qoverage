import QtQuick 6.3                         //COV:null
import QtQuick.Controls 6.3                //COV:null
// Note: created because of QTBUG-116618   //COV:null
                                           //COV:null
ApplicationWindow {                        //COV:1
    visible: true                          //COV:1
    width: 200                             //COV:1
    height: 200                            //COV:1
    title: "Test"                          //COV:1
    id: root                               //COV:null
                                           //COV:null
    property string a : " \" "             //COV:1
    property string b : " ' "              //COV:1
    property string c : ' " '              //COV:1
    property string d : ' \' '             //COV:1
    property string e : " < > "            //COV:1
    property string f : " & "              //COV:1
    property string g : "  \n  "           //COV:1
    property string h : "  < >  ' \" & "   //COV:1
                                           //COV:null
    Component.onCompleted: {               //COV:null
      console.log('Hello World')           //COV:1
      quittimer.running = true             //COV:1
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