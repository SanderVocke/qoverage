import "./simple.qml.qoverage.js" as QoverageTracker

import QtQuick 6.3
import QtQuick.Controls 6.3
import QtQuick.Controls.Material 6.3

ApplicationWindow { 
Connections {  Component.onCompleted: QoverageTracker.trace_obj_create(2) }

Connections { Component.onDestruction: QoverageTracker.trace_finalize( new Error().stack.replace(/.*file:\/\//, "").replace(/:.*/, "") ) }
 
    visible: true
    width: 1050
    height: 550
    minimumWidth: 500
    minimumHeight: 350
    title: "Test"
    id: appWindow

    Material.theme: Material.Dark

    Repeater { 
Connections {  Component.onCompleted: QoverageTracker.trace_obj_create(3) }
 
        model: 10
    
        Label { 
Connections {  Component.onCompleted: QoverageTracker.trace_obj_create(4) }
 
            anchors.fill: parent
            text: "Hello World"

            Component.onCompleted: {  
                console.log('I am a little piggy')
                 ; QoverageTracker.trace_exec_block(0);  if (index < 5) {  
                    console.log('Who went to france')
                 ; QoverageTracker.trace_exec_block(1);  }
            }
          }
      }
  }
