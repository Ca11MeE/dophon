from dophon import dophon_boot
from dophon.boot import TORNADO


@dophon_boot
def run(boot):
    boot.run(TORNADO)


run()