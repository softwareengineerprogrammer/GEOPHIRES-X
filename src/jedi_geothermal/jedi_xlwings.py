import shutil
import tempfile
import uuid
from pathlib import Path

import xlwings as xw

if __name__ == '__main__':
    working_file = Path(tempfile.gettempdir(), f'{uuid.uuid4()!s}.xlsm').absolute()
    shutil.copyfile('01d-jedi-geothermal-model-rel-gt12-23-16.xlsm', working_file)
    wb = xw.Book(working_file)
    project_data = wb.sheets['ProjectData']
    print(project_data)
    # print(project_data['B16'])
    #
    # results = wb['Summary Results']
    # print(results['B28'].value)
    # print(wb['Calculations']['AG146'].value)
