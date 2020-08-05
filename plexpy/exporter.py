# -*- coding: utf-8 -*-

# This file is part of Tautulli.
#
#  Tautulli is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Tautulli is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Tautulli.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
from future.builtins import str
from backports import csv

import json
import os
import threading

from functools import partial, reduce
from io import open
from multiprocessing.dummy import Pool as ThreadPool

import plexpy
if plexpy.PYTHON2:
    import database
    import datatables
    import helpers
    import logger
    from plex import Plex
else:
    from plexpy import database
    from plexpy import datatables
    from plexpy import helpers
    from plexpy import logger
    from plexpy.plex import Plex


MOVIE_ATTRS = {
    'addedAt': helpers.datetime_to_iso,
    'art': None,
    'audienceRating': None,
    'audienceRatingImage': None,
    'chapters': {
        'id': None,
        'tag': None,
        'index': None,
        'start': None,
        'end': None,
        'thumb': None
    },
    'chapterSource': None,
    'collections': {
        'id': None,
        'tag': None
    },
    'contentRating': None,
    'countries': {
        'id': None,
        'tag': None
    },
    'directors': {
        'id': None,
        'tag': None
    },
    'duration': None,
    'durationHuman': lambda i:  helpers.human_duration(getattr(i, 'duration', 0), sig='dhm'),
    'fields': {
        'name': None,
        'locked': None
    },
    'genres': {
        'id': None,
        'tag': None
    },
    'guid': None,
    'key': None,
    'labels': {
        'id': None,
        'tag': None
    },
    'lastViewedAt': helpers.datetime_to_iso,
    'librarySectionID': None,
    'librarySectionKey': None,
    'librarySectionTitle': None,
    'locations': None,
    'media': {
        'aspectRatio': None,
        'audioChannels': None,
        'audioCodec': None,
        'audioProfile': None,
        'bitrate': None,
        'container': None,
        'duration': None,
        'height': None,
        'id': None,
        'has64bitOffsets': None,
        'optimizedForStreaming': None,
        'optimizedVersion': None,
        'target': None,
        'title': None,
        'videoCodec': None,
        'videoFrameRate': None,
        'videoProfile': None,
        'videoResolution': None,
        'width': None,
        'parts': {
            'accessible': None,
            'audioProfile': None,
            'container': None,
            'deepAnalysisVersion': None,
            'duration': None,
            'exists': None,
            'file': None,
            'has64bitOffsets': None,
            'id': None,
            'indexes': None,
            'key': None,
            'size': None,
            'sizeHuman': lambda i: helpers.human_file_size(getattr(i, 'size', 0)),
            'optimizedForStreaming': None,
            'requiredBandwidths': lambda e: [int(b) for b in e.split(',')] if e else None,
            'syncItemId': None,
            'syncState': None,
            'videoProfile': None,
            'videoStreams': {
                'codec': None,
                'codecID': None,
                'default': None,
                'displayTitle': None,
                'extendedDisplayTitle': None,
                'id': None,
                'index': None,
                'language': None,
                'languageCode': None,
                'selected': None,
                'streamType': None,
                'title': None,
                'type': None,
                'bitDepth': None,
                'bitrate': None,
                'cabac': None,
                'chromaLocation': None,
                'chromaSubsampling': None,
                'colorPrimaries': None,
                'colorRange': None,
                'colorSpace': None,
                'colorTrc': None,
                'duration': None,
                'frameRate': None,
                'frameRateMode': None,
                'hasScalingMatrix': None,
                'hdr': lambda i: helpers.is_hdr(getattr(i, 'bitDepth', 0), getattr(i, 'colorSpace', '')),
                'height': None,
                'level': None,
                'pixelAspectRatio': None,
                'pixelFormat': None,
                'profile': None,
                'refFrames': None,
                'requiredBandwidths': lambda e: [int(b) for b in e.split(',')] if e else None,
                'scanType': None,
                'streamIdentifier': None,
                'width': None
            },
            'audioStreams': {
                'codec': None,
                'codecID': None,
                'default': None,
                'displayTitle': None,
                'extendedDisplayTitle': None,
                'id': None,
                'index': None,
                'language': None,
                'languageCode': None,
                'selected': None,
                'streamType': None,
                'title': None,
                'type': None,
                'audioChannelLayout': None,
                'bitDepth': None,
                'bitrate': None,
                'bitrateMode': None,
                'channels': None,
                'dialogNorm': None,
                'duration': None,
                'profile': None,
                'requiredBandwidths': lambda e: [int(b) for b in e.split(',')] if e else None,
                'samplingRate': None
            },
            'subtitleStreams': {
                'codec': None,
                'codecID': None,
                'default': None,
                'displayTitle': None,
                'extendedDisplayTitle': None,
                'id': None,
                'index': None,
                'language': None,
                'languageCode': None,
                'requiredBandwidths': lambda e: [int(b) for b in e.split(',')] if e else None,
                'selected': None,
                'streamType': None,
                'title': None,
                'type': None,
                'forced': None,
                'format': None,
                'headerCompression': None,
                'key': None
            }
        }
    },
    'originallyAvailableAt': partial(helpers.datetime_to_iso, to_date=True),
    'originalTitle': None,
    'producers': {
        'id': None,
        'tag': None
    },
    'rating': None,
    'ratingImage': None,
    'ratingKey': None,
    'roles': {
        'id': None,
        'tag': None,
        'role': None,
        'thumb': None
    },
    'studio': None,
    'summary': None,
    'tagline': None,
    'thumb': None,
    'title': None,
    'titleSort': None,
    'type': None,
    'updatedAt': helpers.datetime_to_iso,
    'userRating': None,
    'viewCount': None,
    'writers': {
        'id': None,
        'tag': None
    },
    'year': None
}

