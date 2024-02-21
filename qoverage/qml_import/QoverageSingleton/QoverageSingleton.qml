pragma Singleton
import QtQuick

QtObject {
     signal aboutToQuit()

     Component.onDestruction: {
          console.log("Singleton destructing");
          aboutToQuit()
     }

     Component.onCompleted: console.log("Created singleton")
}