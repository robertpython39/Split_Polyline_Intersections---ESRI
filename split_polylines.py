# -------------------------------------------------------------------------------
# Name:        Split_Polylines_and_add_new_fields
# Purpose:     intern
#
# Author:      rnicolescu
#
# Created:     01/07/2022
# Copyright:   (c) rnicolescu 2022
# Licence:     <your license here>
# -------------------------------------------------------------------------------
x = """
                                        $$\           
                                        \__|          
 $$$$$$\   $$$$$$\   $$$$$$$\  $$$$$$\  $$\  $$$$$$$\ 
 \____$$\ $$  __$$\ $$  _____|$$  __$$\ $$ |$$  _____|
 $$$$$$$ |$$ |  \__|$$ /      $$ /  $$ |$$ |\$$$$$$\  
$$  __$$ |$$ |      $$ |      $$ |  $$ |$$ | \____$$\ 
\$$$$$$$ |$$ |      \$$$$$$$\ \$$$$$$$ |$$ |$$$$$$$  |
 \_______|\__|       \_______| \____$$ |\__|\_______/ 
                              $$\   $$ |              
                              \$$$$$$  |              
                               \______/               

"""
print x

from arcpy import env
from datetime import datetime
import glob
import arcpy
import os
import shutil


now = datetime.now()
dt_string = now.strftime("%d.%m.%Y %H:%M:%S")
parent = os.getcwd()
temp_folder = os.path.join(parent, "Temp_Output")
final_folder = os.path.join(parent, "Final_Output")

path_in = raw_input("Add path to folder for processing polylines:")
if path_in.endswith("\\"):
    path_in = path_in[0:-1]

def folder_creation():
    with open("log.txt", "a") as logFile:
        logFile.write("\n")
        logFile.write(dt_string + "\tINFO\t==>\tTemp Folder and Final Folder created\n")

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
        print "{} folder created".format(temp_folder)
    if not os.path.exists(final_folder):
        os.makedirs(final_folder)
        print "{} folder created".format(final_folder)

def new_fields():
    with open("log.txt", "a") as logFile:
        env.workspace = path_in
        env.overwriteOutput = True
        logFile.write(dt_string + "\tINFO\t==>\tWorkspace loaded {}\n".format(path_in))
        glob_path = path_in + "\\*.shp"
        for file in glob.glob(glob_path):
            logFile.write("\n")
            fn = os.path.basename(file)
            logFile.write(dt_string + "\tINFO\t==>\tCopying file:  {}\n".format(fn))
            logFile.write("_" * 65)
            logFile.write("\n")
            arcpy.Copy_management(fn, temp_folder + "\\{}".format(fn))
            print "{} copyied succesfully.".format(fn)

        env.workspace = temp_folder
        env.overwriteOutput = True

        for fn in arcpy.ListFeatureClasses():
            logFile.write("\n")
            logFile.write(dt_string + "\tINFO\t==>\tAdding field DATE to  {}\n".format(fn))
            arcpy.AddField_management(fn, "DATE", "TEXT", 80)
            logFile.write(dt_string + "\tINFO\t==>\tAdding field LENGTH to  {}\n".format(fn))
            arcpy.AddField_management(fn, "LENGTH", "SHORT")
            logFile.write(dt_string + "\tINFO\t==>\tAdding field FCODE to  {}\n".format(fn))
            arcpy.AddField_management(fn, "FCODE", "TEXT", 80)
            logFile.write(dt_string + "\tINFO\t==>\tAdding field POLYTYPE to  {}\n".format(fn))
            arcpy.AddField_management(fn, "POLYTYPE", "TEXT", 80)
            logFile.write(dt_string + "\tINFO\t==>\tAdding field PROJECTION to  {}\n".format(fn))
            arcpy.AddField_management(fn, "PROJECTION", "TEXT", 80)
            logFile.write("_" * 65)
            logFile.write("\n")

def delete_old_fields():
    with open("log.txt", "a") as logFile:
        env.workspace = temp_folder
        env.overwriteOutput = True

        fields_to_avoid = ["FID", "Shape", "OBJECTID", "DATE", "LENGTH", "FCODE", "POLYTYPE", "PROJECTION"]
        fc_list = arcpy.ListFeatureClasses()

        for fn in fc_list:
            logFile.write("\n")
            fields = arcpy.ListFields(fn)
            for field in fields:
                if (not field.name in fields_to_avoid):
                    arcpy.DeleteField_management(fn, field.name)
                    logFile.write(dt_string + "\tINFO\t==>\tDeleting field {}\n".format(field.name))
                    print "{} field deleted succesfully".format(field.name)
            logFile.write("_" * 65)
            logFile.write("\n")


def date_field():
    with open("log.txt", "a") as logFile:
        env.workspace = temp_folder
        env.overwriteOutput = True
        logFile.write("\n")
        for file in glob.glob(temp_folder + "\\*.shp"):
            date_string = now.strftime("%d.%m.%Y")
            fn = os.path.basename(file)
            print "Adding current date to {}".format(fn)
            expression = "!Date!.replace(!Date!,'" + str(date_string) + "')"
            arcpy.CalculateField_management(file, 'Date', expression, 'PYTHON_9.3')
            logFile.write(dt_string + "\tINFO\t==>\tCurrent date added to {}\n".format(fn))

        logFile.write("_" * 65)
        logFile.write("\n")

