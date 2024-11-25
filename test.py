from DataStructure import *

cht1 = Chart([0,0,0], [1,1,1], nGrid=(2, 2, 2))
cht2 = cht1.refine(2)

bld1 = Bundle(cht1, 8)
bld2 = bld1.refine(2)
# PROBLEM: as nGrid gets greater, efficiency declines greatly! Attempt to use MPI for interpolation.
print(bld1)

root = TreeNode(bld1)
print(root)
