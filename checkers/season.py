import logging
import itertools
from pathlib import Path

from helpers.season import Season
from helpers.corefile import CF
from helpers.naming import cmpCoreFileNaming
from configs.runtime import *
from .naming import *
from .tracks import *

import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm




__all__ = [
    'chkSeason',
    'chkSeasonFiles',
    'chkSeasonNaming',
    'chkSeasonPerNamingField',
    'chkSeasonNaming',
    'chkNamingDependency',
    'chkFinalNamingConflict',
    # 'chkCorrelatedNaming',
    # 'chkGlobalNaming'
    ]

# INFO = namedtuple('NAMING_INFO',
#                   field_names='crc ' # the crc32 of the file
#                               'src ' # the path to the SouRCe file
#                               'dst ' # the path to the DEStination
#                               'g '   # the Groupname used for this file
#                               's '   # the Showname used for this file
#                               'l '   # the Location of the file relative to season root
#                               't '   # the Tynename of the video content
#                               'i1 '  # the main indexing info
#                               'i2 '  # the sub indexing info
#                               'n '   # the Note
#                               'c '   # the Customized name, but later to be re-used as the final Content name
#                               'x '   # the suffiX to be prepend right before the file extension
#                               'e',   # the file Extension
#                   defaults=[''] * 7 + [None] * 2 + [''] * 4)





# def chkNaming(default_info:dict, naming_infos:list[dict], logger:logging.Logger) \
#     -> tuple[bool, INFO, list[INFO]]:
#     '''Check the naming plan given by user and further format it for later actual naming.'''

#     logger.info('Checking the base naming config (@default) .....................................')
#     default : INFO = procDefaultNaming(default_info, logger)
#     if (not default.g) or (not default.s):
#         return False, default, []
#     logger.info(f'@default = "{default.g}|{default.s}|{default.x}"')

#     logger.info('Checking the naming config of each file ........................................')
#     infos : list[INFO] = chkNamingInfos(naming_infos, default, logger)

#     logger.info('Performing auto indexing .......................................................')
#     infos = fillAutoIndex(default, infos, logger)

# # assert bool(cname) != any((tname, idx1, idx2, note)), 'doNaming() enforces' # TODO move this to after auto indexing

#     logger.info('Assembling the final content name ..............................................')
#     fmtContentName(infos, logger)

#     logger.info('Checking correlated naming restriction .........................................')
#     infos = chkCorrelatedNaming(infos, logger)

#     logger.info('Checking global naming restriction .............................................')
#     chkGlobalNaming(default, infos, logger)

#     logger.info('Checking final naming conflict .................................................')
#     if not chkFinalNaming(infos, logger):
#         logger.error('VNE stopped because of naming conflict.')
#         return False, default, []

#     logger.info(f'Final Naming ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓')
#     ret_infos = []
#     for naming_info in naming_infos:
#         for info in infos:
#             if naming_info[CRC32_VAR] == info.crc:
#                 ret_infos.append(info)
#                 break
#         else:
#             raise ValueError('The number of naming infos must match.')
#     for i, naming_info in zip(ret_infos, naming_infos):
#         g = naming_info[GRPTAG_VAR]
#         s = naming_info[SHOWNAME_VAR]
#         l = naming_info[LOCATION_VAR]
#         t = naming_info[TYPENAME_VAR]
#         i1 = naming_info[IDX1_VAR]
#         i2 = naming_info[IDX2_VAR]
#         n = naming_info[NOTE_VAR]
#         c = naming_info[CUSTOM_VAR]
#         x = naming_info[SUFFIX_VAR]
#         logger.info(f'"{i.crc}" : "{g}|{s}|{l}|{t}|{i1}|{i2}|{n}|{c}|{x}" → "{i.g}|{i.s}|{i.l}|{i.c}|{i.x}"')
#     logger.info(f'↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑')

#     return True, default, ret_infos

def chkSeasonFiles(cfs:list[CF]|set[CF], logger:logging.Logger):

    with logging_redirect_tqdm([logger]):
        pbar = tqdm.tqdm(total=len(cfs), desc='Checking', unit='file', unit_scale=False, ascii=True, dynamic_ncols=True)
        for cf in cfs:
            if cf.ext in VNx_ALL_EXTS:
                chkFile(cf, logger=logger)
            else:
                logger.error(f'"{cf.ext}" is not a valid extension to check.')
            pbar.update(1)
        pbar.close()


# def chkCorrelatedNaming(infos: list[INFO], logger:logging.Logger) -> list[INFO]:

