import csv
from ast import literal_eval
csv_file = "test.csv"

module_name = "test_regmap"
verilog_file = module_name+".vams"


def convertOutputToDecimal(value):
    # Function to convert value in 'Default' column
    if (type(value) == int):
        return value
    if (type(value) == str):
        if ('0x' in value.lower()):
            return literal_eval(value)
        return literal_eval('0x'+value)
    raise Exception('Unable to convert value = {}'.format(value))


def rename(name):
    # rename the Filed Name
    if ('SDSPLLID_') in name:
        return name.replace('SDSPLLID_', '')
    if ('SDSPHYID_') in name:
        return name.replace('SDSPHYID_', '')
    return name


# Open input CSV file and read it into a list of dictionaries
with open(csv_file, "r") as file:
    reader = csv.DictReader(file, delimiter=",")
    rows = [row for row in reader]

# Open output Verilog-A file and write the module header
with open(verilog_file, "w") as file:
    file.write('`include "constants.vams"\n`include "disciplines.vams"\n')
    file.write("module {}(".format(module_name))

    writeModuleName = ''
    writePorts = ''
    writeSignalsBehaviour = ''
    writeSetRegs = ''

    # Iterate over the rows a third time and write the Verilog-A code
    for row in rows:
        if (row["Filed Name"] != '') and (row['Direction'] == 'ID'):
            try:
                output = convertOutputToDecimal(row["Default"])
                portName = rename(row["Filed Name"])
                width = int(row["Width"])
                paramName = "set_{}".format(portName)
                if width == 1:
                    portDirection = "output {};\n".format(portName)
                    portDirection += "electrical {};\n".format(portName)
                    signalBahaviour = "\tV({}) <+ transition( {} ? hi : lo , td, tr, tf);\n".format(portName,
                                                                                                    paramName)
                else:
                    portDirection = "output [{}:0] {};\n".format(
                        width - 1, portName)
                    portDirection += "electrical [{}:0] {};\n".format(
                        width - 1, portName)
                    signalBahaviour = '\tgenerate j({}, 0)\n'.format(width-1)
                    signalBahaviour += '\t\tV({}[j]) <+ transition ( ({} >> j ) & 1 ? hi : lo, td, tr, tf);\n'.format(
                        portName, paramName)
                writeModuleName += '{}, '.format(portName)
                writePorts += portDirection
                writeSetRegs += "parameter integer {} = {};\n".format(
                    paramName, output)
                writeSignalsBehaviour += signalBahaviour
            except:
                print('error at {}, value = {}'.format(
                    row["Filed Name"], row["Default"]))

    writeModuleName = writeModuleName[:-2]

    # start writing verilog-a code
    file.write("{});\n".format(writeModuleName))
    file.write(writePorts)
    file.write(writeSetRegs)
    file.write("\nparameter real td=0 from [0:inf);\n")
    file.write("parameter real tr=10p from [0:inf);\n")
    file.write("parameter real tf=10p from [0:inf);\n")
    file.write("parameter real hi=1.1 from [0:inf);\n")
    file.write("parameter real lo=0 from [0:inf);\n")

    file.write("\nanalog begin\n")
    file.write(writeSignalsBehaviour)

    file.write("end\n")

    file.write("endmodule\n")
