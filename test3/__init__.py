from dophon import boot


def run():
    boot.fix_static(enhance_power=True)
    boot.fix_template()
    boot.run_app_ssl()
    # boot.run_app()


run()
