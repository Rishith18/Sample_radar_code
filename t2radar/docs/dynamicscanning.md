# Dynamic Scanning

Dynamic Scanning is defined as the ability to stop and start the radar scanning at will, rather than configuring the radar to stop at a certain number of scans. This feature is only available in GUI mode, as we hijack `tkinter`'s event loop to enable this functionality.

## The Problem

Python is an inherently single-threaded language, and operations like waiting for incoming packets would block any kind of interactive functionailty, including button presses through `tkinter`. This also means that we would be too busy to send the `MRM_CONTROL_REQUEST` packet required to stop the radar from scanning.

## The Solution

Traditionally, problems such as these would be solved by implementing some sort of timeshare system, where operations would be done in discrete chunks to allow for other operations to be done in between. However, this would be very complicated to implement.

Fortunately, we can achieve a similar effect by abusing `tkinter`'s `.after()` method, which executes a function after a specified delay. By calling this method on a function from within itself, we can create a loop that allows for UI interaction while still performing the required operations.

While there are drawbacks to using this system, such as reduced responsiveness and increased CPU usage, it is a simple and effective solution to the problem at hand.

> This solution is implemented in run_frame.py [here](/src/gui/partials/run_frame.py) in method `__run_dynamic_scan()`
