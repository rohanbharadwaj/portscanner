CSE508 – Spring 2015
====================

Distributed Network and TCP Port Scanner with Web UI
----------------------------------------------------

Network Scanners and Port Scanners are essential tools when trying to
understand the layout of a network and the services that a specific host
is running. In this project, you are called to design and implement a
Distributed Network and Port Scanner with a Web UI that can be used to
control the scanner.

Your scanner must be distributed so that many hosts (called scanning
nodes) can participate in a single scanning effort.

You can use whatever language and protocols you want to implement the
scanning nodes and the communication between the main server and the
scanning nodes. Obviously, you should implement everything by yourself.
**DO NOT** use a ready-made port scanner and just make it distributed.
**ANY** code fragments that you find and use from the web, you should
document them in your report.

Components:
-----------

### Main controlling server with Web UI

In your project, there is one main server that is orchestrating the
scanning effort of your distributed network and port scanner. This
server should accept jobs through a Web UI (use Bootstrap to make the
UI), communicate with your individual scanning nodes, collect the
information from the scanning nodes, and present it to the user.

The controlling server must have a way where scanning nodes can
automatically subscribe themselves. Thus, a controlling server must be
able to command a variable number of scanning nodes without any code
changes. For instance, if there are 10 scanning nodes and a user
requests the scanning of all ports from a remote IP address, the main
controlling server must send out to each scanning node the IP address of
the target, the mode of scanning (isAlive/port scanning), the ports that
the node must scan (e.g. 100-500) and the mode of scanning (see next
section).

The server must collect the information sent back from each server,
create a report, store it in a database, and show the report to the user
through the Web UI.

### Scanning Nodes

This is where the meat of the project will be. Each scanning node can
connect to the main controlling server and report for duty. Once the
scanning node is registered, it will then wait for commands from the
central server. The commands that can arrive from the server are:

<ul>
<li>
Check whether an IP address is alive (e.g. 1.2.3.4)

</li>
<li>
Find which IP addresses are alive in a block of IP addresses (e.g.
1.2.3.4/255)

</li>
<li>
Port scan an IP address for a given set of ports using any of the
following scanning modes: (More info [here][])

</li>
<ul>
<li>
Normal Port Scanning (full TCP connect to the remote IP address)

</li>
-   When this mode is requested, you should also grab the banner send by
    the server and send it back to the controlling server

<li>
TCP SYN Scanning (only send the initial SYN Packet and

  [here]: http://nmap.org/nmap_doc.html#connect
