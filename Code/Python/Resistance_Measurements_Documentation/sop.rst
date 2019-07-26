***
SOP
***

.. _sop-home:

Entering a Wafer in the Database
================================
* In order to access the database, go to the following link: `Database <http://686qvalessio:5000/admin/>`_
* Navigate to the *Wafer* tab and click on *Create*
* In **Name** enter wafer name
* In **Date** enter creation date
* In **Approximate Jc** enter Approximate Jc (in A/m\ :sup:`2`\ )
* Enter chips if previously entered chips are associated with the wafer. If it's a new wafer, leave blank
* After completing all fields, click *Save* 


Entering a Chip in the Database
=================================

* In order to access the database, go to the following link: `Database <http://686qvalessio:5000/admin/>`_
* Navigate to the *Chip* tab and click on *Create*

  * If the chip is the first of its wafer, follow the steps in `Entering a Wafer in the Database`_

  * If the chip is the first of its type, follow the steps in `Entering a Design in the Database`_

* In **Name** enter chip name in the following format: **Wafer Name-Chip Location**

* In **Location** enter chip location
* The fields that follow should contain the corresponding wafer and design in the drop-down that results when it is clicked
* Leave the **JJ Measurements** field blank
* After completing all fields, click *Save*

Entering a Design in the Database
=================================
* In order to access the database, go to the following link: `Database <http://686qvalessio:5000/admin/>`_
* Navigate to the *Design* tab and click on *Create*
* In **Name** enter design name
* In **Date** enter design date
* Select all of the devices associated with the design in the dropdown of the **Device Id** field
* If there are diferent devices than what is in the database already, follow the steps in `Entering a Device in the Database`_
* Leave the **Chips** and **JJ Measurements** fields blank

Entering a Device in the Database
=================================
* In order to access the database, go to the following link: `Database <http://686qvalessio:5000/admin/>`_
* Navigate to the *Device* tab and click *Create*
* In **Design Id** enter the design that the device is associated with. (Can be multiple)
* In **Name** enter device name
* In **Type** enter device type

  * The options are: 'JJArray', 'SingleJunction', 'Via', 'ResistorArray', or 'SQUID'

* In **Num JJs** enter the number of JJs for the device. The following are for reference:

+-------------+---------------------+
| Device Type | Number of Junctions |
+=============+=====================+
| Single      |                     |
| Junction    |         1           |
+-------------+---------------------+
| JJ Array    |        400          |
+-------------+---------------------+
| SQUID       |         2           |
+-------------+---------------------+
| Via         |         0           |
+-------------+---------------------+
| Resistor    |         0           |
| Array       |                     |
+-------------+---------------------+
| Stacked     |         2           |
| Junction    |                     |
+-------------+---------------------+

* In **JJ Radius Nom** enter the radius of the Junction, in um. (For those that are 0, enter 0)
* **Pads** relate to the pads on chip that the device is connected to. There are four of these
* **Card 1** and **Card 2** are the cards in the switch box that the pads are wired to. See the `Xcel file <7011_switch_matrix.xlsx>`_
* **Channel 1** and **Channel 2** are related to the banks on the card
* (Optional) Enter a description


Taking Measurements
===================

There are two ways to take measurements:

* `Using the GUI`_
* `Command Line`_

Using the GUI
=============

* Open an IPython console or use the Ipython console insde Spyder

* Enter the following::
  
   %cd "Z:/JPulecio/Code/Python/Resistance_Measurements/Beta"

* Hit enter and then type::  

   run Measurement_GUI_v3.py

* Select a Wafer and Chip from the dropdown menus at the top of the GUI

* If a chip is entered after running the GUI, you must refresh the database in order for the chip to appear in the dropdown

* Select which devices to measure by using the checkboxes in the table. To toggle all devices on and off use the radio button labelled "All" in the top right corner below "Close All Graphs"

* Click the button for which measurment is needed
  
  * The Full test button on top will run the Warm and then Cold test
    
  * After the warm test is complete a pop-up window will appear with any abnormal graphs. Hitting Ok will open another pop-up window that will prompt you to Continue with the Cold Test. This will start the Cold test immediately so **do not** hit okay until ready.

  * The Warm test will only run the warm portion of the Full Test but does save the data to the database.

  * The Cold test will only run the cold portion of the Full Test but does save the data to the database.

  * The Contunity, I-V, and RN buttons run their respective tests but do NOT save the data to the database 


* *Note:* Occasionally while using the GUI, some of the images of graphs are not saved, but the full data will still be saved. This bug is being worked on. 


Command Line
============

* Once the chip is in the database and ready to be measured enter the following code in the command line::

	
   %cd "Z:/JPulecio/Code/Python/Resistance_Measurements"
   import Measurement_Functions as mf
   import database_v4 as d
   import imp

* These commands go to the correct directory and import the important modules that will be used

* The correct chip should now be populated into the workspace

  * First, get an array of all the chips in the database::

	all_chips = d.show_all_chips()

  * Next, select the most recent chip entered (the last one in the array)::
	
	chip = all_chips[-1]

  * Alternatively, show all the chips and select which one is to be measured::

	# print all the chips with their index:

	for i in range(0,len(all_chips)):
		print("%s: %s"%(i, all_chips[i].name))

    * Select the corresponding index for the chip from the printed list::

        	chip = all_chips[5] # for example

* Get the devices associated with the selected chip::

	devices = d.show_devices_from_chip(chip.name)

* Begin to dunk the chip. While it is stil at room temperature (still near top of dewar), plug in cables A, B, C, D to corresponding locations on probe. Execute the following function::

	mf.measure_PCM_chip_warm(chip.name, devices)

  * This function has built-in continuity checks for all the devices. Take note if a device seems to be open or shorted. That is, the I-V line is not linear.

* Once all measurements are taken, proceed to slowly dunk the probe as to not trap flux.

* After fully dunked, execute the following function::

	mf.measure_PCM_chip_cold(chip.name, devices)

* Now the chip is fully measured, but the values found for normal resistance could be wrong. It is necessary to manually overwrite correct Rn values

  * Find the directory which has all the data. Can be found `here <http://686qvalessio:5000/admin/jj_measurement/>`_ or by going to the directory:

	*E:/Users/volt.686QVACTEST/Documents/JPulecio/OneDrive/National Institute of Standards and Technology (NIST)/SEG - Documents/SFQ_circuits/Measurements*

  * Import the function that will allow to select points for slope and will automatically overwrite data in database::

	import Overwrite_Rn as OR

  * By looking through images of Rn, find a device which has an incorrect Rn found

  * Copy the entire path to the corresponding *_Rn_raw.dat* file for that device (or drag and drop the file into command line) in place of filename::

	OR.open_data("filename")

  * This function will open a graph with the sweep taken to find Rn. Click two points to find slope for Rn and then a point for Imax. Follow instructions printed out, if needed.

* Done! Measurements can be seen in all their glory in the `report <http://686qvalessio:5001/report>`_.

	
