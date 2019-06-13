

class VMWriter:
    """
    generates a vm file
    """

    def __init__(self, out):
        """
        creates a new output .vm file and prepares it for writing
        :param out: the output file
        """
        self.output = out

    def write_push(self, segment, index):
        """
        writes a vm push command
        :param segment: the memory segment to push from
        :param index: index of the segment
        :return: None
        """
        with open(self.output, 'a') as vm:
            vm.write("push " + segment + " " + str(index) + "\n")

    def write_pop(self, segment, index):
        """
        writes a vm pop command
        :param segment: the memory segment to pop to
        :param index: index of the segment
        :return: None
        """
        with open(self.output, 'a') as vm:
            vm.write("pop " + segment + " " + str(index) + "\n")

    def write_arithmetic(self, command):
        """
        writes a vm arithmetic command
        :param command: the command to write
        :return: None
        """
        with open(self.output, 'a') as vm:
            vm.write(command + "\n")

    def write_label(self, label):
        """
        writes a vm label command
        :param label: the label to write
        :return: None
        """
        with open(self.output, 'a') as vm:
            vm.write("label " + label + "\n")

    def write_goto(self, label):
        """
        writes a vm goto command
        :param label: the label to go to
        :return: None
        """
        with open(self.output, 'a') as vm:
            vm.write("goto " + label + "\n")

    def write_if(self, label):
        """
        writes a vm if-goto command
        :param label: the label to goto
        :return: None
        """
        with open(self.output, 'a') as vm:
            vm.write("if-goto " + label + "\n")

    def write_call(self, name, n_args):
        """
        writes a vm call command
        :param name: name of the function to call
        :param n_args: number of arguments
        :return: None
        """
        with open(self.output, 'a') as vm:
            vm.write("call " + name + " " + str(n_args) + "\n")

    def write_function(self, name, n_locals):
        """
        writes a vm function command
        :param name: name of the function to call
        :param n_locals: number of the function's local variables
        :return: None
        """
        with open(self.output, 'a') as vm:
            vm.write("function " + name + " " + str(n_locals) + "\n")

    def write_return(self):
        """
        writes a vm return command
        :return: None
        """
        with open(self.output, 'a') as vm:
            vm.write("return\n")
