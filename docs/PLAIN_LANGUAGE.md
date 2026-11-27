# What does Vortex do?

Vortex asks two connected questions: can organized motion help gather particles, and can describing that motion with a compact rule help us store it in smaller files? Each question needs its own test.

Imagine dropping a thin string into moving water. Some parts stretch, some bunch together, and some turn. Vortex uses a known mathematical flow to show that motion and check whether the computer's calculations are correct.

It also tests a recipe for an animation. Instead of saving every position of every point, a small set of instructions rebuilds the planned shapes. That worked when we compared the recipe with the original calculation on the same computer. Different computer systems can produce tiny differences, which matter when checking for an exact match.

We also tested ordinary compression on a separate set of flow data. Compression means storing information using fewer bytes so the file takes up less space. Standard compression made the smallest files in that test. We have not yet shown that a new method based on motion can beat it.

The useful result so far is a working set of demonstrations, checking tools, and measured results. Someone else can run the tools and check what happened. We have not yet shown that the proposed flow collects particles or that a new motion-based method saves space on independent data.

For the collection test, particles must move according to specified forces. We would count how many enter a collector, how many stay after a set time, how many leave, and how much energy the process uses. A donut shape by itself is not a successful collection result. Gathering particles also does not mean squeezing the liquid into a smaller volume.

For the storage test, we would start with motion we did not design to match our recipe. We would save the rule and every correction it needs, then check whether the full package is smaller than ordinary compression while rebuilding the exact data.

The connection is simple: a successful collection experiment could supply real motion data for the storage test. Passing either test would not automatically mean passing the other.

The donut-shaped animation is a shape we programmed. It does not prove that real water behaves that way. Rebuilding point positions also does not rebuild every pixel of a video.

## What can I try?

- Open [Inkline Vector Lab](../demos/inkline/index.html) in a browser after downloading the repository. It shows the known swirling pattern and a moving point.
- Open [Juicy Donut Lab](../demos/torus/index.html) to explore a smaller preview of the planned shape change.
- Read the [paper](Vortex-Thread-Motion-v1.0.0.pdf) for the math, measurements, sources, and limits.

Aaron Michael Weis | OneiroNexus