SHOW_ATTRS = {
    'addedAt': helpers.datetime_to_iso,
    'art': None,
    'banner': None,
    'childCount': None,
    'collections': {
        'id': None,
        'tag': None
    },
    'contentRating': None,
    'duration': None,
    'durationHuman': lambda i:  helpers.human_duration(getattr(i, 'duration', 0), sig='dhm'),
    'fields': {
        'name': None,
        'locked': None
    },
    'genres': {
        'id': None,
        'tag': None
    },
    'guid': None,
    'index': None,
    'key': None,
    'labels': {
        'id': None,
        'tag': None
    },
    'lastViewedAt': helpers.datetime_to_iso,
    'leafCount': None,
    'librarySectionID': None,
    'librarySectionKey': None,
    'librarySectionTitle': None,
    'locations': None,
    'originallyAvailableAt': partial(helpers.datetime_to_iso, to_date=True),
    'rating': None,
    'ratingKey': None,
    'roles': {
        'id': None,
        'tag': None,
        'role': None,
        'thumb': None
    },
    'studio': None,
    'summary': None,
    'theme': None,
    'thumb': None,
    'title': None,
    'titleSort': None,
    'type': None,
    'updatedAt': helpers.datetime_to_iso,
    'userRating': None,
    'viewCount': None,
    'viewedLeafCount': None,
    'year': None,
    'seasons': lambda e: helpers.get_attrs_to_dict(e, MEDIA_TYPES[e.type][0])
}

SEASON_ATTRS = {
    'addedAt': helpers.datetime_to_iso,
    'art': None,
    'fields': {
        'name': None,
        'locked': None
    },
    'guid': None,
    'index': None,
    'key': None,
    'lastViewedAt': helpers.datetime_to_iso,
    'leafCount': None,
    'librarySectionID': None,
    'librarySectionKey': None,
    'librarySectionTitle': None,
    'parentGuid': None,
    'parentIndex': None,
    'parentKey': None,
    'parentRatingKey': None,
    'parentTheme': None,
    'parentThumb': None,
    'parentTitle': None,
    'ratingKey': None,
    'summary': None,
    'thumb': None,
    'title': None,
    'titleSort': None,
    'type': None,
    'updatedAt': helpers.datetime_to_iso,
    'userRating': None,
    'viewCount': None,
    'viewedLeafCount': None,
    'episodes': lambda e: helpers.get_attrs_to_dict(e, MEDIA_TYPES[e.type][0])
}

