from imports import *

VNR_USAGE = '''VideoNamingRechecker (VNR) accepts the following input:
1. one dir -> do basic checking without reference group
2. two dirs -> match videos inside two dirs and generate a VNR.csv for your review
3. one VNR.csv -> do video comparison as instructed in CSV (will also do 1 for input dirnames with 'vcb')
4. even numbers of files (mkv/mp4/png/flac) -> do video comparison (will also do 1 for input filenames with 'vcb')
'''




def doComparison(*groups:list[Path], grpname:str='0', subgrps_names:list[str]=[], logger:logging.Logger):

    if len(groups) < 2:
        logger.error('At least 2 groups are required.')

    if subgrps_names and (len(subgrps_names) != len(groups) or len(set(subgrps_names)) != len(subgrps_names)):
        logger.warning('The supplied names do not match the number of groups. Falling back to default names.')
        subgrps_names = [str(i) for i in range(len(groups))]
    elif not subgrps_names:
        subgrps_names = [str(i) for i in range(len(groups))]

    for (n1, n2), (g1, g2) in zip(itertools.combinations(subgrps_names, 2), itertools.combinations(groups, 2)):

        l1, l2 = len(g1), len(g2)
        if l1 == 0 or l2 == 0:
            logger.error(f'Cannot compare empty group.')
            continue

        g1 = [FI(f) for f in g1]
        g2 = [FI(f) for f in g2]

        if any(fi.has_video for fi in g1+g2):
            logger.info('Comparing video...')
            cmpVideoContent(g1, g2, logger)

        if any(fi.has_audio for fi in g1+g2):
            logger.info('Comparing audio...')
            diff_audios = cmpAudioContent(g1, g2, logger)
            for k, diff_audio, freq in diff_audios:
                img_path = findCommonParentDir(*[fi.path for fi in g1+g2])
                if not img_path:
                    print('!!! Cannot find a common parent dir of your input. '
                        'The spectrogram of audio difference will be written under the same dir as this script.')
                    img_path = Path(__file__).parent
                img_path = img_path.joinpath(f'VNR-{TIMESTAMP}-DiffAudio-{grpname if grpname else 0}-{n1}vs{n2}-a{k}.log')
                if mkSpectrogram(img_path, diff_audio, freq):
                    logger.info(f'Successfully written spectrogram to "{img_path}".')
                else:
                    logger.error(f'Failed to write spectrogram to "{img_path}".')

        if any(fi.has_menu for fi in g1+g2):
            logger.info('Comparing menu...')
            cmpMenuContent(g1, g2, logger)

        if any(fi.has_image for fi in g1+g2):
            logger.info('Comparing menu...')
            cmpImageContent(g1, g2, logger)

        if any(fi.has_text for fi in g1+g2):
            logger.info('Comparing text...')
            cmpTextContent(g1, g2, logger)

        cmpNaming(g1, g2, logger)




def readCSV4VNR(input_path:Path) -> tuple[bool, dict[str, list[tuple[str, str, str]]]]:

    if not input_path or not (input_path := Path(input_path)).is_file():
        return False, {}

    # vnr_csv_dicts : list[dict[str, str]]
    success, vnr_csv_dicts = readCSV(input_path)
    if not success:
        return False, {}
    vnr_csv_dicts = unquotEntries4CSV(vnr_csv_dicts)

    grouping_dicts : dict[str, list[tuple[str, str, str]]] = {}

    for vnr_csv_dict in vnr_csv_dicts:
        k = vnr_csv_dict[VNR_GRP_IDX_CN]
        if k in grouping_dicts.keys():
            grouping_dicts[k].append(
                (vnr_csv_dict[VNR_SUBGRP_IDX_CN],
                 vnr_csv_dict[ENABLE_CN],
                 vnr_csv_dict[FULLPATH_CN]))
        else:
            grouping_dicts[k] = [
                (vnr_csv_dict[VNR_SUBGRP_IDX_CN],
                 vnr_csv_dict[ENABLE_CN],
                 vnr_csv_dict[FULLPATH_CN])]

    return True, grouping_dicts




