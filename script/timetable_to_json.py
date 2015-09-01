#-*- coding: utf-8 -*-
import json
import xlrd

year = raw_input("Year: ")
semester = raw_input("Semester: ")
workbook = xlrd.open_workbook(unicode(str(year)+"년 "+str(semester)+"학기"+".xls",'utf-8'))
sheet = workbook.sheet_by_index(0)
lecturelist = []

for i in range(1, sheet.nrows-1):
	l = {}
	l['lecture_course'] = sheet.cell_value(i,1)
	l['lecture_key'] =  sheet.cell_value(i,3)
	l['lecture_name'] =  sheet.cell_value(i,4)
	l['lecture_prof'] =  sheet.cell_value(i,5)
	if unicode("서울",'utf-8') in sheet.cell_value(i,6):
		c = 0
	elif unicode("일산",'utf-8') in sheet.cell_value(i,6):
		c = 1
	else:
		c = 2
	l['lecture_campus'] = c # 서울 0 / 일산 1 / None 2
	l['lecture_daytime'] = sheet.cell_value(i,7)
	l['lecture_location'] = sheet.cell_value(i,8)
	l['lecture_point'] = sheet.cell_value(i,9)
	l['lecture_type'] = sheet.cell_value(i,16)
	l['lecture_lang'] = sheet.cell_value(i,17)
	l['lecture_etc'] = sheet.cell_value(i,21)
	lecturelist.append(l)

with open(str(year)+'-'+str(semester)+'.json', 'w') as outfile:
	json.dump(lecturelist, outfile)