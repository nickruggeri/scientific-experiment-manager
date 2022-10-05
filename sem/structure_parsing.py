import logging
import re
from pathlib import Path
from typing import Iterable, List, Tuple


def recursive_folder_parsing(
    root_dir: Path, parsers: List[re.Pattern]
) -> Iterable[Tuple[Path, dict]]:
    """Iteratively go through the subdirectories of root_dir.
    The ones that match the parser tree are returned along with their parsed arguments
    in a flattened way.
    The structure to be parsed is specified via a list of expected patterns, organized
    according to the folder levels. The first pattern specifies the folders to select,
    the second patterns the subfolders, and so on.

    :param root_dir: root directory.
    :param parsers: ordered list of regular expression patterns.
        Every patterns specified the folders that are considered at every level.
    :return: an iterable of (directory, parameters) tuples.
    """
    for subdir in root_dir.glob("*"):
        match = parsers[0].match(subdir.name)
        if match is None:
            logging.info("Recursive parsing: skipped due to not parsing", subdir)
            continue

        if len(parsers) == 1:
            yield subdir, match.groupdict()
        else:
            for subsubdir, matchdict in recursive_folder_parsing(subdir, parsers[1:]):
                yield subsubdir, {**match.groupdict(), **matchdict}
