Welcome to Octavius's documentation!
=================================

Octavius is a new distributed testing infrastructure used to test and monitor our
products in the network.

Lego 3 is a completely new project, written from scratch, but its requirements based on insights
from the previous Lego infrastructure we used.

Features
--------
* **Zero deploy** - With Octavius, if your component support SSH and python, you won't have to upload anything to allow
  your tests to run code on your setup components!

* **New Technologies** - Octavius was developed in python3.8 and therefore supports new python3
  features and new third party libraries. You can read on more new technologies used in Octavius below.

* **Resource Management** - Octavius have a lego manager which can allocate unused components for
  your tests. It can also control the timing of the tests to allow maximum usage of the setup.
  Lego manager will also provide information on the state of the setup.

.. warning:: Most of the features mentioned above in **Resource Management** aren't implemented
 yet.


New Technologies
-----------------
1. **Python 3.8** - In order to take leverage of AsyncIO and Python's most advanced features.
2. **Pytest** - A testing framework provides many features

   * Async tests - test may run simultaneously.
   * Easy test runner - Auto-discovery of test modules and functions
   * Fixtures - for managing small or parametrized long-lived test resources
   * Detailed info on failing assert statements (no need to remember self.assert* names)
   * Rich plugin architecture, with over 315+ external plugins and thriving community

3. **RPyC** - Provides a simple way of executing code on remote machines and easy deployment of
   slaves. Using RPyC all remote code is identical (allows arbitrary code execution) and the
   specify logic implemented by the client which uses the machine.
4. **AsyncIO** - Allows running multiple tests simultaneously. This way, when one test waits
   for setup other tests are able to run.

Terminology
-----------
* **Test** - Code which runs on the user's computer.
* **Component** - API to a remote machine on which we want to run code.
* **Lego Plugin / Lego Core** - Core functionality for running the Lego test. Actually, this is a PyTest plugin.
* **User Library** - Wrapper of Core Library which implements user-specific logic.
* **Resource Manager** - Service which managers the setup resources. Runs on the central server. Each test requiring setup will perform allocations and deallocations using this service. The Resource Manager enables to control of the setup - tests relationship (view and manage the setup usage by users, test priority management, test info (run time, runnings numbers, etc.)).


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   guides/installation_guide
   guides/tutorial
   guides/conventions_guide
   development_helpers/developer_helpers
   configurations/conventions_linters



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
