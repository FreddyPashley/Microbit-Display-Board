# Definitions

* Bit - Physical microbit

* Bot - A bit active in the display board

* Server - A bit containing the desired display message, as well as the code to distribute the message to the bots

* Serial - The hexadecimal serial code unique to a bit

# Message Format

`recipient:id:status_code:data`

* recipient - The serial number of the intended receiving device. Exception is `SERVER` which will be detected by the server bit

* id - Transmission ID. A random integer value to minimise the likelyhood of identical IDs at the same time.

* status_code - Aids in the interpretation of the transmission. Mainly used for distinguishing between instructions and display data.

    * 0 - Reply not expected
    * 1 - Reply expected
    * 2 - Preset instruction
    * 3 - Display

* data - Self-explanatory.

# Pre-set instructions

* send_serial - Bit is to sent its serial

* wait_for_id_press - Bit is to wait for a button press, then will send serial

* does_id_exist - Bit is to send serial if their serial matches serial in data

* clear - Bit is to clear its screen
