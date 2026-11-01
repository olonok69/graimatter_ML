"""Hiding data in a model, and the defences that remove it (demo 6).

Two channels, both on the same synthetic cohort as the other demos:

* ``weights`` — least-significant-bit steganography in the model's float
  parameters, the way EvilModel (2021) hid files in a network's weights.
* ``behaviour`` — a secret that only a trigger input brings out, the way
  backdoor watermarking (Adi et al. 2018) and memorisation (Song et al. 2017)
  encode a message in what the model does rather than in its bytes.

* ``defences`` — clipping the low bits, quantising, adding noise, and a
  distribution test, and how much of each channel they remove.

Walkthrough: Demo guide §6 (docs/guide/Demo_Guide_EN.md; Spanish: Guia_Demos_ES.md).
Nothing here hides executable code: the payload is a short text or a few
fabricated records, to stand for data exfiltrated from a TRE.
"""
