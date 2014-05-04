#!/usr/bin/env python
# -*- coding: utf-8 -*-


import cgi


class Builder(object):
    """
    XML Builder
    """

    def __init__(self, **kw):
        self.__encoding = 'utf-8'  # 内部默认编码: utf-8

        self.__options = {
            'encoding': 'utf-8',            # XML编码
            'header_declare': True,         # 是否XML头部声明
            'version': '1.0',               # XML版本号
            'root': None,                   # XML根节点
            'cdata': True,                  # 是否使用XML CDATA格式
            'indent': None,                 # XML层次缩进
            'ksort': False,                 # 标签是否排序
            'reverse': False,               # 标签排序时是否反序
            'hasattr': False,               # 是否包含属性
            'attrkey': 'attr',              # 标签属性标识key
            'valuekey': 'value'             # 标签值标识key
        }

        self.__tree = []
        self.set_options(**kw)

    def set_options(self, **kw):
        for k, v in kw.iteritems():
            if k in self.__options:
                self.__options[k] = v

    def get_options(self):
        return self.__options

    def dict2xml(self, data, root=None):
        """
        # convert dict to xml
        # @param   dict data
        # @return  str
        # @todo
        """
        if self.__options['header_declare']:
            self.__tree.append(self.build_xml_header())

        root = self.__options['root']
        if not root:
            if len(data) == 1:
                root, data = data.items()[0]
                if self.__options['hasattr']:
                    data = data.get(self.__options['valuekey']) or ''
            else:
                raise ValueError('miss parameter[root] or the length of the data must be 1.')

        self.build_tree(data, root)
        xml = ''.join(self.__tree).strip()
        if self.__options['encoding'] != self.__encoding:
            xml = xml.decode(self.__options['encoding'])
        return xml

    def build_xml_header(self):
        """
        # xml header
        # @return str
        # @todo
        """
        return '<?xml version="%s" encoding="%s"?>' % (self.__options['version'], self.__options['encoding'])

    def build_tree(self, data, root=None, attrs={}, depth=0):
        """
        # build the tree for xml
        """
        indent = ('\n%s' % (self.__options['indent'] * depth)) if self.__options['indent'] else ''
        if isinstance(data, dict):
            self.__tree.append('%s%s' % (indent, self.tag_start(root, attrs)))
            iter = data.iteritems()
            if self.__options['ksort']:
                iter = sorted(iter, key=lambda x:x[0], reverse=self.__options['reverse'])
            for k, v in iter:
                attrs = {}
                if self.__options['hasattr'] and isinstance(v, dict):
                    attrs = v.get(self.__options['attrkey']) or {}
                    v = v.get(self.__options['valuekey']) or ''
                self.build_tree(v, k, attrs, depth+1)
            self.__tree.append('%s%s' % (indent, self.tag_end(root)))
        elif isinstance(data, (list, tuple)):
            for v in data:
                self.build_tree(v, root, attrs, depth)
        elif isinstance(data, (int, long, float)):
            self.__tree.append(indent)
            data = self.safedata(str(data), self.__options['cdata'])
            self.__tree.append(self.build_tag(root, data, attrs))
        else:
            self.__tree.append(indent)
            data = self.safedata(data or '', self.__options['cdata'])
            self.__tree.append(self.build_tag(root, data, attrs))

    def safedata(self, data, cdata=True):
        """
        # convert to safe data
        # @params str data
        # @params bool cdata
        # @return str
        # @todo
        """
        safe = ('<![CDATA[%s]]>' % data) if cdata else cgi.escape(data)
        return safe

    def build_tag(self, tag, text='', attrs={}):
        """
        # build tag info
        # @param   str tag
        # @param   str text
        # @param   dict attrs
        # @return  str
        # @todo
        """
        return '%s%s%s' % (self.tag_start(tag, attrs), text, self.tag_end(tag))

    def build_attr(self, attrs):
        attrs = sorted(attrs.iteritems(), key=lambda x: x[0])
        return ' '.join(map(lambda x: '%s="%s"' % x, attrs))

    def tag_start(self, tag, attrs={}):
        return '<%s %s>' % (tag, self.build_attr(attrs)) if attrs else '<%s>' % tag

    def tag_end(self, tag):
        return '</%s>' % tag