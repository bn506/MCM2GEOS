#!/usr/share/anaconda/bin/python

# Program summary

# Strip the windows newline ^M

# remove the first blank ignore

# Fix the misplaced ';' (Equations not going to anything)

# Add the DEFFIX variables 

# Import required modules
import os
import glob
import re
import argparse
import subprocess





def main():
#Read in the arguments


######################################################################
# Read in the arguments
######################################################################   

   parser = argparse.ArgumentParser(description='This creates KPP folders from a MCM.kpp file.')
   parser.add_argument('-i', '--input', help='Input .kpp file', required=True)
   parser.add_argument('-o', '--output', help='Output folder name', required=True)
   parser.add_argument('-m', '--manual_kpp', help='Chose Manual kpp generation', required=False)
   args = parser.parse_args()


# If KPP isnt working correctly allow manual kpp runs
   exicute_kpp_manualy = False
   if args.manual_kpp == 'true' :
      exicute_kpp_manualy = True

# Show the arguments
   print ("Input file is '" + args.input + "'")
   print ("Output folder is'" + args.output + "'" )


# Use the arguments
   input_file = args.input
   output_folder = args.output
   if not os.path.exists(output_folder):
      os.makedirs(output_folder)
   gckpp = os.path.join(output_folder, 'gckpp.kpp') 



######################################################################
# Fix kpp
######################################################################

#Fix the .kpp and create a new gckpp.kpp file
   Update_Kpp(input_file,gckpp)


######################################################################
#  Exicute kpp
######################################################################

   Exicute_KPP(output_folder,exicute_kpp_manualy)
   

######################################################################
#  Rename the Files from .f to .F90
######################################################################
 
 
   Rename_Files(output_folder)

   print "Script Complete"

######################################################################
#  END OF MAIN PROGRAM
######################################################################

#
#
#
#
#
#
#



######################################################################
#  Subroutines
######################################################################

def Exicute_KPP(directory,exicute_kpp_manualy):


# Decend into the folder containing gckpp.kpp
   os.chdir(directory)

# Create a option to do manual kpp calls due to buggs with kpp in testing.
   if not exicute_kpp_manualy:
      print "Calling KPP"
# Does a system call for kpp
      try:
         subprocess.check_call(["/home/bn506/Downloads/kpp_2_2_3/kpp-2.2.3/bin/kpp", "gckpp.kpp"]) # Temp kpp
#         subprocess.check_call(["kpp", "gckpp.kpp"]) # Default kpp curently not working - see diff
      except subprocess.CalledProcessError:
         pass # Errors in KPP
      except OSError:
         pass # KPP not found

      print "KPP files generated"
   
   else:
      print 'manual kpp generation chosen. Please run kpp now and press enter when kpp has finished.'
      wait = input("Press Enter when KPP is complete")
      print 'Continueing'

   os.chdir('../')




######################################################################
def Rename_Files(directory):


   print "Changing files from .f90 to .F90"
   
   os.chdir(directory)

# Change the generated filetypes from .f to .F90
   files_to_change = '*.f90'
   old_end='.f90'
   new_end='.F90'


   for filename in glob.glob(files_to_change):
      newfile = filename
      newfile = newfile.replace(old_end, new_end)
      os.rename(filename, newfile)

   os.chdir('../')

   print 'Files renamed'
   return





######################################################################
def Update_Kpp(input_file,gckpp):

   print 'Updating the MCM kpp file to be compatable with GeosChem'

# Open the kpp file to fix
   f1 = open(input_file, 'rb')
   f2 = open(gckpp, 'wb')

# Get the conversion dictionary
   Photol_Conversion = Get_Photol_Dictionary()

   for line in f1:
# Strip the windows newline
      line = line.replace('\r','')


# Add the kpp options

      if line.startswith('{*******'):
         line = ( '#LANGUAGE   FORTRAN90 \n' 
         +        '#HESSIAN    OFF \n'          
         +        '#STOICMAT   OFF \n'
         +        '\n' 
         +        str(line)
         )


# Replace the first blank ignore with O2
      if line.startswith(' ='):
         line = line.replace(' =','O2 =')

# Fix the O + O3 equation
      if 'O + O3 = :' in line:
         line = line.replace('O + O3 = :','O + O3 = O2 :')

# #Fix the OH + HO2 equation
      if 'OH + HO2 = :' in line:
         line = line.replace('OH + HO2 = :','OH + HO2 = H2O + O2 :')

