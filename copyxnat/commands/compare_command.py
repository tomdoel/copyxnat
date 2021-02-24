# coding=utf-8

"""Command which compares contents of XNAT projects"""
import os

from copyxnat.xnat.commands import Command


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

    def _run(self, xnat_item, from_parent):  # pylint: disable=unused-argument
        # self.outputs += xnat_item.user_visible_info() + os.linesep
        # self.inputs.reporter.output(xnat_item.user_visible_info())
        # self._recurse(xnat_item=xnat_item)

        src_children = {item.label: item for item in
                        xnat_item.get_children(self.ignore_filter)}
        dst_children = {item.label: item for item in
                        from_parent.get_children(self.ignore_filter)}

        both = set(src_children.keys()).intersection(dst_children.keys())
        only_src = set(src_children.keys()).difference(dst_children.keys())
        only_dst = set(dst_children.keys()).difference(src_children.keys())

        for label in only_src:
            text = 'Missing from dst: {}'.format(
                src_children[label].user_visible_info())
            self.outputs += text + os.linesep
            self.inputs.reporter.output(text)
        for label in only_dst:
            text = 'Missing from src: {}'.format(
                dst_children[label].user_visible_info())
            self.outputs += text + os.linesep
            self.inputs.reporter.output(text)
        for label in both:
            text = 'Present in both: {}'.format(
                src_children[label].user_visible_info())
            self.inputs.reporter.debug(text)

        for child_label in both:
            src_child = src_children[child_label]
            dst_child = dst_children[child_label]
            self.run_next(xnat_item=src_child, from_parent=dst_child)

    def print_results(self):
        """Output results to user"""
        print("Differences between projects {}:".format(self.scope))  ## pylint:disable=no-member
        print(self.outputs)
