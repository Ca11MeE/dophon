from dophon import dophon_boot
from dophon.boot import BeanScan
from dophon.boot import TORNADO


@dophon_boot
@BeanScan()
def run(boot):
    boot.run(TORNADO)


run()