# Add the DEFFIX
      if line.startswith('#INCLUDE atoms'):
         line = (str(line) + '\n' + \
         '\n' + \
         '#DEFFIX' + '\n' +
         'EMISSION        =          IGNORE;' + '\n' +
#      'H2              =          IGNORE;' + '\n' +
         'N2              =          IGNORE;' + '\n' +
#      'O2              =          IGNORE;' + '\n' +
         'H2O             =          IGNORE;' + '\n' +
         'DRYDEP          =          IGNORE;' + '\n' +
         '\n')    


#Search the line and replace any items in the dictionary with its defaniton
      for Key in Photol_Conversion.keys():
         if Key in line:
            line = line.replace(Key, Photol_Conversion[Key])

# Write the updated line   
      f2.write(line)

# Close the files
   f1.close()
   f2.close()
   print 'Update Complete'
   return



######################################################################
def Update_Photol(text, Photol_Conversion):
   for key in Photol_Conversion.items():
      text = text.replace(*key)      
   return text




######################################################################
def Get_Photol_Dictionary():


# Photol conversion Dictionary
# This should be put into a module
# At present some of the J values arent used, and unknown.
# They might need edditing later

   Photol_Conversion = {
      'J(1)'   :  'PHOTOL(3)',
      'J(2)'   :  'PHOTOL(2)',
      'J(3)'   :  'PHOTOL(5)',
      'J(4)'   :  'PHOTOL(4)',
      'J(5)'   :  'PHOTOL(13)',
      'J(6)'   :  'PHOTOL(12)',
      'J(7)'   :  'PHOTOL(10)',
      'J(8)'   :  'PHOTOL(9)',   
      'J(9)'   :  '(1.0)',#############
      'J(10)'   :  '(1.0))',##########
      'J(11)'   :  'PHOTOL(7)',
      'J(12)'   :  'PHOTOL(8)',
      'J(13)'   :  '(PHOTOL(15)+PHOTOL(16))', #Might need devidint by 2
      'J(14)'   :  'PHOTOL(18)',
      'J(15)'   :  'PHOTOL(18)',
      'J(16)'   :  'PHOTOL(18)',
      'J(17)'   :  'PHOTOL(18)',
      'J(18)'   :  '0.5*PHOTOL(28)',   
      'J(19)'   :  '0.5*PHOTOL(28)',
      'J(20)'   :  'PHOTOL(############)',
      'J(21)'   :  '(PHOTOL(15)+PHOTOL(16))',   #Might need deviding by 2
      'J(22)'   :  'PHOTOL(21)',
      'J(23)'   :  '(0.6*PHOTOL(27))',
      'J(24)'   :  '(0.4*PHOTOL(27))',
      'J(25)'   :  '1.0',###
      'J(26)'   :  '1.0',#####
      'J(27)'   :  '1.0',###
      'J(28)'   :  '1.0',   ####
      'J(29)'   :  '1.0',####
      'J(30)'   :  '1.0',####
      'J(31)'   :  'PHOTOL(25)',
      'J(32)'   :  '(0.5*PHOTOL(24))',
      'J(33)'   :  '(0.5*PHOTOL(24))',
      'J(34)'   :  'PHOTOL(26)',
      'J(35)'   :  'PHOTOL(26)',
      'J(36)'   :  '1.0',#####
      'J(37)'   :  '1.0',#####
      'J(38)'   :  '1.0',   ####
      'J(39)'   :  '1.0',#####
      'J(40)'   :  '1.0',######
      'J(41)'   :  'PHOTOL(6)',
      'J(42)'   :  '1.0',####
      'J(43)'   :  '1.0',#
      'J(44)'   :  '1.0',##
      'J(45)'   :  '1.0',###
      'J(46)'   :  '1.0',####
      'J(47)'   :  '1.0',####
      'J(48)'   :  '1.0',##
      'J(49)'   :  '1.0',##
      'J(50)'   :  '1.0',#
      'J(51)'   :  'PHOTOL(22)',
      'J(52)'   :  'PHOTOL(22)',
      'J(53)'   :  'PHOTOL(22',
      'J(54)'   :  'PHOTOL(22)',
      'J(55)'   :  'PHOTOL(22)',
      'J(56)'   :  'PHOTOL(22)',
      'J(57)'   :  'PHOTOL(22)',
      }
   
   return Photol_Conversion


if __name__ == '__main__':
   main()
