#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tornado.ioloop
import tornado.web
import re


class Field(object):
    def __init__(self, error_msg_dict, required):
        self.id_valid = False
        self.value = None
        self.error = None
        self.name = None
        self.error_msg = error_msg_dict
        self.required = required

    def match(self, name, value):
        self.name = name

        if not self.required:
            self.id_valid = True
            self.value = value
        else:
            if not value:
                if self.error_msg.get('required', None):
                    self.error = self.error_msg['required']
                else:
                    self.error = "%s is required" % name
            else:
                ret = re.match(self.REGULAR, value)
                if ret:
                    self.id_valid = True
                    self.value = ret.group()
                else:
                    if self.error_msg.get('valid', None):
                        self.error = self.error_msg['valid']
                    else:
                        self.error = "%s is invalid" % name


class IPField(Field):
    REGULAR = "^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$"

    def __init__(self, error_msg_dict=None, required=True):
        error_msg = {}  # {'required': 'IP不能为空', 'valid': 'IP格式错误'}
        if error_msg_dict:
            error_msg.update(error_msg_dict)

        super(IPField, self).__init__(error_msg_dict=error_msg, required=required)


class IntegerField(Field):
    REGULAR = "^\d+$"

    def __init__(self, error_msg_dict=None, required=True):
        error_msg = {'required': '数字不能为空', 'valid': '数字格式错误'}
        if error_msg_dict:
            error_msg.update(error_msg_dict)

        super(IntegerField, self).__init__(error_msg_dict=error_msg, required=required)


class CheckBoxField(Field):
    def __init__(self, error_msg_dict=None, required=True):
        error_msg = {}  # {'required': 'IP不能为空', 'valid': 'IP格式错误'}
        if error_msg_dict:
            error_msg.update(error_msg_dict)

        super(CheckBoxField, self).__init__(error_msg_dict=error_msg, required=required)

    def match(self, name, value):
        self.name = name

        if not self.required:
            self.id_valid = True
            self.value = value
        else:
            if not value:
                if self.error_msg.get('required', None):
                    self.error = self.error_msg['required']
                else:
                    self.error = "%s is required" % name
            else:
                if isinstance(name, list):
                    self.id_valid = True
                    self.value = value
                else:
                    if self.error_msg.get('valid', None):
                        self.error = self.error_msg['valid']
                    else:
                        self.error = "%s is invalid" % name


class FileField(Field):
    REGULAR = "^(\w+\.pdf)|(\w+\.mp3)|(\w+\.py)$"

    def __init__(self, error_msg_dict=None, required=True):
        error_msg = {}  # {'required': '数字不能为空', 'valid': '数字格式错误'}
        if error_msg_dict:
            error_msg.update(error_msg_dict)

        super(FileField, self).__init__(error_msg_dict=error_msg, required=required)

    def match(self, name, value):
        self.name = name
        self.value = []
        if not self.required:
            self.id_valid = True
            self.value = value
        else:
            if not value:
                if self.error_msg.get('required', None):
                    self.error = self.error_msg['required']
                else:
                    self.error = "%s is required" % name
            else:
                m = re.compile(self.REGULAR)
                if isinstance(value, list):
                    for file_name in value:
                        r = m.match(file_name)
                        if r:
                            self.value.append(r.group())
                            self.id_valid = True
                        else:
                            self.id_valid = False
                            if self.error_msg.get('valid', None):
                                self.error = self.error_msg['valid']
                            else:
                                self.error = "%s is invalid" % name
                            break
                else:
                    if self.error_msg.get('valid', None):
                        self.error = self.error_msg['valid']
                    else:
                        self.error = "%s is invalid" % name

    def save(self, request, upload_path=""):

        file_metas = request.files[self.name]
        for meta in file_metas:
            file_name = meta['filename']
            with open(file_name, 'wb') as up:
                up.write(meta['body'])