def length():
    with open("log.txt", "a") as logFile:
        env.workspace = temp_folder
        env.overwriteOutput = True

        field_to_process = ("LENGTH")
        expr = '!shape.length@meters!'
        logFile.write("\n")
        for file in glob.glob(temp_folder + "\\*.shp"):
            fn = os.path.basename(file)
            fields = arcpy.ListFields(fn)
            logFile.write(dt_string + "\tINFO\t==>\tTotal length (meters) calculated for shapefile {}\n".format(fn))
            for field in fields:
                arcpy.CalculateField_management(fn, field_to_process, expr, "PYTHON")
        logFile.write("_" * 65)
        logFile.write("\n")

def fcode():
    with open("log.txt", "a") as logFile:
        env.workspace = temp_folder
        env.overwriteOutput = True

        field_to_update = ("FCODE")
        logFile.write("\n")
        logFile.write(dt_string + "\tINFO\t==>\tFCODE name added to the field {}\n".format(field_to_update))
        for file in glob.glob(temp_folder + "\\*.shp"):
            fn = os.path.basename(file)
            print "Adding {} to {} ".format(fn, field_to_update)
            expression = "!FCODE!.replace(!FCODE!,'" + str(fn[0:-4]) + "')"
            arcpy.CalculateField_management(file, 'FCODE', expression, 'PYTHON_9.3')
        logFile.write("_" * 65)
        logFile.write("\n")

def polytype():
    with open("log.txt", "a") as logFile:
        env.workspace = temp_folder
        env.overwriteOutput = True
        logFile.write("\n")
        field_to_write = ("POLYTYPE")

        for file in glob.glob(temp_folder + "\\*.shp"):
            fn = os.path.basename(file)
            print "Adding geometry type to field POLYTYPE in {}".format(fn)
            desc = arcpy.Describe(fn)
            geometryType = desc.shapeType
            fields = arcpy.ListFields(fn)
            logFile.write(dt_string + "\tINFO\t==>\tGeometry type writed to the field {} and shapefile {}\n".format(field_to_write, fn))
            for field in fields:
                with arcpy.da.UpdateCursor(fn, field_to_write) as cursor:
                    for row in cursor:
                        if (geometryType == "Polyline") and (field.name in field_to_write):
                            row[0] = "Polyline"
                            cursor.updateRow(row)
        logFile.write("_" * 65)
        logFile.write("\n")

def projection():
    with open("log.txt", "a") as logFile:
        env.workspace = temp_folder
        env.overwriteOutput = True
        logFile.write("\n")
        field_to_write = ("PROJECTION")
        for file in glob.glob(temp_folder + "\\*.shp"):
            fn = os.path.basename(file)
            desc = arcpy.Describe(fn)
            projection = desc.SpatialReference
            fields = arcpy.ListFields(fn)
            print "Adding {} to field {} in {}".format(projection.Name ,field_to_write, fn)
            logFile.write(dt_string + "\tINFO\t==>\tProjection CS writed to the field {} and shapefile {}\n".format(field_to_write, fn))
            for field in fields:
                with arcpy.da.UpdateCursor(fn, field_to_write) as cursor:
                    for row in cursor:
                        row[0] = str(projection.Name)
                        cursor.updateRow(row)
        logFile.write("_" * 65)
        logFile.write("\n")


def intersection_split():
    with open("log.txt", "a") as logFile:
        env.workspace = temp_folder
        env.overwriteOutput = True
        logFile.write("\n")
        for file in glob.glob(temp_folder + "\\*.shp"):
            fn = os.path.basename(file)
            print "Splitting {}".format(fn)
            arcpy.FeatureToLine_management(fn, temp_folder + "\\temp__{}".format(fn))
            logFile.write(dt_string + "\tINFO\t==>\tSplitting {} at intersection\n".format(fn))
        logFile.write("_" * 65)
        logFile.write("\n")


def output_folder_copy():
    with open("log.txt", "a") as logFile:
        env.workspace = temp_folder
        env.overwriteOutput = True
        logFile.write("\n")
        for file in glob.glob(temp_folder + "\\*.shp"):
            fn = os.path.basename(file)
            print "Copy {} to final folder".format(fn)
            if fn.startswith("temp__"):
                logFile.write(dt_string + "\tINFO\t==>\tShapefile {} copyed to {} and renamed like original shapefile\n".format(fn, final_folder))
                arcpy.Copy_management(fn, final_folder + "\\{}".format(fn[6:]))
        logFile.write("_" * 65)
        logFile.write("\n")

def delete_temps():

    with open("log.txt", "a") as logFile:
        logFile.write("\n")
        logFile.write(dt_string + "\tINFO\t==>\tTemporary folder deleted \n")
        logFile.write("_" * 65)
        logFile.write("\n")
        logFile.write("\n")
        logFile.write(dt_string + "\tINFO\t==>\tScript done! \n")
        shutil.rmtree(temp_folder)
        logFile.write("_" * 65)
        logFile.write("\n")

if __name__ == '__main__':
    globals()

    with open("log.txt", "w") as logFile:
        logFile.write("\n")
        logFile.write(dt_string + "\tINFO\t==>\tScript begin runing\n")
        logFile.write("_" * 65)
        logFile.write("\n")

    folder_creation()
    new_fields()
    date_field()
    delete_old_fields()
    fcode()
    polytype()
    projection()
    intersection_split()
    length()
    output_folder_copy()
    delete_temps()  # va fi chemata ultima functia aceasta
    print "Script done"
    logFile.close()

