_TweakOutputModules = [
    "fileName",
    "logicalFileName",
    "compressionLevel",
    "basketSize",
    "splitLevel",
    "overrideInputFileSplitLevels",
    "maxSize",
    "fastCloning",
    "sortBaskets",
    "dropMetaData",
    "SelectEvents.SelectEvents",
    "dataset.dataTier",
    "dataset.filterName",
]

_TweakParams = [
    # options
    "process.options.fileMode",
    "process.options.wantSummary",
    "process.options.allowUnscheduled",
    "process.options.makeTriggerResults",
    "process.options.Rethrow",
    "process.options.SkipEvent",
    "process.options.FailPath",
    "process.options.FailModule",
    "process.options.IgnoreCompletely",

    # config metadata
    "process.configurationMetadata.name",
    "process.configurationMetadata.version",
    "process.configurationMetadata.annotation",

    # source
    "process.source.maxEvents",
    "process.source.skipEvents",
    "process.source.firstEvent",
    "process.source.firstRun",
    "process.source.firstLuminosityBlock",
    "process.source.numberEventsInRun",
    "process.source.fileNames",
    "process.source.secondaryFileNames",
    "process.source.fileMatchMode",
    "process.source.overrideCatalog",
    "process.source.numberEventsInLuminosityBlock",
    "process.source.firstTime",
    "process.source.timeBetweenEvents",
    "process.source.eventCreationDelay",
    "process.source.needSecondaryFileNames",
    "process.source.parametersMustMatch",
    "process.source.branchesMustMatch",
    "process.source.setRunNumber",
    "process.source.skipBadFiles",
    "process.source.eventsToSkip",
    "process.source.lumisToSkip",
    "process.source.eventsToProcess",
    "process.source.lumisToProcess",
    "process.source.noEventSort",
    "process.source.duplicateCheckMode",
    "process.source.inputCommands",
    "process.source.dropDescendantsOfDroppedBranches",

    # maxevents
    "process.maxEvents.input",
    "process.maxEvents.output",

    # random seeds
    "process.RandomNumberGeneratorService.*.initialSeed",
    "process.GlobalTag.globaltag",

]


class TweakMakerLite():
    def __init__(self, process_params=None, output_modules_params=None):
        self.process_level = process_params or _TweakParams
        self.output_modules_level = output_modules_params or _TweakOutputModules

    def make(self, process, add_parameters_list=False):
        expanded_params = {}
        # Process parameters
        for param in self.process_level:
            self.expand_parameter(process, param, expanded_params, '')

        # Output modules
        for output_module_name in process.outputModules_():
            output_module = getattr(process, output_module_name)
            for param in self.output_modules_level:
                full_path = 'process.%s.%s' % (output_module_name, param)
                if self.has_parameter(output_module, param):
                    expanded_params[full_path] = self.get_parameter(process, full_path)   

        # Print all expanded parameters before expand dict
        # for k in sorted(expanded_params):
        #     print('%s %s' % (k, expanded_params[k]))

        expanded_dict = self.expand_dict(expanded_params, add_parameters_list)
        return expanded_dict

    def expand_dict(self, dictionary, add_parameters_list=False):
        result = {}
        for key, value in dictionary.items():
            key = key.split('.')
            current_level = result
            while len(key) > 1:
                key_part = key.pop(0)
                if key_part not in current_level:
                    current_level[key_part] = {}

                current_level = current_level[key_part]

            if add_parameters_list:
                if 'parameters_' not in current_level:
                    current_level['parameters_'] = []

                current_level['parameters_'].append(key[0])

            current_level[key[0]] = value

        return result


    def has_parameter(self, process, path):
        if isinstance(path, str):
            path = path.split('.')
            if path[0] == 'process':
                path.pop(0)

        if not path:
            return True

        if hasattr(process, path[0]):
            return self.has_parameter(getattr(process, path[0]), path[1:])

        return False

    def get_parameter(self, process, path):
        if isinstance(path, str):
            path = path.split('.')
            if path[0] == 'process':
                path.pop(0)

        if not path:
            return process.value()

        return self.get_parameter(getattr(process, path[0]), path[1:])

    def expand_parameter(self, process, path, results, full_path=''):
        if isinstance(path, str):
            path = path.split('.')
            if path[0] == 'process':
                full_path += path.pop(0)

        if not path:
            results[full_path] = process.value()
            return

        parameter = path[0]
        if parameter == '*':
            next_params = list(process.parameters_())
        else:
            next_params = [parameter]

        for next_param in next_params:
            if hasattr(process, next_param):
                next_path = ('%s.%s' % (full_path, next_param)).strip('.')
                self.expand_parameter(getattr(process, next_param),
                                      path[1:],
                                      results,
                                      next_path)