EPISODE_ATTRS = {
    'addedAt': helpers.datetime_to_iso,
    'art': None,
    'chapterSource': None,
    'contentRating': None,
    'directors': {
        'id': None,
        'tag': None
    },
    'duration': None,
    'durationHuman': lambda i:  helpers.human_duration(getattr(i, 'duration', 0), sig='dhm'),
    'fields': {
        'name': None,
        'locked': None
    },
    'grandparentArt': None,
    'grandparentGuid': None,
    'grandparentKey': None,
    'grandparentRatingKey': None,
    'grandparentTheme': None,
    'grandparentThumb': None,
    'grandparentTitle': None,
    'guid': None,
    'index': None,
    'key': None,
    'lastViewedAt': helpers.datetime_to_iso,
    'librarySectionID': None,
    'librarySectionKey': None,
    'librarySectionTitle': None,
    'locations': None,
    'media': {
        'aspectRatio': None,
        'audioChannels': None,
        'audioCodec': None,
        'audioProfile': None,
        'bitrate': None,
        'container': None,
        'duration': None,
        'height': None,
        'id': None,
        'has64bitOffsets': None,
        'optimizedForStreaming': None,
        'optimizedVersion': None,
        'target': None,
        'title': None,
        'videoCodec': None,
        'videoFrameRate': None,
        'videoProfile': None,
        'videoResolution': None,
        'width': None,
        'parts': {
            'accessible': None,
            'audioProfile': None,
            'container': None,
            'deepAnalysisVersion': None,
            'duration': None,
            'exists': None,
            'file': None,
            'has64bitOffsets': None,
            'id': None,
            'indexes': None,
            'key': None,
            'size': None,
            'sizeHuman': lambda i: helpers.human_file_size(getattr(i, 'size', 0)),
            'optimizedForStreaming': None,
            'requiredBandwidths': lambda e: [int(b) for b in e.split(',')] if e else None,
            'syncItemId': None,
            'syncState': None,
            'videoProfile': None,
            'videoStreams': {
                'codec': None,
                'codecID': None,
                'default': None,
                'displayTitle': None,
                'extendedDisplayTitle': None,
                'id': None,
                'index': None,
                'language': None,
                'languageCode': None,
                'selected': None,
                'streamType': None,
                'title': None,
                'type': None,
                'bitDepth': None,
                'bitrate': None,
                'cabac': None,
                'chromaLocation': None,
                'chromaSubsampling': None,
                'colorPrimaries': None,
                'colorRange': None,
                'colorSpace': None,
                'colorTrc': None,
                'duration': None,
                'frameRate': None,
                'frameRateMode': None,
                'hasScalingMatrix': None,
                'hdr': lambda i: helpers.is_hdr(getattr(i, 'bitDepth', 0), getattr(i, 'colorSpace', '')),
                'height': None,
                'level': None,
                'pixelAspectRatio': None,
                'pixelFormat': None,
                'profile': None,
                'refFrames': None,
                'requiredBandwidths': lambda e: [int(b) for b in e.split(',')] if e else None,
                'scanType': None,
                'streamIdentifier': None,
                'width': None
            },
            'audioStreams': {
                'codec': None,
                'codecID': None,
                'default': None,
                'displayTitle': None,
                'extendedDisplayTitle': None,
                'id': None,
                'index': None,
                'language': None,
                'languageCode': None,
                'selected': None,
                'streamType': None,
                'title': None,
                'type': None,
                'audioChannelLayout': None,
                'bitDepth': None,
                'bitrate': None,
                'bitrateMode': None,
                'channels': None,
                'dialogNorm': None,
                'duration': None,
                'profile': None,
                'requiredBandwidths': lambda e: [int(b) for b in e.split(',')] if e else None,
                'samplingRate': None
            },
            'subtitleStreams': {
                'codec': None,
                'codecID': None,
                'default': None,
                'displayTitle': None,
                'extendedDisplayTitle': None,
                'id': None,
                'index': None,
                'language': None,
                'languageCode': None,
                'requiredBandwidths': lambda e: [int(b) for b in e.split(',')] if e else None,
                'selected': None,
                'streamType': None,
                'title': None,
                'type': None,
                'forced': None,
                'format': None,
                'headerCompression': None,
                'key': None
            }
        }
    },
    'originallyAvailableAt': partial(helpers.datetime_to_iso, to_date=True),
    'parentGuid': None,
    'parentIndex': None,
    'parentKey': None,
    'parentRatingKey': None,
    'parentThumb': None,
    'parentTitle': None,
    'rating': None,
    'ratingKey': None,
    'summary': None,
    'thumb': None,
    'title': None,
    'titleSort': None,
    'type': None,
    'updatedAt': helpers.datetime_to_iso,
    'userRating': None,
    'viewCount': None,
    'writers': {
        'id': None,
        'tag': None
    },
    'year': None
}

