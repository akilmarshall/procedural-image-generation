from pygen.util import TIS
from pygen.fragment import FragmentCorner, FragmentCenter

tis = TIS()
center = FragmentCenter(tis)
corner = FragmentCorner(tis)

tis.dump_all_neighbor()
center.dump_all_fragment()
corner.dump_all_fragment()
