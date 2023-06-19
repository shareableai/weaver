"""
The point of Weaver is to replace Pickle in a specialised capacity.

Weaver provides a clear and queryable object for serialization, at the cost of performance.

Pickle should be selected whenever performance is of a concern. Weaver should be selected when reproducibility,
safety, and visibility, is more important.

Weaver optionally uses a backend through ShareableAI, which allows for storing reused class artefacts in a more general
way. In addition to reducing bloat within the final item - it's a little silly to advocate for visibility and also try
and show you a 5GB Tensor(!) - this allows for sharing large items that reuse artefacts in a very cheap manner.
"""

import weaver

__version__ = (0, 0, 1)
