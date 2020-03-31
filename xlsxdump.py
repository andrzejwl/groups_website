import xlsxwriter

def xlsx_dump(subjectName, groupsDict, oneSheet = True):
    if oneSheet:
        wb = xlsxwriter.Workbook('excel/'+subjectName+'.xlsx')
        bold = wb.add_format({'bold': True})
        sheet = wb.add_worksheet('All Groups')
        row = 1
        col = 0
        for i, group in enumerate(groupsDict):
            sheet.write('A'+str(row), group['day'], bold)
            sheet.write('B'+str(row), group['time'], bold)
            for iter, member in enumerate(group['members']):
                sheet.write(row, col, member['first_name']+ ' ' + member['last_name'])
                sheet.write(row, col +1, member['index_number'])
                row += 1

            row += 2
        wb.close()
    else:
        wb = xlsxwriter.Workbook('excel/'+subjectName+'.xlsx')
        bold = wb.add_format({'bold': True})
        for i, group in enumerate(groupsDict):
            sheet = wb.add_worksheet('group'+str(i+1))
            sheet.write('A1', group['day'], bold)
            sheet.write('B1', group['time'], bold)

            row = 1
            col = 0
            for iter, member in enumerate(group['members']):
                sheet.write(row, col, member['first_name']+ ' ' + member['last_name'])
                sheet.write(row, col +1, member['index_number'])
                wb.close()
                row += 1
