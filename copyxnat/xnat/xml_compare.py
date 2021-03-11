# coding=utf-8

"""Compare XML strings"""
from collections import OrderedDict

import xmltodict as xmltodict
from lxml import etree


def xml_compare(src_string, dst_string):
    src_d = xmltodict.parse(src_string)
    dst_d = xmltodict.parse(dst_string)
    compare_dicts(src_d, dst_d)


def compare_dicts(src, dst):
    both = set(src.keys()).intersection(dst.keys())
    only_src = set(src.keys()).difference(dst.keys())
    only_dst = set(dst.keys()).difference(src.keys())

    for key in only_src:
        src_value = src[key]
        if isinstance(src_value, dict):
            item = 'Element'
        else:
            item = 'Attribute'
        text = ' - {} {} missing from dst: {}:{}'.format(item, key, src_value, '')
        print(text)
    for key in only_dst:
        dst_value = dst[key]
        if isinstance(dst_value, dict):
            item = 'Element'
        else:
            item = 'Attribute'
        text = ' - {} {} added to dst: {}:{}'.format(item, key, '', dst_value)
        print(text)
    for key in both:
        src_value = src[key]
        dst_value = dst[key]
        if isinstance(src_value, dict):
            # print('Comparing elements {}'.format(key))
            compare_dicts(src_value, dst_value)
        elif isinstance(src_value, list):
            next_src = list_to_dict(src_value)
            next_dst = list_to_dict(dst_value)
            compare_dicts(next_src, next_dst)
        else:
            if compare_values(key, src_value, dst_value):
                text = ' - Attribute {} matches: {}:{}'.format(key, src_value, dst_value)
                # print(text)
            else:
                text = ' - Attribute {} differs: {}:{}'.format(key, src_value, dst_value)
                print(text)


def compare_values(key, src_value, dst_value):
    if key == '@xsi:schemaLocation':
        return src_value.replace('web.xnat.local', 'web2.xnat.local') == dst_value
    return src_value == dst_value


def list_to_dict(list_to_convert):
    dict_out = {}
    for item in list_to_convert:
        if isinstance(item, OrderedDict):
            if '@label' in item:
                dict_out[item['@label']] = item
            elif '@ID' in item:
                dict_out[item['@ID']] = item
            else:
                raise RuntimeError
        else:
            raise RuntimeError
    return dict_out
