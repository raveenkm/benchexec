
"""
BenchExec is a framework for reliable benchmarking.
This file is part of BenchExec.

Copyright (C) 2007-2015  Dirk Beyer
All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import benchexec.tools.template
import benchexec.result as result
import os
class Tool(benchexec.tools.template.BaseTool):

    REQUIRED_PATHS = ["viap_tool.py","viap_svcomp.py","config.properties","SyntaxFilter.py","graphclass.py","commandclass.py","packages"]

    def executable(self):
        return util.find_executable('viap_tool.py')

    def program_files(self, executable):
        installDir = os.path.join(os.path.dirname(executable), os.path.pardir)
        return util.flatten(util.expand_filename_pattern(path, installDir) for path in self.REQUIRED_PATHS)
    
    def version(self, executable):
        stdout = self._version_from_tool(executable, '-version')
        return stdout
    
    def name(self):
        return 'VerifierIntegerAssignmentPrograms'

    def cmdline(self, executable, options, tasks, propertyfile, rlimits):
        assert len(tasks) == 1
        assert propertyfile is not None
        spec = ['--spec=' + propertyfile]
        return [executable] + options + spec + tasks
    
    def determine_result(self, returncode, returnsignal, output, isTimeout):
        status = result.RESULT_UNKNOWN
        stroutput = str(output)
        if "VIAP_STANDARD_OUTPUT_True" in stroutput:
            status = result.RESULT_TRUE_PROP
        elif "VIAP_STANDARD_OUTPUT_False" in stroutput:
            status = result.RESULT_FALSE_REACH
        return status


