#!/usr/bin/env python3

# vim: filetype=python tabstop=2 expandtab

# itv
# Copyright (C) 2015 Jashandeep Sohi <jashandeep.s.sohi@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
Download ITV Player (www.itv.com/itvplayer) programmes.
"""

__version__ = "0.2.0"

import argparse
from lxml import etree
import requests
import re
from os import path
import subprocess

if __name__ == "__main__":
  arg_parser = argparse.ArgumentParser(
    description = __doc__,
  )
  arg_parser.add_argument(
    "url",
    help = "Video URL.",
    action = "store",
  )
  arg_parser.add_argument(
    "filename",
    help = """
      Output filename. By default, a name is constructed using information about
      the program (i.e. title, episode name, bitrate, etc.)
    """,
    action = "store",
    nargs = "?",
  )
  arg_parser.add_argument(
    "-d", "--dir",
    help = "Download directory (default: '%(default)s').",
    action = "store",
    default = "."
  )
  arg_parser.add_argument(
    "-s", "--start",
    help = "Start at given time (default: '%(default)s').",
    action = "store",
    default = 0,
    type = int,
  )
  arg_parser.add_argument(
    "-e", "--end",
    help = "End at given time (default: '%(default)s').",
    action = "store",
    default = -1,
    type = int,
  )
  arg_parser.add_argument(
    "-p", "--proxy",
    help = """
      Proxy address (e.g. 'http://x.x.x.x:xx', 'socks://x.x.x.x:xx') for making
      HTTP requests to the metadata. The actual video stream is not proxied.
    """,
    action = "store",
    default = ""
  )
  resume_group = arg_parser.add_mutually_exclusive_group()
  resume_group.add_argument(
    "-r", "--resume",
    help = "Attempt to resume (set by default).",
    action = "store_true",
    default = True
  )
  resume_group.add_argument(
    "-R", "--no-resume",
    help = """
      Do not attempt to resume. This will overwrite the old file, if any.
    """,
    action = "store_false",
    dest = "resume"
  )
  args = arg_parser.parse_args()
    
  session = requests.Session()
  session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:32.0) Gecko/20100101 "
                  "Firefox/32.0",
  })
  
  page_req = session.get(args.url)
  pid_match = re.search('"productionId":"(.*?)"', page_req.text)
  
  try:
    pid = pid_match.group(1).replace("\\", "")
  except:
    arg_parser.error("could not parse video pid from page")
  
  soap_msg = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/" xmlns:itv="http://schemas.datacontract.org/2004/07/Itv.BB.Mercury.Common.Types" xmlns:com="http://schemas.itv.com/2009/05/Common">
    <soapenv:Header/>
    <soapenv:Body>
    <tem:GetPlaylist>
    <tem:request>
    <itv:ProductionId>{pid}</itv:ProductionId>
    <itv:RequestGuid>FFFFFFFF-FFFF-FFFF-FFFF-FFFFFFFFFFFF</itv:RequestGuid>
    <itv:Vodcrid>
    <com:Id/>
    <com:Partition>itv.com</com:Partition>
    </itv:Vodcrid>
    </tem:request>
    <tem:userInfo>
    <itv:Broadcaster>Itv</itv:Broadcaster>
    <itv:GeoLocationToken>
    <itv:Token/>
    </itv:GeoLocationToken>
    <itv:RevenueScienceValue>ITVPLAYER.12.18.4</itv:RevenueScienceValue>
    <itv:SessionId/>
    <itv:SsoToken/>
    <itv:UserToken/>
    </tem:userInfo>
    <tem:siteInfo>
    <itv:AdvertisingRestriction>None</itv:AdvertisingRestriction>
    <itv:AdvertisingSite>ITV</itv:AdvertisingSite>
    <itv:AdvertisingType>Any</itv:AdvertisingType>
    <itv:Area>ITVPLAYER.VIDEO</itv:Area>
    <itv:Category/>
    <itv:Platform>DotCom</itv:Platform>
    <itv:Site>ItvCom</itv:Site>
    </tem:siteInfo>
    <tem:deviceInfo>
    <itv:ScreenSize>Big</itv:ScreenSize>
    </tem:deviceInfo>
    <tem:playerInfo>
    <itv:Version>2</itv:Version>
    </tem:playerInfo>
    </tem:GetPlaylist>
    </soapenv:Body>
    </soapenv:Envelope>
  """.format(pid = pid)
  
  media_req = session.post(
    "http://mercury.itv.com/PlaylistService.svc",
    headers = {
      "Referer": "http://www.itv.com/mercury/Mercury_VideoPlayer.swf"
                 "?v=1.6.479/[[DYNAMIC]]/2",
      "Content-type": "text/xml; charset=utf-8",
      "SOAPAction": "http://tempuri.org/PlaylistService/GetPlaylist",
    },
    data = soap_msg,
    proxies = {"http": args.proxy} if args.proxy else None,
    timeout = 20
  )
  media_req_tree = etree.fromstring(media_req.text)
  
  if not media_req_tree.xpath("boolean(//ProgrammeTitle)"):
    arg_parser.error("media request failed")
  
  title = media_req_tree.xpath("//ProgrammeTitle/text()")[0]
  ep_title = media_req_tree.xpath("//EpisodeTitle/text()")[0]
  
  media_files = media_req_tree.xpath("//VideoEntries/Video/MediaFiles")[0]
  
  rtmp_url = media_files.xpath("@base")[0]
  media_file = media_files.xpath(
    "MediaFile[not(../MediaFile/@bitrate > @bitrate)]"
  )[0]
  bitrate = int(media_file.xpath("@bitrate")[0]) // 1000
  rtmp_playpath = media_file.xpath("URL/text()")[0]
  
  file_path = path.join(
    args.dir,
    args.filename if args.filename else re.sub(
      "[\W_]+",
      "-",
      "-".join(map(str, filter(None, (
        title,
        ep_title,
        bitrate,
        args.start,
        args.end if args.end > 0 else None
      ))))
    ).lower() + ".flv"
  )
  
  proc = subprocess.Popen(
    [
      "rtmpdump",
      "-r", rtmp_url,
      "--playpath", rtmp_playpath,
      "--pageUrl", args.url,
      "--swfVfy", "http://www.itv.com/mercury/Mercury_VideoPlayer.swf"
                  "?v=1.6.479/[[DYNAMIC]]/2"
      "--flashVer", "WIN 15,0,0,189",
      "--flv", file_path,
      "--resume" if args.resume else "",
      "--start={}".format(args.start),
      "--stop={}".format(args.end) if args.end > 0 else ""
    ]
  )
  try:
    proc.communicate()
  except KeyboardInterrupt:
    pass
