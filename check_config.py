class Check:
    def config_file(self, parameter_list: dict, config: dict):
        for parameter in parameter_list:
            if parameter not in config:
                raise ValueError(f"{parameter} error: {parameter_list[parameter]}")
        