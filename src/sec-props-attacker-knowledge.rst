.. _sec-attacker-knowledge:

Attacker Knowledge and Corruption
---------------------------------

Attacker Knowledge
~~~~~~~~~~~~~~~~~~

In DY* we consider an active network attacker that can
read messages from the trace,
corrupt states
and derive new terms from these.
With "attacker knowledge",
we denote the set of all terms that the attacker
can construct.
The attacker knowledge is defined recursively
in the ``attacker_knows_aux`` function in ``DY.Core.Attacker.Knowledge``
which we will now discuss on a high level.

The base case consists of three possibilities:

* The attacker knows any *message* that is sent over the network,
  i.e., the content of every message entry on the trace.
* The attacker knows any *constant*,
  i.e., values like strings and numbers.
  (That is, he can construct any string.)
* The attacker knows the content of any *state*,
  that he corrupted (via a corruption entry on the trace).

From this immediate knowledge he can read from the trace,
and any prior knowledge he has,
he can construct more terms by applying cryptographical functions.
:todo:`ignoring concat and split on purpose! since we didn't talk about our symbolic terms so far, and i don't know where we actually need this`
For example for public key encryption: 

* If the attacker knows a private key,
  he also knows the corresponding public key.
* If the attacker knows
  the public key, the nonce and the plaintext,
  he can construct the ciphertext corresponding to
  the public key encryption
  of the plaintext using the public key and the nonce.
* If the attacker knows the private key
  and a ciphertext,
  he can construct the decrypted plaintext
  corresponding to the ciphertext under that private key.

And there are similar intuitive derivation rules
for symmetric encryption (AEAD), signatures, hashes,
Diffie-Hellman, KDFs and KEM,
which we will not go into details here.

.. remember:: Attacker Knowledge

   The attacker knows any
   
   * message on the trace,
   * constant and
   * state, he corrupted.

   From this knowledge,
   he can build more terms by applying cryptographic functions.
   For example public key de-/encryption and related keys.

Corruption
~~~~~~~~~~

In DY* we have a fine-grained corruption model,
where the attacker can corrupt single states of a participant,
a whole session of a participant,
or the full state of a participant.

:todo:`Work in progress: continue from here`