#     for i, info in enumerate(infos):
#         # logger.info('Checking for "{}"...'.format(info.src))

#         # counterpart check
#         if info.e.endswith('mka'):
#             counterpart = False
#             for j, info2 in enumerate(infos):
#                 # mka counterpart requires [:9] all
#                 if (i != j) and (info2.e == 'mkv') and all(cmpNamingInfo(info, info2)[:9]):
#                     counterpart = True
#                     break
#             if not counterpart:
#                 logger.warning(f'Found dangling MKA having no counterpart MKV ("{info.crc}").')

#         if info.e == 'ass':
#             counterpart = False
#             for j, info2 in enumerate(infos):
#                 # ass counterpart requires [:8] at custom (ex. suffix)
#                 if (i != j) and (info2.e == 'mkv') and all(cmpNamingInfo(info, info2)[:8]):
#                     counterpart = True
#                     break
#             if not counterpart:
#                 logger.warning('Found dangling ASS having no counterpart MKV.')

#         if info.e == 'flac':
#             counterpart = False
#             for j, info2 in enumerate(infos):
#                 # flac counterpart only requires [:4] at typename
#                 # because we can have one [Menu].flac but multi [Menu01~4].png
#                 if (i != j) and (info2.e == 'png') and all(cmpNamingInfo(info, info2)[:4]):
#                     counterpart = True
#                     break
#             if not counterpart:
#                 logger.warning('Found dangling FLAC having no counterpart PNG.')

#     # TODO: stopped the user if an invalid refernce is found
#     # TODO: warn that naming reference refers to another reference

#     return infos




# def chkGlobalNaming(default:INFO, infos:list[INFO], logger:logging.Logger):

#     num_vid = len([info for info in infos if ((info.g == '') and (info.e in VNx_VID_EXTS))])
#     num_ass = len([info for info in infos if ((info.g == '') and (info.e in VNx_SUB_EXTS))])
#     num_arc = len([info for info in infos if ((info.g == '') and (info.e in VNx_ARC_EXTS))])
#     num_mka = len([info for info in infos if ((info.g == '') and (info.e in VNx_EXT_AUD_EXTS))])

#     # if mka presents, the amount of mkv/mka at root should match
#     if num_mka and (num_mka != num_vid):
#         logger.warning(f'The amount of MKA seems incorrect at root (got {num_mka} but {num_vid} videos).')

#     # if coop with subsgrp with ass
#     if default.g.endswith('VCB-Studio') and default.g != 'VCB-Studio' and default.x == '':
#         if num_ass % num_vid != 0:
#             logger.warning(f'The amount of ASS subs seems incorrect (got {num_ass} but {num_vid} videos).')
#         if num_arc != 1:
#             logger.warning(f'The amount of font pack seems incorrect (expect 1 got {num_arc}).')

#     # if we have a base language suffix, check if all video have the same language tag
#     # if default.x in COMMON_SUBS_LANG_TAGS:
#     #     for info in infos:
#     #         if info.src.lower().endswith(VID_EXT) and info.x != default.x:
#     #             logger.warning(f'Base language suffix is "{default.x}" but this is "{info.x}" ("{info.src}").')
#     #         elif info.x != default.x: # also, other files should have no language tag
#     #             logger.warning(f'The file should have no language suffix ("{info.src}").')

#     # TODO check each ass/mka all have a counterpart mkv/mp4



def chkNamingDependency(season: Season, logger:logging.Logger, hook:bool=True) -> bool:

    ok = True
    dep_cfs = list(cf for cf in season.cfs if cf.e in VNx_DEP_EXTS)
    idp_cfs = list(cf for cf in season.cfs if cf.e not in VNx_DEP_EXTS)

    for i, dep_cf in enumerate(dep_cfs):
        if dep_cf.depends: continue
        counterparts = [cf for cf in idp_cfs if all(cmpCoreFileNaming(cf, dep_cf)[:8])] # match any except suffix
        if counterparts:
            if hook:
                dep_cf.depends = counterparts[0]
                logger.info(f'The file with CRC32 0x{dep_cf.crc} now depends CRC32 0x{counterparts[0].crc} for naming.')
            if counterparts[1:]:
                logger.warning(f'Found more than 1 counterpart videos for file with CRC32 0x{dep_cf.crc} '
                               f'to copy the naming from. You config may be incorrect.')
        else:
            logger.error(f'Found NO counterpart video for "{dep_cf.crc}" to copy the quality/track label.')
            ok = False

    return ok






