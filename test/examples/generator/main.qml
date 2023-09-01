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
        test_gen()                                        //COV:1
        quittimer.running = true                          //COV:1
    }                                                     //COV:null
                                                          //COV:null
    function* generator() {                               //COV:null
        yield "Hello";                                    //COV:1
        yield "world";                                    //COV:1
        yield "from";                                     //COV:1
        yield "QML!";                                     //COV:1
        yield "I am out of reach";                        //COV:0
    }                                                     //COV:null
                                                          //COV:null
    function* nest_gen1() {                               //COV:null
        yield 1;                                          //COV:1
    }                                                     //COV:null
                                                          //COV:null
    function* nest_gen2() {                               //COV:null
        yield 0;                                          //COV:1
        yield *nest_gen1();                               //COV:1
        yield 2;                                          //COV:0
    }                                                     //COV:null
                                                          //COV:null
    function test_gen() {                                 //COV:null
        var g = generator();                              //COV:1
        var g2 = nest_gen2();                             //COV:1
                                                          //COV:1
        console.log(g.next().value)                       //COV:1
        console.log(g.next().value)                       //COV:1
        console.log(g.next().value)                       //COV:1
        console.log(g.next().value)                       //COV:1
                                                          //COV:1
        console.log(g2.next().value)                      //COV:1
        console.log(g2.next().value)                      //COV:1
    }                                                     //COV:null
                                                          //COV:null
                                                          //COV:null
    Timer {                                               //COV:null
        id: quittimer                                     //COV:null
        running: false                                    //COV:1
        interval: 200                                     //COV:1
        onTriggered: Qt.callLater(Qt.quit)                //COV:1
    }                                                     //COV:null
}                                                         //COV:null
                                                          //COV:null
