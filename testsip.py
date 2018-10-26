import re

pattern = "^Via:\\s+SIP/2\\.0/UDP\\s+([-.\\w]+):([0-9]+)(?:(?<[.0-9]+>;)|" \
          "(?<rport>;rport(?:=(?<\d.*>[0-9]+))?)|(?<\[0-9]+>;)|;[^;\\n\\s=]+(?:=[^;]*)?)*\\s*$"

what_test = "Via: SIP/2.0/UDP 192.168.1.4:62486;rport=12345;branch=z9hG4bK-524287-1---3ff9a622846c0a01;stck=3449406834;received=90.206.135.26";
print re.match(pattern, what_test)