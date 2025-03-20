.. DYStar Documentation documentation master file, created by
   sphinx-quickstart on Tue Jul 16 17:39:45 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Security Analysis of Cryptographic Protocols with DY*
======================================================

..
   The following introduction text is taken from our website https://www.sec.uni-stuttgart.de/research/dystar/

DY* (pronounce as "D-Y Star") is a formal verification framework for the symbolic analysis of cryptographic protocols.
The name consists of "DY" which stands for the underlying Dolev-Yao Model
and the star (\*) referring to the programming language it is written in: `F* <https://fstar-lang.org/>`_.

The framework accounts for advanced protocol features
like unbounded loops and mutable recursive data structures,
as well as low-level implementation details like
protocol state machines and message formats,
which are often at the root of real-world attacks.


DY* extends a long line of research on using dependent type systems for this task,
but takes a fundamentally new approach by explicitly modeling the global trace-based semantics within the framework,
hence bridging the gap between trace-based and type-based protocol analyses.
This approach enables us to uniformly, precisely, and soundly model, for the first time using dependent types, long-lived mutable protocol state, equational theories, fine-grained dynamic corruption, and trace-based security properties like forward secrecy and post-compromise security.

DY* is built as a library of F* modules that includes
a model of low-level protocol execution,
a Dolev-Yao symbolic attacker,
and generic security abstractions and lemmas,
all verified using F*.
The library exposes a high-level API that facilitates succinct security proofs for protocol code.

The code is available at `GitHub <https://github.com/REPROSEC/dolev-yao-star-extrinsic>`_.


In this document, we give a hands-on introduction to DY* as taught in a practical course for computer science students.

A document containing more details on the technical concepts and underlying theory of DY* can be found at :todo:`link to detailed technical doc`.
The code examples used in this tutorial and all solutions can be found at :todo:`link to GitHub Repo for this Tutorial`.


..
   |today| bablbla aha heute doch?

   Add your content using ``reStructuredText`` syntax. See the
   `reStructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_
   documentation for details.

   .. math::
      :label: eq1

      (a + b)^2  &=  (a + b)(a + b) \\
                 &=  a^2 + 2ab + b^2


   Normal text again after :math:numref:`eq1`.

   .. attention::
      achtung achtung

   .. hint::
      achtung achtung

   .. important::
      achtung achtung

   .. note::
      achtung achtung

   .. tip::
      achtung achtung


   .. reveal::
      :header: Show/Hide Code


       .. code-block::

          val f : nat -> string
          let f = fun x -> x + 4 // a simple function


.. role:: fstar(code)
   :language: fstar
   :class: highlight
   
.. toctree::
   :maxdepth: 3
   :caption: Contents

   introduction
   modelling-protocols
   stating-sec-props
   proof-method