ARTIST_ATTRS = {
    'addedAt': helpers.datetime_to_iso,
    'art': None,
    'collections': {
        'id': None,
        'tag': None
    },
    'countries': {
        'id': None,
        'tag': None
    },
    'fields': {
        'name': None,
        'locked': None
    },
    'genres': {
        'id': None,
        'tag': None
    },
    'guid': None,
    'index': None,
    'key': None,
    'lastViewedAt': helpers.datetime_to_iso,
    'librarySectionID': None,
    'librarySectionKey': None,
    'librarySectionTitle': None,
    'locations': None,
    'moods':  {
        'id': None,
        'tag': None
    },
    'rating': None,
    'ratingKey': None,
    'styles':  {
        'id': None,
        'tag': None
    },
    'summary': None,
    'thumb': None,
    'title': None,
    'titleSort': None,
    'type': None,
    'updatedAt': helpers.datetime_to_iso,
    'userRating': None,
    'viewCount': None,
    'albums': lambda e: helpers.get_attrs_to_dict(e, MEDIA_TYPES[e.type][0])
}

ALBUM_ATTRS = {
    'addedAt': helpers.datetime_to_iso,
    'art': None,
    'collections': {
        'id': None,
        'tag': None
    },
    'fields': {
        'name': None,
        'locked': None
    },
    'genres': {
        'id': None,
        'tag': None
    },
    'guid': None,
    'index': None,
    'key': None,
    'labels': {
        'id': None,
        'tag': None
    },
    'lastViewedAt': helpers.datetime_to_iso,
    'leafCount': None,
    'librarySectionID': None,
    'librarySectionKey': None,
    'librarySectionTitle': None,
    'loudnessAnalysisVersion': None,
    'moods':  {
        'id': None,
        'tag': None
    },
    'originallyAvailableAt': partial(helpers.datetime_to_iso, to_date=True),
    'parentGuid': None,
    'parentKey': None,
    'parentRatingKey': None,
    'parentThumb': None,
    'parentTitle': None,
    'rating': None,
    'ratingKey': None,
    'styles':  {
        'id': None,
        'tag': None
    },
    'summary': None,
    'thumb': None,
    'title': None,
    'titleSort': None,
    'type': None,
    'updatedAt': helpers.datetime_to_iso,
    'userRating': None,
    'viewCount': None,
    'viewedLeafCount': None,
    'tracks': lambda e: helpers.get_attrs_to_dict(e, MEDIA_TYPES[e.type][0])
}

TRACK_ATTRS = {
    'addedAt': helpers.datetime_to_iso,
    'art': None,
    'duration': None,
    'durationHuman': lambda i:  helpers.human_duration(getattr(i, 'duration', 0), sig='dhm'),
    'grandparentArt': None,
    'grandparentGuid': None,
    'grandparentKey': None,
    'grandparentRatingKey': None,
    'grandparentThumb': None,
    'grandparentTitle': None,
    'guid': None,
    'index': None,
    'key': None,
    'lastViewedAt': helpers.datetime_to_iso,
    'librarySectionID': None,
    'librarySectionKey': None,
    'librarySectionTitle': None,
    'media': {
        'audioChannels': None,
        'audioCodec': None,
        'audioProfile': None,
        'bitrate': None,
        'container': None,
        'duration': None,
        'id': None,
        'title': None,
        'parts': {
            'accessible': None,
            'audioProfile': None,
            'container': None,
            'deepAnalysisVersion': None,
            'duration': None,
            'exists': None,
            'file': None,
            'hasThumbnail': None,
            'id': None,
            'key': None,
            'size': None,
            'sizeHuman': lambda i: helpers.human_file_size(getattr(i, 'size', 0)),
            'requiredBandwidths': lambda e: [int(b) for b in e.split(',')] if e else None,
            'syncItemId': None,
            'syncState': None,
            'audioStreams': {
                'codec': None,
                'codecID': None,
                'default': None,
                'displayTitle': None,
                'extendedDisplayTitle': None,
                'id': None,
                'index': None,
                'selected': None,
                'streamType': None,
                'title': None,
                'type': None,
                'albumGain': None,
                'albumPeak': None,
                'albumRange': None,
                'audioChannelLayout': None,
                'bitrate': None,
                'channels': None,
                'duration': None,
                'endRamp': None,
                'gain': None,
                'loudness': None,
                'lra': None,
                'peak': None,
                'requiredBandwidths': lambda e: [int(b) for b in e.split(',')] if e else None,
                'samplingRate': None,
                'startRamp': None,
            },
            'lyricStreams': {
                'codec': None,
                'codecID': None,
                'default': None,
                'displayTitle': None,
                'extendedDisplayTitle': None,
                'id': None,
                'index': None,
                'minLines': None,
                'provider': None,
                'streamType': None,
                'timed': None,
                'title': None,
                'type': None,
                'format': None,
                'key': None
            }
        }
    },
    'moods':  {
        'id': None,
        'tag': None
    },
    'originalTitle': None,
    'parentGuid': None,
    'parentIndex': None,
    'parentKey': None,
    'parentRatingKey': None,
    'parentThumb': None,
    'parentTitle': None,
    'ratingCount': None,
    'ratingKey': None,
    'summary': None,
    'thumb': None,
    'title': None,
    'titleSort': None,
    'type': None,
    'updatedAt': helpers.datetime_to_iso,
    'userRating': None,
    'viewCount': None,
    'year': None,
}

