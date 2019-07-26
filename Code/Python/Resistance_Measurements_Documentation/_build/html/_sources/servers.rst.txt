********************
Server/ DB Reference
********************

Starting the Servers
====================
* There must always be an anaconda command prompt open, which is running all 3 of the server ports simultaneously
* If there is a problem with the servers, the first check would be to see if this windows is open. If not, the servers may have to be started
	* If they are open and there are issues, CTRL+BREAK (break/pause button) and restart the servers 
* To start the servers, open any command prompt and run (the cd may not be necessary)::

   cd E:\Users\volt.686QVACTEST
   begin_servers.cmd

* This should run 3 separate processes in the same window and begin the servers hosting the SQL database, this homepage, the DB view, and report.

Under the Hood
==============
* There are four main things that happen if everything is to be run smoothly:
* The mysql database is started (not sure how necessary)
	* located in MariaDB/mariadb-10.2.12-winx64/mariadb-10.2.12-winx64/bin
	* command is mysqld --console
* The static homepage is served through the http.server python built-in
	* done by cd'ing into html directory and running python -m http.server [port #] (we use 8000)
* The flask page for the DB is started
	* JPulecio\Flask\flask-admin-run1\flask_test3.py
* The flask page for the report is started
	* JPulecio\Flask\Reports\app.py
