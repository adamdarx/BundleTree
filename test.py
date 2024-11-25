from DataStructure import *

cht1 = Chart([0,0,0], [1,1,1], (2,2,2))
cht2 = cht1.refine(2)

print(cht1)

bld1 = Bundle(cht1, 8)
bld2 = bld1.refine(2)

root = TreeNode(bld1)
