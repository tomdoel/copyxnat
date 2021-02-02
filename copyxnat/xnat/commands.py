# coding=utf-8

"""Commands defining actions that can be performed with copyxnat"""
import abc

from copyxnat.xnat.xnat_interface import XnatExperiment, XnatProject


def commands() -> dict:
    """Return a dictionary containing factories for all commands"""
    return {'export': ExportCommand,
            'show': ShowCommand,
            'copy': CopyCommand,
            'check_datatypes': CheckDatatypesCommand,
            }


class Command:
    """Wraps a command function and its input variables"""
    def __init__(self, function, outputs_function, reset_function, inputs):
        self.function = function
        self.outputs_function = outputs_function
        self.reset_function = reset_function
        self.inputs = inputs


class CommandInputs:
    def __init__(self, dst_xnat, reporter, fix_scan_types, dst_project=None):
        self.dst_project = dst_project
        self.fix_scan_types = fix_scan_types
        self.reporter = reporter
        self.dst_xnat = dst_xnat


def command_factory(command, command_inputs, initial_result=None):
    """Factory for creating a Command wrapper"""

    def run_command(xnat_item, from_parent):
        nonlocal inputs, output_result, output_tostring
        command_return = command_fn(xnat_item=xnat_item,
                                    inputs=inputs,
                                    outputs=output_result,
                                    from_parent=from_parent)
        output_result = command_return.outputs
        if command_return.tostring:
            output_tostring = command_return.tostring
        return command_return

    def reset():
        nonlocal output_result
        output_result = None

    def get_outputs():
        return {'result': output_result, 'tostring': output_tostring}

    def result_tostring(result):
        return "Output from {}: {}".format(command.NAME, result)

    command_fn = command.run
    inputs = {
        'dst_xnat': command_inputs.dst_xnat,
        'dst_project': command_inputs.dst_project,
        'fix_scan_types': command_inputs.fix_scan_types,
        'reporter': command_inputs.reporter
    }
    output_result = initial_result
    output_tostring = result_tostring

    return Command(function=run_command,
                   reset_function=reset,
                   outputs_function=get_outputs,
                   inputs=inputs)


class CommandBase(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def run(xnat_item, inputs, outputs, from_parent):
        """Function that will be run on each item in the XNAT server"""


class CommandReturn:
    """Class for return values for a command function call"""
    def __init__(self, outputs, to_children=None, recurse=True, tostring=None):
        self.outputs = outputs
        self.to_children = to_children
        self.recurse = recurse
        self.tostring = tostring


class ExportCommand(CommandBase):
    NAME = 'Download'
    USE_DST_SERVER = True
    CACHE_TYPE = 'downloads'

    @staticmethod
    def run(xnat_item, inputs, outputs, from_parent):  # pylint: disable=unused-argument
        """Command which exports XNAT project data onto local disk"""
        return_value = xnat_item.export()
        return CommandReturn(outputs=outputs, to_children=return_value)


class ShowCommand(CommandBase):
    NAME = 'Show'
    USE_DST_SERVER = False
    CACHE_TYPE = 'cache'

    @staticmethod
    def run(xnat_item, inputs, outputs, from_parent):  # pylint: disable=unused-argument
        """Command which displays contents of XNAT projects"""
        print(xnat_item.user_visible_info())
        return CommandReturn(outputs=outputs)


class CopyCommand(CommandBase):
    NAME = 'Copy'
    USE_DST_SERVER = True
    CACHE_TYPE = 'cache'

    @staticmethod
    def run(xnat_item, inputs, outputs, from_parent):
        """Command which copies XNAT projects between servers"""

        # Override the project name
        dst_name = inputs['dst_project'] if isinstance(xnat_item, XnatProject) \
            else None

        copied_item = xnat_item.duplicate(
            destination_parent=from_parent,
            fix_scan_types=inputs['fix_scan_types'],
            dst_label=dst_name,
            dry_run=inputs['reporter'].dry_run)
        return CommandReturn(outputs, to_children=copied_item)


class CheckDatatypesCommand(CommandBase):
    NAME = 'Check Datatypes'
    USE_DST_SERVER = True
    CACHE_TYPE = 'cache'

    @staticmethod
    def run(xnat_item, inputs, outputs, from_parent):  # pylint: disable=unused-argument
        """
        Command which checks if destination server has all the
        scan datatypes that are present on the source server
        """

        # On first run, set up the outputs
        if outputs is None:
            outputs = {
                'datatypes_on_dest': inputs['dst_xnat'].datatypes(),
                'missing_session_datatypes': set(),
                'ids_with_empty_datatypes': set(),
                'required_experiment_datatypes': set()
            }

        datatype = xnat_item.interface.datatype()
        if isinstance(xnat_item, XnatExperiment):
            outputs['required_experiment_datatypes'].add(datatype)

            if datatype not in outputs['datatypes_on_dest']:
                outputs['missing_session_datatypes'].add(datatype)
                inputs['reporter'].warning(
                    'Session datatype {} needs to be added to '
                    'destination server. '.format(datatype))

            else:
                inputs['reporter'].verbose_log('OK: session datatype {} is on '
                                     'destination server.'.format(datatype))
        if datatype:
            inputs['reporter'].verbose_log(
                'Known datatype for {} {} {}'.format(xnat_item._name,  # pylint: disable=protected-access
                                                     xnat_item.label,
                                                     xnat_item.full_name))

        else:
            item_id = '{} {} {}'.format(xnat_item._name,  # pylint: disable=protected-access
                                        xnat_item.label,
                                        xnat_item.full_name)

            inputs['reporter'].warning('Empty datatype for {}'.format(item_id))
            outputs['ids_with_empty_datatypes'].add(item_id)

        return CommandReturn(outputs=outputs, tostring=check_datatypes_tostring)


def check_datatypes_tostring(result):
    """Coverts check-datatypes output to human readable form"""
    return str(result)
