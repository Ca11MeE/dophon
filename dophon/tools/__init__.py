import platform


def is_windows():
    return 'Windows' == platform.system()


def is_not_windows():
    return not is_windows()


def show_banner():
    print("""
          .o8                       oooo                              
         "888                       `888                              
     .oooo888   .ooooo.  oo.ooooo.   888 .oo.    .ooooo.  ooo. .oo.   
    d88' `888  d88' `88b  888' `88b  888P"Y88b  d88' `88b `888P"Y88b  
    888   888  888   888  888   888  888   888  888   888  888   888  
    888   888  888   888  888   888  888   888  888   888  888   888  
    `Y8bod88P" `Y8bod8P'  888bod8P' o888o o888o `Y8bod8P' o888o o888o 
                          888                                         
                         o888o                                                     
     Author:CallMeE
     Url:https://github.com/Ca11MeE/dophon.git
         https://gitee.com/callmee/dophon.git                                                                          
    """)
