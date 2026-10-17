import openpyxl,sys
wb=openpyxl.load_workbook(sys.argv[1],data_only=True,read_only=True)
maxr=int(sys.argv[2]) if len(sys.argv)>2 else 15
for ws in wb.worksheets:
    print('=== SHEET',ws.title)
    for i,row in enumerate(ws.iter_rows(values_only=True)):
        if i>=maxr: break
        r=[c for c in row if c is not None]
        if r: print(i,r[:25])