PHOTO_ALBUM_ATTRS = {
    # For some reason photos needs to be first,
    # otherwise the photo album ratingKey gets
    # clobbered by the first photo's ratingKey
    'photos': lambda e: helpers.get_attrs_to_dict(e, MEDIA_TYPES[e.type][0]),
    'addedAt': helpers.datetime_to_iso,
    'art': None,
    'composite': None,
    'guid': None,
    'index': None,
    'key': None,
    'librarySectionID': None,
    'librarySectionKey': None,
    'librarySectionTitle': None,
    'ratingKey': None,
    'summary': None,
    'thumb': None,
    'title': None,
    'type': None,
    'updatedAt': helpers.datetime_to_iso
}

PHOTO_ATTRS = {
    'addedAt': helpers.datetime_to_iso,
    'createdAtAccuracy': None,
    'createdAtTZOffset': None,
    'guid': None,
    'index': None,
    'key': None,
    'librarySectionID': None,
    'librarySectionKey': None,
    'librarySectionTitle': None,
    'originallyAvailableAt': partial(helpers.datetime_to_iso, to_date=True),
    'parentGuid': None,
    'parentIndex': None,
    'parentKey': None,
    'parentRatingKey': None,
    'parentThumb': None,
    'parentTitle': None,
    'ratingKey': None,
    'summary': None,
    'thumb': None,
    'title': None,
    'type': None,
    'updatedAt': helpers.datetime_to_iso,
    'year': None,
    'media': {
        'aperture': None,
        'aspectRatio': None,
        'container': None,
        'height': None,
        'id': None,
        'iso': None,
        'lens': None,
        'make': None,
        'model': None,
        'width': None,
        'parts': {
            'accessible': None,
            'container': None,
            'exists': None,
            'file': None,
            'id': None,
            'key': None,
            'size': None,
            'sizeHuman': lambda i: helpers.human_file_size(getattr(i, 'size', 0)),
        }
    },
    'tag': {
        'id': None,
        'tag': None,
        'title': None
    }
}

COLLECTION_ATTRS = {
    'addedAt': helpers.datetime_to_iso,
    'childCount': None,
    'collectionMode': None,
    'collectionSort': None,
    'contentRating': None,
    'fields': {
        'name': None,
        'locked': None
    },
    'guid': None,
    'index': None,
    'key': None,
    'librarySectionID': None,
    'librarySectionKey': None,
    'librarySectionTitle': None,
    'maxYear': None,
    'minYear': None,
    'ratingKey': None,
    'subtype': None,
    'summary': None,
    'thumb': None,
    'title': None,
    'type': None,
    'updatedAt': helpers.datetime_to_iso,
    'children': lambda e: helpers.get_attrs_to_dict(e, MEDIA_TYPES[e.type][0])
}

PLAYLIST_ATTRS = {
    'addedAt': helpers.datetime_to_iso,
    'composite': None,
    'duration': None,
    'durationHuman': lambda i:  helpers.human_duration(getattr(i, 'duration', 0), sig='dhm'),
    'guid': None,
    'key': None,
    'leafCount': None,
    'playlistType': None,
    'ratingKey': None,
    'smart': None,
    'summary': None,
    'title': None,
    'type': None,
    'updatedAt': helpers.datetime_to_iso,
    'items': lambda e: helpers.get_attrs_to_dict(e, MEDIA_TYPES[e.type][0])
}