def writeCSV4VNR(ouput_path:Path, grouping_dict:dict[str, list[tuple[str, str, str]]]) -> bool:

    if not ouput_path or (output_path := Path(ouput_path)).exists():
        return False

    vnr_csv_dicts : list[dict] = []
    for group_idx, group_list in grouping_dict.items():
        for group in group_list:
            vnr_csv_dict = dict(zip(VNR_CSV_TITLE_DICT.keys(), (group_idx, *group)))
            vnr_csv_dicts.append(vnr_csv_dict)

    return writeCSV(output_path, quotEntries4CSV(vnr_csv_dicts))




def main2doStandardCheck(input_dir:Path):

    logger = initLogger(log_path := input_dir.parent.joinpath(f'VNR-{TIMESTAMP}.log'))
    logger.info(f'Using VideoNamingRechecker (VNR) of AfterCollation {AC_VERSION}')
    logger.info(f'Mode: do standard checking of naming and files for "{input_dir}".')

    subdirs = listDir(input_dir, rglob=False)
    subfiles = listDir(input_dir, rglob=False)

    if not subdirs and not subfiles:
        logger.error(f'Cannot check empty dir "{input_dir}".')
    # NOTE we just assume so, this is not robust however
    elif subdirs and not subdirs:
        chkSeriesNaming(input_dir, logger)
    else:
        chkSeasonNaming(input_dir, logger)

    logger.info('')
    logger.info('NEXT:')
    logger.info(f'View the log "{log_path}".')
    logger.info(f'For any ERROR, you should now start fixing them.')
    logger.info(f'For any WARNING, you should make sure they do not matter.')
    logger.info(f'Some INFO may still contain a notice, do not skip them too fast.')
    logger.info('')




def main2doComparisonFromCSV(input_csv_path:Path):

    logger = initLogger(log_path := input_csv_path.parent.joinpath(f'VNR-{TIMESTAMP}.log'))
    logger.info(f'Using VideoNamingRechecker (VNR) of AfterCollation {AC_VERSION}')
    logger.info(f'Mode: do video comparison as instructed in "{input_csv_path}".')

    succ, groups = readCSV4VNR(input_csv_path)
    if not succ:
        logger.error(f'Failed to read "{input_csv_path}".')
        logging.shutdown()
        return

    for grouping_id, group_items in groups.items():

        if not grouping_id:
            continue

        logger.info(f'------------------------------------------------------------------------------------------------')
        logger.info(f'Checking grouping "{grouping_id}" with the following items:')
        subgrps, enableds, fullpaths = zip(*group_items)
        enableds = toEnabledList(enableds)
        for sub_grp, enabled, fullpath in zip(subgrps, enableds, fullpaths):
            logger.info(f'{sub_grp:s} ({"E" if enabled else "D"}): "{fullpath}"')
        if sum(enableds) < 2:
            logger.warning('Cannot check this group due to <2 items enabled. Skipping.')
            continue
        subgrps = [sub_grp for sub_grp, enabled in zip(subgrps, enableds) if enabled]
        fullpaths = [full_path for full_path, enabled in zip(fullpaths, enableds) if enabled]
        subgrp_tags = list(set(subgrps))
        assert subgrp_tags # this should never happen

        fullpaths = [Path(fullpath) for fullpath in fullpaths]
        all_files_exist = True
        for fullpath in fullpaths:
            if not fullpath.is_file():
                logger.error(f'File "{fullpath}" is missing.')
                all_files_exist = False
        if not all_files_exist:
            logger.error('Some files are missing. Please check again.')
            continue

        # NOTE this is no longer considered as unsupported
        # if len(valid_subgrps) > 2:
        #     logger.error(f'>2 subgroups defined in group "{grouping_id}". It will be converted to 2 subgroups.')
        #     valid_subgrps = valid_subgrps[:2]
        #     subgrps = [(valid_subgrps[-1] if (sub_grp not in valid_subgrps) else sub_grp) for sub_grp in subgrps]
        #     logger.info(f'Converted subgrouping:')
        #     for sub_grp, fullpath in zip(subgrps, fullpaths):
        #         logger.info(f'{sub_grp:s}: "{fullpath}"')

        if len(subgrp_tags) == 1:
            subgrps = ['1', '2']
            if len(fullpaths) > 2:
                logger.warning('>2 items defined in a single subgroup. Plz note auto subgrouping is not accurate.')
                base_parent = fullpaths[0].parent
                for i, fullpath in zip(itertools.count(), fullpaths):
                    subgrps[i] = '1' if fullpath.is_relative_to(base_parent) else '2'
                logger.info(f'Auto subgrouping:')
                for sub_grp, fullpath in zip(subgrps, fullpaths):
                    logger.info(f'{sub_grp:s}: "{fullpath}"')

        src = [fullpath for (sub_grp, fullpath) in zip(subgrps, fullpaths) if sub_grp == subgrp_tags[0]]
        refs = []
        for subgrp_tag in subgrp_tags[1:]:
            refs.append([fullpath for (sub_grp, fullpath) in zip(subgrps, fullpaths) if sub_grp == subgrp_tag])

        doComparison(src, *refs, grpname=grouping_id, subgrps_names=subgrp_tags, logger=logger)




