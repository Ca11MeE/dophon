from dophon import dophon_boot

# from dophon import boot

# boot.tornado()

@dophon_boot
def run(boot):
    boot.tornado()
    pass

run()