MOVIE_LEVELS = {
    1: [
        'ratingKey', 'title', 'titleSort', 'originalTitle', 'originallyAvailableAt', 'year',
        'rating', 'ratingImage', 'audienceRating', 'audienceRatingImage', 'userRating', 'contentRating',
        'studio', 'tagline', 'summary', 'guid', 'duration', 'durationHuman', 'type'
    ],
    2: [
        'directors.tag', 'writers.tag', 'producers.tag', 'roles.tag', 'roles.role',
        'countries.tag', 'genres.tag', 'collections.tag', 'labels.tag', 'fields.name', 'fields.locked'
    ],
    3: [
        'art', 'thumb', 'key', 'chapterSource',
        'chapters.tag', 'chapters.index', 'chapters.start', 'chapters.end', 'chapters.thumb',
        'updatedAt', 'lastViewedAt', 'viewCount'
    ],
    4: [
        'locations', 'media.aspectRatio', 'media.audioChannels', 'media.audioCodec', 'media.audioProfile',
        'media.bitrate', 'media.container', 'media.duration', 'media.height', 'media.width',
        'media.videoCodec', 'media.videoFrameRate', 'media.videoProfile', 'media.videoResolution',
        'media.optimizedVersion'
    ],
    5: [
        'media.parts.accessible', 'media.parts.exists', 'media.parts.file', 'media.parts.duration',
        'media.parts.container', 'media.parts.indexes', 'media.parts.size', 'media.parts.sizeHuman',
        'media.parts.audioProfile', 'media.parts.videoProfile',
        'media.parts.optimizedForStreaming', 'media.parts.deepAnalysisVersion'
    ],
    6: [
        'media.parts.videoStreams.codec', 'media.parts.videoStreams.bitrate',
        'media.parts.videoStreams.language', 'media.parts.videoStreams.languageCode',
        'media.parts.videoStreams.title', 'media.parts.videoStreams.displayTitle',
        'media.parts.videoStreams.extendedDisplayTitle', 'media.parts.videoStreams.hdr',
        'media.parts.videoStreams.bitDepth', 'media.parts.videoStreams.colorSpace',
        'media.parts.videoStreams.frameRate', 'media.parts.videoStreams.level',
        'media.parts.videoStreams.profile', 'media.parts.videoStreams.refFrames',
        'media.parts.videoStreams.scanType', 'media.parts.videoStreams.default',
        'media.parts.videoStreams.height', 'media.parts.videoStreams.width',
        'media.parts.audioStreams.codec', 'media.parts.audioStreams.bitrate',
        'media.parts.audioStreams.language', 'media.parts.audioStreams.languageCode',
        'media.parts.audioStreams.title', 'media.parts.audioStreams.displayTitle',
        'media.parts.audioStreams.extendedDisplayTitle', 'media.parts.audioStreams.bitDepth',
        'media.parts.audioStreams.channels', 'media.parts.audioStreams.audioChannelLayout',
        'media.parts.audioStreams.profile', 'media.parts.audioStreams.samplingRate',
        'media.parts.audioStreams.default',
        'media.parts.subtitleStreams.codec', 'media.parts.subtitleStreams.format',
        'media.parts.subtitleStreams.language', 'media.parts.subtitleStreams.languageCode',
        'media.parts.subtitleStreams.title', 'media.parts.subtitleStreams.displayTitle',
        'media.parts.subtitleStreams.extendedDisplayTitle', 'media.parts.subtitleStreams.forced',
        'media.parts.subtitleStreams.default'
    ]
}

SHOW_LEVELS = {}

SEASON_LEVELS = {}

EPISODE_LEVELS = {}

ARTIST_LEVELS = {}

ALBUM_LEVELS = {}

TRACK_LEVELS = {}

PHOTO_ALBUM_LEVELS = {}

PHOTO_LEVELS = {}

COLLECTION_LEVELS = {}

PLAYLIST_LEVELS = {}

MEDIA_TYPES = {
    'movie': (MOVIE_ATTRS, MOVIE_LEVELS),
    'show': (SHOW_ATTRS, SHOW_LEVELS),
    'season': (SEASON_ATTRS, SEASON_LEVELS),
    'episode': (EPISODE_ATTRS, EPISODE_LEVELS),
    'artist': (ARTIST_ATTRS, ARTIST_LEVELS),
    'album': (ALBUM_ATTRS, ALBUM_LEVELS),
    'track': (TRACK_ATTRS, TRACK_LEVELS),
    'photo album': (PHOTO_ALBUM_ATTRS, PHOTO_ALBUM_LEVELS),
    'photo': (PHOTO_ATTRS, PHOTO_LEVELS),
    'collection': (COLLECTION_ATTRS, COLLECTION_LEVELS),
    'playlist': (PLAYLIST_ATTRS, PLAYLIST_LEVELS)
}