class Form(object):
    def __init__(self):
        self.value_dict = {}
        self.error_dict = {}
        self.valid_status = True

    def validate(self, request, depth=10, pre_key=""):

        self.initialize()
        self.__valid(self, request, depth, pre_key)

    def initialize(self):
        pass

    def __valid(self, form_obj, request, depth, pre_key):
        """
        验证用户表单请求的数据
        :param form_obj: Form对象（Form派生类的对象）
        :param request: Http请求上下文（用于从请求中获取用户提交的值）
        :param depth: 对Form内容的深度的支持
        :param pre_key: Html中name属性值的前缀（多层Form时，内部递归时设置，无需理会）
        :return: 是否验证通过，True：验证成功；False：验证失败
        """

        depth -= 1
        if depth < 0:
            return None
        form_field_dict = form_obj.__dict__
        for key, field_obj in form_field_dict.items():
            print key, field_obj
            if isinstance(field_obj, Form) or isinstance(field_obj, Field):
                if isinstance(field_obj, Form):
                    # 获取以key开头的所有的值，以参数的形式传至
                    self.__valid(field_obj, request, depth, key)
                    continue
                if pre_key:
                    key = "%s.%s" % (pre_key, key)

                if isinstance(field_obj, CheckBoxField):
                    post_value = request.get_arguments(key, None)
                elif isinstance(field_obj, FileField):
                    post_value = []
                    file_list = request.request.files.get(key, None)
                    for file_item in file_list:
                        post_value.append(file_item['filename'])
                else:
                    post_value = request.get_argument(key, None)

                print post_value
                # 让提交的数据 和 定义的正则表达式进行匹配
                field_obj.match(key, post_value)
                if field_obj.id_valid:
                    self.value_dict[key] = field_obj.value
                else:
                    self.error_dict[key] = field_obj.error
                    self.valid_status = False


class ListForm(object):
    def __init__(self, form_type):
        self.form_type = form_type
        self.valid_status = True
        self.value_dict = {}
        self.error_dict = {}

    def validate(self, request):
        name_list = request.request.arguments.keys() + request.request.files.keys()
        index = 0
        flag = False
        while True:
            pre_key = "[%d]" % index
            for name in name_list:
                if name.startswith(pre_key):
                    flag = True
                    break
            if flag:
                form_obj = self.form_type()
                form_obj.validate(request, depth=10, pre_key="[%d]" % index)
                if form_obj.valid_status:
                    self.value_dict[index] = form_obj.value_dict
                else:
                    self.error_dict[index] = form_obj.error_dict
                    self.valid_status = False
            else:
                break

            index += 1
            flag = False


class MainForm(Form):
    def __init__(self):
        # self.ip = IPField(required=True)
        # self.port = IntegerField(required=True)
        # self.new_ip = IPField(required=True)
        # self.second = SecondForm()
        self.fff = FileField(required=True)
        super(MainForm, self).__init__()


#
# class SecondForm(Form):
#
#     def __init__(self):
#         self.ip = IPField(required=True)
#         self.new_ip = IPField(required=True)
#
#         super(SecondForm, self).__init__()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

    def post(self, *args, **kwargs):
        # for i in  dir(self.request):
        #     print i
        # print self.request.arguments
        # print self.request.files
        # print self.request.query
        # name_list = self.request.arguments.keys() + self.request.files.keys()
        # print name_list

        # list_form = ListForm(MainForm)
        # list_form.validate(self)
        #
        # print list_form.valid_status
        # print list_form.value_dict
        # print list_form.error_dict

        # obj = MainForm()
        # obj.validate(self)
        #
        # print "验证结果：", obj.valid_status
        # print "符合验证结果：", obj.value_dict
        # print "错误信息:"
        # for key, item in obj.error_dict.items():
        #     print key,item
        # print self.get_arguments('favor'),type(self.get_arguments('favor'))
        # print self.get_argument('favor'),type(self.get_argument('favor'))
        # print type(self.get_argument('fff')),self.get_argument('fff')
        # print self.request.files
        # obj = MainForm()
        # obj.validate(self)
        # print obj.valid_status
        # print obj.value_dict
        # print obj.error_dict
        # print self.request,type(self.request)
        # obj.fff.save(self.request)
        # from tornado.httputil import HTTPServerRequest
        # name_list = self.request.arguments.keys() + self.request.files.keys()
        # print name_list
        # print self.request.files,type(self.request.files)
        # print len(self.request.files.get('fff'))

        # obj = MainForm()
        # obj.validate(self)
        # print obj.valid_status
        # print obj.value_dict
        # print obj.error_dict
        # obj.fff.save(self.request)
        self.write('ok')


settings = {
    'template_path': 'template',
    'static_path': 'static',
    'static_url_prefix': '/static/',
    'cookie_secret': 'aiuasdhflashjdfoiuashdfiuh',
    'login_url': '/login'
}

application = tornado.web.Application([
    (r"/index", MainHandler),
], **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()