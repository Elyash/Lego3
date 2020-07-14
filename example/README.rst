Octavius Example
===============
As Octavius has a different usage than the old Lego version, we've added a basic example.
Newcomers should look at this example and hopefully understand better the new features of Octavius.
The theme of this example is **the Zoo.**

Components
-----------
Giraffe
^^^^^^^^
Giraffe is a very important component. Everybody could see the Giraffe because of it's long neck,
therefore we don't want to leave on it any unwanted logs.

Zebra
^^^^^^^^
Zebra isn't as important as a Giraffe, and most people don't even visit it when they go to the zoo.
Therefore we don't care if we leave on it any logs.
But, we have easy access to a Zebra and from there we can send information to other animals at the Zoo.

*Note:* It's important to mention that both of these components support
SSH, and have python installed on them.

Tools
-----

Tetanus
^^^^^^^^
Tetanus is the tool we developed for a Giraffe. Tetanus is a simple tool, it listens on a specific
port for UDP packets. Then it sends back the received data, to the animal who sent the packet.

Setup
-----
In our setup, we have only one Giraffe, whose name is "bob".
We also have 2 Zebras, one named "alice" and the other named "logan".
You could look at their configuration in [pytest.ini](/example/pytest.ini) (pytest configuration file).
