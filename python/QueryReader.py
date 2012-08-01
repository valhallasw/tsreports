# Copyright (c) 2008 River Tarnell <river@wikimedia.org>. 
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely. This software is provided 'as-is', without any express or implied
# warranty.
#
# $Id: QueryReader.py 9 2008-09-15 20:07:32Z river $

def read(file):
	"""
	Read a formatted query file.
	
	The file looks like this:
	
	  %section
	  section contents...
	  %end
	  Now you can write any text outside a section and it's ignored.
	  %nextsection
	  more code
	  %end
	"""
	sections = []

	insect = False
	cursect = ''
	for line in file:
		line = line.rstrip()
		if len(line) == 0 or line[0] == '#':
			continue

		if not insect:
			if not line[0] == '%':
				continue
			bits = line.split(' ', 1)
			if bits[0] in ['%nightly']:
				sections.append( (bits[0][1:], "") )
				continue
			if len(bits) == 2:
				sections.append( (bits[0][1:], bits[1]) )
				continue
			insect = True
			cursect = line[1:]
			content = ''
			continue
		else:	# in section
			if len(line) >= 1 and line[0] == '#':
				continue
			if line == '%end':
				insect = False
				sections.append( (cursect, content) )
				continue
			else:
				content += line + "\n"

	return sections

#import sys
#se = read(file(sys.argv[1]))
#for s in se:
#	print "section [%s] value [%s]\n" % (s[0], s[1])