def export(section_id=None, rating_key=None, file_format='json', level=1):
    timestamp = helpers.timestamp()

    level = helpers.cast_to_int(level)

    if not section_id and not rating_key:
        logger.error("Tautulli Exporter :: Export called but no section_id or rating_key provided.")
        return
    elif rating_key and not str(rating_key).isdigit():
        logger.error("Tautulli Exporter :: Export called with invalid rating_key '%s'.", rating_key)
        return
    elif section_id and not str(section_id).isdigit():
        logger.error("Tautulli Exporter :: Export called with invalid section_id '%s'.", section_id)
        return
    elif not level:
        logger.error("Tautulli Exporter :: Export called with invalid level '%s'.", level)
        return
    elif file_format not in ('json', 'csv'):
        logger.error("Tautulli Exporter :: Export called but invalid file_format '%s' provided.", file_format)
        return

    plex = Plex(plexpy.CONFIG.PMS_URL, plexpy.CONFIG.PMS_TOKEN)

    if rating_key:
        logger.debug("Tautulli Exporter :: Export called with rating_key %s, level %d", rating_key, level)

        item = plex.get_item(helpers.cast_to_int(rating_key))
        media_type = item.type

        if media_type != 'playlist':
            section_id = item.librarySectionID

        if media_type in ('season', 'episode', 'album', 'track'):
            item_title = item._defaultSyncTitle()
        else:
            item_title = item.title

        if media_type == 'photo' and item.TAG == 'Directory':
            media_type = 'photo album'

        filename = '{} - {} [{}].{}.{}'.format(
            media_type.title(), item_title, rating_key, helpers.timestamp_to_YMDHMS(timestamp), file_format)

        items = [item]

    elif section_id:
        logger.debug("Tautulli Exporter :: Export called with section_id %s, level %d", section_id, level)

        library = plex.get_library(section_id)
        media_type = library.type
        library_title = library.title
        filename = 'Library - {} [{}].{}.{}'.format(
            library_title, section_id, helpers.timestamp_to_YMDHMS(timestamp), file_format)
        items = library.all()

    else:
        return

    if media_type not in MEDIA_TYPES:
        logger.error("Tautulli Exporter :: Cannot export media type '%s'", media_type)
        return

    media_attrs, level_attrs = MEDIA_TYPES[media_type]

    if level == 9:
        export_attrs = media_attrs
    else:
        if level not in level_attrs:
            logger.error("Tautulli Exporter :: Export called with invalid level '%s'.", level)
            return

        export_attrs_set = set()
        _levels = sorted(level_attrs.keys())
        for _level in _levels[:_levels.index(level) + 1]:
            export_attrs_set.update(level_attrs[_level])

        export_attrs_list = []
        for attr in export_attrs_set:
            split_attr = attr.split('.')
            try:
                value = helpers.get_by_path(media_attrs, split_attr)
            except KeyError:
                logger.warn("Tautulli Exporter :: Unknown export attribute '%s', skipping...", attr)
                continue

            for _attr in reversed(split_attr):
                value = {_attr: value}

            export_attrs_list.append(value)

        export_attrs = reduce(helpers.dict_merge, export_attrs_list)

    filename = helpers.clean_filename(filename)

    export_id = add_export(timestamp=timestamp,
                           section_id=section_id,
                           rating_key=rating_key,
                           media_type=media_type,
                           file_format=file_format,
                           filename=filename)
    if not export_id:
        logger.error("Tautulli Exporter :: Failed to export '%s'", filename)
        return

    threading.Thread(target=_real_export,
                     kwargs={'export_id': export_id,
                             'items': items,
                             'attrs': export_attrs,
                             'file_format': file_format,
                             'filename': filename}).start()

    return True


def _real_export(export_id, items, attrs, file_format, filename):
    logger.info("Tautulli Exporter :: Starting export for '%s'...", filename)

    filepath = get_export_filepath(filename)

    part = partial(helpers.get_attrs_to_dict, attrs=attrs)
    pool = ThreadPool(processes=4)
    success = True

    try:
        result = pool.map(part, items)

        if file_format == 'json':
            json_data = json.dumps(result, indent=4, ensure_ascii=False, sort_keys=True)
            with open(filepath, 'w', encoding='utf-8') as outfile:
                outfile.write(json_data)

        elif file_format == 'csv':
            flatten_result = helpers.flatten_dict(result)
            flatten_attrs = set().union(*flatten_result)
            with open(filepath, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, sorted(flatten_attrs))
                writer.writeheader()
                writer.writerows(flatten_result)

        file_size = os.path.getsize(filepath)

    except Exception as e:
        set_export_state(export_id=export_id, success=False)
        logger.error("Tautulli Exporter :: Failed to export '%s': %s", filename, e)
        success = False

    finally:
        pool.close()
        pool.join()

    if not success:
        return

    set_export_state(export_id=export_id, file_size=file_size)
    logger.info("Tautulli Exporter :: Successfully exported to '%s'", filepath)


