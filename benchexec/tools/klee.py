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
import benchexec.result as result
import benchexec.util as util
import benchexec.tools.template
import benchexec.model
import os

class Tool(benchexec.tools.template.BaseTool):
    """
    Tool info for KLEE (https://klee.github.io).
    """
    REQUIRED_PATHS = [
        "bin",
        "include",
        "klee_build",
        "libraries"
    ]

    def executable(self):
        return util.find_executable('bin/klee')


    def program_files(self, executable):
        return self._program_files_from_executable(
            executable, self.REQUIRED_PATHS, parent_dir=True)

    def version(self, executable):
        """
        The output looks like this:
        KLEE 0.2.0 (https://klee.github.io)
          Built May 22 2015 (12:47:34)
          Build mode: Release
          Build revision: 6118403fa4315388946babd25be38a9524a5e2c5

        LLVM (http://llvm.org/):
          LLVM version 3.4.2

          Optimized build.
          Built Oct 15 2014 (13:57:47).
          Default target: x86_64-pc-linux-gnu
          Host CPU: bdver1
        """
        stdout = self._version_from_tool(executable)
        line = next(l for l in stdout.splitlines() if l.startswith('KLEE'))
        line = line.replace('KLEE' , '')
        line = line.split('(')[0]
        return line.strip()

    def cmdline(self, executable, options, tasks, propertyfile=None, rlimits={}):
        if benchexec.model.MEMLIMIT in rlimits:
            options += ["--max-memory="+str(rlimits[benchexec.model.MEMLIMIT])]
        if benchexec.model.TIMELIMIT in rlimits:
            options += ["--max-time="+str(rlimits[benchexec.model.TIMELIMIT])]
        if benchexec.model.WALLTIMELIMIT in rlimits:
            options += ["--max-walltime="+str(rlimits[benchexec.model.WALLTIMELIMIT])]
        if benchexec.model.SOFTTIMELIMIT in rlimits:
            options += ["--max-cputime-soft="+str(rlimits[benchexec.model.SOFTTIMELIMIT])]
        if benchexec.model.HARDTIMELIMIT in rlimits:
            options += ["--max-cputime-hard="+str(rlimits[benchexec.model.HARDTIMELIMIT])]

        return [executable] + options + tasks

    def name(self):
        return 'KLEE'


    def determine_result(self, returncode, returnsignal, output, isTimeout):
        """
        Parse the output of the tool and extract the verification result.
        This method always needs to be overridden.
        If the tool gave a result, this method needs to return one of the
        benchexec.result.RESULT_* strings.
        Otherwise an arbitrary string can be returned that will be shown to the user
        and should give some indication of the failure reason
        (e.g., "CRASH", "OUT_OF_MEMORY", etc.).
        """
        for line in output:
            if line.startswith('KLEE: ERROR: '):
                if line.find('ASSERTION FAIL:')!=-1:
                    return result.RESULT_FALSE_REACH
                elif line.find('memory error: out of bound pointer')!=-1:
                    return result.RESULT_FALSE_DEREF
                elif line.find('overflow')!=-1:
                    return result.RESULT_FALSE_OVERFLOW
                else:
                    return "ERROR ({0})".format(returncode)
            if line.startswith('KLEE: done'):
                return result.RESULT_DONE
        return result.RESULT_UNKNOWN


    def get_value_from_output(self, lines, identifier):
        # search for the text in output and get its value,
        # stop after the first line, that contains the searched text
        for line in lines:
            if line.startswith('KLEE: done: ') and line.find(identifier+' = ')!=-1:
                startPosition = line.rfind('=') + 2
                return line[startPosition:].strip()
        return None
