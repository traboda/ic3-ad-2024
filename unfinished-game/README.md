# Unfinished Game

## Game

The overall flow of a game session is as follows:

* Client connects to server over TCP
* Client enters username & password to either register/login
* Client plays game
* Client disconnects

The game itself is composed of two things

* rooms (with titles and descriptions)
* items (with titles and actions that can be performed)
    * NOTE (which can be read)
    * TELEPORT (which when taken teleports user)
    * SWORD (special item)
    * SCRIBE (special item)

There are three valid commands that a player can make

* mov arg (used to move around in the world)
* take arg (used to interact with items)
* read arg (used to read items that are notes)

where arg is a three letter word derived from the title of the
room/object. Some examples are given below.

* to move to a room titled INSIDE THE CAVE
    * mov ITC
* to interact with A Blue Diamond
    * take ABD

The objective of the game is to kill the orc that resides within
the cave. If the player picks up the sword from inside the room
before going to the cave, the player automatically wins. Once they
win the game, they can go to the winners room and record a message
by interacting with the rat scribe. Then they can retry the game
again and again as many times as they want.


## Objective

The actual objective of the player is to read the message stored by
a random player. This is possible because of the following things.

* After finishing the game, the player can change their username to
whatever they want to (but the password remains the same).
* The rat scribe will print previously stored player messages if there
are any.

This makes it seem trivial but there are obstacles to this approach.

* When storing the message, it's encrypted using the player password.
* When printing the message, it's decrypted using the current password.

This means that when we try to change the username and print the password,
it won't be perfectly decrypted as it will be decrypted using our original
player password.

## Vulnerability

The actual encryption/decryption process is quite simple. A 64bit seed is
derived from the password and its then used to initialize a PRNG and its
out is used to xor encode the message. Since its xor encoding, the process
is just repeated to decrypt the message.

The seed is bruteforcable as the program discards 32bits and only uses the
remaining 32bits as seed to the PRNG and we already know the initial bytes
of the message ('flag{'). The exploit itself is a bit more involved as the
actual encoded message will be encoded once more with the attacker password
when printed.

Check out exploit.c to see how seed can be bruteforced using multiple threads
within seconds on a modern machine and check out exploit-full.c for the full
chain exploit.

