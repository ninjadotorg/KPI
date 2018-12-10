import sys
from subprocess import Popen, PIPE
import re


def convert_to(folder, source, timeout=None):
    args = [libreoffice_exec(), '--headless', '--convert-to', 'pdf', '--outdir', folder, source]
    p = Popen(args, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()
    filename = re.search('-> (.*?) using filter', output)

    if filename is None:
        raise LibreOfficeError(output)
    else:
        return filename.group(1)


def libreoffice_exec():
    # TODO: Provide support for more platforms
    if sys.platform == 'darwin':
        return '/Applications/LibreOffice.app/Contents/MacOS/soffice'
    return 'libreoffice'


class LibreOfficeError(Exception):
    def __init__(self, output):
        self.output = output


if __name__ == '__main__':
    print('Converted to ' + convert_to(sys.argv[1], sys.argv[2]))