def chkFinalNamingConflict(season: Season, logger:logging.Logger) -> bool:

    ok = True
    names = []
    crc32s = []
    for cf in season.cfs:
        i_name = f'{cf.e}//{cf.g}//{cf.t}//{cf.l}//{cf.f}//{cf.x}'
        names.append(i_name)
        crc32s.append(cf.crc32)
    # we need to show every conflict to the user, so cant use a faster method like set()
    for i, i_name, i_crc32 in zip(itertools.count(), names, crc32s):
        for j, j_name, j_crc32 in zip(itertools.count(), names[i+1:], crc32s[i+1:]):
            if i_name == j_name:
                ok = False
                logger.error(f'Found naming conflict between files with CRC32 0x{i_crc32} vs 0x{j_crc32} '
                             f'(possibly at CSV line {i+2} and {i+j+2}).')

    return ok




def chkSeasonPerNamingField(season:Season, logger:logging.Logger) -> bool:

    ok = True

    ok = ok if chkGrpTag(season.g, logger) else False
    ok = ok if chkTitle(season.t, logger) else False
    ok = ok if chkSuffix(season.x, logger) else False

    for cf in season.cfs:
        ok = ok if chkGrpTag(cf.g, logger) else False
        ok = ok if chkTitle(cf.t, logger) else False
        ok = ok if chkLocation(cf.l, logger) else False
        ok = ok if chkTypeName(cf.c, logger) else False
        ok = ok if chkIndex(cf.i1, cf.i2, logger) else False
        ok = ok if chkNote(cf.n, logger) else False
        ok = ok if chkCustom(cf.f, logger) else False
        ok = ok if chkSuffix(cf.x, logger) else False

    return ok




def chkSeasonNaming(season:Season, logger:logging.Logger) -> bool:

    if not chkSeasonPerNamingField(season, logger): return False
    if not chkFinalNaming(season, logger): return False
    if not chkCorrelatedNaming(season, logger): return False
    if not chkGlobalNaming(season, logger): return False
    return True

    logger.error('Naming draft is invalid.')



    logger.info('Checking the base naming config (@default) .....................................')
    default : INFO = procDefaultNaming(default_info, logger)
    if (not default.g) or (not default.s):
        return False, default, []
    logger.info(f'@default = "{default.g}|{default.s}|{default.x}"')

    logger.info('Checking the naming config of each file ........................................')
    infos : list[INFO] = chkNamingInfos(naming_infos, default, logger)

    logger.info('Performing auto indexing .......................................................')
    infos = fillAutoIndex(default, infos, logger)

    # assert bool(cname) != any((tname, idx1, idx2, note)), 'doNaming() enforces' # TODO move this to after auto indexing

    logger.info('Assembling the final content name ..............................................')
    fmtContentName(infos, logger)

    logger.info('Checking correlated naming restriction .........................................')
    infos = chkCorrelatedNaming(infos, logger)

    logger.info('Checking global naming restriction .............................................')
    chkGlobalNaming(default, infos, logger)

    logger.info('Checking final naming conflict .................................................')
    if not chkFinalNaming(infos, logger):
        logger.error('VNE stopped because of naming conflict.')
        return False, default, []

    logger.info(f'Final Naming ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓')
    ret_infos = []
    for naming_info in naming_infos:
        for info in infos:
            if naming_info[CRC32_VAR] == info.crc:
                ret_infos.append(info)
                break
        else:
            raise ValueError('The number of naming infos must match.')
    for i, naming_info in zip(ret_infos, naming_infos):
        g = naming_info[GRPTAG_VAR]
        s = naming_info[TITLE_VAR]
        l = naming_info[LOCATION_VAR]
        t = naming_info[CLASSIFY_VAR]
        i1 = naming_info[IDX1_VAR]
        i2 = naming_info[IDX2_VAR]
        n = naming_info[NOTE_VAR]
        c = naming_info[CUSTOM_VAR]
        x = naming_info[SUFFIX_VAR]
        logger.info(f'"{i.crc}" : "{g}|{s}|{l}|{t}|{i1}|{i2}|{n}|{c}|{x}" → "{i.g}|{i.s}|{i.l}|{i.c}|{i.x}"')
    logger.info(f'↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑')

    return True, default, ret_infos




def chkSeason(season:Season, logger:logging.Logger) -> bool:
    if not chkSeasonNaming(season, logger): return False
    if not chkSeasonFiles(season, logger): return False
    return True