def get_export(export_id):
    db = database.MonitorDatabase()
    result = db.select_single('SELECT filename, file_format, complete '
                              'FROM exports WHERE id = ?',
                              [export_id])

    if result:
        result['exists'] = check_export_exists(result['filename'])

    return result


def add_export(timestamp, section_id, rating_key, media_type, file_format, filename):
    keys = {'timestamp': timestamp,
            'section_id': section_id,
            'rating_key': rating_key,
            'media_type': media_type}

    values = {'file_format': file_format,
              'filename': filename}

    db = database.MonitorDatabase()
    try:
        db.upsert(table_name='exports', key_dict=keys, value_dict=values)
        return db.last_insert_id()
    except Exception as e:
        logger.error("Tautulli Exporter :: Unable to save export to database: %s", e)
        return False


def set_export_state(export_id, file_size=None, success=True):
    if success:
        complete = 1
    else:
        complete = -1

    keys = {'id': export_id}
    values = {'complete': complete,
              'file_size': file_size}

    db = database.MonitorDatabase()
    db.upsert(table_name='exports', key_dict=keys, value_dict=values)


def delete_export(export_id):
    db = database.MonitorDatabase()
    if str(export_id).isdigit():
        export_data = get_export(export_id=export_id)

        logger.info("Tautulli Exporter :: Deleting export_id %s from the database.", export_id)
        result = db.action('DELETE FROM exports WHERE id = ?', args=[export_id])

        if export_data and export_data['exists']:
            filepath = get_export_filepath(export_data['filename'])
            logger.info("Tautulli Exporter :: Deleting exported file from '%s'.", filepath)
            try:
                os.remove(filepath)
            except OSError as e:
                logger.error("Tautulli Exporter :: Failed to delete exported file '%s': %s", filepath, e)
        return True
    else:
        return False


def delete_all_exports():
    db = database.MonitorDatabase()
    result = db.select('SELECT filename FROM exports')

    logger.info("Tautulli Exporter :: Deleting all exports from the database.")

    deleted_files = True
    for row in result:
        if check_export_exists(row['filename']):
            filepath = get_export_filepath(row['filename'])
            try:
                os.remove(filepath)
            except OSError as e:
                logger.error("Tautulli Exporter :: Failed to delete exported file '%s': %s", filepath, e)
                deleted_files = False
                break

    if deleted_files:
        database.delete_exports()
        return True


def cancel_exports():
    db = database.MonitorDatabase()
    db.action('UPDATE exports SET complete = -1 WHERE complete = 0')


def get_export_datatable(section_id=None, rating_key=None, kwargs=None):
    default_return = {'recordsFiltered': 0,
                      'recordsTotal': 0,
                      'draw': 0,
                      'data': 'null',
                      'error': 'Unable to execute database query.'}

    data_tables = datatables.DataTables()

    custom_where = []
    if section_id:
        custom_where.append(['exports.section_id', section_id])
    if rating_key:
        custom_where.append(['exports.rating_key', rating_key])

    columns = ['exports.id AS export_id',
               'exports.timestamp',
               'exports.section_id',
               'exports.rating_key',
               'exports.media_type',
               'exports.filename',
               'exports.file_format',
               'exports.file_size',
               'exports.complete'
               ]
    try:
        query = data_tables.ssp_query(table_name='exports',
                                      columns=columns,
                                      custom_where=custom_where,
                                      group_by=[],
                                      join_types=[],
                                      join_tables=[],
                                      join_evals=[],
                                      kwargs=kwargs)
    except Exception as e:
        logger.warn("Tautulli Exporter :: Unable to execute database query for get_export_datatable: %s.", e)
        return default_return

    result = query['result']

    rows = []
    for item in result:
        media_type_title = item['media_type'].title()
        exists = helpers.cast_to_int(check_export_exists(item['filename']))

        row = {'export_id': item['export_id'],
               'timestamp': item['timestamp'],
               'section_id': item['section_id'],
               'rating_key': item['rating_key'],
               'media_type': item['media_type'],
               'media_type_title': media_type_title,
               'filename': item['filename'],
               'file_format': item['file_format'],
               'file_size': item['file_size'],
               'complete': item['complete'],
               'exists': exists
               }

        rows.append(row)

    result = {'recordsFiltered': query['filteredCount'],
              'recordsTotal': query['totalCount'],
              'data': rows,
              'draw': query['draw']
              }

    return result


def get_export_filepath(filename):
    return os.path.join(plexpy.CONFIG.EXPORT_DIR, filename)


def check_export_exists(filename):
    return os.path.isfile(get_export_filepath(filename))
