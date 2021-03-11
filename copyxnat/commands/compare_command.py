# coding=utf-8

"""Command which compares contents of XNAT projects"""
import os

from copyxnat.xnat.commands import Command
from copyxnat.xnat.xml_compare import xml_compare


class CompareCommand(Command):
    """Command which displays contents of XNAT projects"""

    NAME = 'Compare'
    VERB = 'compare'
    COMMAND_LINE = 'compare'
    USE_DST_SERVER = True
    MODIFY_SRC_SERVER = False
    MODIFY_DST_SERVER = False
    CACHE_TYPE = 'cache'
    HELP = 'Compare XNAT projects'

    def __init__(self, inputs, scope):
        super().__init__(inputs, scope)
        label = self.inputs.dst_project
        self.initial_from_parent = inputs.dst_xnat.project(label)
        self.outputs = ''
        self.inputs.reporter.output('Comparing {}'.format(scope))

    def _run(self, xnat_item, from_parent):
        self._compare(src_item=xnat_item, dst_item=from_parent)
        self._check_children_and_recurse(src_item=xnat_item,
                                         dst_item=from_parent)

    def _compare(self, src_item, dst_item):
        if getattr(src_item, "get_xml_string", None) and getattr(
                dst_item, "get_xml", None):
            print('Comparing {} vs {}'.format(src_item.user_visible_info(),
                                              dst_item.user_visible_info()))
            src_xml = src_item.get_xml_string()
            dst_xml = dst_item.get_xml_string()
            xml_compare(src_string=src_xml, dst_string=dst_xml)

    def _check_children_and_recurse(self, src_item, dst_item):
        src_children = {self._key(item): item for item in
                        src_item.get_children(self.ignore_filter)}
        dst_children = {self._key(item): item for item in
                        dst_item.get_children(self.ignore_filter)}

        both = set(src_children.keys()).intersection(dst_children.keys())
        only_src = set(src_children.keys()).difference(dst_children.keys())
        only_dst = set(dst_children.keys()).difference(src_children.keys())

        for key in only_src:
            text = ' - Missing from dst: {}'.format(
                src_children[key].user_visible_info())
            self.outputs += text + os.linesep
            self.inputs.reporter.output(text)
        for key in only_dst:
            text = ' - Missing from src: {}'.format(
                dst_children[key].user_visible_info())
            self.outputs += text + os.linesep
            self.inputs.reporter.output(text)
        for key in both:
            text = ' - Present in both: {}'.format(
                src_children[key].user_visible_info())
            self.inputs.reporter.debug(text)

        for child_label in both:
            src_child = src_children[child_label]
            dst_child = dst_children[child_label]
            self.run_next(xnat_item=src_child, from_parent=dst_child)

    @staticmethod
    def _key(xnat_item):
        return str(xnat_item.xnat_type) + xnat_item.label

    def print_results(self):
        """Output results to user"""
        self.inputs.reporter.output("Differences between projects "
                                    "{}:".format(self.scope))
        if self.outputs:
            self.inputs.reporter.output(str(self.outputs))
        else:
            self.inputs.reporter.output(' - no differences found')
