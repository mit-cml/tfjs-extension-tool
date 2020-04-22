# Anatomy of an App Inventor TFJS Extension

This document serves as an overview of the anatomy of an App Inventor TensorFlow.JS extension. The extension can be viewed primarily as two key parts: app.js, the JavaScript portion responsible for model setup and evaluation; and TensorflowTemplate.java, the Java side that App Inventor users interact with to build an app that serves as a bridge between the blocks language and the sandboxed JavaScript environment of app.js.

## app.js

app.js represents the bulk of the model setup, invocation, and processing. As it is currently architected, the model evaluation is done in `runClassifier`, with the remainder of the functions used for setup, configuration, and teardown.

### Functions

* `setupCamera` - Configures the browser's camera for video
* `loadVideo` - Loads and starts the video stream
* `runClassifier` - Starts running the neural network on the video stream
    * `classifyFrame` - Classifies a single frame of the stream and schedules itself for the next animation frame
* `loadModel` - Loads the neural network model
* `startVideo` - Runs the model by setting up the video stream and then running the classifier
* `stopVideo` - Stops running the model
* `setCameraFacingMode` - Sets whether to use the front facing or rear facing camera

### Initialization

The code at the very end of the file is where the work is initiated:

```javascript
loadModel().then(model => {
  net = model;
  TensorflowTemplate.ready();
});
```

This loads the model and then signals the extension's `Ready` event. 

Note: `TensorflowTemplate` is a placeholder. When the extension is created by appinventor-tfjs, it is replaced with the name of the extension class, e.g., `LookExtension`.

## TensorflowTemplate.java

The TensorflowTemplate.java file serves as the base of the App Inventor extension. It is the bridge between the blocks language/YAIL and the JavaScript environment where the model evaluation occurs. It provides implementations for WebView interfaces to intercept and process requests from the JavaScript side of the extension to keep the model encapsulated in the extension. Lastly, it provides the API for the JavaScript code to raise events in the blocks language so they can be handled by the app.

### App Inventor API

* `Initialize` - Called by runtime.scm after the component has been created and configured, sets a flag to allow the rest of the functionality in the extension to work
* Properties
    * `Enabled` - Sets whether to run the model or not (default: True)
    * `WebViewer` - Sets the WebViewer component, the WebView of which will be used to run the model
    * `UseCamera` - Sets whether to use the front facing or back facing camera
* Methods
    * N/A
* Events
    * `ModelReady` - Runs when the model has been loaded in the WebView and is ready to run
    * `Error` - Runs when an error occurs in the JavaScript
    * `GotResult` - Runs when the model has results to report to the user

### JavaScript Bridge API (AppInventorTFJS)

* `ready` - Called from JS once the TFJS model has loaded
* `reportResult` - Called from JS when the TFJS model has results to report
* `error` - Called from JS when an error occurs

### Internal API

* WebView setup
    * `configureWebView` - Sets up the WebView associated with a WebViewer component to support the TFJS extension
    * `requestHardwareAcceleration` - Asks the Android system for hardware acceleration support
    * `assertWebView` - Asserts the presence of a configured WebView and throws an IllegalStateException if not properly configured
* Activity lifecycle management
    * `onDelete` - Tears down the TFJS extension infrastructure when the component is deleted
    * `onPause` - Pauses the camera in the WebView
    * `onResume` - Resumes the camera in the WebView
    * `onStop` - Tears down the TFJS extension infrastructure when the Activity is stopped

## Sample Execution Path

This example assumes a LookExtension created with the Mobilenet TFJFS model. The numbering of the event loops is to representing the ordering of events. There may be other events that happen between these iterations of the event loop, but they are not relevant to the execution of the extension. Identation roughly correspondes to call stack depth.

### First event loop

1. Components are created (WebViewer1, LookExtension1)
2. LookExtension1 is configured with the following properties:
    1. Enabled = True
    2. UseCamera = FRONT_CAMERA
    3. WebViewer = WebViewer1
        1. WebViewer1's view (WebView) is set up via `configureWebView` and the loading of the extension's index.html is initiated.
3. Initialize is called on LookExtension1
4. Initialize is called on Screen1

### Second event loop

1. WebView loads index.html and its corresponding JS files
2. `loadModel` initiates asynchronous loading of the mobilenet model

### Third event loop

1. Model finishes loading and calls back on the `AppInventorTFJS.ready` method, queuing the event

### Fourth event loop

1. `ModelReady` event is run in blocks
2. If `Enabled` is True, `UseCamera` is called with the configured camera
    1. `setCameraFacingMode` is called with a flag indicating the direction of camera desired
        1. `setCameraFacingMode` sets the `forwardCamera` flag and queues a request to `startVideo` on the next animation frame

### Fifth event loop

1. `startVideo` runs and attempts to get access to the video device
2. If the user has already granted permission previous, jump to **Seventh event loop**
3. Otherwise, a callback is made to `WebChromeClient.onPermissionRequest` (defined in `configureWebView`), which prompts the user for CAMERA permission

### Sixth event loop

1. If the user denies permission, a PermissionDenied event is raised on Screen1 (END EXECUTION)
2. Otherwise, the PermissionRequest callback is invoked to inform the WebView the permission has been granted

### Seventh event loop

1. The `video` object in the WebView is configured and a `classifyFrame` invocation of the `net` using the `video` object is queued for the next frame

### (N % 2 == 0)th event loop

1. The `net` is used to classify the current `video` frame
2. `AppInventorTFJS.reportResult` is invoked from the JS side to report the results to the Java side passing a JSON representation of the result
    1. The results are parsed on the Java side of the bridge
    2. The `GotResult` event is queued for the next run loop
3. `classifyFrame` is queued for the next frame

### (N % 2 == 1)th event loop

1. The `GotResult` event is run in the blocks with the results of the `net` classification