def main2doMatching2CSV(input1_dir:Path, input2_dir:Path):

    log_path = findCommonParentDir(input1_dir, input2_dir)
    if not log_path:
        print('!!! Cannot find a common parent dir of your input. '
              'Output log will be located at the same dir as this script.')
        log_path = Path(__file__).parent.joinpath(f'VNR-{TIMESTAMP}.log')
    elif log_path.is_dir():
        log_path = log_path.joinpath(f'VNR-{TIMESTAMP}.log')
    else:
        log_path = log_path.parent.joinpath(f'VNR-{TIMESTAMP}.log')

    logger = initLogger(log_path)
    logger.info(f'Using VideoNamingRechecker (VNR) of AfterCollation {AC_VERSION}')
    logger.info(f'Mode: try video matching between "{input1_dir}" and "{input2_dir}".')

    assert input1_dir.is_dir() and input2_dir.is_dir()

    input1_fs_all : list[Path] = listFile(input1_dir, ext=VNx_MAIN_EXTS)
    input2_fs_all : list[Path] = listFile(input2_dir, ext=VNx_MAIN_EXTS)
    input1_fs = filterOutCDsScans(input1_fs_all)
    input2_fs = filterOutCDsScans(input2_fs_all)
    if len(input1_fs) != len(input1_fs_all):
        logger.info(f'Removed some FLAC in {STD_CDS_DIRNAME} from the input dir "{input1_dir}".')
    if len(input2_fs) != len(input2_fs_all):
        logger.info(f'Removed some FLAC in {STD_CDS_DIRNAME} from the input dir "{input2_dir}".')

    input1_fis = [FI(f) for f in input1_fs]
    input2_fis = [FI(f) for f in input2_fs]

    groups : dict[str, list[tuple[str, str, str]]] = dict()
    if not input1_fis or not input2_fis:
        logger.warning('No video files found in either of the input dirs.')
        logger.info('VNR will still try to generate a non-ref CSV in case you want to fill it by yourself.')
        if input1_fis and not input2_fis:
            for i, input1_fi in enumerate(input1_fis):
                groups[str(i)] = [('', '', input1_fi.path.resolve().as_posix())]
        elif input2_fis and not input1_fis:
            for i, input2_fi in enumerate(input2_fis):
                groups[str(i)] = [('', '', input2_fi.path.resolve().as_posix())]
        else:
            raise ValueError # NOTE this should be never reached

        csv_parent = findCommonParentDir(input1_dir, input2_dir)
        if not csv_parent: csv_path = input1_dir.parent.joinpath(f'VNR-{TIMESTAMP}.csv')
        else: csv_path = csv_parent.joinpath(f'VNR-{TIMESTAMP}.csv')
        if writeCSV4VNR(csv_path, groups):
            logger.info(f'Successfully written to "{csv_path}"..')
        else:
            logger.error(f'Failed to write to "{csv_path}".')
        logging.shutdown()
        return

    groups : dict[str, list[tuple[str, str, str]]] = dict()
    idx = itertools.count(1)

    # now let's start matching, we do it in this order:
    # 1. match by chapter timestamps, high robust (may fail if main videos rarely use identical chapters)
    # 2. match by audio samples, high robust (may fail in CMs with identical audio)
    # 3. match by duration, mid robust (may fail in any videos having identical duration)

    #***********************************************************************************************
    # step 1: match by chapter timestamps

    for input1_fi in input1_fis[:]: # make a copy of the list, so we can call .remove() in the loop
        # NOTE we only match the first menu track, is this not robust enough?
        matches = [input2_fi for input2_fi in input2_fis if (
                   input1_fi.menu_tracks and input2_fi.menu_tracks
                   and matchMenuTimeStamps(input1_fi.menu_timestamps[0], input2_fi.menu_timestamps[0]))]
        if len(matches) == 1:
            groups[str(next(idx))] = [
                ('1', '', input1_fi.path.resolve().as_posix()),
                ('2', '', matches[0].path.resolve().as_posix())
            ]
            input1_fis.remove(input1_fi)
            input2_fis.remove(matches[0])
            logger.info(f'Matched by chapter timestamp: "{input1_fi.path}" <-> "{matches[0].path}"')
        elif len(matches) > 1:
            logger.warning(f'Cannot match "{input1_fi.path}" as multiple counterparts have the same chapter timestamp.')
        else:
            if input1_fi.menu_tracks:
                logger.warning(f'Cannot match "{input1_fi.path}" as NO counterpart has the same chapter timestamp.')

    #***********************************************************************************************
    # step 2: match by audio digest
    if ENABLE_VNA_AUDIO_SAMPLES:
        for input1_fi in input1_fis[:]: # make a copy of the list, so we can call .remove() in the loop
            matches = [input2_fi for input2_fi in input2_fis \
                       if cmpAudioSamples(input1_fi.audio_samples, input2_fi.audio_samples)]
            if len(matches) == 1:
                groups[str(next(idx))] = [
                    ('1', '', input1_fi.path.resolve().as_posix()),
                    ('2', '', matches[0].path.resolve().as_posix())
                ]
                input1_fis.remove(input1_fi)
                input2_fis.remove(matches[0])
                logger.info(f'Matched by audio digest: "{input1_fi.path}" <-> "{matches[0].path}"')
            elif len(matches) > 1:
                logger.warning(f'Cannot match "{input1_fi.path}" as multiple counterparts have the same audio digest.')
            else:
                if input1_fi.audio_samples:
                    logger.warning(f'Cannot match "{input1_fi.path}" as NO counterpart has the same audio digest.')

    #***********************************************************************************************
    # step 3: match by duration
    for input1_fi in input1_fis[:]: # make a copy of the list, so we can call .remove() in the loop
        matches = [input2_fi for input2_fi in input2_fis if (
                    input1_fi.has_duration and input2_fi.has_duration
                    and matchTime(input1_fi.duration, input2_fi.duration))]
        if len(matches) == 1:
            groups[str(next(idx))] = [
                ('1', '', input1_fi.path.resolve().as_posix()),
                ('2', '', matches[0].path.resolve().as_posix())
            ]
            input1_fis.remove(input1_fi)
            input2_fis.remove(matches[0])
            logger.info(f'Matched by duration: "{input1_fi.path}" <-> "{matches[0].path}"')
        elif len(matches) > 1:
            # TODO this implementation is dirty, fix it
            if all('menu' in fi.path.name.lower() for fi in (input1_fi, *matches)):
                subidx = itertools.count(1)
                group : list[tuple[str, str, str]] = []
                group.append((str(next(subidx)), '', input1_fi.path.resolve().as_posix()))
                for match in matches:
                    group.append((str(next(subidx)), '', match.path.resolve().as_posix()))
                    input2_fis.remove(match)
                input1_fis.remove(input1_fi)
                groups[str(next(idx))] = group
                logger.info(f'Matched by duration for menus: "{input1_fi.path}". (NOTE this is not robust)')
            else:
                logger.warning(f'Cannot match "{input1_fi.path}" as multiple counterparts have the same duration.')
        else:
            logger.warning(f'Cannot match "{input1_fi.path}" as NO counterpart has the same duration.')

    # we need to do this again for input2_fis
    for input2_fi in input2_fis[:]: # make a copy of the list, so we can call .remove() in the loop
        matches = [input1_fi for input1_fi in input1_fis if (
                    input2_fi.has_duration and input1_fi.has_duration
                    and matchTime(input2_fi.duration, input1_fi.duration))]
        if len(matches) == 1:
            groups[str(next(idx))] = [
                ('1', '', input2_fi.path.resolve().as_posix()),
                ('2', '', matches[0].path.resolve().as_posix())
            ]
            input2_fis.remove(input2_fi)
            input1_fis.remove(matches[0])
            logger.info(f'Matched by duration: "{matches[0].path}" <-> "{input2_fi.path}"')
        elif len(matches) > 1:
            # TODO this implementation is dirty, fix it
            if all('menu' in fi.path.name.lower() for fi in (input2_fi, *matches)):
                subidx = itertools.count(1)
                group : list[tuple[str, str, str]] = []
                group.append((str(next(subidx)), '', input2_fi.path.resolve().as_posix()))
                for match in matches:
                    group.append((str(next(subidx)), '', match.path.resolve().as_posix()))
                    input1_fis.remove(match)
                input2_fis.remove(input2_fi)
                groups[str(next(idx))] = group
                logger.info(f'Matched by duration for menus: "{input2_fi.path}". (NOTE this is not robust)')
            else:
                logger.warning(f'Cannot match "{input2_fi.path}" as multiple counterparts have the same duration.')
        else:
            logger.warning(f'Cannot match "{input2_fi.path}" as NO counterpart has the same duration.')

    #***********************************************************************************************
    # slicing is common in videos, so we need to match the rest by filename

    for input1_fi in [input1_fi for input1_fi in input1_fis if input1_fi.menu_tracks]:
        timestamps = input1_fi.menu_timestamps[0]
        if len(timestamps) < 2: continue # this seems an incorrect menu
        distances = [(timestamps[i+1] - timestamps[i]) for i in range(len(timestamps)-1)]
        founds : list[FI] = []
        for i, distance in enumerate(distances):
            for input2_fi in input2_fis:
                if input2_fi in founds: continue
                if matchTime(distance, input2_fi.duration):
                    founds.append(input2_fi)
                    break
        if len(founds) == len(distances):
            matched_group : list[tuple[str, str, str]] = []
            matched_group.append(('1', '', input1_fi.path.resolve().as_posix()))
            for found in founds:
                matched_group.append(('2', '', found.path.resolve().as_posix()))
                input2_fis.remove(found)
            input1_fis.remove(input1_fi)
            groups[str(next(idx))] = matched_group
            logger.info(f'Matched sliced videos: {input1_fi}')

    # we need to do this again for input2_fis
    for input2_fi in [input2_fi for input2_fi in input2_fis if input2_fi.menu_tracks]:
        timestamps = input2_fi.menu_timestamps[0]
        if len(timestamps) < 2: continue # this seems an incorrect menu
        distances = [(timestamps[i+1] - timestamps[i]) for i in range(len(timestamps)-1)]
        founds : list[FI] = []
        for i, distance in enumerate(distances):
            for input1_fi in input1_fis:
                if input1_fi in founds: continue
                if matchTime(distance, input1_fi.duration):
                    founds.append(input1_fi)
                    break
        if len(founds) == len(distances):
            matched_group : list[tuple[str, str, str]] = []
            # NOTE always place input1_fis first
            for found in founds:
                matched_group.append(('1', '', found.path.resolve().as_posix()))
                input1_fis.remove(found)
            input2_fis.remove(input2_fi)
            matched_group.append(('2', '', input2_fi.path.resolve().as_posix()))
            groups[str(next(idx))] = matched_group
            logger.info(f'Matched sliced videos: {input2_fi}')

    #***********************************************************************************************
    # place all the rest into an unnamed group
    unmatched_group : list[tuple[str, str, str]] = []
    for input1_fi in input1_fis:
        unmatched_group.append(('', '', input1_fi.path.resolve().as_posix()))
    for input2_fi in input2_fis:
        unmatched_group.append(('', '', input2_fi.path.resolve().as_posix()))
    if unmatched_group:
        groups[''] = unmatched_group

    #***********************************************************************************************
    # write the result to a CSV

    csv_parent = findCommonParentDir(input1_dir, input2_dir)
    if not csv_parent: csv_path = input1_dir.parent.joinpath(f'VNR-{TIMESTAMP}.csv')
    else: csv_path = csv_parent.joinpath(f'VNR-{TIMESTAMP}.csv')
    if writeCSV4VNR(csv_path, groups):
        logger.info(f'Successfully written to "{csv_path}".')
        logger.info('')
        logger.info('NEXT:')
        logger.info('Please check again the matching result.')
        logger.info('And then drop the CSV to VNR again to start the comparison.')
        logger.info('')
    else:
        logger.error(f'Failed to write to "{csv_path}".')




