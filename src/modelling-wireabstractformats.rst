Wire-format and Abstract Formats for Messages and Sessions
-----------------------------------------------------------

:todo:`should this concept move to the concepts section? (without code records)`

On the lowest level of a real network,
messages are sent in a wire-format
which can be thought of as a byte-stream without any structure.
But the different network layers interpret this stream
and give it some structure to make processing on higher layers easier.
For example a UDP message contains
some header that has several fields with meta-information followed by the actual
content of the message.
Further, the higher layers don’t really care about or even need to
know how their message is encoded on the lower layers.
They just work with the content they need.

In DY* we use the same idea:
The content of entries on the trace are stored in the wire-format, which is called :fstar:`bytes`.
But if we implement a protocol we don’t want to work with the wire-format,
instead we are only interested in the *content* of the messages.
We collect the different components of our messages in an *abstract format*.


Abstract Formats for Messages
.............................

.. example:: Abstract Message Format for the Two-Message Protocol

   The first message of the Two-Message Protocol (the Ping)
   has the following abstract structure:
   it consists of two entries,
   one of which is the name of Alice and the other one is some nonce.

   The second message (the Ack) contains only one entry: the nonce.

In our implementations, we use F*'s `record type <https://fstar-lang.org/tutorial/book/part1/part1_inductives.html#records>`_ for abstract message formats.

.. _ex-abstract-messages-twomessagep:

.. example:: The records for the Abstract Format for the Two-Message Protocol
           
   We define a new type for the Ping message,
   collecting the two entries:
      
    .. code::

       type ping_t = {
         alice: principal;
         n_a : bytes;
       }

   The name of Alice is captured in the :code:`alice` component.
   It is a field of type :code:`principal` (which is just a :code:`string`).

   The nonce is caputured in the :code:`n_a` component.
   This field is of type :code:`bytes`.

   Similarly, we define a new type for the Ack message:

   .. code::

      type ack_t = {
        n_a : bytes;
      }

.. example:: Abstract Message Format for the Online? Example

   The messages of the Online? protocol,
   have the same structures as the messages for the Two-Message protocol.
   We can thus use the same record types.

.. exercise:: Abstract Message Format for the Needham-Schroeder Protocol

   Describe the abstract message format for the Needham-Schroeder protocol
   and define the corresponding record types.

   .. toggle-answer::

      The first message consists of two parts:
      the name of Alice, and a nonce.
      Similarly to before, we define the record:

      .. code::

         type message1_t = {
           alice: principal;
           n_a : bytes;
         }
         
      The second message also has two parts:
      the two nonces.
      We define the record:

      .. code::

         type message2_t = {
           n_a : bytes;
           n_b : bytes;
         }

      The final message contains only the nonce of Bob:

      .. code::

         type message3_t = {
           n_b : bytes;
         }
      

Abstract Formats for States
...........................
         
We do the same for states:
States are also stored on the trace in the wire-format,
however, we want to work with a more structured abstract format.

.. example:: Abstract State Format for the Two-Message Protocol

   In the Two-Message protocol,
   we have three states
   (recall from `Example: States in one run of the Two-Message Protocol <ex-states-twomessage>`):

   * The first state (SentPing) consists of two parts: the nonce :math:`n_A` and the name of Bob.
   * The second state (SentAck) also consists of two parts: the nonce :math:`n_A` and the name of Alice.
   * Finally, the third state (ReceivedAck) also consists of two parts: the nonce :math:`n_A` and the name of Bob.

   This describes the abstract state format.


.. _ex-abstract-state-twomessage:
   
.. example:: The records for the Abstract State Format for the Two-Message Protocol

   From the abstract state format,
   we define the record types:

   .. code::
      
      type sent_ping_t = {
        bob : principal;
        n_a : bytes;
      }

   .. code::

      type sent_ack_t = {
        alice: principal;
        n_a : bytes;
      }

   .. code::
      
      type received_ack_t = {
        bob : principal;
        n_a : bytes;
      }

.. exercise:: Abstract State Format for the Needham-Schroeder Protocol

   Describe the abstract state format for the Needham-Schroeder protocol
   and define the corresponding record types.
   (Refer to `Exercise:States in the Needham-Schroeder Protocol <ex-states-ns>` for the states.)
   Consider *only* the states storing the progress of the protocol. (I.e., ignore the states for storing keys.)


   .. toggle-answer::
                  
      There are 4 kinds of states for storing the protocol progress:

      * The state, after Alice sent the first messge (SentMsg1):
        it contains two parts: the nonce :math:`n_A` and the name of Bob
      * The state after Bob replied with a second message (SentMsg2):
        it contains three parts: the two nonces :math:`n_A` and :math:`n_B` and the name of Alice
      * The state after Alice receives the third message from Bob:
        it contains three parts: the two nonces and the name of Bob
      * The state after Bob received the third message from Alice:
        it stores the same things as the previous state of Bob:
        the two nonces and the name of Alice


      We define the record types:

      .. code::

         type sent_msg1_t = {
           bob : principal;
           n_a : bytes;
         }

      .. code::

         type sent_msg2_t = {
           alice : principal;
           n_a : bytes;
           n_b : bytes;
         }

      .. code::

         type sent_msg3_t = {
           bob : principal;
           n_a : bytes;
           n_b : bytes;
         }

      .. code::

         type received_msg3_t = {
           alice : principal;
           n_a : bytes;
           n_b : bytes;
         }

Translating between Abstract and Wire-Format
.............................................
         
Once we have our abstract message and state formats,
we need to take care of transforming this abstract format to the
wire-format and vice versa.
For example, when sending a message and when receiving a message,
we need to translate from the abstract message format to the wire-format and vice versa, respectively.
Similarly, when we want to store a state on the trace,
we need to translate from the abstract state format to the wire-format.
We call the translations *serializing* (abstract to wire-format) and *parsing* (wire to abstract format).

We use a tool called `Comparse <https://github.com/TWal/comparse>`_ for translating between abstract and wire-format.
We will not go into the details of how Comparse works.
We just use it and explain everything necessary for that.


.. remember:: 

   * Everything stored on the trace, is stored using the *wire-format* :code:`bytes`.
   * In a protocol model, we work with *abstract formats*
     for messages and states, i.e., just the contents.
   * Translating from abstract to wire-format is called *serializing*
   * Translating from wire to abstract format is called *parsing*
