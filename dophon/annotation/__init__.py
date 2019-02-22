# coding: utf-8
from dophon.annotation import AutoWired
from dophon.annotation import res, req
from dophon.annotation.AutoWired import *
from dophon.annotation.description import *

"""
注解集合(部分)
author:CallMeE
date:2018-06-01


"""
__all__ = [
    'ResponseBody',
    'ResponseTemplate',
    'AutoParam',
    'FullParam',
    'RequestMapping',
    'GetRoute',
    'PostRoute',
    'Get',
    'Post',
    'AutoWired',
    'AsResBody',
    'AsResTemp',
    'AsArgs',
    'AsJson',
    'AsFile',
    'BeanConfig',
    'bean',
    'Bean',
    'Desc'
]

AutoWired = AutoWired

ResponseBody = AsResBody = res.response_body

ResponseTemplate = AsResTemp = res.response_template

AutoParam = AsArgs = req.auto_param

FullParam = AsJson = req.full_param

FileParam = AsFile = req.file_param

BeanConfig = AutoWired.BeanConfig

bean = AutoWired.bean

Bean = AutoWired.Bean

RequestMapping = req.request_mapping

GetRoute = req.get_route

PostRoute = req.post_route

Get = req.get

Post = req.post

Desc = desc
