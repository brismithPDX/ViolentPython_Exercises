import zipfile
import optparse
from threading import Thread


def print_verbose(message, verbose):
    if verbose is True:
        print(message)
    else:
        pass


def extract_file(in_file, password, verbose):

    # Attempt to open the zip file with required password
    try:
        print_verbose('Testing Password: ' + password, verbose)

        in_file.extractall(pwd=password)

        print('\n###\nFound Password: ' + password + '\n###')

    # Handle BadPassword Error and Runtime Errors
    except RuntimeError as e:
        pass

    # Handle BadZipFile Error
    except zipfile.BadZipFile as e:
        print('Bad Zip file')

        print_verbose('ERROR: Bad Zip File, Complete Error Message is: \n' + str(e), verbose)

    # Handle Large Zip File Decompression Error requiring ZIP64 extensions
    except zipfile.LargeZipFile:
        print('###\nERROR: Zipfile Requires x64 (ZIP64) functionality - Could Not Open File')
        print('Password is likely : ' + password + '\n###')
        exit(-1)

    # Handle unexpected errors
    except Exception as e:
        print_verbose('ERROR: Unknown Error in extract_file(), Complete Error Message is: \n'
                      + str(e), verbose)
        print('ERROR: Unknown Error in extract_file() - Execution will continue')


def main():
    # Setup and read in available arguments and assign them to the argument dictionary for use late
    parser = optparse.OptionParser("program usage" + " -f <zipfile> -d <dictionary> -v <verbose>")

    # Create and configure available program options
    parser.add_option('-f', '--file', dest='zip_name', type='string', help='specify zip file')
    parser.add_option('-d', '--dict', dest='dict_name', type='string', help='specify dictionary file')
    parser.add_option('-v', '--verbose', dest='verbose', help='Enables verbose output', default=False,
                      action="store_true")

    (options, args) = parser.parse_args()

    # Print help & Usage information to the command line if user failed to provide required arguments
    if(options.zip_name is None) | (options.dict_name is None):
        print(parser.usage)
        exit(0)

    else:
        print('###\nStarting Dict Attack on file... \n###')

        zip_name = options.zip_name
        dict_name = options.dict_name

        zip_file = zipfile.ZipFile(zip_name)
        pass_file = open(dict_name)

        for line in pass_file.readlines():
            password = line.strip('\n')
            t = Thread(target=extract_file, args=(zip_file, password, options.verbose))
            t.start()


# Start Program Execution
if __name__ == '__main__':
    main()
