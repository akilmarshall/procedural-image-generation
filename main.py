from pygen.util import TIS
from pygen.fragment import FragmentCenter

tis = TIS()
tis.dump_all_neighbor()
frag = FragmentCenter(tis)
frag.dump_all_fragment()
