# -*- coding: utf-8 -*-
from dophon import blue_print
from dophon.annotation import *
from flask import url_for
from flask import render_template
from flask import send_from_directory
app = blue_print('FrameworkStaticRoute', __name__,static_folder='D:/Desktop/dophon/test3/static')
@RequestMapping('/<file_name>',['get','post'])
def DDesktopdophontest3static__8ec295e25b3e11e9a9d6e3a6865c(file_name):
	"""
	static file route in /<file_name>
	:param file_name: static file name
	:return static file blob
	"""
	return render_template(f'/{file_name}') if file_name.endswith('.html') else send_from_directory('D:/Desktop/dophon/test3/static',f'{file_name}',as_attachment=True)