def main2doDroppedComparison(*paths:Path):

    assert len(paths) % 2 == 0
    group1 = paths[:len(paths)//2]
    group2 = paths[len(paths)//2:]

    log_path = findCommonParentDir(*paths)
    if not log_path:
        print('!!! Cannot find a common parent dir of your input. '
              'Output log will be located at the same dir as this script.')
        log_path = Path(__file__).parent.joinpath(f'VNR-{TIMESTAMP}.log')
    elif log_path.is_dir():
        log_path = log_path.joinpath(f'VNR-{TIMESTAMP}.log')
    else:
        log_path = log_path.parent.joinpath(f'VNR-{TIMESTAMP}.log')

    logger = initLogger(log_path)
    logger.info(f'Using VideoNamingRechecker (VNR) of AfterCollation {AC_VERSION}')
    logger.info(f'Mode: do video comparison from directly dropped files.')

    total = len(group1)
    for i, (path1, path2) in enumerate(zip(group1, group2)):
        logger.info(f'------------------------------------------------------------------------------------------------')
        logger.info(f'Checking grouping "{i+1:03d}/{total:03d}" with the following items:')
        logger.info(f'a: "{path1}"')
        logger.info(f'b: "{path2}"')
        doComparison([path1], [path2], logger=logger)




def _cli(*paths:Path):

    n = len(paths)
    if (n == 1) and (path := paths[0]).is_dir():
        main2doStandardCheck(paths[0])
    elif (n == 1) and (path := paths[0]).is_file() \
    and re.match(VNR_TABLE_FILENAME_PATTERN, path.name):
        main2doComparisonFromCSV(paths[0])
    elif n == 2 and paths[0].is_dir() and paths[1].is_dir():
        main2doMatching2CSV(paths[0], paths[1])
    elif (not n % 2) and all(p.is_file() and p.suffix.endswith(VNx_MAIN_EXTS) for p in paths):
        main2doDroppedComparison(*paths)
    else:
        printCliNotice(VNR_USAGE, paths)




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