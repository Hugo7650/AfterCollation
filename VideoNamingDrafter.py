from imports import *

VND_USAGE = f'''
VideoNamingDrafter (VND) only accepts the following input:
1. drop/cli a single folder
2. drop/cli a single folder and a single VNA.csv/yaml/json

VND includes the following behaviors:
1. check the file integrity and mediainfo, and then generate a VND.log for your inspection
2. try guessing some naming fields from the input files (also from VNA if supplied)
3. generate a VND.csv which can be used to name the files by VNE
'''




def main(input_dir:Path, vna_file:Path|None=None):

    logger = initLogger(log_path := input_dir.parent.joinpath(f'VND-{TIMESTAMP}.log'))
    logger.info(f'Using VideoNamingDrafter (VND) of AfterCollation {AC_VERSION}')
    logger.info(f'The input dir is "{input_dir}' + (f' and "{vna_file}".' if vna_file else '.'))

    vna_base, vna_configs = loadVNAInfo(vna_file, logger)

    files = listVNxFilePaths(input_dir, logger)
    cfs = toCoreFileObjs(files, logger, mp=getCRC32MultiProc(files, logger))
    cmpCRC32VND(cfs, findCRC32InFilenames(files), logger)
    if ENABLE_FILE_CHECKING_IN_VND: chkSeasonFiles(cfs, logger)

    # NOTE first guess naming and then fill each FI from VNA
    # so the naming instruction in VNA will not be overwritten
    # also, audio samples will not appear in files_naming_dicts to be sent to VNE
    # so we cannot use files_naming_dicts for fillNamingFieldsFromVNA()
    guessNamingFieldsEarly(cfs, logger)
    if vna_base or vna_configs:
        logger.info(f'Matching files to VNA instruction ...')
        fillNamingFieldsFromVNA(cfs, vna_configs, logger)
    files_naming_dicts = pickInfo4NamingDraft(cfs, logger)

    # don't forget to update the default dict from VNA, which is not updated in fillFieldsFromVNA()
    # NOTE leave useful fields as '' to notify the user that they can fill it
    default_naming_dict = dict(zip(files_naming_dicts[0].keys(), itertools.repeat(BASE_LINE_LABEL)))
    for k in VND_BASE_LINE_USER_DICT.keys():
        default_naming_dict[k] = ''
    for k, v in VNA_BASE_LINE_USER_DICT.items():
        default_naming_dict[k] = vna_base.get(v, '')

    logger.info(f'Preparing to generate the naming proposal ...')
    csv_path = input_dir.parent.joinpath(f'VND-{TIMESTAMP}.csv')
    csv_dicts = quotEntries4CSV([default_naming_dict] + files_naming_dicts)
    if not writeCSV(csv_path, csv_dicts):
        logger.error(f'Failed to save the naming proposal to "{csv_path}".')
    else:
        logger.info(f'The naming proposal is saved to "{csv_path}".')

    logging.shutdown()




def _cli(*paths:Path):

    n = len(paths)
    if (n == 1) and (path := paths[0]).is_dir():
        main(path)
    elif n == 2 and paths[0].is_dir() and paths[1].is_file() and re.match(VNA_CONFS_FILENAME_PATTERN, paths[1].name):
        main(paths[0], paths[1])
    elif n == 2 and paths[1].is_dir() and paths[0].is_file() and re.match(VNA_CONFS_FILENAME_PATTERN, paths[0].name):
        main(paths[1], paths[0])
    else:
        printCliNotice(VND_USAGE, paths)




if __name__ == '__main__':

    paths = [Path(p) for p in sys.argv[1:]]
    if DEBUG:
        _cli(*paths)
    else: # if catch the exception as below, vscode doesn't jump to the actual line
        try:
            _cli(*paths)
        except Exception as e:
            print(f'!!! Run into an unexpected error:\n{e}\nPlease report.')

    input('Press ENTER to exit...')
