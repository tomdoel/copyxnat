# coding=utf-8

"""Command which compares contents of XNAT projects"""
import os

from copyxnat.pyreporter.pyreporter import ProjectFailure
from copyxnat.xnat.commands import Command
from copyxnat.xnat.xml_cleaner import XmlCleaner


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
        super(CompareCommand, self).__init__(inputs, scope)
        label = self.inputs.dst_project
        self.initial_from_parent = inputs.dst_xnat.project(label)
        if not self.initial_from_parent.exists_on_server():
            message = 'Project {} does not exist on destination server'.format(
                label)
            self.inputs.reporter.error(message)
            raise ProjectFailure(message)

        self.outputs = ''
        self.xml_cleaner = XmlCleaner(app_settings=inputs.app_settings,
                                      reporter=inputs.reporter)
        self.inputs.reporter.debug('Comparing {}'.format(scope))

    def _run(self, xnat_item, from_parent):
        # Add the before and after IDs so they won't be included in differences
        self.xml_cleaner.add_tag_remaps(src_item=xnat_item,
                                        dst_item=from_parent)

        # Recurse to children before checking item itself, so that child ID
        # remappings are added before the parent XML is processed
        self._check_children_and_recurse(src_item=xnat_item,
                                         dst_item=from_parent)

        self._compare(src_item=xnat_item, dst_item=from_parent)
        return True

    def _compare(self, src_item, dst_item):
        if getattr(src_item, "get_xml_string", None) and getattr(
                dst_item, "get_xml", None):
            src_xml = src_item.get_xml_string()
            dst_xml = dst_item.get_xml_string()
            self.xml_cleaner.xml_compare(
                src_string=src_xml, dst_string=dst_xml, src_item=src_item,
                dst_item=dst_item)

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
                src_children[key].full_name_label())
            self._output(text)
        for key in only_dst:
            text = ' - Missing from src: {}'.format(
                dst_children[key].full_name_label())
            self._output(text)
        for key in both:
            text = ' - Present in both: {}'.format(
                src_children[key].full_name_label())
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
        self.inputs.reporter.output("Differences between project structure for "
                                    "{}:".format(self.scope))
        if self.outputs:
            self.inputs.reporter.output(str(self.outputs))
        else:
            self.inputs.reporter.output(' - project structure matches')

    def _output(self, text):
        self.outputs = self.outputs + text + os.linesep
